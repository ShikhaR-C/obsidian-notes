# Phase 4: Analytics Query APIs

## Goal

Build aggregation endpoints that transform raw event data into meaningful analytics: funnels, retention cohorts, session metrics, event counts, and live feeds. These APIs power the Next.js dashboard (Phase 6).

## Prerequisites

- Phase 1 complete (event data exists in MongoDB)
- Phase 3 recommended (meaningful business events being tracked)

## Deliverables

- 7 query endpoints for the analytics API
- MongoDB aggregation pipelines optimized with indexes
- SuperAdmin-only access control
- Pagination and date range filtering

---

## Step 4.1: Analytics Query Routes

**File to create:** `api_v3/routes/analytics/queries.js`

```javascript
const express = require("express")
const router = express.Router()
const { protect, authorize } = require("../../../helpers/auth")
const {
  getOverview,
  getEventCounts,
  getLiveEvents,
  getFunnel,
  getRetention,
  getSessions,
  getUserActivity,
} = require("../../controllers/analytics/queries")

// All query routes are SuperAdmin only
router.use(protect)
router.use(authorize("superadmin"))

router.get("/overview", getOverview)
router.get("/events/count", getEventCounts)
router.get("/events/live", getLiveEvents)
router.get("/funnel", getFunnel)
router.get("/retention", getRetention)
router.get("/sessions", getSessions)
router.get("/users/activity", getUserActivity)

module.exports = router
```

**File to modify:** `api_v3/routes/analytics/index.js`

Add: `router.use("/query", require("./queries"));`

---

## Step 4.2: Overview Endpoint

**Endpoint:** `GET /api/v3/analytics/query/overview`

**Query params:** `?from=&to=&company_id=`

**Returns:** DAU, WAU, MAU, total events today, average session duration, top events

```javascript
exports.getOverview = asyncHandler(async (req, res) => {
  const { company_id } = req.query
  const now = new Date()
  const todayStart = new Date(now)
  todayStart.setHours(0, 0, 0, 0)
  const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  const monthAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)

  const matchFilter = {}
  if (company_id) matchFilter.company_id = new mongoose.Types.ObjectId(company_id)

  // Use $facet for parallel aggregation in a single query
  const result = await AnalyticsEvent.aggregate([
    { $match: { ...matchFilter, server_timestamp: { $gte: monthAgo } } },
    {
      $facet: {
        dau: [
          { $match: { server_timestamp: { $gte: todayStart } } },
          { $group: { _id: "$user_id" } },
          { $count: "count" },
        ],
        wau: [
          { $match: { server_timestamp: { $gte: weekAgo } } },
          { $group: { _id: "$user_id" } },
          { $count: "count" },
        ],
        mau: [{ $group: { _id: "$user_id" } }, { $count: "count" }],
        eventsToday: [{ $match: { server_timestamp: { $gte: todayStart } } }, { $count: "count" }],
        topEvents: [
          { $match: { server_timestamp: { $gte: weekAgo } } },
          { $group: { _id: "$event_name", count: { $sum: 1 } } },
          { $sort: { count: -1 } },
          { $limit: 10 },
        ],
      },
    },
  ])

  // Session duration average
  const sessionAvg = await AnalyticsSession.aggregate([
    { $match: { started_at: { $gte: weekAgo }, duration_ms: { $gt: 0 } } },
    { $group: { _id: null, avg_duration: { $avg: "$duration_ms" } } },
  ])

  const facet = result[0]
  res.json({
    success: true,
    data: {
      dau: facet.dau[0]?.count || 0,
      wau: facet.wau[0]?.count || 0,
      mau: facet.mau[0]?.count || 0,
      events_today: facet.eventsToday[0]?.count || 0,
      avg_session_duration_ms: sessionAvg[0]?.avg_duration || 0,
      top_events: facet.topEvents,
    },
  })
})
```

---

## Step 4.3: Event Counts Endpoint

**Endpoint:** `GET /api/v3/analytics/query/events/count`

**Query params:** `?event_name=&event_category=&group_by=day|hour|week|month&from=&to=&company_id=&user_role=&device_os=`

```javascript
exports.getEventCounts = asyncHandler(async (req, res) => {
  const {
    event_name,
    event_category,
    group_by = "day",
    from,
    to,
    company_id,
    user_role,
    device_os,
  } = req.query

  const matchFilter = {}
  if (event_name) matchFilter.event_name = event_name
  if (event_category) matchFilter.event_category = event_category
  if (company_id) matchFilter.company_id = new mongoose.Types.ObjectId(company_id)
  if (user_role) matchFilter.user_role = user_role
  if (device_os) matchFilter.device_os = device_os
  if (from || to) {
    matchFilter.server_timestamp = {}
    if (from) matchFilter.server_timestamp.$gte = new Date(from)
    if (to) matchFilter.server_timestamp.$lte = new Date(to)
  }

  const dateFormats = {
    hour: "%Y-%m-%d %H:00",
    day: "%Y-%m-%d",
    week: "%Y-W%V",
    month: "%Y-%m",
  }

  const result = await AnalyticsEvent.aggregate([
    { $match: matchFilter },
    {
      $group: {
        _id: {
          period: {
            $dateToString: {
              format: dateFormats[group_by],
              date: "$server_timestamp",
              timezone: "Asia/Kolkata",
            },
          },
          event_name: "$event_name",
        },
        count: { $sum: 1 },
        unique_users: { $addToSet: "$user_id" },
      },
    },
    {
      $project: {
        _id: 0,
        period: "$_id.period",
        event_name: "$_id.event_name",
        count: 1,
        unique_users: { $size: "$unique_users" },
      },
    },
    { $sort: { period: 1 } },
  ])

  res.json({ success: true, data: result })
})
```

---

## Step 4.4: Live Events Feed

**Endpoint:** `GET /api/v3/analytics/query/events/live`

**Query params:** `?limit=100&event_name=&event_category=&user_id=`

```javascript
exports.getLiveEvents = asyncHandler(async (req, res) => {
  const { limit = 100, event_name, event_category, user_id } = req.query

  const matchFilter = {}
  if (event_name) matchFilter.event_name = event_name
  if (event_category) matchFilter.event_category = event_category
  if (user_id) matchFilter.user_id = new mongoose.Types.ObjectId(user_id)

  const events = await AnalyticsEvent.find(matchFilter)
    .sort({ server_timestamp: -1 })
    .limit(Math.min(parseInt(limit), 500))
    .select(
      "event_name event_category event_properties screen_name user_id user_role device_os app_version server_timestamp session_id",
    )
    .lean()

  res.json({ success: true, data: events, count: events.length })
})
```

---

## Step 4.5: Funnel Analysis Endpoint

**Endpoint:** `GET /api/v3/analytics/query/funnel`

**Query params:** `?steps=order_submitted,invoice_created,payment_completed&from=&to=&company_id=`

```javascript
exports.getFunnel = asyncHandler(async (req, res, next) => {
  const { steps: stepsStr, from, to, company_id } = req.query

  if (!stepsStr)
    return next(new ErrorResponse("steps parameter required (comma-separated event names)", 400))

  const steps = stepsStr.split(",").map((s) => s.trim())

  const matchFilter = { event_name: { $in: steps } }
  if (company_id) matchFilter.company_id = new mongoose.Types.ObjectId(company_id)
  if (from || to) {
    matchFilter.server_timestamp = {}
    if (from) matchFilter.server_timestamp.$gte = new Date(from)
    if (to) matchFilter.server_timestamp.$lte = new Date(to)
  }

  const userSteps = await AnalyticsEvent.aggregate([
    { $match: matchFilter },
    { $sort: { server_timestamp: 1 } },
    {
      $group: {
        _id: "$user_id",
        completed_steps: { $addToSet: "$event_name" },
        first_event: { $first: "$server_timestamp" },
        last_event: { $last: "$server_timestamp" },
      },
    },
  ])

  const funnelData = steps.map((step, index) => {
    const usersAtStep = userSteps.filter((u) => u.completed_steps.includes(step)).length
    const previousCount =
      index === 0
        ? userSteps.length
        : userSteps.filter((u) => u.completed_steps.includes(steps[index - 1])).length

    return {
      step_index: index,
      event_name: step,
      users: usersAtStep,
      conversion_rate: previousCount > 0 ? ((usersAtStep / previousCount) * 100).toFixed(1) : 0,
      overall_rate: userSteps.length > 0 ? ((usersAtStep / userSteps.length) * 100).toFixed(1) : 0,
    }
  })

  res.json({
    success: true,
    data: {
      steps: funnelData,
      total_users: userSteps.length,
      date_range: { from, to },
    },
  })
})
```

---

## Step 4.6: Retention Cohort Endpoint

**Endpoint:** `GET /api/v3/analytics/query/retention`

**Query params:** `?period=week|month&cohorts=8&company_id=`

```javascript
exports.getRetention = asyncHandler(async (req, res) => {
  const { period = "week", cohorts = 8, company_id } = req.query
  const numCohorts = Math.min(parseInt(cohorts), 12)

  const periodMs = period === "week" ? 7 * 24 * 60 * 60 * 1000 : 30 * 24 * 60 * 60 * 1000
  const lookbackMs = numCohorts * periodMs
  const startDate = new Date(Date.now() - lookbackMs)

  const matchFilter = { server_timestamp: { $gte: startDate } }
  if (company_id) matchFilter.company_id = new mongoose.Types.ObjectId(company_id)

  // Find each user's first event date and active dates
  const userFirstSeen = await AnalyticsEvent.aggregate([
    { $match: { ...matchFilter, user_id: { $ne: null } } },
    {
      $group: {
        _id: "$user_id",
        first_seen: { $min: "$server_timestamp" },
        active_dates: {
          $addToSet: {
            $dateToString: {
              format: "%Y-%m-%d",
              date: "$server_timestamp",
              timezone: "Asia/Kolkata",
            },
          },
        },
      },
    },
  ])

  // Build cohort grid
  const cohortGrid = []
  for (let i = 0; i < numCohorts; i++) {
    const cohortStart = new Date(startDate.getTime() + i * periodMs)
    const cohortEnd = new Date(cohortStart.getTime() + periodMs)

    const cohortUsers = userFirstSeen.filter(
      (u) => u.first_seen >= cohortStart && u.first_seen < cohortEnd,
    )
    const cohortSize = cohortUsers.length
    const retention = []

    for (let j = 0; j <= numCohorts - i - 1; j++) {
      const periodStart = new Date(cohortStart.getTime() + j * periodMs)
      const periodEnd = new Date(periodStart.getTime() + periodMs)

      const activeInPeriod = cohortUsers.filter((u) =>
        u.active_dates.some((d) => {
          const date = new Date(d)
          return date >= periodStart && date < periodEnd
        }),
      ).length

      retention.push({
        period_index: j,
        active_users: activeInPeriod,
        retention_rate: cohortSize > 0 ? ((activeInPeriod / cohortSize) * 100).toFixed(1) : 0,
      })
    }

    cohortGrid.push({
      cohort_start: cohortStart,
      cohort_end: cohortEnd,
      cohort_size: cohortSize,
      retention,
    })
  }

  res.json({ success: true, data: { period, cohorts: cohortGrid } })
})
```

---

## Step 4.7: Sessions Endpoint

**Endpoint:** `GET /api/v3/analytics/query/sessions`

**Query params:** `?from=&to=&user_id=&page=1&limit=50&min_duration=&max_duration=`

```javascript
exports.getSessions = asyncHandler(async (req, res) => {
  const { from, to, user_id, page = 1, limit = 50, min_duration, max_duration } = req.query

  const filter = {}
  if (user_id) filter.user_id = new mongoose.Types.ObjectId(user_id)
  if (from || to) {
    filter.started_at = {}
    if (from) filter.started_at.$gte = new Date(from)
    if (to) filter.started_at.$lte = new Date(to)
  }
  if (min_duration) filter.duration_ms = { $gte: parseInt(min_duration) }
  if (max_duration)
    filter.duration_ms = {
      ...filter.duration_ms,
      $lte: parseInt(max_duration),
    }

  const skip = (parseInt(page) - 1) * parseInt(limit)

  const [sessions, total] = await Promise.all([
    AnalyticsSession.find(filter)
      .sort({ started_at: -1 })
      .skip(skip)
      .limit(parseInt(limit))
      .populate("user_id", "username email role")
      .lean(),
    AnalyticsSession.countDocuments(filter),
  ])

  res.json({
    success: true,
    data: sessions,
    pagination: {
      page: parseInt(page),
      limit: parseInt(limit),
      total,
      pages: Math.ceil(total / parseInt(limit)),
    },
  })
})
```

---

## Step 4.8: User Activity Endpoint

**Endpoint:** `GET /api/v3/analytics/query/users/activity`

**Query params:** `?from=&to=&sort_by=event_count|last_active&limit=50&page=1`

```javascript
exports.getUserActivity = asyncHandler(async (req, res) => {
  const { from, to, sort_by = "event_count", limit = 50, page = 1 } = req.query

  const matchFilter = { user_id: { $ne: null } }
  if (from || to) {
    matchFilter.server_timestamp = {}
    if (from) matchFilter.server_timestamp.$gte = new Date(from)
    if (to) matchFilter.server_timestamp.$lte = new Date(to)
  }

  const sortField = sort_by === "last_active" ? { last_active: -1 } : { event_count: -1 }
  const skip = (parseInt(page) - 1) * parseInt(limit)

  const result = await AnalyticsEvent.aggregate([
    { $match: matchFilter },
    {
      $group: {
        _id: "$user_id",
        event_count: { $sum: 1 },
        session_count: { $addToSet: "$session_id" },
        first_active: { $min: "$server_timestamp" },
        last_active: { $max: "$server_timestamp" },
        roles: { $addToSet: "$user_role" },
        devices: { $addToSet: "$device_os" },
      },
    },
    {
      $project: {
        user_id: "$_id",
        event_count: 1,
        session_count: { $size: "$session_count" },
        first_active: 1,
        last_active: 1,
        roles: 1,
        devices: 1,
      },
    },
    { $sort: sortField },
    { $skip: skip },
    { $limit: parseInt(limit) },
    {
      $lookup: {
        from: "users",
        localField: "_id",
        foreignField: "_id",
        as: "user_info",
        pipeline: [{ $project: { username: 1, email: 1, phone: 1, role: 1 } }],
      },
    },
    { $unwind: { path: "$user_info", preserveNullAndEmptyArrays: true } },
  ])

  res.json({ success: true, data: result, count: result.length })
})
```

---

## Step 4.9: Additional Aggregation Indexes

**File to modify:** `models/analytics_events.js`

```javascript
// Funnel queries
analytics_event_Schema.index({
  event_name: 1,
  user_id: 1,
  server_timestamp: -1,
})
// Live feed
analytics_event_Schema.index({ server_timestamp: -1, event_name: 1 })
// User activity
analytics_event_Schema.index({ user_id: 1, server_timestamp: -1 })
```

---

## Step 4.10: Verification Checklist

- [ ] Seed 1000+ test events across 20+ users, 50+ sessions, 30 days
- [ ] `GET /analytics/query/overview` → returns valid DAU/WAU/MAU counts
- [ ] `GET /analytics/query/events/count?event_name=order_submitted&group_by=day` → returns daily counts
- [ ] `GET /analytics/query/events/live?limit=50` → returns chronological feed
- [ ] `GET /analytics/query/funnel?steps=order_submitted,invoice_created,payment_completed` → returns step-by-step conversion
- [ ] `GET /analytics/query/retention?period=week&cohorts=4` → returns cohort grid with retention %
- [ ] `GET /analytics/query/sessions?page=1&limit=10` → returns paginated sessions
- [ ] `GET /analytics/query/users/activity?sort_by=event_count` → returns top active users
- [ ] All endpoints return 403 for non-superadmin users
- [ ] All endpoints support `company_id` filtering
- [ ] Query response time < 500ms for 10K events

---

## Files Summary

| Action | File                                                       |
| ------ | ---------------------------------------------------------- |
| CREATE | `api_v3/routes/analytics/queries.js`                       |
| CREATE | `api_v3/controllers/analytics/queries.js`                  |
| MODIFY | `api_v3/routes/analytics/index.js` — mount query routes    |
| MODIFY | `models/analytics_events.js` — add query-optimized indexes |
