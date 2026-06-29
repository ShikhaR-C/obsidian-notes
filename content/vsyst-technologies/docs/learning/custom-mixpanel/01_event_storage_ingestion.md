# Phase 1: Event Storage Foundation & Backend Ingestion API

## Goal

Create MongoDB schemas optimized for time-series event storage, build the batch ingestion endpoint, and enhance existing logging middleware with a correlation ID. Delivers a working event pipeline.

## Prerequisites

- None (this is the foundation phase)

## Deliverables

- `analytics_events` Mongoose model
- `analytics_sessions` Mongoose model
- `POST /api/v3/analytics/events` batch ingestion endpoint
- `POST /api/v3/analytics/session` session create/update endpoint
- Enhanced logging middleware with `request_id` correlation

---

## Step 1.1: Create `analytics_events` Model

**File to create:** `models/analytics_events.js`

### Schema Design

```javascript
const mongoose = require("mongoose");

const analytics_event_Schema = new mongoose.Schema(
  {
    // Identity
    user_id: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "users",
      index: true,
    },
    device_id: { type: String, index: true }, // from meta.uniqueId
    session_id: { type: String, index: true }, // UUID generated on app open
    company_id: { type: mongoose.Schema.Types.ObjectId, index: true },

    // Event data
    event_name: { type: String, required: true, index: true }, // e.g., "screen_view", "button_click", "order_created"
    event_category: { type: String, index: true }, // "navigation", "order", "invoice", "payment", "auth", "system"
    event_properties: { type: mongoose.Schema.Types.Mixed }, // arbitrary key-value pairs per event

    // Context
    screen_name: { type: String },
    user_role: { type: String, enum: ["superadmin", "dealer", "customer"] },
    app_version: { type: String },
    build_number: { type: String },
    device_os: { type: String }, // "iOS" or "Android"
    device_brand: { type: String },
    system_version: { type: String },

    // Correlation
    api_request_id: { type: String }, // links to enhanced logs collection

    // Timing
    client_timestamp: { type: Date }, // when event actually occurred on device
    server_timestamp: { type: Date, default: Date.now },
    timeIST: { type: String },
  },
  { timestamps: true },
);

// Compound indexes for common query patterns
analytics_event_Schema.index({ event_name: 1, server_timestamp: -1 });
analytics_event_Schema.index({
  user_id: 1,
  session_id: 1,
  server_timestamp: 1,
});
analytics_event_Schema.index({
  company_id: 1,
  event_name: 1,
  server_timestamp: -1,
});
analytics_event_Schema.index({ session_id: 1, server_timestamp: 1 });
analytics_event_Schema.index(
  { server_timestamp: 1 },
  { expireAfterSeconds: 7776000 },
); // 90-day TTL

module.exports = mongoose.model("analytics_events", analytics_event_Schema);
```

### Design Decisions

- Uses **default mongoose connection** (main GST2010 database), same as logs/errors models
- **TTL index** (90-day expiry) for automatic cleanup — configurable via constant
- `client_timestamp` separate from `server_timestamp` — handles offline-queued events that arrive late
- `session_id` is client-generated UUID — enables session reconstruction without server-side session management
- `Mixed` type for `event_properties` matches existing pattern in `logs.js` and `errors.js`
- **Event categories**: navigation, order, invoice, payment, auth, vehicle, voucher, system, server

---

## Step 1.2: Create `analytics_sessions` Model

**File to create:** `models/analytics_sessions.js`

```javascript
const mongoose = require("mongoose");

const analytics_session_Schema = new mongoose.Schema(
  {
    session_id: { type: String, required: true, unique: true },
    user_id: {
      type: mongoose.Schema.Types.ObjectId,
      ref: "users",
      index: true,
    },
    device_id: { type: String },
    company_id: { type: mongoose.Schema.Types.ObjectId },
    user_role: { type: String },

    // Session lifecycle
    started_at: { type: Date, required: true },
    ended_at: { type: Date },
    duration_ms: { type: Number }, // computed on session end
    is_active: { type: Boolean, default: true },

    // Session summary (updated incrementally)
    event_count: { type: Number, default: 0 },
    screens_visited: [{ type: String }],

    // Device context (captured once at session start)
    app_version: { type: String },
    device_os: { type: String },
    device_brand: { type: String },
    system_version: { type: String },
    build_number: { type: String },
  },
  { timestamps: true },
);

analytics_session_Schema.index({ user_id: 1, started_at: -1 });
analytics_session_Schema.index({ started_at: -1 });
analytics_session_Schema.index({ is_active: 1 });

module.exports = mongoose.model("analytics_sessions", analytics_session_Schema);
```

---

## Step 1.3: Create Batch Ingestion Controller

**File to create:** `api_v3/controllers/analytics/events.js`

```javascript
const asyncHandler = require("../../../helpers/async");
const AnalyticsEvent = require("../../../models/analytics_events");
const ErrorResponse = require("../../../helpers/ErrorResponse");
const { getUserFromToken } = require("../../../helpers/auth");

// @desc    Batch ingest analytics events
// @route   POST /api/v3/analytics/events
// @access  API Key required
exports.ingestEvents = asyncHandler(async (req, res, next) => {
  const { events } = req.body;

  if (!events || !Array.isArray(events) || events.length === 0) {
    return next(new ErrorResponse("Events array is required", 400));
  }

  if (events.length > 50) {
    return next(new ErrorResponse("Maximum 50 events per batch", 400));
  }

  // Extract user context from JWT if available
  let userContext = {};
  try {
    const decoded = await getUserFromToken(req.headers);
    if (decoded && decoded.user) {
      userContext = {
        user_id: decoded.user._id,
        company_id: decoded.user.co_id,
        user_role: decoded.user.role,
      };
    }
  } catch (e) {
    // Anonymous events are OK (pre-login screens)
  }

  const now = new Date();
  const timeIST = now.toLocaleString("en-US", { timeZone: "Asia/Kolkata" });

  // Enrich each event
  const enrichedEvents = events.map((event) => ({
    ...event,
    ...userContext,
    // Client values override if present
    user_id: event.user_id || userContext.user_id,
    company_id: event.company_id || userContext.company_id,
    user_role: event.user_role || userContext.user_role,
    server_timestamp: now,
    timeIST,
  }));

  let accepted = 0;
  let rejected = 0;

  try {
    const result = await AnalyticsEvent.insertMany(enrichedEvents, {
      ordered: false,
    });
    accepted = result.length;
  } catch (err) {
    if (err.insertedDocs) {
      accepted = err.insertedDocs.length;
      rejected = enrichedEvents.length - accepted;
    } else {
      return next(new ErrorResponse("Failed to ingest events", 500));
    }
  }

  res.status(201).json({
    success: true,
    data: { accepted, rejected, total: events.length },
  });
});
```

---

## Step 1.4: Create Session Controller

**File to create:** `api_v3/controllers/analytics/sessions.js`

```javascript
const asyncHandler = require("../../../helpers/async");
const AnalyticsSession = require("../../../models/analytics_sessions");
const ErrorResponse = require("../../../helpers/ErrorResponse");

// @desc    Create or update analytics session
// @route   POST /api/v3/analytics/session
exports.upsertSession = asyncHandler(async (req, res, next) => {
  const { session_id, action, ...sessionData } = req.body;

  if (!session_id) {
    return next(new ErrorResponse("session_id is required", 400));
  }

  if (action === "start") {
    const session = await AnalyticsSession.findOneAndUpdate(
      { session_id },
      {
        $set: {
          ...sessionData,
          session_id,
          started_at: new Date(),
          is_active: true,
        },
      },
      { upsert: true, new: true },
    );
    return res.status(201).json({ success: true, data: session });
  }

  if (action === "end") {
    const session = await AnalyticsSession.findOneAndUpdate(
      { session_id },
      {
        $set: {
          ended_at: new Date(),
          is_active: false,
          ...sessionData,
        },
      },
      { new: true },
    );
    return res.status(200).json({ success: true, data: session });
  }

  if (action === "update") {
    const updateOps = { $inc: { event_count: 1 } };
    if (sessionData.screen_name) {
      updateOps.$addToSet = { screens_visited: sessionData.screen_name };
    }
    const session = await AnalyticsSession.findOneAndUpdate(
      { session_id },
      updateOps,
      { new: true },
    );
    return res.status(200).json({ success: true, data: session });
  }

  return next(
    new ErrorResponse("action must be 'start', 'end', or 'update'", 400),
  );
});
```

---

## Step 1.5: Create Analytics Routes

**File to create:** `api_v3/routes/analytics/index.js`

```javascript
const express = require("express");
const router = express.Router();
const { ingestEvents } = require("../../controllers/analytics/events");
const { upsertSession } = require("../../controllers/analytics/sessions");

router.post("/events", ingestEvents);
router.post("/session", upsertSession);

module.exports = router;
```

---

## Step 1.6: Register Analytics Routes in API v3

**File to modify:** `api_v/api3.js`

Add **before** `check_user_company_status()` middleware:

```javascript
router.use("/analytics", require("./../api_v3/routes/analytics"));
```

**Why before company check?** We want to capture events even from users whose company status is in transition, and pre-login screen views from unauthenticated users. The API key middleware (`api_key_v3`) still applies for security.

---

## Step 1.7: Enhance Logging Middleware with Correlation ID

**File to modify:** `helpers/middlewares.js`

In the `logging()` middleware (lines 119-174):

1. Add `const { v4: uuidv4 } = require("uuid");` at the top of the file
2. At the start of the middleware function, generate: `req.request_id = uuidv4();`
3. Include `request_id: req.request_id` in the `morganDuplicate` object stored to the logs collection
4. Set response header: `res.setHeader("X-Request-ID", req.request_id);` so the frontend can capture it

**File to modify:** `models/logs.js`

Add field: `request_id: { type: String, index: true }`

**File to modify:** `package.json`

Add dependency: `"uuid": "^9.0.0"`

---

## Step 1.8: Verification Checklist

- [ ] `npm install` succeeds with uuid added
- [ ] Start dev server, POST batch of 3 test events to `/api/v3/analytics/events` with valid JWT — returns `{ accepted: 3, rejected: 0 }`
- [ ] Verify events stored in MongoDB `analytics_events` collection with correct timestamps and enriched user context
- [ ] POST session start event, verify `analytics_sessions` document created with `is_active: true`
- [ ] POST session end, verify `ended_at` populated and `is_active: false`
- [ ] Make any normal API request, verify `logs` collection now includes `request_id` field
- [ ] Check response header `X-Request-ID` is present on API responses
- [ ] Send event with matching `api_request_id`, verify correlation is queryable: `db.analytics_events.find({ api_request_id: "some-uuid" })`
- [ ] Verify TTL index exists: `db.analytics_events.getIndexes()`

---

## Files Summary

| Action | File                                       |
| ------ | ------------------------------------------ |
| CREATE | `models/analytics_events.js`               |
| CREATE | `models/analytics_sessions.js`             |
| CREATE | `api_v3/controllers/analytics/events.js`   |
| CREATE | `api_v3/controllers/analytics/sessions.js` |
| CREATE | `api_v3/routes/analytics/index.js`         |
| MODIFY | `api_v/api3.js` — add analytics route      |
| MODIFY | `helpers/middlewares.js` — add request_id  |
| MODIFY | `models/logs.js` — add request_id field    |
| MODIFY | `package.json` — add uuid dependency       |
