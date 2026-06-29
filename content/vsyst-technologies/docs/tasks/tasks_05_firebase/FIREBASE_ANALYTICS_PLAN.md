# Plan: Firebase Analytics — Event Instrumentation for DZZLO OMS

> Companion to `FIREBASE_INTEGRATION_PLAN.md`. That plan installs `@react-native-firebase/analytics` and wires global screen tracking inside every `NavigationContainer`. **This** plan focuses exclusively on **what events to fire, where, and with which parameters** — across Customer, Dealer, Auth and Common screens. Assume Firebase is already initialized and `logScreenView` is already called on every navigation change (Step 6 of the integration plan).

---

## 1. Firebase Analytics — Quick Tutorial

Firebase Analytics (Google Analytics for Firebase) is a free, unlimited event-reporting SDK. It records named **events** with up to **25 parameters** each, attaches them to an **installation ID** (or a `user_id` you set), and lets you:

- See real-time events in **DebugView** (enabled on a device),
- Explore usage in **Dashboard / Events / Audiences / Funnels / Retention**,
- Export raw event data to **BigQuery**,
- Use events as triggers for **Remote Config**, **A/B Testing**, and **Cloud Messaging** audiences.

### Core concepts

| Concept           | Meaning                                                                                                                                                    |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Event**         | A named action. `snake_case`, ≤40 chars, ≤500 distinct names/app. Don't collide with [reserved names](https://support.google.com/firebase/answer/9237506). |
| **Parameter**     | Key/value attached to an event. ≤25 params/event, key ≤40 chars, string value ≤100 chars. Numbers OK too.                                                  |
| **User property** | Long-lived trait on the user (e.g. `role`, `company_scope`, `theme`). Max 25 per app.                                                                      |
| **User ID**       | Stable app-level identifier (`setUserId`). Distinct from Google's random `app_instance_id`. Required for cross-device joins.                               |
| **Screen view**   | Special event `screen_view`, fired by the SDK when `logScreenView` is called. Surfaces in Screens report.                                                  |
| **DebugView**     | Real-time event stream for a specific device with `adb shell setprop debug.firebase.analytics.app <pkg>` / `-FIRDebugEnabled` launch arg.                  |

### Reserved / automatic events (do NOT re-use these names)

`app_remove`, `app_update`, `first_open`, `session_start`, `screen_view`, `user_engagement`, `in_app_purchase`, `login`, `sign_up`, `search`, `select_content`, `share`, `view_item`, `view_item_list`.

> **Note:** `login`, `sign_up`, `search`, `select_content`, `view_item` are **recommended** names — use them when they fit (Google renders them nicely in the dashboard). That's why the Auth plan below uses `login` and `sign_up` rather than `auth_login_success` / `auth_register_submit`.

---

## 2. Useful Methods (via `@react-native-firebase/analytics`)

All examples assume `import analytics from '@react-native-firebase/analytics';` **or** the helpers added to `src/utils/firebase.js` in the integration plan.

| Method                                                     | When to call                                                                                                      |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `analytics().logEvent(name, params)`                       | Every custom event below. Keys/values are coerced to string/number.                                               |
| `analytics().logScreenView({ screen_name, screen_class })` | Inside `onStateChange` of each `NavigationContainer` (see Step 6 of integration plan).                            |
| `analytics().setUserId(id)`                                | After login, using the app's user id. Pass `null` on logout.                                                      |
| `analytics().setUserProperty(name, value)`                 | Role (`customer`/`dealer`), `user_scope`, `company_id`, `theme`, `verified_email`.                                |
| `analytics().setUserProperties({ ... })`                   | Convenience — set several at once.                                                                                |
| `analytics().setAnalyticsCollectionEnabled(bool)`          | Respect an in-app "share diagnostics" switch if you add one.                                                      |
| `analytics().logLogin({ method })`                         | Recommended wrapper for login success. `method` = `'password'` / `'otp'` / `'email'`.                             |
| `analytics().logSignUp({ method })`                        | Recommended wrapper for registration success.                                                                     |
| `analytics().logSearch({ search_term })`                   | Global search box (if one exists) — for lists, prefer a custom `list_search` event so you can scope to list type. |
| `analytics().logSelectContent({ content_type, item_id })`  | Tapping a list row. Handy: shows up under "Content" in dashboard.                                                 |
| `analytics().logShare({ method, content_type, item_id })`  | "Share invoice / order" actions.                                                                                  |
| `analytics().resetAnalyticsData()`                         | On account deletion only.                                                                                         |
| `analytics().setDefaultEventParameters({ ... })`           | Globally attach `role`, `app_version`, `company_id` to every event (reduces per-call repetition — see §6).        |

> **Rule of thumb:** prefer recommended events (`login`, `sign_up`, `select_content`, `search`, `share`, `view_item`) where they fit. Use custom `snake_case` names for everything else.

---

## 3. Parameter Conventions for DZZLO OMS

Define once in `src/utils/analyticsEvents.js` (see §9) and reuse everywhere.

### Global params (attached to every event via `setDefaultEventParameters`)

| Param         | Source                                      | Example               |
| ------------- | ------------------------------------------- | --------------------- |
| `role`        | `selectUserScope` from auth slice           | `customer` / `dealer` |
| `company_id`  | current active company in auth state        | `c_123`               |
| `app_version` | `DeviceInfo.getVersion()` (once at startup) | `1.76.100`            |

### Per-event params (pass at call site)

| Param name       | Type   | Use                                                                  |
| ---------------- | ------ | -------------------------------------------------------------------- |
| `screen_name`    | string | Always set when the event originates from a named screen.            |
| `item_id`        | string | Business entity id (`order_id` / `invoice_id` / `payment_id` / etc). |
| `item_type`      | string | `order`, `invoice`, `payment`, `voucher`, `user`, `vehicle`, …       |
| `amount`         | number | In base currency units (paise). Never string.                        |
| `count`          | number | Number of items affected (selected rows, page size).                 |
| `status`         | string | `ok`, `err`, `pending`, `paid`, …                                    |
| `filter_type`    | string | Which filter was applied: `status`, `date_range`, `company`, …       |
| `filter_value`   | string | The filter value — `unpaid`, `last_7_days`, `c_123`.                 |
| `search_term`    | string | Trim + lowercase at call site. **Do not log PII.**                   |
| `failure_reason` | string | `network`, `validation`, `server_401`, `server_500`, …               |
| `duration_ms`    | number | Optional — for flows you want to time yourself.                      |

> **PII rule:** never put phone numbers, full emails, addresses, passwords, or free-text user content into analytics params. Hash or truncate if you must (e.g. `phone_country: 'IN'`, `email_domain: 'gmail.com'`).

---

## 4. Screen Type Taxonomy — Where Events Live

The app has **no single `NavigationContainer`**. Instead, `AppNavigatorContainer.js` swaps between role-based trees:

```
AppNavigatorContainer
├── AuthNavigator (Stack)             — not logged in
├── CustomerDrawer (Drawer)           — role = customer
│   ├── customerTab (BottomTabs)      — Orders / Invoices / Payments
│   ├── customer      (Stack: Profile, CompanyProfile, Notifications, OTPManager)
│   ├── customerCompany (Stack)
│   ├── customerDealer  (Stack: Dealers, DealerSettings, AddDealers, DiscountScreen, PayOnAc)
│   ├── customerUser    (Stack: Users, AddEditUsers)
│   ├── customerVehicle (Tab → Stack: Vehicles, Drivers, Requests)
│   ├── dProducts       (Stack: Products, ProductDates)
│   ├── customerReport  (Stack: Reports, DailyReport, TcsTds)
│   ├── details         (Stack: Invoice, Order, Voucher detail screens)
│   ├── settings / help / redux  (Stacks)
│   └── validateUser (Stack — shown until email+phone verified)
├── DealerDrawer (Drawer)             — role = dealer
│   ├── dealerTab (BottomTabs)        — Orders / Invoices / Payments
│   ├── dealer + DealerCustomer + DealerUser + DealerCompany + DealerProduct + DealerReport Stacks …
│   └── details / settings / help (shared with Customer)
```

### Event distribution by screen-type

| Screen type     | What belongs here                                                                                                                                                            | Event patterns                                                                                                        |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Drawer**      | Role-level navigation: opening/closing the drawer, jumping to a drawer item, logout, theme switch via drawer footer.                                                         | `drawer_open`, `drawer_item_select` (param: `target`), `logout`                                                       |
| **BottomTab**   | Tab switches on `customerTab` / `dealerTab` / `customerVehicle` tab.                                                                                                         | `tab_switch` (params: `tab_from`, `tab_to`, `tab_group`)                                                              |
| **Stack**       | The bulk — every list, form, detail screen. Fire lifecycle + action events.                                                                                                  | `list_view_load`, `list_filter_apply`, `list_search`, `list_refresh`, `list_item_select`, `form_submit`, `form_error` |
| **Modal**       | Full-screen modals (e.g. `OTPmodule`, `PassModal`, alert confirmations).                                                                                                     | `modal_open`, `modal_submit`, `modal_dismiss`                                                                         |
| **BottomSheet** | The many `BSheet` components: `SelectVehicle`, `SelectDealer`, `SelectProduct`, `AttachInvs`, `SelectCustomers`, `AddDealerBS`, `InfoVehicle`, `InviteUser`, `SummaryModal`. | `sheet_open`, `sheet_submit`, `sheet_item_select`, `sheet_dismiss`                                                    |
| **Inline UI**   | Inline toggles, switches, sort/order controls that don't open a new screen.                                                                                                  | Domain-specific: `settings_theme_change`, `notif_toggle`, `list_sort_change`                                          |

> **Screen-view events** (`screen_view`) are auto-fired by the `onStateChange` hook in §6 of the integration plan — Stack/Tab/Drawer screens all appear there. **Bottom sheets are NOT screens** in React Navigation terms → fire a manual `sheet_open` event on mount of each sheet to capture them.

---

## 5. Screen Sources Inventory

Relative to `dzzlo_oms_app/src/`.

### 5.1 Auth group (`screens/Login/` + `screens/Common/ValidateUser`)

| Screen          | Nav type | Source file                                   |
| --------------- | -------- | --------------------------------------------- |
| Welcome         | Stack    | `screens/Login/AuthNavigator/Welcome*`        |
| Login           | Stack    | `screens/Login/AuthNavigator/Login*`          |
| Customer Signup | Stack    | `screens/Login/AuthNavigator/Customer*`       |
| Dealer Signup   | Stack    | `screens/Login/AuthNavigator/Dealer*`         |
| ForgotPassword  | BSheet   | `screens/Login/AuthNavigator/ForgotPassword*` |
| ValidateUser    | Stack    | `screens/Common/ValidateUser`                 |

### 5.2 Customer group (`screens/Customer/`)

Companies · CompanyProfile · Dealers · Invoices · NewOrder · NewPayment · Notifications · Orders · Payments · Profile · Requests · Users · VehicleReports · Vehicles — full table in §7.2.

### 5.3 Dealer group (`screens/Dealer/`)

Companies · CompanyProfile · Customers · EditSalesOrder · Invoices · NewInvoice · NewSalesOrder · NewVoucher · Notifications · Orders · Payments · ProductDates · Products · Profile · Users — full table in §7.3.

### 5.4 Common group (`screens/Common/`)

Accounts · CompanyUsers · ContactUs · DailySummary · Help · Invites · Invoices · Orders · Payments · Products · Profile · RelationList · Reports · Requests · Settings · SisterCompanies · Users · ValidateUser · Vehicles · `_Invoice_` · `_Order_` · `_Voucher_` — full table in §7.4.

---

## 6. Global Setup (one-time)

### 6.1 Attach role / company / version to every event

In `App.js` after auth state is hydrated:

```js
import analytics from "@react-native-firebase/analytics";
import DeviceInfo from "react-native-device-info";

analytics().setDefaultEventParameters({
  app_version: DeviceInfo.getVersion(),
});

// Keep this in sync with the auth slice
store.subscribe(() => {
  const s = store.getState();
  const role = selectUserScope(s);
  const companyId = selectActiveCompanyId(s);
  const userId = selectUserId(s);
  analytics().setDefaultEventParameters({
    app_version: DeviceInfo.getVersion(),
    role,
    company_id: companyId,
  });
  analytics().setUserId(userId ?? null);
  if (role) analytics().setUserProperty("role", role);
});
```

### 6.2 Drawer / Tab events

Add to `navigation/Customer/Drawer.js` and `navigation/Dealer/Drawer.js`:

```js
<Drawer.Navigator
  screenListeners={{
    drawerItemPress: (e) => {
      analytics().logEvent('drawer_item_select', { target: e.target });
    },
  }}
>
```

Add to both `TrnTab.js` files:

```js
<Tab.Navigator
  screenListeners={({ route }) => ({
    tabPress: () => {
      analytics().logEvent('tab_switch', { tab_group: 'trn', tab_to: route.name });
    },
  })}
>
```

### 6.3 Bottom-sheet helper

Because sheets aren't tracked by `logScreenView`, wrap every `BottomSheet` open with:

```js
// src/hooks/useLogSheet.js
import { useEffect } from "react";
import analytics from "@react-native-firebase/analytics";

export const useLogSheet = (sheetName, isVisible, params = {}) => {
  useEffect(() => {
    if (isVisible)
      analytics().logEvent("sheet_open", { sheet_name: sheetName, ...params });
  }, [isVisible, sheetName]);
};
```

---

## 7. Event Catalog by Group

> Naming rules applied below:
>
> - Prefix: `auth_`, `customer_`, `dealer_`, or none for Common (reused across roles — `role` default param disambiguates).
> - Verbs: `view`, `create`, `update`, `delete`, `submit`, `select`, `filter`, `search`, `refresh`, `toggle`.
> - Keep names ≤40 chars. Lowercase snake_case.

### 7.1 Auth group

| Screen          | Screen type | Action                           | Event                         | Params                                                   |
| --------------- | ----------- | -------------------------------- | ----------------------------- | -------------------------------------------------------- |
| Welcome         | Stack       | Tap "Login"                      | `auth_login_navigate`         | —                                                        |
| Welcome         | Stack       | Tap "Register Customer / Dealer" | `auth_register_navigate`      | `role`                                                   |
| Login           | Stack       | Toggle show password             | `auth_password_show_toggle`   | `shown`                                                  |
| Login           | Stack       | Submit credentials               | `auth_credential_submit`      | `login_method` (`email`/`phone`)                         |
| Login           | Stack       | OTP requested                    | `auth_otp_request`            | `login_method`                                           |
| Login           | Stack       | OTP verified OK                  | `login` _(recommended)_       | `method: 'otp'`                                          |
| Login           | Stack       | OTP verify failed                | `auth_otp_verify_failed`      | `failure_reason`                                         |
| Login           | Stack       | Password login OK                | `login` _(recommended)_       | `method: 'password'`                                     |
| Login           | Stack       | Login failed                     | `auth_login_failed`           | `login_method`, `failure_reason`                         |
| ForgotPassword  | BSheet      | Open                             | `sheet_open`                  | `sheet_name: 'forgot_password'`                          |
| ForgotPassword  | BSheet      | Submit reset request             | `auth_forgot_password_submit` | `method`                                                 |
| ForgotPassword  | BSheet      | Reset confirmed                  | `auth_reset_password_confirm` | `status`                                                 |
| Customer Signup | Stack       | Submit                           | `sign_up` _(recommended)_     | `method`, `role: 'customer'`                             |
| Customer Signup | Stack       | Submit failed                    | `auth_register_failed`        | `role: 'customer'`, `failure_reason`, `field_error_type` |
| Dealer Signup   | Stack       | Submit                           | `sign_up` _(recommended)_     | `method`, `role: 'dealer'`                               |
| Dealer Signup   | Stack       | Submit failed                    | `auth_register_failed`        | `role: 'dealer'`, `failure_reason`                       |
| ValidateUser    | Stack       | Verify email                     | `auth_email_verify`           | `status`                                                 |
| ValidateUser    | Stack       | Verify phone                     | `auth_phone_verify`           | `status`                                                 |
| Any             | —           | Logout                           | `logout`                      | `initiated_from` (`drawer`/`settings`)                   |

### 7.2 Customer group

| Screen         | Screen type           | Action                                 | Event                                                              | Params                                        |
| -------------- | --------------------- | -------------------------------------- | ------------------------------------------------------------------ | --------------------------------------------- |
| Orders (list)  | BottomTab → Stack     | Filter status                          | `customer_order_list_filter`                                       | `filter_value`                                |
| Orders         | Stack                 | Search                                 | `customer_order_list_search`                                       | `search_term`                                 |
| Orders         | Stack                 | Pull-to-refresh                        | `customer_order_list_refresh`                                      | `count`                                       |
| Orders         | Stack                 | Tap row                                | `select_content` _(recommended)_                                   | `content_type: 'order'`, `item_id`            |
| NewOrder       | Stack                 | Open SelectVehicle sheet               | `sheet_open`                                                       | `sheet_name: 'select_vehicle'`                |
| NewOrder       | BSheet                | Vehicle selected                       | `customer_order_vehicle_select`                                    | `item_id`                                     |
| NewOrder       | BSheet                | Dealer selected                        | `customer_order_dealer_select`                                     | `item_id`                                     |
| NewOrder       | BSheet                | Product selected                       | `customer_order_product_select`                                    | `item_id`                                     |
| NewOrder       | Stack                 | Quantity changed                       | `customer_order_quantity_input`                                    | `item_id`, `quantity`                         |
| NewOrder       | Stack                 | Assign driver                          | `customer_order_driver_assign`                                     | `item_id`                                     |
| NewOrder       | Stack                 | Credit summary viewed                  | `customer_order_credit_view`                                       | `amount`                                      |
| NewOrder       | Stack                 | Submit                                 | `customer_order_create`                                            | `item_id`, `amount`, `count`                  |
| NewOrder       | Stack                 | Update existing                        | `customer_order_update`                                            | `item_id`, `amount`                           |
| Invoices       | BottomTab → Stack     | Filter                                 | `customer_invoice_list_filter`                                     | `filter_value`                                |
| Invoices       | Stack                 | Search                                 | `customer_invoice_list_search`                                     | `search_term`                                 |
| Invoices       | Stack                 | Tap row                                | `select_content`                                                   | `content_type: 'invoice'`, `item_id`          |
| NewPayment     | Stack                 | Submit voucher                         | `customer_payment_submit`                                          | `item_id`, `amount`, `count`                  |
| NewPayment     | BSheet (ShowInvsBS)   | Toggle invoice                         | `customer_payment_invoice_toggle`                                  | `item_id`                                     |
| NewPayment     | Stack                 | Toggle TDS                             | `customer_payment_tds_toggle`                                      | `enabled`                                     |
| Payments       | BottomTab → Stack     | Filter / search / tap                  | `customer_payment_list_*`                                          | —                                             |
| Dealers        | Stack                 | Search / sort / refresh                | `customer_dealer_list_*`                                           | —                                             |
| Dealers        | Stack                 | Tap dealer row                         | `select_content`                                                   | `content_type: 'dealer'`, `item_id`           |
| Dealers        | Stack                 | Tap balance / credit / daily           | `customer_dealer_{balance\|credit\|daily}_view`                    | `item_id`                                     |
| AddDealers     | BSheet                | Submit                                 | `customer_dealer_create`                                           | `item_id`                                     |
| DealerSettings | Stack                 | Tax toggle / update                    | `customer_dealer_tax_toggle` / `customer_dealer_tax_update`        | `tax_type`, `enabled`, `percentage`           |
| Vehicles       | Tab → Stack           | Tab switch vehicle/driver              | `tab_switch`                                                       | `tab_group: 'customer_vehicle'`, `tab_to`     |
| Vehicles       | Stack                 | Search / filter / refresh              | `customer_vehicle_list_*`                                          | —                                             |
| Vehicles       | BSheet (AddVehicle)   | Submit                                 | `customer_vehicle_create`                                          | `item_id`                                     |
| Vehicles       | BSheet (AssignDriver) | Select                                 | `customer_vehicle_driver_assign`                                   | `item_id`, `driver_id`                        |
| Vehicles       | BSheet (AddDriver)    | Submit                                 | `customer_driver_create`                                           | `item_id`                                     |
| VehicleReports | Stack                 | Date range / sort / refresh / view     | `customer_vehicle_report_*`                                        | `start_date`, `end_date`, `item_id`           |
| Requests       | Stack (Tab)           | Hire/rent tab switch                   | `customer_vehicle_request_tab_switch`                              | `tab_to`                                      |
| Requests       | Stack                 | Submit hire/rent                       | `customer_vehicle_{hire\|rent}_submit`                             | `item_id`                                     |
| Users          | Stack                 | Open invite                            | `customer_user_invite_open`                                        | —                                             |
| Users          | Stack                 | Submit invite                          | `customer_user_invite_submit`                                      | `invite_type`                                 |
| AddEditUsers   | Stack                 | Activate / deactivate / remove / role  | `customer_user_{activate\|deactivate\|remove\|role_update}`        | `item_id`, `new_role`                         |
| OTPManager     | Stack                 | Set manager                            | `customer_user_otp_manager_set`                                    | `item_id`                                     |
| Companies      | Stack                 | AddEditCompany submit                  | `customer_company_save`                                            | `item_id`                                     |
| CompanyProfile | Stack                 | Setting toggle / field update          | `customer_profile_{setting_toggle\|field_update\|location_select}` | `setting_name`, `state_name`, `district_name` |
| Profile        | Stack                 | Address update / refresh / pic upload  | `customer_profile_{address_update\|refresh\|picture_upload}`       | —                                             |
| Notifications  | Stack                 | Toggle type / disable all / enable all | `customer_notification_{toggle\|disable_all\|enable_all}`          | `notification_type`, `enabled`                |

### 7.3 Dealer group

| Screen         | Screen type              | Action                                 | Event                                                                       | Params                                      |
| -------------- | ------------------------ | -------------------------------------- | --------------------------------------------------------------------------- | ------------------------------------------- |
| Orders         | BottomTab → Stack        | Status filter                          | `dealer_order_status_filter`                                                | `filter_value`                              |
| Orders         | Stack                    | Search / pagination                    | `dealer_order_{search\|pagination}`                                         | `search_term`, `page_number`, `count`       |
| Orders         | Stack                    | Tap row                                | `select_content`                                                            | `content_type: 'order'`, `item_id`          |
| Orders         | Modal (OTPmodule)        | Driver OTP verify                      | `dealer_order_otp_verify`                                                   | `item_id`, `status`                         |
| Orders         | Stack                    | Process order                          | `dealer_order_process`                                                      | `item_id`, `process_type`                   |
| Orders         | Stack                    | Edit SO open                           | `dealer_order_edit_open`                                                    | `item_id`                                   |
| NewSalesOrder  | Stack                    | Add product / qty                      | `dealer_product_add` / `dealer_product_quantity_update`                     | `item_id`, `quantity`                       |
| NewSalesOrder  | Stack                    | Cash reimbursement                     | `dealer_cash_reimb_add`                                                     | `amount`                                    |
| NewSalesOrder  | Stack                    | Submit                                 | `dealer_sales_order_submit`                                                 | `item_id`, `amount`, `count`                |
| NewSalesOrder  | Modal                    | Amount mismatch warning                | `dealer_sales_order_warning`                                                | `warning_type`                              |
| EditSalesOrder | Stack                    | Qty / reimb update                     | `dealer_so_{product_update\|reimb_update}`                                  | `item_id`, `quantity`, `amount`             |
| EditSalesOrder | Stack                    | Save / delete                          | `dealer_so_{update_submit\|delete}`                                         | `item_id`                                   |
| Invoices       | BottomTab → Stack        | Filter / search / refresh / paginate   | `dealer_invoice_{filter\|search\|list_refresh\|pagination}`                 | `filter_value`, `count`                     |
| NewInvoice     | Stack                    | Customer / order select                | `dealer_invoice_{customer_select\|order_select}`                            | `item_id`, `count`, `amount`                |
| NewInvoice     | BSheet (SummaryModal)    | Date / type select                     | `dealer_invoice_{date_select\|type_select}`                                 | `invoice_type`, `invoice_date`              |
| NewInvoice     | BSheet                   | Submit                                 | `dealer_invoice_create`                                                     | `item_id`, `amount`, `count`                |
| NewInvoice     | Stack                    | Preview                                | `dealer_invoice_preview`                                                    | `item_id`                                   |
| Payments       | BottomTab → Stack        | Filter / search / paginate             | `dealer_payment_{filter\|search\|pagination}`                               | —                                           |
| Payments       | BSheet (AttachInvs)      | Attach                                 | `dealer_payment_invoice_attach`                                             | `item_id`, `count`, `amount`                |
| NewVoucher     | BSheet (SelectCustomers) | Customer select                        | `dealer_voucher_customer_select`                                            | `item_id`                                   |
| NewVoucher     | Stack                    | Submit                                 | `dealer_voucher_submit`                                                     | `item_id`, `amount`, `count`                |
| Customers      | Stack                    | Search / filter / sort                 | `dealer_customer_{search\|filter\|sort}`                                    | `search_term`, `filter_value`, `sort_field` |
| Customers      | Modal (credit)           | Open                                   | `dealer_customer_credit_view`                                               | `item_id`, `amount`                         |
| Products       | Stack                    | Open PSOC / Other                      | `dealer_product_{psoc_view\|other_view}`                                    | `item_id`, `count`                          |
| ProductDates   | Stack                    | Month change / rate CRUD               | `dealer_product_rate_{month_view\|create\|update\|delete}`                  | `item_id`, `amount`                         |
| Users          | Stack                    | Invite / credit view                   | `dealer_user_{invite\|credit_view}`                                         | `item_id`, `amount`                         |
| Users          | Stack (AddEditUsers)     | Create/edit submit                     | `dealer_user_create_or_edit`                                                | `item_id`, `action`                         |
| CompanyProfile | Stack                    | Tax / state / district / verify toggle | `dealer_company_{tax_toggle\|state_select\|district_select\|verify_toggle}` | —                                           |
| Profile        | Stack                    | Address update / refresh               | `dealer_profile_{address_update\|refresh}`                                  | —                                           |
| Profile        | Modal (PassModal)        | Password change                        | `dealer_profile_password_change`                                            | `status`                                    |
| Notifications  | Stack                    | Toggle / en-all / dis-all              | `dealer_notif_{toggle\|enable_all\|disable_all}`                            | `notif_type`, `enabled`                     |

### 7.4 Common group (shared — `role` default param disambiguates)

| Screen                                | Screen type    | Action                                  | Event                                                                                  | Params                                                         |
| ------------------------------------- | -------------- | --------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Orders                                | Stack          | Load / search / filter / refresh / view | `list_view_load`, `list_search`, `list_filter_apply`, `list_refresh`, `select_content` | `list_type: 'order'`, `filter_type`, `filter_value`, `item_id` |
| Invoices                              | Stack          | Same pattern                            | same as above                                                                          | `list_type: 'invoice'`                                         |
| Payments                              | Stack          | Same pattern + email                    | same + `payment_email_submit`                                                          | `list_type: 'payment'`                                         |
| Accounts                              | Stack          | Load / email / detail / sync            | `accounts_{view_load\|email_submit\|detail_view\|sync_trigger}`                        | `period_type`, `record_type`                                   |
| Reports                               | Stack          | Navigate to subreport                   | `report_{daily_open\|tcs_open\|tds_open}`                                              | —                                                              |
| DailyReport                           | Stack          | Month / year / toggle / email           | `report_tcstds_{month_select\|year_select\|email_submit}`                              | `is_tcs`, `month`, `financial_year`                            |
| DailySummary                          | Stack          | PO/SO toggle / refresh                  | `daily_summary_{po_toggle\|so_toggle\|refresh}`                                        | `order_type`                                                   |
| Help                                  | Stack          | Manual open / contact                   | `help_{manual_customer_open\|manual_dealer_open\|contact_navigate}`                    | —                                                              |
| ContactUs                             | Stack          | Submit                                  | `contact_us_submit`                                                                    | `message_length`, `status`, `failure_reason`                   |
| Settings                              | Stack          | Theme change / delete-account nav       | `settings_theme_change`, `settings_navigate_delete_account`                            | `theme_selected`                                               |
| DeleteAccount                         | Stack + Modal  | Confirm / success                       | `{account\|company}_delete_{confirm\|success\|failed}`                                 | `failure_reason`                                               |
| SisterCompanies                       | Stack          | List / add                              | `companies_{view\|create}`                                                             | `item_id`                                                      |
| Users                                 | Stack + BSheet | Invite submit / accept / decline        | `invite_user_submit`, `invite_{accept\|decline}`                                       | `invite_type`, `status`                                        |
| Invites                               | Stack          | Refresh / accept / decline              | `invites_{refresh\|accept_success\|decline_success\|accept_failed}`                    | `item_id`                                                      |
| RelationList                          | Stack          | View / credit detail                    | `relation_{list_view\|credit_detail_view}`                                             | `relation_type`                                                |
| Vehicles                              | Stack          | View / refresh                          | `common_vehicle_{view\|refresh}`                                                       | —                                                              |
| `_Invoice_` / `_Order_` / `_Voucher_` | Stack (detail) | Share / download / scroll-to-end        | `detail_{share\|download\|view}`                                                       | `content_type`, `item_id`                                      |

---

## 8. Implementation Steps (per screen)

### Step A — Add the helper utility

Create `dzzlo_oms_app/src/utils/analyticsEvents.js`:

```js
import analytics from "@react-native-firebase/analytics";

const safeLog = async (name, params = {}) => {
  try {
    await analytics().logEvent(name, params);
  } catch (e) {
    if (__DEV__) console.warn("[analytics] logEvent failed", name, e);
  }
};

// Domain wrappers — import these instead of calling analytics() directly
export const trackOrderCreate = ({ order_id, amount, count }) =>
  safeLog("customer_order_create", {
    item_id: String(order_id),
    amount,
    count,
  });

export const trackListFilter = ({ list_type, filter_type, filter_value }) =>
  safeLog("list_filter_apply", {
    list_type,
    filter_type,
    filter_value: String(filter_value),
  });

export const trackListSearch = ({ list_type, search_term }) =>
  safeLog("list_search", {
    list_type,
    search_term: (search_term ?? "").slice(0, 100).toLowerCase(),
  });

export const trackSelectContent = ({ content_type, item_id }) =>
  analytics().logSelectContent({ content_type, item_id: String(item_id) });

export const trackSheetOpen = (sheet_name, extra = {}) =>
  safeLog("sheet_open", { sheet_name, ...extra });

export const trackTabSwitch = ({ tab_group, tab_to }) =>
  safeLog("tab_switch", { tab_group, tab_to });

export const trackLogin = (method) => analytics().logLogin({ method });
export const trackSignUp = (method) => analytics().logSignUp({ method });
export const trackLogout = (initiated_from) =>
  safeLog("logout", { initiated_from });
```

### Step B — Wire each screen

**Pattern 1 — Button press:**

```js
// src/screens/Customer/NewOrder/index.js
import { trackOrderCreate } from "../../../utils/analyticsEvents";

const handleSubmit = async () => {
  const res = await createOrder(payload).unwrap();
  trackOrderCreate({
    order_id: res.id,
    amount: res.amount,
    count: items.length,
  });
  navigation.goBack();
};
```

**Pattern 2 — List filter / search (debounced):**

```js
// src/screens/Common/Orders/index.js
import {
  trackListFilter,
  trackListSearch,
} from "../../../utils/analyticsEvents";
import { useEffect } from "react";

useEffect(() => {
  if (!statusFilter) return;
  trackListFilter({
    list_type: "order",
    filter_type: "status",
    filter_value: statusFilter,
  });
}, [statusFilter]);

// Debounce search so we don't fire on every keystroke
useEffect(() => {
  const t = setTimeout(() => {
    if (searchTerm?.length >= 2)
      trackListSearch({ list_type: "order", search_term: searchTerm });
  }, 600);
  return () => clearTimeout(t);
}, [searchTerm]);
```

**Pattern 3 — Row tap (use recommended `select_content`):**

```js
<Pressable onPress={() => {
  trackSelectContent({ content_type: 'order', item_id: order.id });
  navigation.navigate('details', { screen: 'Order', params: { id: order.id } });
}}>
```

**Pattern 4 — Bottom sheet open:**

```js
// src/screens/Customer/NewOrder/BSheets/SelectVehicle.js
import { useLogSheet } from '../../../../hooks/useLogSheet';

const SelectVehicleSheet = ({ visible, ... }) => {
  useLogSheet('select_vehicle', visible);
  ...
};
```

**Pattern 5 — RTK Query mutation via middleware (already proposed in integration plan §7):**

The `rtkQueryPerfLogger` middleware already fires `api_call { endpoint, status }` for **every** RTK Query call. That gives you raw "something was submitted" visibility for free — the domain-specific events above layer business semantics on top.

### Step C — Set user properties on login / role switch

```js
// src/store/slices/auth.js — inside the login thunk's fulfilled handler
import analytics from "@react-native-firebase/analytics";
import { trackLogin } from "../../utils/analyticsEvents";

await analytics().setUserId(user.id);
await analytics().setUserProperty("role", user.scope);
await analytics().setUserProperty("company_id", activeCompany.id);
trackLogin(method); // 'password' | 'otp' | 'email'
```

### Step D — Per-group checklist

For each screen listed in §7:

1. Open the screen source file.
2. Add a `screen_name` constant at top: `const SCREEN = 'customer_new_order';` (for consistency in params).
3. For every `onPress` / `handleSubmit` / toggle, call the helper — **keep event names exactly as in §7**.
4. For every `BottomSheet` / `Modal`, add `useLogSheet(name, visible)`.
5. For every form submit with a known failure path (RTK Query `error`), also fire the `*_failed` variant with `failure_reason`.

---

## 9. How to Pass Parameters — Dos & Don'ts

### Do

- Keep keys to the shared dictionary in §3 so Firebase can auto-merge across screens.
- Always `String(id)` business IDs so type stays consistent across events.
- Put **amounts in base units** (`amount: 125000` for ₹1,250.00) so aggregation works.
- Pass `status: 'ok' | 'err'` on every submit/terminal event — powers funnel drop-off analysis.
- Keep `search_term` lowercase + trimmed + clamped to 100 chars.

### Don't

- Don't use camelCase keys (`orderId` → `order_id` / prefer shared `item_id`).
- Don't log PII — names, phones, full emails, addresses, OTP codes, passwords.
- Don't put long JSON into a single param — split it; values get truncated at 100 chars.
- Don't fire on every keystroke — debounce searches by 500–700ms.
- Don't reinvent reserved names (see §1).
- Don't block UX on `await` — `safeLog` swallows errors and fires-and-forgets.

---

## 10. Verifying in Firebase

### 10.1 Local DebugView (real-time — the fast loop)

```bash
# Android
adb shell setprop debug.firebase.analytics.app in.vsyst.dzzlooms
adb logcat -s FA FA-SVC

# To disable
adb shell setprop debug.firebase.analytics.app .none.
```

```bash
# iOS — add launch arg in Xcode scheme: -FIRDebugEnabled
# Or: xcrun simctl launch booted in.vsyst.dzzlooms -FIRDebugEnabled
```

Then in Firebase console: **Analytics → DebugView** → pick the device → events stream in within seconds. Click an event to see its params.

### 10.2 Events dashboard

**Analytics → Events** shows aggregated counts per event name (up to 24h delay for first-seen events). Click an event to:

- See parameter distributions.
- **Mark a parameter for reporting** (needed — by default custom params aren't indexed). Do this once per `(event, param)` pair you want to slice on.

### 10.3 Audiences & Funnels

- **Audiences**: define by event match + user properties (e.g. "dealers who created 3+ invoices last 7 days").
- **Funnels** (Explore): define step sequence like `screen_view(NewOrder) → customer_order_product_select → customer_order_create` to measure completion rate.

### 10.4 BigQuery export

Enable once in Project Settings → Integrations → BigQuery. Events land in `analytics_<property_id>.events_YYYYMMDD` ~24h later. Lets you SQL over the raw stream — far more flexible than the dashboards.

### 10.5 Smoke test before shipping

1. Fresh install debug build on a device with DebugView enabled.
2. Walk through one flow per role:
   - **Auth:** login → expect `login` with `method`.
   - **Customer:** open Orders → change filter → open NewOrder → pick vehicle/dealer/product → submit.
   - **Dealer:** open Customers → create NewSalesOrder → create NewInvoice → submit payment voucher.
3. Confirm each expected event appears with expected params (no `undefined`, no PII).
4. For every custom param you want to slice by later, click into the event in the Events dashboard and **Mark as conversion / Register parameter**.

---

## 11. Rollout

| Phase | Scope                                                                                                | Exit criteria                                       |
| ----- | ---------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| 1     | §6 global setup + `utils/analyticsEvents.js` + auth events (login/signup/logout)                     | Login flow visible in DebugView                     |
| 2     | Customer list screens (Orders, Invoices, Payments, Dealers) — filter/search/tap/refresh              | 4 list screens fully instrumented                   |
| 3     | Customer form screens (NewOrder, NewPayment, AddDealers, AddEditUsers, Vehicles sheets)              | All customer conversion events firing               |
| 4     | Dealer equivalents (Orders, Invoices, Payments, NewSalesOrder, NewInvoice, NewVoucher, ProductDates) | All dealer conversion events firing                 |
| 5     | Common screens (Accounts, Reports, Settings, Invites, ContactUs, DeleteAccount)                      | All shared screens instrumented                     |
| 6     | Bottom-sheet `sheet_open` coverage across all sheets                                                 | `sheet_open` visible with every unique `sheet_name` |
| 7     | Mark parameters for reporting, build Audiences + one funnel per role                                 | Dashboards usable without BigQuery                  |

---

## 12. Files Touched (summary)

| File                                                                                     | Change                                                                   |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `dzzlo_oms_app/src/utils/analyticsEvents.js`                                             | **New** — typed wrappers for every event in §7                           |
| `dzzlo_oms_app/src/hooks/useLogSheet.js`                                                 | **New** — fires `sheet_open` on mount                                    |
| `dzzlo_oms_app/App.js`                                                                   | `setDefaultEventParameters`, `setUserId`, `setUserProperty` subscription |
| `dzzlo_oms_app/src/navigation/{Customer,Dealer}/Drawer.js`                               | `screenListeners.drawerItemPress` → `drawer_item_select`                 |
| `dzzlo_oms_app/src/navigation/{Customer,Dealer}/TrnTab.js`                               | `screenListeners.tabPress` → `tab_switch`                                |
| `dzzlo_oms_app/src/store/slices/auth.js` (or login thunk)                                | Fire `login` / `sign_up` / `logout`; set user properties                 |
| `dzzlo_oms_app/src/screens/Login/**`                                                     | Auth events (§7.1)                                                       |
| `dzzlo_oms_app/src/screens/Customer/**`                                                  | Customer events (§7.2)                                                   |
| `dzzlo_oms_app/src/screens/Dealer/**`                                                    | Dealer events (§7.3)                                                     |
| `dzzlo_oms_app/src/screens/Common/**`                                                    | Common events (§7.4)                                                     |
| `dzzlo_oms_app/src/store/middleware/rtkQueryPerfLogger.js` (already in integration plan) | Already emits `api_call` — no change                                     |
