# Phase 3: Business Event Instrumentation

## Goal

Instrument critical business flows with meaningful analytics events on both frontend (React Native) and backend (Express API). This is where the analytics system becomes actually useful — tracking real user behavior and business metrics.

## Prerequisites

- Phase 2 complete (Analytics SDK available in the app)

## Deliverables

- Centralized event taxonomy constants
- Frontend instrumentation across all major flows
- Backend server-side event emission for critical transactions
- Complete funnel coverage for Order → Invoice → Payment flow

---

## Step 3.1: Define Event Taxonomy

**File to create:** `dzzlo_oms_app/src/utils/Analytics/events.js`

### Event Naming Convention

- Format: `{entity}_{action}` in snake_case
- Categories group related events for filtering

```javascript
export const EVENTS = {
  // === Auth ===
  AUTH_LOGIN_STARTED: "auth_login_started",
  AUTH_LOGIN_SUCCESS: "auth_login_success",
  AUTH_LOGIN_FAILED: "auth_login_failed",
  AUTH_LOGOUT: "auth_logout",
  AUTH_OTP_REQUESTED: "auth_otp_requested",
  AUTH_OTP_VERIFIED: "auth_otp_verified",
  AUTH_SIGNUP_STARTED: "auth_signup_started",
  AUTH_SIGNUP_COMPLETED: "auth_signup_completed",
  AUTH_PASSWORD_RESET: "auth_password_reset",

  // === Orders (Primary Funnel) ===
  ORDER_LIST_VIEWED: "order_list_viewed",
  ORDER_DETAIL_VIEWED: "order_detail_viewed",
  ORDER_CREATE_STARTED: "order_create_started",
  ORDER_PRODUCT_SELECTED: "order_product_selected",
  ORDER_QUANTITY_ENTERED: "order_quantity_entered",
  ORDER_SUBMITTED: "order_submitted",
  ORDER_SUBMIT_FAILED: "order_submit_failed",
  ORDER_STATUS_CHANGED: "order_status_changed",
  ORDER_PROCESSED: "order_processed",
  ORDER_OTP_SENT: "order_otp_sent",
  ORDER_OTP_VERIFIED: "order_otp_verified",
  ORDER_DELETED: "order_deleted",

  // === Sales Orders ===
  SO_CREATED: "so_created",
  SO_VIEWED: "so_viewed",
  SO_STATUS_CHANGED: "so_status_changed",

  // === Invoices (Funnel Stage 2) ===
  INVOICE_LIST_VIEWED: "invoice_list_viewed",
  INVOICE_DETAIL_VIEWED: "invoice_detail_viewed",
  INVOICE_CREATED: "invoice_created",
  INVOICE_CREATE_FAILED: "invoice_create_failed",
  INVOICE_PDF_DOWNLOADED: "invoice_pdf_downloaded",
  INVOICE_EXCEL_DOWNLOADED: "invoice_excel_downloaded",
  INVOICE_EMAILED: "invoice_emailed",

  // === Payments (Funnel Stage 3) ===
  PAYMENT_LIST_VIEWED: "payment_list_viewed",
  PAYMENT_INITIATED: "payment_initiated",
  PAYMENT_COMPLETED: "payment_completed",
  PAYMENT_FAILED: "payment_failed",
  PAYMENT_APPROVED: "payment_approved",

  // === Vouchers ===
  VOUCHER_CREATED: "voucher_created",
  VOUCHER_VIEWED: "voucher_viewed",
  VOUCHER_APPROVED: "voucher_approved",

  // === Vehicles ===
  VEHICLE_REQUEST_CREATED: "vehicle_request_created",
  VEHICLE_TRIP_STARTED: "vehicle_trip_started",
  VEHICLE_TRIP_COMPLETED: "vehicle_trip_completed",
  VEHICLE_LOCATION_UPDATED: "vehicle_location_updated",

  // === Customers & Dealers ===
  CUSTOMER_CREATED: "customer_created",
  CUSTOMER_VIEWED: "customer_viewed",
  DEALER_CREATED: "dealer_created",
  DEALER_VIEWED: "dealer_viewed",
  RELATION_CREATED: "relation_created",

  // === Products & Pricing ===
  PRODUCT_CREATED: "product_created",
  RATE_UPDATED: "rate_updated",

  // === Company/Profile ===
  COMPANY_SWITCHED: "company_switched",
  PROFILE_UPDATED: "profile_updated",
  NOTIFICATION_PREF_CHANGED: "notification_pref_changed",

  // === System ===
  APP_OPENED: "app_opened",
  APP_BACKGROUNDED: "app_backgrounded",
  APP_CRASHED: "app_crashed",
  APP_UPDATED: "app_updated",
  PUSH_RECEIVED: "push_received",
  PUSH_CLICKED: "push_clicked",
  NETWORK_OFFLINE: "network_offline",
  NETWORK_RESTORED: "network_restored",

  // === Reports ===
  REPORT_VIEWED: "report_viewed",
  REPORT_EXPORTED: "report_exported",
  DAILY_SUMMARY_VIEWED: "daily_summary_viewed",
}

export const CATEGORIES = {
  AUTH: "auth",
  ORDER: "order",
  INVOICE: "invoice",
  PAYMENT: "payment",
  VOUCHER: "voucher",
  VEHICLE: "vehicle",
  MASTER_DATA: "master_data",
  NAVIGATION: "navigation",
  PROFILE: "profile",
  SYSTEM: "system",
  REPORT: "report",
}
```

---

## Step 3.2: Instrument Auth Flow (Frontend)

**Files to modify:**

### `src/screens/Login/AuthNavigator/Login.js`

```javascript
import Analytics from "../../../utils/Analytics"
import { EVENTS, CATEGORIES } from "../../../utils/Analytics/events"

// On login button press:
Analytics.track(EVENTS.AUTH_LOGIN_STARTED, {
  category: CATEGORIES.AUTH,
  method: isOTP ? "otp" : "password",
})

// On login success:
Analytics.track(EVENTS.AUTH_LOGIN_SUCCESS, {
  category: CATEGORIES.AUTH,
  method: isOTP ? "otp" : "password",
  user_role: response.user.role,
})

// On login failure:
Analytics.track(EVENTS.AUTH_LOGIN_FAILED, {
  category: CATEGORIES.AUTH,
  error: errorMessage,
})
```

### `src/screens/Login/AuthNavigator/ForgotPassword.js`

```javascript
Analytics.track(EVENTS.AUTH_PASSWORD_RESET, { category: CATEGORIES.AUTH })
```

### `src/screens/Login/AuthNavigator/Customer.js` / `Dealer.js`

```javascript
Analytics.track(EVENTS.AUTH_SIGNUP_COMPLETED, {
  category: CATEGORIES.AUTH,
  role: "customer", // or 'dealer'
})
```

---

## Step 3.3: Instrument Order Flow (Frontend — Primary Funnel)

This is the most critical funnel: Order Creation → Processing → Delivery

### Dealer-side Order Creation (`src/screens/Dealer/NewSalesOrder/`)

```javascript
// Screen opened
Analytics.track(EVENTS.ORDER_CREATE_STARTED, {
  category: CATEGORIES.ORDER,
  role: "dealer",
})

// Product selected
Analytics.track(EVENTS.ORDER_PRODUCT_SELECTED, {
  category: CATEGORIES.ORDER,
  product_id: selectedProduct._id,
  product_name: selectedProduct.name,
})

// Quantity entered
Analytics.track(EVENTS.ORDER_QUANTITY_ENTERED, {
  category: CATEGORIES.ORDER,
  quantity: qty,
  unit: selectedUnit,
})

// Order submitted
Analytics.track(EVENTS.ORDER_SUBMITTED, {
  category: CATEGORIES.ORDER,
  role: "dealer",
  items_count: items.length,
  total_amount: totalAmount,
  customer_id: selectedCustomer._id,
})
```

### Customer-side Order View (`src/screens/Customer/Orders/`)

```javascript
// Order list viewed
Analytics.track(EVENTS.ORDER_LIST_VIEWED, {
  category: CATEGORIES.ORDER,
  role: "customer",
  filter_status: activeFilter,
  results_count: orders.length,
})

// Order detail viewed
Analytics.track(EVENTS.ORDER_DETAIL_VIEWED, {
  category: CATEGORIES.ORDER,
  order_id: order._id,
  order_status: order.status,
})
```

### RTK Query Order Mutations (`src/store/apis/dzzlooms/order_msts.js`)

Use `onQueryStarted` for tracking API-level results:

```javascript
createOrder: builder.mutation({
  // ... existing config
  async onQueryStarted(arg, { queryFulfilled }) {
    try {
      const { data } = await queryFulfilled;
      Analytics.track(EVENTS.ORDER_SUBMITTED, {
        category: CATEGORIES.ORDER,
        order_id: data?.data?._id,
        source: 'api_confirmed',
      });
    } catch (err) {
      Analytics.track(EVENTS.ORDER_SUBMIT_FAILED, {
        category: CATEGORIES.ORDER,
        error: err?.error?.data?.error,
      });
    }
  },
}),
```

---

## Step 3.4: Instrument Invoice Flow (Frontend)

### `src/screens/Dealer/NewInvoice/`

```javascript
Analytics.track(EVENTS.INVOICE_CREATED, {
  category: CATEGORIES.INVOICE,
  order_id: linkedOrderId,
  amount: invoiceAmount,
  has_gst: Boolean(gstNumber),
})
```

### `src/screens/Common/Invoices/`

```javascript
Analytics.track(EVENTS.INVOICE_LIST_VIEWED, {
  category: CATEGORIES.INVOICE,
  count: invoices.length,
})

Analytics.track(EVENTS.INVOICE_DETAIL_VIEWED, {
  category: CATEGORIES.INVOICE,
  invoice_id: invoice._id,
  amount: invoice.total,
})
```

### `src/components/Download/` (PDF/Excel export)

```javascript
Analytics.track(EVENTS.INVOICE_PDF_DOWNLOADED, {
  category: CATEGORIES.INVOICE,
  invoice_id: invoiceId,
})
```

---

## Step 3.5: Instrument Payment Flow (Frontend)

**Files:** `src/screens/Customer/Payments/`, `src/screens/Dealer/Payments/`

```javascript
Analytics.track(EVENTS.PAYMENT_INITIATED, {
  category: CATEGORIES.PAYMENT,
  amount: paymentAmount,
  method: paymentMethod,
  invoice_id: linkedInvoiceId,
})

Analytics.track(EVENTS.PAYMENT_COMPLETED, {
  category: CATEGORIES.PAYMENT,
  amount: paymentAmount,
  transaction_id: txnId,
})

Analytics.track(EVENTS.PAYMENT_FAILED, {
  category: CATEGORIES.PAYMENT,
  error: errorMessage,
  amount: paymentAmount,
})
```

---

## Step 3.6: Instrument Push Notifications

**File to modify:** `src/helpers/OneSignal/index.js`

```javascript
import Analytics from "../../utils/Analytics"
import { EVENTS, CATEGORIES } from "../../utils/Analytics/events"

// In the click handler (line 26-29):
OneSignal.Notifications.addEventListener("click", (event) => {
  Analytics.track(EVENTS.PUSH_CLICKED, {
    category: CATEGORIES.SYSTEM,
    notification_type: event.notification?.additionalData?.type,
    notification_id: event.notification?.notificationId,
  })
  // ... existing navigation logic
})
```

---

## Step 3.7: Instrument System Events

### Error Boundary (`src/components/Error/ErrorBoundary.js`)

```javascript
// In componentDidCatch:
Analytics.track(EVENTS.APP_CRASHED, {
  category: CATEGORIES.SYSTEM,
  error_name: error.name,
  error_message: error.message,
  component_stack: errorInfo?.componentStack?.substring(0, 500),
})
```

### App Lifecycle (`App.js` or `AppNavigatorContainer.js`)

```javascript
AppState.addEventListener("change", (nextState) => {
  if (nextState === "active") {
    Analytics.track(EVENTS.APP_OPENED, { category: CATEGORIES.SYSTEM })
  } else if (nextState === "background") {
    Analytics.track(EVENTS.APP_BACKGROUNDED, { category: CATEGORIES.SYSTEM })
  }
})
```

---

## Step 3.8: Backend Server-Side Event Emission

For critical business transactions, emit events from the backend where the DB write actually succeeds. More reliable than frontend-only tracking.

**File to create:** `dzzlo_oms_api/helpers/analyticsEmitter.js`

```javascript
const AnalyticsEvent = require("../models/analytics_events")

const emitServerEvent = (eventName, { user_id, company_id, user_role, properties = {} }) => {
  const now = new Date()
  const timeIST = now.toLocaleString("en-US", { timeZone: "Asia/Kolkata" })

  // Fire and forget — never block the API response
  AnalyticsEvent.create({
    event_name: eventName,
    event_category: "server",
    user_id,
    company_id,
    user_role,
    event_properties: properties,
    client_timestamp: now,
    server_timestamp: now,
    timeIST,
  }).catch((err) => console.error("Analytics emit failed:", err.message))
}

module.exports = { emitServerEvent }
```

### Backend Files to Instrument:

**`api_v3/controllers/collections/order_msts.js`** — After successful order creation:

```javascript
emitServerEvent("order_created_server", {
  user_id: req.user._id,
  company_id: req.user.co_id,
  user_role: req.user.role,
  properties: { order_id: newOrder._id, items_count: newOrder.items?.length },
})
```

**`api_v3/controllers/collections/invs.js`** — After invoice creation:

```javascript
emitServerEvent("invoice_created_server", {
  user_id: req.user._id,
  company_id: req.user.co_id,
  user_role: req.user.role,
  properties: { invoice_id: newInv._id, amount: newInv.total },
})
```

**`api_v3/controllers/auth/index.js`** — After login:

```javascript
emitServerEvent("auth_login_server", {
  user_id: user._id,
  company_id: user.co_id,
  user_role: user.role,
  properties: { method: loginMethod, ip: req.ip },
})
```

---

## Step 3.9: The Primary Business Funnel

The most valuable funnel to track end-to-end:

```
Order Created → Sales Order Created → Invoice Created → Payment Completed
```

With this instrumentation, you can query:

- How many orders convert to invoices? (and how long does it take?)
- Where do users drop off in the order creation flow?
- Which products are ordered most frequently?
- Average time from order to payment completion
- Failure rates at each stage

---

## Step 3.10: Verification Checklist

- [ ] Complete full order flow → verify 5+ events: create_started → product_selected → quantity_entered → submitted → (server) order_created_server
- [ ] Complete invoice flow → verify events from list view through creation and PDF download
- [ ] Tap a push notification → verify `push_clicked` event captured
- [ ] Login and logout → verify auth events with user identity
- [ ] Trigger app crash (dev mode) → verify `app_crashed` event
- [ ] Query MongoDB: `db.analytics_events.find({ event_category: "order" })` → verify order funnel is reconstructible
- [ ] Compare frontend `order_submitted` count vs backend `order_created_server` count → should be close

---

## Files Summary

| Action | File                                                | Project       |
| ------ | --------------------------------------------------- | ------------- |
| CREATE | `src/utils/Analytics/events.js`                     | dzzlo_oms_app |
| CREATE | `helpers/analyticsEmitter.js`                       | dzzlo_oms_api |
| MODIFY | `src/screens/Login/AuthNavigator/Login.js`          | dzzlo_oms_app |
| MODIFY | `src/screens/Login/AuthNavigator/ForgotPassword.js` | dzzlo_oms_app |
| MODIFY | `src/screens/Login/AuthNavigator/Customer.js`       | dzzlo_oms_app |
| MODIFY | `src/screens/Dealer/NewSalesOrder/`                 | dzzlo_oms_app |
| MODIFY | `src/screens/Customer/Orders/`                      | dzzlo_oms_app |
| MODIFY | `src/store/apis/dzzlooms/order_msts.js`             | dzzlo_oms_app |
| MODIFY | `src/screens/Dealer/NewInvoice/`                    | dzzlo_oms_app |
| MODIFY | `src/screens/Common/Invoices/`                      | dzzlo_oms_app |
| MODIFY | `src/components/Download/`                          | dzzlo_oms_app |
| MODIFY | `src/screens/Customer/Payments/`                    | dzzlo_oms_app |
| MODIFY | `src/helpers/OneSignal/index.js`                    | dzzlo_oms_app |
| MODIFY | `src/components/Error/ErrorBoundary.js`             | dzzlo_oms_app |
| MODIFY | `api_v3/controllers/collections/order_msts.js`      | dzzlo_oms_api |
| MODIFY | `api_v3/controllers/collections/invs.js`            | dzzlo_oms_api |
| MODIFY | `api_v3/controllers/auth/index.js`                  | dzzlo_oms_api |
