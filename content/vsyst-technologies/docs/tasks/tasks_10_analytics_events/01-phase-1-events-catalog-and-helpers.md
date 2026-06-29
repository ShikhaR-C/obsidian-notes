# Phase 1 — Event Catalog + Helpers (no screen edits)

**Outcome:** the single source of truth (`src/config/events.js`) and a one-liner `track()` helper exist, and `firebase.js` gains user-context + breadcrumb helpers. Nothing in the UI changes yet, so this phase is risk-free to ship.

---

## 1.1 Create `src/config/events.js`

Modelled on `app-kavana-l/src/config/events.ts`, in JS with `Object.freeze` (project is JS per `AI.md`).

> **Coverage principle (verified against the codebase):** the `api_call` event already fires for **every** RTK Query endpoint (from `rtkQueryPerfLogger.js`), so raw endpoint-level coverage exists for free. The `EVENTS` catalog is therefore **curated for high-value business funnels** — it does **not** need a 1:1 entry per endpoint. Each event below was checked against a real RTK mutation in `src/store/apis/dzzlooms/` (named in the comment); the long tail (`fetch_*`, internal refreshes) stays on `api_call`.

```js
// src/config/events.js
// Single source of truth for Firebase Analytics event names, screen
// identifiers, and milestone thresholds. snake_case, object_action.
// Rules: name <= 40 chars, no firebase_/google_/ga_ prefix, ids go in
// params (never in the name), role is a default param (not in the name).

export const EVENTS = Object.freeze({
  // ── App lifecycle ──
  APP_OPENED: 'app_opened',
  TIME_TO_INTERACTIVE: 'time_to_interactive',

  // ── Auth funnel ──
  AUTH_SCREEN_VIEWED: 'auth_screen_viewed',
  LOGIN_ATTEMPTED: 'login_attempted',
  LOGIN_SUCCEEDED: 'login_succeeded',
  LOGIN_FAILED: 'login_failed',
  OTP_REQUESTED: 'otp_requested',
  OTP_VERIFIED: 'otp_verified',
  OTP_FAILED: 'otp_failed',
  FORGOT_PASSWORD_SUBMITTED: 'forgot_password_submitted', // auth_forgotPassword
  PASSWORD_RESET_SUBMITTED: 'password_reset_submitted', // auth_resetPassword
  LOGOUT: 'logout', // auth_logout

  // ── Onboarding / validation ──
  VALIDATE_USER_VIEWED: 'validate_user_viewed',
  USER_VERIFICATION_COMPLETED: 'user_verification_completed', // verifyUserStart/verifyUserEnd
  BETA_USER_SUBMITTED: 'beta_user_submitted', // auth_signup
  COMPANY_SELECTED: 'company_selected',

  // ── Orders ──
  NEW_ORDER_VIEWED: 'new_order_viewed',
  ORDER_CREATED: 'order_created', // add_order_msts
  ORDER_CREATE_FAILED: 'order_create_failed',
  ORDER_PROCESSED: 'order_processed', // process_order_msts (delivery/checkout)
  ORDER_STATUS_CHANGED: 'order_status_changed', // update_order_msts_status
  ORDER_DELETED: 'order_deleted', // delete_order_msts
  ORDER_OTP_VERIFIED: 'order_otp_verified', // OTPmodule / check_order_msts
  EMERGENCY_OTP_USED: 'emergency_otp_used', // EmergencyOTPBS

  // ── Sales orders (dealer) ──
  NEW_SALES_ORDER_VIEWED: 'new_sales_order_viewed',
  SALES_ORDER_CREATED: 'sales_order_created', // add_so_msts
  SALES_ORDER_EDITED: 'sales_order_edited', // update_so_msts
  SALES_ORDER_DELETED: 'sales_order_deleted', // delete_so_msts

  // ── Invoices ──
  NEW_INVOICE_VIEWED: 'new_invoice_viewed',
  INVOICE_CREATED: 'invoice_created', // add_invs
  INVOICE_UPDATED: 'invoice_updated', // update_invs
  INVOICE_EMAILED: 'invoice_emailed', // email_inv
  INVOICE_PDF_GENERATED: 'invoice_pdf_generated', // components/Download (client-side)
  INVOICE_DOWNLOADED: 'invoice_downloaded',

  // ── Payments / vouchers ──
  NEW_PAYMENT_VIEWED: 'new_payment_viewed',
  PAYMENT_RECORDED: 'payment_recorded', // add_voc_msts / add_dealer_voc_msts / add_cust_on_acc_voc_msts
  PAYMENT_FAILED: 'payment_failed',
  PAYMENT_STATUS_CHANGED: 'payment_status_changed', // updateVocStatus / updateCashOrderVocStatus
  PAYTM_INITIATED: 'paytm_initiated', // NewPayment/Paytm.js
  VOUCHER_CREATED: 'voucher_created', // {voucher_type}
  VOUCHER_EMAILED: 'voucher_emailed', // email_voc
  INVOICES_ATTACHED_TO_PAYMENT: 'invoices_attached_to_payment', // attachInvoices

  // ── Products / rates ──
  PRODUCT_CREATED: 'product_created', // add_prod_msts
  PRODUCT_UPDATED: 'product_updated', // update_prod_msts (UpdateProd)
  PRODUCT_RATE_SET: 'product_rate_set', // add_rate_msts / update_rate_msts
  PRODUCT_DISCOUNT_SET: 'product_discount_set', // add_prod_disc / edit_prod_disc
  PSOC_PRODUCTS_IMPORTED: 'psoc_products_imported', // import_psoc_prods
  PRODUCT_DATES_VIEWED: 'product_dates_viewed',

  // ── Relations / credit ──
  DEALER_ADDED: 'dealer_added', // add_dealer_custs (customer side)
  CUSTOMER_ADDED: 'customer_added', // add_dealer_custs (dealer side)
  DISCOUNT_SET: 'discount_set', // relation discount via update_dealer_custs (distinct from product_discount_set)
  CREDIT_LIMIT_CHANGED: 'credit_limit_changed', // update_dealer_custs (CreditLimitBS)
  TCS_TDS_SETTINGS_SAVED: 'tcs_tds_settings_saved', // update_dealer_custs (TCSTDSSettings)
  OPENING_BALANCE_SET: 'opening_balance_set', // update_first_bal_dealer_custs

  // ── Vehicles ──
  VEHICLE_ADDED: 'vehicle_added', // add_veh_msts
  DRIVER_ADDED: 'driver_added', // add_dvr_msts / add_dvr_cust
  DRIVER_ASSIGNED: 'driver_assigned', // replaceDriver
  DRIVER_FREED: 'driver_freed', // freeDriver
  VEHICLE_REQUEST_CREATED: 'vehicle_request_created', // add_veh_req {request_type: 'hire'|'rent'}
  VEHICLE_REQUEST_ACCEPTED: 'vehicle_request_accepted', // accept_hire_veh_req / accept_own_veh_req

  // ── Reports / exports ──
  REPORT_VIEWED: 'report_viewed',
  EXCEL_EXPORTED: 'excel_exported',
  PDF_EXPORTED: 'pdf_exported',
  DAILY_SUMMARY_VIEWED: 'daily_summary_viewed',
  ACCOUNT_STATEMENT_VIEWED: 'account_statement_viewed',
  ACCOUNT_STATEMENT_EMAILED: 'account_statement_emailed', // email_acc

  // ── Company / users ──
  COMPANY_SWITCHED: 'company_switched', // switch_sister_cust_msts / switch_sister_dealer_msts
  SISTER_COMPANY_VIEWED: 'sister_company_viewed',
  SISTER_COMPANY_ADDED: 'sister_company_added', // add_sister_cust_msts / add_sister_dealer_msts
  COMPANY_DELETED: 'company_deleted', // delete_company
  USER_INVITED: 'user_invited', // add_invite
  INVITE_ACCEPTED: 'invite_accepted', // accept_invite
  INVITE_DECLINED: 'invite_declined', // decline_invite
  USER_ADDED: 'user_added', // add_users
  USER_STATUS_CHANGED: 'user_status_changed', // activate_users / inactivate_users / remove_users
  CONTACT_US_SUBMITTED: 'contact_us_submitted', // add_contact_us

  // ── Engagement / UX ──
  SEARCH_PERFORMED: 'search_performed',
  FILTER_APPLIED: 'filter_applied',
  THEME_CHANGED: 'theme_changed',
  PULL_TO_REFRESH: 'pull_to_refresh',
  TAB_SWITCHED: 'tab_switched',

  // ── Settings / account ──
  SETTINGS_VIEWED: 'settings_viewed',
  DELETE_ACCOUNT_INITIATED: 'delete_account_initiated',
  DELETE_ACCOUNT_CONFIRMED: 'delete_account_confirmed',
  CODEPUSH_CHECKED: 'codepush_checked',

  // ── Activation milestones (see EVENT_TRIGGERS) ──
  FIRST_ORDER_CREATED: 'first_order_created',
  FIRST_INVOICE_CREATED: 'first_invoice_created',
  FIRST_PAYMENT_RECORDED: 'first_payment_recorded',

  // ── Error-adjacent ──
  ERROR_BOUNDARY_TRIGGERED: 'error_boundary_triggered',
  NETWORK_LOST: 'network_lost',
  NETWORK_RESTORED: 'network_restored',
});

// Canonical screen identifiers (the reference app's `screenSources`), passed
// as a `source` param so the same event from different origins is
// distinguishable. VALUES mirror the ACTUAL React Navigation route names (from
// src/navigation/{Auth,Customer,Dealer,Common}) so they line up with the
// auto-tracked screen_view events — keep them in sync if routes are renamed.
//
// Grouping convention (per request):
//   AUTH_*   — auth stack         (src/navigation/Auth)
//   COMMON_* — registered in BOTH role trees; role is a default param so the
//              same route under customer vs dealer is already distinguishable
//   CUST_*   — customer-only routes (src/navigation/Customer/{Main,TrnTab})
//   DLR_*    — dealer-only routes   (src/navigation/Dealer/{Main,TrnTab})
export const SCREENS = Object.freeze({
  // ── Auth ──
  AUTH_WELCOME: 'Welcome',
  AUTH_LOGIN: 'Login',
  AUTH_FORGOT_PASSWORD: 'ForgotPassword',
  AUTH_CUSTOMER_SIGNUP: 'Customer', // beta-user customer registration
  AUTH_DEALER_SIGNUP: 'Dealer', // beta-user dealer registration
  AUTH_VALIDATE_USER: 'validateUser',

  // ── Common (both role trees) ──
  COMMON_ORDERS: 'Orders',
  COMMON_INVOICES: 'Invoices',
  COMMON_INVOICES_TAB: 'InvoicesTab',
  COMMON_INVOICE_DETAIL: 'Invoice',
  COMMON_PAYMENTS: 'Payments',
  COMMON_PAYMENTS_TAB: 'PaymentsTab',
  COMMON_ACCOUNTS: 'Accounts',
  COMMON_ADV_DEP_LEDGER: 'AdvDepLedger',
  COMMON_REPORTS: 'Reports',
  COMMON_DAILY_REPORT: 'DailyReport',
  COMMON_DAILY_SUMMARY: 'DailySummary',
  COMMON_TCS_TDS_REPORT: 'TcsTdsReport',
  COMMON_PRODUCT_DATES: 'ProductDates',
  COMMON_DEALER_PRODUCTS: 'DProducts', // shared dealer-product browser
  COMMON_DISCOUNT: 'Discount',
  COMMON_NOTIFICATIONS: 'Notifications',
  COMMON_USERS: 'Users',
  COMMON_ADD_EDIT_USER: 'AddEditUsers',
  COMMON_ADD_EDIT_COMPANY: 'AddEditCompany',
  COMMON_COMPANY_PROFILE: 'CompanyProfile',
  COMMON_PROFILE: 'Profile',
  COMMON_SETTINGS: 'settings',
  COMMON_DELETE_ACCOUNT: 'DeleteAccount',
  COMMON_HELP: 'help',
  COMMON_CONTACT_US: 'ContactUs',
  COMMON_INVOICE_DETAILS_NAV: 'details',

  // ── Customer-only ──
  CUST_NEW_ORDER: 'NewOrder',
  CUST_NEW_PAYMENT: 'NewPayment',
  CUST_NEW_PAYMENT_ACK: 'NewPayAck',
  CUST_DEALER_ORDER: 'DealerOrder', // customer viewing a dealer's order
  CUST_ACCOUNTS_TXN: 'CPAccounts', // customer-party sectional accounts
  CUST_DEALERS: 'Dealers',
  CUST_ADD_DEALER: 'AddDealers',
  CUST_DEALER_SETTINGS: 'DealerSettings',
  CUST_COMPANY: 'CustomerCompany',
  CUST_VEHICLES: 'Vehicles',
  CUST_VEHICLE_REQUESTS: 'VehicleRequests',
  CUST_VEHICLE_REPORTS: 'VehicleReports',
  CUST_OTP_MANAGER: 'OTPManager',

  // ── Dealer-only ──
  DLR_NEW_SALES_ORDER: 'NewSalesOrder',
  DLR_EDIT_SALES_ORDER: 'EditSalesOrder',
  DLR_NEW_INVOICE: 'NewInvoice',
  DLR_NEW_INVOICE_SUMMARY: 'NewInvoiceSummary',
  DLR_NEW_VOUCHER: 'NewVoucher',
  DLR_CUSTOMER_ORDER: 'CustomerOrder', // dealer viewing a customer's order
  DLR_ACCOUNTS_TXN: 'DPAccounts', // dealer-party sectional accounts
  DLR_CUSTOMERS: 'Customers',
  DLR_CUSTOMER_SETTINGS: 'CustSettings',
  DLR_COMPANY: 'DealerCompany',
  DLR_PRODUCTS: 'Products',
  DLR_PSOC_PRODUCTS: 'PsocProds',
  DLR_SET_PRODUCT_RATE: 'SetProductRate',
  DLR_UPDATE_PRODUCT: 'UpdateProd',
});

// Named CTA / origin sources for ambiguous buttons (reference `CTA_SOURCES`).
export const SOURCES = Object.freeze({
  ORDER_LIST_ROW: 'order_list_row',
  ORDER_DETAIL: 'order_detail',
  DRAWER: 'drawer',
  TAB_BAR: 'tab_bar',
  EMPTY_STATE_CTA: 'empty_state_cta',
});

// Milestone thresholds (reference `EVENT_TRIGGERS`). Fire the milestone event
// when the running count crosses the threshold (compare against a persisted
// AsyncStorage counter, not the API total, to fire exactly once).
export const EVENT_TRIGGERS = Object.freeze({
  FIRST_ORDER_CREATED: 1,
  FIRST_INVOICE_CREATED: 1,
  FIRST_PAYMENT_RECORDED: 1,
});
```

> **Naming review gate:** before merging, eyeball every value against the GA4 limits (≤40 chars, no reserved prefix). A quick test asserts this (see 1.4).

---

## 1.2 Extend `src/utils/firebase.js`

Add three helpers; keep the existing exports byte-for-byte stable (they're already consumed by middleware + `RestartContext`).

```js
import deviceInfo from 'react-native-device-info'; // already a dependency (^15)

// Set all queryable dimensions at once: call on login and on company switch.
// - setDefaultEventParameters(): attaches role/company_id/app_version to EVERY
//   analytics event automatically (incl. the existing `api_call`) — the
//   reference app's pattern (firebaseAnalytics.ts). track() then stays thin.
// - setUserProperty(): registers them as GA4 user properties (segmentation).
// - crashlytics().setAttribute(): same keys on every crash report.
// `accountVerified` is the role-appropriate verified flag (dealer_verified for
// dealers, cust_verified for customers) — there is NO user_status field.
export const setUserContext = async ({ userId, role, companyId, accountVerified, scope } = {}) => {
  const appVersion = deviceInfo.getVersion();
  const r = role != null ? String(role) : undefined;
  const c = companyId != null ? String(companyId) : undefined;
  try {
    // One call → default param on every future event. Keys must be non-null.
    await analytics().setDefaultEventParameters({
      ...(r ? { role: r } : {}),
      ...(c ? { company_id: c } : {}),
      app_version: appVersion,
    });
    await Promise.all([
      setUser(userId), // existing helper: sets crashlytics + analytics user id
      r && analytics().setUserProperty('role', r),
      r && crashlytics().setAttribute('role', r),
      c && analytics().setUserProperty('company_id', c),
      c && crashlytics().setAttribute('company_id', c),
      accountVerified != null && analytics().setUserProperty('account_verified', String(!!accountVerified)),
      scope && analytics().setUserProperty('scope', String(scope)),
      analytics().setUserProperty('app_version', appVersion),
      crashlytics().setAttribute('app_version', appVersion),
    ].filter(Boolean));
  } catch (e) {
    console.warn('[firebase] setUserContext failed', e);
  }
};

// Crashlytics breadcrumb — cheap, synchronous-ish trail that shows up above a
// crash. Call on navigation + before risky actions.
export const logBreadcrumb = message => {
  try {
    crashlytics().log(message);
  } catch (e) {
    /* ignore */
  }
};

// Attach the current screen as a Crashlytics attribute so every crash report
// names the screen the user was on.
export const setScreenAttr = screenName => {
  try {
    crashlytics().setAttribute('screen', String(screenName ?? ''));
  } catch (e) {
    /* ignore */
  }
};
```

> `react-native-device-info@^15` is already in `package.json` — no new dependency.

---

## 1.3 Create `src/utils/analytics.js` (thin call-site layer)

Keeps every call-site a one-liner and injects cross-cutting default params so we never repeat `role`/`company_id`. Gated by a Remote Config kill-switch.

`role`/`company_id`/`app_version` are already attached to every event via `setDefaultEventParameters` (see 1.2), so `track()` does **not** re-inject them — it only adds the kill-switch and a dev log. This keeps it a true one-liner.

```js
// src/utils/analytics.js
import { logEvent, getRemoteValue } from './firebase';

// Remote Config kill-switch (default true; set false in console to silence
// analytics in prod without a release). Returns boolean; never throws.
const enabled = () => {
  try {
    const v = getRemoteValue('analytics_enabled');
    return v?.asBoolean?.() ?? true;
  } catch {
    return true;
  }
};

// Fire-and-forget. Never await this on a hot path. role/company_id/app_version
// ride along as default event params (set in setUserContext), so callers pass
// only event-specific params here.
export const track = (name, params = {}) => {
  if (__DEV__) console.log('[analytics]', name, params); // reference parity: analyticsLogger
  if (!enabled()) return Promise.resolve();
  return logEvent(name, params);
};
```

Add `analytics_enabled: true` to the `initRemoteConfig({})` defaults call in `AppNavigatorContainer.js`:

```js
initRemoteConfig({ analytics_enabled: true });
```

---

## 1.4 Tests (`__tests__`)

The app already has Jest (`jest.config.js`, `jest.setup.js`). Add a catalog sanity test — no Firebase mock needed since it only inspects the constants:

```js
// __tests__/events.test.js
import { EVENTS, SCREENS } from '../src/config/events';

describe('events catalog', () => {
  const names = Object.values(EVENTS);

  it('every event name is GA4-valid', () => {
    for (const n of names) {
      expect(n).toMatch(/^[a-z][a-z0-9_]{0,39}$/);          // <=40, snake_case
      expect(n).not.toMatch(/^(firebase_|google_|ga_)/);    // no reserved prefix
    }
  });

  it('has no duplicate event names', () => {
    expect(new Set(names).size).toBe(names.length);
  });

  it('screen ids are unique', () => {
    const s = Object.values(SCREENS);
    expect(new Set(s).size).toBe(s.length);
  });
});
```

---

## Phase 1 checklist

- [ ] `src/config/events.js` created (`EVENTS`, `SCREENS`, `SOURCES`, `EVENT_TRIGGERS`).
- [ ] `firebase.js` gains `setUserContext`, `logBreadcrumb`, `setScreenAttr` (existing exports untouched).
- [ ] `src/utils/analytics.js` `track()` helper created with kill-switch.
- [ ] `initRemoteConfig({ analytics_enabled: true })` default added.
- [ ] `__tests__/events.test.js` passes (`yarn test`).
- [ ] `yarn lint` clean.

No screens changed → safe to merge & ship independently.
