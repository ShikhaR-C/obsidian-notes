# Phase 5: Pre-Computed Aggregations (Performance Optimization)

## Goal

For queries that scan large date ranges, pre-compute daily/weekly/monthly aggregations using a scheduled job. Prevents expensive real-time aggregations on growing event data. Target: historical queries respond in <200ms regardless of data volume.

## Prerequisites

- Phase 4 complete (query patterns defined)

## Deliverables

- `analytics_aggs` Mongoose model for pre-computed metrics
- Aggregation worker script (runs daily)
- PM2 cron integration for scheduling
- Query endpoints updated to use pre-computed data for historical periods

---

## Step 5.1: Create `analytics_aggs` Model

**File to create:** `models/analytics_aggs.js`

```javascript
const mongoose = require("mongoose")

const analytics_agg_Schema = new mongoose.Schema(
  {
    // Metric identification
    metric_name: { type: String, required: true },
    period_type: {
      type: String,
      enum: ["hourly", "daily", "weekly", "monthly"],
      required: true,
    },
    period_start: { type: Date, required: true },
    period_end: { type: Date },

    // Dimension breakdowns (null = "all")
    company_id: { type: mongoose.Schema.Types.ObjectId },
    user_role: { type: String },
    event_name: { type: String },
    device_os: { type: String },

    // Metric values
    value: { type: Number, default: 0 },
    unique_users: { type: Number, default: 0 },
    detail: { type: mongoose.Schema.Types.Mixed },
  },
  { timestamps: true },
)

// Upsert key — one document per metric+period+dimensions
analytics_agg_Schema.index(
  {
    metric_name: 1,
    period_type: 1,
    period_start: 1,
    company_id: 1,
    user_role: 1,
    event_name: 1,
    device_os: 1,
  },
  { unique: true },
)

// Query indexes
analytics_agg_Schema.index({
  metric_name: 1,
  period_type: 1,
  period_start: -1,
})
analytics_agg_Schema.index({
  metric_name: 1,
  period_type: 1,
  company_id: 1,
  period_start: -1,
})

module.exports = mongoose.model("analytics_aggs", analytics_agg_Schema)
```

### Metrics Computed

| metric_name            | Description                   | Dimensions                        |
| ---------------------- | ----------------------------- | --------------------------------- |
| `dau`                  | Daily Active Users            | company_id, user_role, device_os  |
| `event_count`          | Event count per name          | company_id, event_name, user_role |
| `session_count`        | Number of sessions            | company_id, device_os             |
| `session_avg_duration` | Average session duration (ms) | company_id, device_os             |
| `top_screens`          | Top screens by view count     | company_id (detail: array)        |
| `new_users`            | First-time users count        | company_id, user_role             |
| `error_count`          | App crash count               | company_id, device_os             |

---

## Step 5.2: Aggregation Worker

**File to create:** `helpers/analyticsAggregator.js`

```javascript
const mongoose = require("mongoose")
const AnalyticsEvent = require("../models/analytics_events")
const AnalyticsSession = require("../models/analytics_sessions")
const AnalyticsAgg = require("../models/analytics_aggs")

const computeDailyAggregations = async (targetDate) => {
  const dayStart = new Date(targetDate)
  dayStart.setHours(0, 0, 0, 0)
  const dayEnd = new Date(dayStart)
  dayEnd.setDate(dayEnd.getDate() + 1)

  console.log(`[Analytics Aggregator] Computing for ${dayStart.toISOString().split("T")[0]}`)

  const dateMatch = { server_timestamp: { $gte: dayStart, $lt: dayEnd } }

  // 1. DAU — broken down by company, role, OS
  const dauResults = await AnalyticsEvent.aggregate([
    { $match: { ...dateMatch, user_id: { $ne: null } } },
    {
      $group: {
        _id: {
          company_id: "$company_id",
          user_role: "$user_role",
          device_os: "$device_os",
        },
        unique_users: { $addToSet: "$user_id" },
      },
    },
    { $project: { _id: 1, unique_users: { $size: "$unique_users" } } },
  ])

  for (const row of dauResults) {
    await AnalyticsAgg.findOneAndUpdate(
      {
        metric_name: "dau",
        period_type: "daily",
        period_start: dayStart,
        company_id: row._id.company_id || null,
        user_role: row._id.user_role || null,
        device_os: row._id.device_os || null,
      },
      {
        $set: {
          period_end: dayEnd,
          value: row.unique_users,
          unique_users: row.unique_users,
        },
      },
      { upsert: true },
    )
  }

  // Global DAU (no dimension breakdown)
  const globalDAU = await AnalyticsEvent.aggregate([
    { $match: { ...dateMatch, user_id: { $ne: null } } },
    { $group: { _id: "$user_id" } },
    { $count: "count" },
  ])

  await AnalyticsAgg.findOneAndUpdate(
    {
      metric_name: "dau",
      period_type: "daily",
      period_start: dayStart,
      company_id: null,
      user_role: null,
      device_os: null,
    },
    {
      $set: {
        period_end: dayEnd,
        value: globalDAU[0]?.count || 0,
        unique_users: globalDAU[0]?.count || 0,
      },
    },
    { upsert: true },
  )

  // 2. Event counts — by event_name, company, role
  const eventCounts = await AnalyticsEvent.aggregate([
    { $match: dateMatch },
    {
      $group: {
        _id: {
          event_name: "$event_name",
          company_id: "$company_id",
          user_role: "$user_role",
        },
        count: { $sum: 1 },
        unique_users: { $addToSet: "$user_id" },
      },
    },
  ])

  for (const row of eventCounts) {
    await AnalyticsAgg.findOneAndUpdate(
      {
        metric_name: "event_count",
        period_type: "daily",
        period_start: dayStart,
        event_name: row._id.event_name,
        company_id: row._id.company_id || null,
        user_role: row._id.user_role || null,
      },
      {
        $set: {
          period_end: dayEnd,
          value: row.count,
          unique_users: row.unique_users?.length || 0,
        },
      },
      { upsert: true },
    )
  }

  // 3. Session metrics
  const sessionMetrics = await AnalyticsSession.aggregate([
    { $match: { started_at: { $gte: dayStart, $lt: dayEnd } } },
    {
      $group: {
        _id: { company_id: "$company_id", device_os: "$device_os" },
        count: { $sum: 1 },
        avg_duration: { $avg: "$duration_ms" },
      },
    },
  ])

  for (const row of sessionMetrics) {
    await AnalyticsAgg.findOneAndUpdate(
      {
        metric_name: "session_count",
        period_type: "daily",
        period_start: dayStart,
        company_id: row._id.company_id || null,
        device_os: row._id.device_os || null,
      },
      { $set: { period_end: dayEnd, value: row.count } },
      { upsert: true },
    )

    await AnalyticsAgg.findOneAndUpdate(
      {
        metric_name: "session_avg_duration",
        period_type: "daily",
        period_start: dayStart,
        company_id: row._id.company_id || null,
        device_os: row._id.device_os || null,
      },
      {
        $set: { period_end: dayEnd, value: Math.round(row.avg_duration || 0) },
      },
      { upsert: true },
    )
  }

  // 4. Top screens
  const topScreens = await AnalyticsEvent.aggregate([
    { $match: { ...dateMatch, event_name: "screen_view" } },
    { $group: { _id: "$screen_name", count: { $sum: 1 } } },
    { $sort: { count: -1 } },
    { $limit: 20 },
  ])

  await AnalyticsAgg.findOneAndUpdate(
    {
      metric_name: "top_screens",
      period_type: "daily",
      period_start: dayStart,
      company_id: null,
    },
    { $set: { period_end: dayEnd, detail: topScreens } },
    { upsert: true },
  )

  console.log(`[Analytics Aggregator] Done for ${dayStart.toISOString().split("T")[0]}`)
}

// Backfill for a range of dates
const backfillAggregations = async (startDate, endDate) => {
  const current = new Date(startDate)
  while (current < endDate) {
    await computeDailyAggregations(current)
    current.setDate(current.getDate() + 1)
  }
}

module.exports = { computeDailyAggregations, backfillAggregations }
```

---

## Step 5.3: PM2 Cron Job Script

**File to create:** `scripts/run_analytics_agg.js`

```javascript
/**
 * Analytics Daily Aggregation Script
 * Run via PM2 cron or manually: node scripts/run_analytics_agg.js [YYYY-MM-DD]
 */
const dotenv = require("dotenv")
dotenv.config({ path: `.env.${process.env.NODE_ENV || "development"}` })

const { connectDB } = require("../helpers/db_conn")
const { computeDailyAggregations } = require("../helpers/analyticsAggregator")

const run = async () => {
  try {
    await connectDB()

    // Default: compute yesterday's aggregations
    const targetDate = process.argv[2]
      ? new Date(process.argv[2])
      : new Date(Date.now() - 24 * 60 * 60 * 1000)

    await computeDailyAggregations(targetDate)
    console.log("[Analytics Cron] Aggregation complete")
    process.exit(0)
  } catch (err) {
    console.error("[Analytics Cron] Failed:", err.message)
    process.exit(1)
  }
}

run()
```

---

## Step 5.4: PM2 Ecosystem Configuration

**File to modify:** `ecosystem.config.js`

Add a new PM2 app entry:

```javascript
{
  name: "analytics-agg",
  script: "./scripts/run_analytics_agg.js",
  cron_restart: "5 0 * * *",   // Run at 00:05 IST daily
  autorestart: false,
  watch: false,
  env: {
    NODE_ENV: "production",
  },
}
```

---

## Step 5.5: Backfill API Endpoint (Admin Only)

**File to modify:** `api_v3/routes/analytics/queries.js`

Add:

```javascript
router.post("/backfill", triggerBackfill)
```

**Controller:**

```javascript
exports.triggerBackfill = asyncHandler(async (req, res, next) => {
  const { from, to } = req.body
  if (!from || !to) return next(new ErrorResponse("from and to dates required", 400))

  const { backfillAggregations } = require("../../../helpers/analyticsAggregator")

  // Run async — don't block the response
  backfillAggregations(new Date(from), new Date(to))
    .then(() => console.log("[Backfill] Complete"))
    .catch((err) => console.error("[Backfill] Failed:", err.message))

  res.json({
    success: true,
    message: `Backfill started for ${from} to ${to}. Running in background.`,
  })
})
```

---

## Step 5.6: Update Query Endpoints — Hybrid Strategy

**File to modify:** `api_v3/controllers/analytics/queries.js`

### Strategy

- **Historical data** (older than 24h): Read from `analytics_aggs` — fast, O(days) not O(events)
- **Today's data**: Query raw `analytics_events` — real-time accuracy
- **Merge results** in the controller

Example for DAU trend:

```javascript
// 29 days from analytics_aggs + today from raw events
const historicalDAU = await AnalyticsAgg.find({
  metric_name: "dau",
  period_type: "daily",
  period_start: { $gte: thirtyDaysAgo, $lt: todayStart },
  company_id: null,
  user_role: null,
  device_os: null,
})
  .sort({ period_start: 1 })
  .lean()

const todayDAU = await AnalyticsEvent.aggregate([
  {
    $match: { server_timestamp: { $gte: todayStart }, user_id: { $ne: null } },
  },
  { $group: { _id: "$user_id" } },
  { $count: "count" },
])

const dauTrend = [
  ...historicalDAU.map((d) => ({ date: d.period_start, value: d.value })),
  { date: todayStart, value: todayDAU[0]?.count || 0 },
]
```

---

## Step 5.7: Verification Checklist

- [ ] Seed 5000+ events across 30 days
- [ ] Run aggregation manually: `node scripts/run_analytics_agg.js 2026-03-15`
- [ ] Verify `analytics_aggs` documents created with correct counts
- [ ] Run backfill: `POST /analytics/query/backfill { from: "2026-03-01", to: "2026-04-01" }`
- [ ] Compare pre-computed DAU with raw aggregation query — numbers must match exactly
- [ ] Benchmark: 30-day trend query < 200ms using pre-computed data
- [ ] Verify PM2 cron config: `pm2 start ecosystem.config.js` shows analytics-agg
- [ ] Verify hybrid queries: overview shows real-time today + pre-computed history

---

## Files Summary

| Action | File                                                              |
| ------ | ----------------------------------------------------------------- |
| CREATE | `models/analytics_aggs.js`                                        |
| CREATE | `helpers/analyticsAggregator.js`                                  |
| CREATE | `scripts/run_analytics_agg.js`                                    |
| MODIFY | `ecosystem.config.js` — add cron job                              |
| MODIFY | `api_v3/controllers/analytics/queries.js` — use pre-computed data |
| MODIFY | `api_v3/routes/analytics/queries.js` — add backfill endpoint      |
