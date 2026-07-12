# Phase 7: Cross-Project Correlation & Advanced Analytics

## Goal

Enable deep-linking between frontend analytics events and backend API logs via correlation IDs. Add user timeline views, error correlation, advanced filtering, and data export capabilities. This is the capstone phase that unlocks the full power of having analytics across all three projects.

## Prerequisites

- Phase 5 complete (pre-computed aggregations)
- Phase 6 complete (Next.js dashboard)

## Deliverables

- Unified user timeline merging frontend events + backend API logs
- Error-to-session correlation
- Advanced multi-dimensional filtering
- Data export (CSV/JSON)
- Alert/threshold system for anomaly detection
- API performance analytics

---

## Step 7.1: User Timeline API

**File to create/modify:** `dzzlo_oms_api/api_v3/controllers/analytics/queries.js`

### New Endpoint: `GET /api/v3/analytics/query/users/:userId/timeline`

**Query params:** `?from=&to=&categories=auth,order&include_api_logs=true&include_errors=true&page=1&limit=100`

This endpoint merges data from THREE collections into one chronological timeline:

```javascript
exports.getUserTimeline = asyncHandler(async (req, res) => {
  const { userId } = req.params
  const {
    from,
    to,
    categories,
    include_api_logs = "true",
    include_errors = "true",
    page = 1,
    limit = 100,
  } = req.query

  const userObjectId = new mongoose.Types.ObjectId(userId)
  const dateFilter = {}
  if (from) dateFilter.$gte = new Date(from)
  if (to) dateFilter.$lte = new Date(to)

  const skip = (parseInt(page) - 1) * parseInt(limit)
  const timelineItems = []

  // 1. Analytics Events (frontend + server events)
  const eventFilter = { user_id: userObjectId }
  if (Object.keys(dateFilter).length) eventFilter.server_timestamp = dateFilter
  if (categories) eventFilter.event_category = { $in: categories.split(",") }

  const events = await AnalyticsEvent.find(eventFilter).sort({ server_timestamp: -1 }).lean()

  events.forEach((e) => {
    timelineItems.push({
      type: "event",
      timestamp: e.server_timestamp,
      data: {
        event_name: e.event_name,
        event_category: e.event_category,
        screen_name: e.screen_name,
        properties: e.event_properties,
        session_id: e.session_id,
        api_request_id: e.api_request_id,
        device_os: e.device_os,
        app_version: e.app_version,
      },
    })
  })

  // 2. Backend API Logs (correlated by user)
  if (include_api_logs === "true") {
    const logFilter = { "user._id": userObjectId }
    if (Object.keys(dateFilter).length) logFilter.createdAt = dateFilter

    const logs = await Log.find(logFilter).sort({ createdAt: -1 }).lean()

    logs.forEach((l) => {
      timelineItems.push({
        type: "api_log",
        timestamp: l.createdAt,
        data: {
          method: l.method,
          url: l.url,
          status: l.status,
          response_time_ms: l.response_time,
          request_id: l.request_id,
          status_message: l.statusMessage,
        },
      })
    })
  }

  // 3. Error Reports
  if (include_errors === "true") {
    const errorFilter = {}
    // errors collection may store userId differently — adapt to actual schema
    if (Object.keys(dateFilter).length) errorFilter.createdAt = dateFilter

    const errors = await ErrorModel.find(errorFilter).sort({ createdAt: -1 }).lean()

    errors.forEach((e) => {
      timelineItems.push({
        type: "error",
        timestamp: e.createdAt,
        data: {
          error_name: e.error_res?.errorName,
          error_message: e.error_res?.errorMessage,
          stack_trace: e.error_res?.stackTrace?.substring(0, 500),
        },
      })
    })
  }

  // Sort all items chronologically (newest first)
  timelineItems.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))

  // Paginate
  const paginatedItems = timelineItems.slice(skip, skip + parseInt(limit))

  // Correlate: link events to their corresponding API logs via request_id
  const requestIds = new Set()
  paginatedItems.forEach((item) => {
    if (item.data.api_request_id) requestIds.add(item.data.api_request_id)
    if (item.data.request_id) requestIds.add(item.data.request_id)
  })

  // Mark correlated pairs
  paginatedItems.forEach((item) => {
    if (item.type === "event" && item.data.api_request_id) {
      const matchingLog = paginatedItems.find(
        (i) => i.type === "api_log" && i.data.request_id === item.data.api_request_id,
      )
      if (matchingLog) {
        item.data.correlated_api_log = {
          method: matchingLog.data.method,
          url: matchingLog.data.url,
          status: matchingLog.data.status,
          response_time_ms: matchingLog.data.response_time_ms,
        }
      }
    }
  })

  res.json({
    success: true,
    data: paginatedItems,
    pagination: {
      page: parseInt(page),
      limit: parseInt(limit),
      total: timelineItems.length,
      pages: Math.ceil(timelineItems.length / parseInt(limit)),
    },
  })
})
```

---

## Step 7.2: Error-to-Session Correlation

### Backend Enhancement

**File to modify:** `dzzlo_oms_app/src/components/Error/ErrorBoundary.js`

When ErrorBoundary fires, include the session_id from Analytics:

```javascript
import Analytics from "../../utils/Analytics"

// In componentDidCatch:
const sessionId = Analytics.session?.getSessionId()

reportError({
  userId,
  errorName: error.name,
  errorMessage: error.message,
  stackTrace: errorInfo?.componentStack,
  session_id: sessionId, // NEW — links error to analytics session
})

// Also emit analytics event
Analytics.track("app_crashed", {
  category: "system",
  error_name: error.name,
  error_message: error.message,
})
```

**File to modify:** `dzzlo_oms_api/models/errors.js`

Add field: `session_id: { type: String, index: true }`

This enables: "Show me everything this user did in the session that led to this crash."

---

## Step 7.3: Advanced Multi-Dimensional Filtering

### Update ALL Query Endpoints

Add these common filter parameters to every analytics query endpoint:

| Parameter        | Type     | Description                                 |
| ---------------- | -------- | ------------------------------------------- |
| `company_id`     | ObjectId | Filter by specific company                  |
| `user_role`      | String   | Filter by role (dealer/customer/superadmin) |
| `device_os`      | String   | Filter by platform (iOS/Android)            |
| `app_version`    | String   | Filter by specific app version              |
| `from`           | Date     | Start date                                  |
| `to`             | Date     | End date                                    |
| `session_id`     | String   | Filter by specific session                  |
| `event_category` | String   | Filter by event category                    |

**Create helper:** `dzzlo_oms_api/helpers/analyticsFilters.js`

```javascript
const mongoose = require("mongoose")

const buildAnalyticsFilter = (query) => {
  const filter = {}

  if (query.company_id) {
    filter.company_id = new mongoose.Types.ObjectId(query.company_id)
  }
  if (query.user_role) filter.user_role = query.user_role
  if (query.device_os) filter.device_os = query.device_os
  if (query.app_version) filter.app_version = query.app_version
  if (query.session_id) filter.session_id = query.session_id
  if (query.event_category) filter.event_category = query.event_category
  if (query.event_name) filter.event_name = query.event_name

  if (query.from || query.to) {
    filter.server_timestamp = {}
    if (query.from) filter.server_timestamp.$gte = new Date(query.from)
    if (query.to) filter.server_timestamp.$lte = new Date(query.to)
  }

  return filter
}

module.exports = { buildAnalyticsFilter }
```

Then refactor all query controllers to use `buildAnalyticsFilter(req.query)` instead of inline filter building.

---

## Step 7.4: Data Export Endpoints

**File to create:** `dzzlo_oms_api/api_v3/controllers/analytics/exports.js`

### CSV Export

```
GET /api/v3/analytics/query/export/events?format=csv&from=&to=&event_name=
```

```javascript
exports.exportEvents = asyncHandler(async (req, res) => {
  const { format = "json", ...filterParams } = req.query
  const filter = buildAnalyticsFilter(filterParams)

  const events = await AnalyticsEvent.find(filter)
    .sort({ server_timestamp: -1 })
    .limit(10000) // Cap at 10K rows
    .lean()

  if (format === "csv") {
    const fields = [
      "event_name",
      "event_category",
      "user_id",
      "user_role",
      "screen_name",
      "device_os",
      "app_version",
      "server_timestamp",
    ]
    const csvHeader = fields.join(",")
    const csvRows = events.map((e) =>
      fields.map((f) => `"${(e[f] || "").toString().replace(/"/g, '""')}"`).join(","),
    )
    const csv = [csvHeader, ...csvRows].join("\n")

    res.setHeader("Content-Type", "text/csv")
    res.setHeader(
      "Content-Disposition",
      `attachment; filename=analytics_events_${new Date().toISOString().split("T")[0]}.csv`,
    )
    return res.send(csv)
  }

  // JSON export
  res.setHeader(
    "Content-Disposition",
    `attachment; filename=analytics_events_${new Date().toISOString().split("T")[0]}.json`,
  )
  res.json({ success: true, data: events, count: events.length })
})
```

### Aggregated Metrics Export

```
GET /api/v3/analytics/query/export/metrics?format=csv&metric_name=dau&period_type=daily&from=&to=
```

---

## Step 7.5: API Performance Analytics

Track and visualize API endpoint performance using existing data from the `logs` collection.

### New Endpoint: `GET /api/v3/analytics/query/api-performance`

```javascript
exports.getApiPerformance = asyncHandler(async (req, res) => {
  const { from, to, min_response_time } = req.query

  const matchFilter = {}
  if (from || to) {
    matchFilter.createdAt = {}
    if (from) matchFilter.createdAt.$gte = new Date(from)
    if (to) matchFilter.createdAt.$lte = new Date(to)
  }

  const result = await Log.aggregate([
    { $match: matchFilter },
    {
      $group: {
        _id: { method: "$method", url: "$url" },
        avg_response_time: { $avg: "$response_time" },
        p95_response_time: {
          $percentile: {
            input: "$response_time",
            p: [0.95],
            method: "approximate",
          },
        },
        max_response_time: { $max: "$response_time" },
        total_requests: { $sum: 1 },
        error_count: {
          $sum: { $cond: [{ $gte: ["$status", 400] }, 1, 0] },
        },
        status_codes: { $push: "$status" },
      },
    },
    {
      $project: {
        endpoint: { $concat: ["$_id.method", " ", "$_id.url"] },
        avg_response_time: { $round: ["$avg_response_time", 1] },
        p95_response_time: 1,
        max_response_time: 1,
        total_requests: 1,
        error_count: 1,
        error_rate: {
          $round: [
            {
              $multiply: [{ $divide: ["$error_count", "$total_requests"] }, 100],
            },
            1,
          ],
        },
      },
    },
    { $sort: { avg_response_time: -1 } },
    { $limit: 50 },
  ])

  res.json({ success: true, data: result })
})
```

### Dashboard Component

Add API Performance page to the Next.js dashboard:

**File to create:** `dzzlo_analytics/src/app/dashboard/api-performance/page.tsx`

Shows:

- Table of endpoints sorted by avg response time
- Sparkline trend for each endpoint
- Error rate highlighting (>5% = red)
- P95 latency chart
- Top slowest endpoints bar chart

---

## Step 7.6: Anomaly Detection / Alerts

### Simple Threshold-Based Alerts

**File to create:** `dzzlo_oms_api/helpers/analyticsAlerts.js`

Configurable thresholds that run daily (after aggregation):

```javascript
const ALERT_THRESHOLDS = {
  dau_drop: {
    metric: "dau",
    condition: "percentage_drop",
    threshold: 30, // Alert if DAU drops more than 30% vs 7-day average
  },
  error_spike: {
    metric: "error_count",
    condition: "percentage_increase",
    threshold: 50, // Alert if errors spike 50% vs yesterday
  },
  session_duration_drop: {
    metric: "session_avg_duration",
    condition: "percentage_drop",
    threshold: 40,
  },
}

const checkAlerts = async () => {
  // Compare today's aggregated metrics vs historical baselines
  // If threshold breached, create alert document and optionally send notification
}
```

**File to create:** `dzzlo_oms_api/models/analytics_alerts.js`

```javascript
const analytics_alert_Schema = new mongoose.Schema(
  {
    alert_type: { type: String, required: true },
    metric_name: { type: String },
    current_value: { type: Number },
    baseline_value: { type: Number },
    threshold: { type: Number },
    percentage_change: { type: Number },
    severity: { type: String, enum: ["info", "warning", "critical"] },
    acknowledged: { type: Boolean, default: false },
    acknowledged_by: { type: mongoose.Schema.Types.ObjectId, ref: "users" },
  },
  { timestamps: true },
)
```

### Dashboard Alerts Panel

**File to create:** `dzzlo_analytics/src/app/dashboard/alerts/page.tsx`

Shows:

- Active alerts with severity badges
- Alert history
- Acknowledge button
- Threshold configuration UI

---

## Step 7.7: Dashboard Enhancements for Correlation

### Session Replay View

**File to modify:** `dzzlo_analytics/src/app/dashboard/sessions/page.tsx`

When clicking a session, show a "session replay" view:

1. All screen views in order (like a breadcrumb)
2. All events within each screen
3. API calls made from each screen (with response times)
4. Errors that occurred in this session
5. Time gaps between events highlighted

```
Session: abc-123 | User: dealer@fuel.com | 4m 32s | 23 events

Timeline:
─────────────────────────────────────────────────
 10:00:01  [screen_view] Orders
 10:00:03  [api_log] GET /order_msts/a/poso → 200 (340ms)
 10:00:15  [order_detail_viewed] Order #4521
 10:00:16  [api_log] GET /order_msts/4521 → 200 (120ms)
 10:01:02  [screen_view] NewInvoice
 10:01:05  [invoice_created] { amount: 45000, order_id: "4521" }
 10:01:06  [api_log] POST /invs → 201 (890ms)
 10:03:20  [screen_view] Payments
 10:04:01  [payment_initiated] { amount: 45000 }
 10:04:33  [payment_completed] { txn_id: "PAY_789" }
─────────────────────────────────────────────────
```

### Cross-link from Errors

On the SuperAdmin ErrLogs screen (or in the Next.js dashboard):

- Each error links to its session timeline
- Shows "What happened before this crash?" context

---

## Step 7.8: Comparison & Segmentation

### Add Compare Mode to Charts

Allow comparing metrics across:

- Two date ranges (this week vs last week)
- Two companies
- iOS vs Android
- Dealer vs Customer

**Implementation:** Add `compare_from`/`compare_to` params to event count endpoints. Return two series for charting.

### User Segmentation

**New endpoint:** `GET /api/v3/analytics/query/segments`

Pre-defined segments:

- Power users (>50 events/week)
- Inactive users (no events in 14 days)
- New users (first seen in last 7 days)
- Mobile-only vs cross-platform
- By app version

---

## Step 7.9: Verification Checklist

- [ ] Perform actions as a specific user in the RN app
- [ ] Open their timeline in the Next.js dashboard -- see frontend events + API logs interleaved chronologically
- [ ] Verify correlation: event with `api_request_id` shows matching API log details inline
- [ ] Trigger an app crash -- verify it appears in both error logs AND analytics timeline with session context
- [ ] Export events as CSV -- verify downloadable file with correct data
- [ ] Export events as JSON -- verify structured data
- [ ] Check API Performance page -- verify endpoint latency rankings
- [ ] Filter analytics by company_id -- verify only that company's data appears
- [ ] Filter by device_os=iOS -- verify only iOS events
- [ ] Compare this week vs last week -- verify dual-series chart
- [ ] Seed alert condition (large DAU drop) -- verify alert created and visible in dashboard

---

## Files Summary

| Action | File                                                                 | Project         |
| ------ | -------------------------------------------------------------------- | --------------- |
| CREATE | `api_v3/controllers/analytics/exports.js`                            | dzzlo_oms_api   |
| CREATE | `helpers/analyticsFilters.js`                                        | dzzlo_oms_api   |
| CREATE | `helpers/analyticsAlerts.js`                                         | dzzlo_oms_api   |
| CREATE | `models/analytics_alerts.js`                                         | dzzlo_oms_api   |
| CREATE | `src/app/dashboard/api-performance/page.tsx`                         | dzzlo_analytics |
| CREATE | `src/app/dashboard/alerts/page.tsx`                                  | dzzlo_analytics |
| MODIFY | `api_v3/controllers/analytics/queries.js` -- add timeline + API perf | dzzlo_oms_api   |
| MODIFY | `api_v3/routes/analytics/queries.js` -- add new routes               | dzzlo_oms_api   |
| MODIFY | `src/components/Error/ErrorBoundary.js` -- add session_id            | dzzlo_oms_app   |
| MODIFY | `models/errors.js` -- add session_id field                           | dzzlo_oms_api   |
| MODIFY | `src/app/dashboard/sessions/page.tsx` -- session replay view         | dzzlo_analytics |
| MODIFY | `src/app/dashboard/users/[userId]/page.tsx` -- correlated timeline   | dzzlo_analytics |
| MODIFY | All query controllers -- use buildAnalyticsFilter                    | dzzlo_oms_api   |

---

## Architecture After Phase 7 Complete

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DZZLO Custom Analytics System                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  dzzlo_oms_app (React Native)                                              │
│  ├─ Analytics SDK (singleton)                                               │
│  │  ├─ Event queue + offline persistence                                    │
│  │  ├─ Session manager                                                      │
│  │  ├─ Screen tracking (auto via React Navigation)                         │
│  │  └─ Business event instrumentation (orders, invoices, payments, auth)   │
│  ├─ Correlation ID in every API request                                     │
│  └─ Error boundary → session_id + analytics event                          │
│        │                                                                    │
│        │ POST /api/v3/analytics/events (batch)                             │
│        │ POST /api/v3/analytics/session                                     │
│        │ + all normal API calls with X-Request-ID header                    │
│        │                                                                    │
│  dzzlo_oms_api (Express + MongoDB)                                         │
│  ├─ Ingestion API (batch events, sessions)                                 │
│  ├─ Query APIs (overview, funnels, retention, sessions, users, timeline)   │
│  ├─ Export APIs (CSV, JSON)                                                 │
│  ├─ API Performance analytics (from logs collection)                       │
│  ├─ Pre-computed aggregations (PM2 cron daily)                             │
│  ├─ Alert system (threshold-based anomaly detection)                       │
│  ├─ Correlation middleware (request_id links events ↔ logs)                │
│  └─ MongoDB Collections:                                                    │
│     ├─ analytics_events (TTL 90 days)                                      │
│     ├─ analytics_sessions                                                   │
│     ├─ analytics_aggs (pre-computed)                                       │
│     ├─ analytics_alerts                                                     │
│     ├─ logs (enhanced with request_id)                                     │
│     └─ errors (enhanced with session_id)                                   │
│        │                                                                    │
│        │ GET /api/v3/analytics/query/*                                      │
│        │                                                                    │
│  dzzlo_analytics (Next.js Dashboard)                                       │
│  ├─ Overview: DAU/WAU/MAU KPIs + trend charts                             │
│  ├─ Live Feed: Real-time event stream                                      │
│  ├─ Funnels: Order→Invoice→Payment conversion                             │
│  ├─ Retention: Weekly/monthly cohort grids                                 │
│  ├─ Sessions: Explorer + replay view                                       │
│  ├─ Events: Explorer with time-series charts                               │
│  ├─ Users: Activity list + correlated timeline                             │
│  ├─ API Performance: Endpoint latency rankings                             │
│  ├─ Alerts: Anomaly detection dashboard                                    │
│  └─ Export: CSV/JSON download from any view                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```
