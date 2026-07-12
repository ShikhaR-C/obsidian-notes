# Phase 2: Frontend Analytics SDK (Event Collection & Offline Queue)

## Goal

Build a lightweight analytics module in the React Native app that captures events, manages sessions, queues events when offline, and flushes them in batches to the Phase 1 ingestion API.

## Prerequisites

- Phase 1 complete (ingestion endpoint available)

## Deliverables

- Analytics core module (singleton)
- Offline queue manager with AsyncStorage persistence
- Session manager with timeout handling
- Automatic screen view tracking via React Navigation
- Auth integration (identify/reset on login/logout)
- Axios interceptor enhancement for correlation IDs

---

## Step 2.1: Analytics Configuration

**File to create:** `src/utils/Analytics/config.js`

```javascript
export const ANALYTICS_CONFIG = {
  flushInterval: 30000, // 30 seconds
  maxBatchSize: 20, // events per flush
  maxQueueSize: 500, // max queued events before dropping oldest
  sessionTimeoutMs: 1800000, // 30 minutes inactivity = new session
  enabled: true, // master kill switch
  endpoint: "/analytics/events",
  sessionEndpoint: "/analytics/session",
  storageKey: "@analytics_queue",
  sessionStorageKey: "@analytics_session",
}
```

---

## Step 2.2: Analytics Core Module (Singleton)

**File to create:** `src/utils/Analytics/index.js`

### Why a Singleton (Not Redux)?

The analytics tracker must be callable from:

- React components (screen views)
- Redux thunks (login/logout in `store/slices/auth.js`)
- Axios interceptors (`utils/API/axiosReqRes.js`)
- Navigation listeners (`AppNavigatorContainer.js`)

A Redux slice would require dispatching from non-component code, adding unnecessary complexity. The singleton pattern mirrors how Mixpanel, Amplitude, and Segment SDKs work.

### API Surface

```javascript
import { ANALYTICS_CONFIG } from "./config"
import { QueueManager } from "./queue"
import { SessionManager } from "./session"
import DeviceInfo from "react-native-device-info"

// Cache static device info at module level (same pattern as createApi.js line 8-18)
const DEVICE_CONTEXT = {
  app_version: DeviceInfo.getVersion(),
  build_number: DeviceInfo.getBuildNumber(),
  device_os: DeviceInfo.getSystemName(),
  device_brand: DeviceInfo.getBrand(),
  system_version: DeviceInfo.getSystemVersion(),
  device_id: DeviceInfo.getUniqueIdSync(),
}

class Analytics {
  constructor() {
    this.queue = null
    this.session = null
    this.userId = null
    this.userRole = null
    this.companyId = null
    this.initialized = false
  }

  init(config = {}) {
    if (this.initialized) return
    this.config = { ...ANALYTICS_CONFIG, ...config }
    this.queue = new QueueManager(this.config)
    this.session = new SessionManager(this.config)
    this.session.start()
    this.initialized = true
  }

  track(eventName, properties = {}) {
    if (!this.initialized || !this.config.enabled) return

    const event = {
      event_name: eventName,
      event_category: properties.category || "general",
      event_properties: properties,
      screen_name: properties.screen_name,
      session_id: this.session.getSessionId(),
      user_id: this.userId,
      user_role: this.userRole,
      company_id: this.companyId,
      client_timestamp: new Date().toISOString(),
      ...DEVICE_CONTEXT,
    }

    this.queue.enqueue(event)
  }

  screen(screenName, properties = {}) {
    this.track("screen_view", {
      ...properties,
      screen_name: screenName,
      category: "navigation",
    })
    this.session.addScreen(screenName)
  }

  identify(userId, { role, companyId } = {}) {
    this.userId = userId
    this.userRole = role
    this.companyId = companyId
  }

  reset() {
    this.userId = null
    this.userRole = null
    this.companyId = null
    this.session.end()
    this.queue.flush()
  }

  flush() {
    if (this.queue) this.queue.flush()
  }

  destroy() {
    if (this.queue) this.queue.destroy()
    if (this.session) this.session.end()
    this.initialized = false
  }
}

export default new Analytics()
```

---

## Step 2.3: Offline Queue Manager

**File to create:** `src/utils/Analytics/queue.js`

### Core Behavior

- Maintains in-memory array of events
- Flush timer runs every `flushInterval` (30s)
- Flushes when queue reaches `maxBatchSize` (20 events) OR timer fires
- On network offline: events accumulate, persisted to AsyncStorage every 60s
- On network restored: immediate flush
- On app background: persist unflushed events to AsyncStorage
- On app foreground: recover events from AsyncStorage, merge into queue
- Drops oldest events if queue exceeds `maxQueueSize` (500)

### Implementation

```javascript
import AsyncStorage from "@react-native-async-storage/async-storage"
import NetInfo from "@react-native-community/netinfo"
import { AppState } from "react-native"
import API from "../API" // existing Axios instance

export class QueueManager {
  constructor(config) {
    this.config = config
    this.queue = []
    this.isFlushing = false
    this.isOnline = true

    // Network listener
    this.netInfoUnsubscribe = NetInfo.addEventListener((state) => {
      this.isOnline = state.isConnected
      if (this.isOnline && this.queue.length > 0) {
        this.flush()
      }
    })

    // AppState listener
    this.appStateSubscription = AppState.addEventListener("change", (nextState) => {
      if (nextState === "background" || nextState === "inactive") {
        this.persistToStorage()
      } else if (nextState === "active") {
        this.recoverFromStorage()
      }
    })

    // Flush timer
    this.flushTimer = setInterval(() => this.flush(), config.flushInterval)

    // Recover any persisted events from previous session
    this.recoverFromStorage()
  }

  enqueue(event) {
    this.queue.push(event)
    if (this.queue.length > this.config.maxQueueSize) {
      this.queue = this.queue.slice(-this.config.maxQueueSize)
    }
    if (this.queue.length >= this.config.maxBatchSize) {
      this.flush()
    }
  }

  async flush() {
    if (this.isFlushing || !this.isOnline || this.queue.length === 0) return

    this.isFlushing = true
    const batch = this.queue.splice(0, this.config.maxBatchSize)

    try {
      await API.post(this.config.endpoint, { events: batch })
    } catch (err) {
      // Put events back at the front of the queue for retry
      this.queue.unshift(...batch)
      console.warn("Analytics flush failed:", err.message)
    } finally {
      this.isFlushing = false
    }

    // If more events remain, flush again
    if (this.queue.length >= this.config.maxBatchSize) {
      this.flush()
    }
  }

  async persistToStorage() {
    if (this.queue.length === 0) return
    try {
      await AsyncStorage.setItem(this.config.storageKey, JSON.stringify(this.queue))
    } catch (err) {
      console.warn("Analytics persist failed:", err.message)
    }
  }

  async recoverFromStorage() {
    try {
      const stored = await AsyncStorage.getItem(this.config.storageKey)
      if (stored) {
        const events = JSON.parse(stored)
        this.queue.unshift(...events)
        await AsyncStorage.removeItem(this.config.storageKey)
      }
    } catch (err) {
      console.warn("Analytics recover failed:", err.message)
    }
  }

  destroy() {
    clearInterval(this.flushTimer)
    this.netInfoUnsubscribe?.()
    this.appStateSubscription?.remove()
    this.persistToStorage()
  }
}
```

---

## Step 2.4: Session Manager

**File to create:** `src/utils/Analytics/session.js`

### Session Lifecycle

- New session on app cold start
- New session after 30 minutes of inactivity
- Session ends on logout or app background exceeding timeout
- Uses `crypto.randomUUID()` (available in Hermes engine, React Native 0.81)

```javascript
import { AppState } from "react-native"
import API from "../API"

export class SessionManager {
  constructor(config) {
    this.config = config
    this.sessionId = null
    this.lastActivityTime = null
    this.backgroundTime = null

    this.appStateSubscription = AppState.addEventListener("change", (nextState) => {
      if (nextState === "background") {
        this.backgroundTime = Date.now()
      } else if (nextState === "active") {
        if (this.backgroundTime) {
          const elapsed = Date.now() - this.backgroundTime
          if (elapsed > this.config.sessionTimeoutMs) {
            this.end()
            this.start()
          }
        }
        this.backgroundTime = null
        this.touch()
      }
    })
  }

  start() {
    this.sessionId = crypto.randomUUID()
    this.lastActivityTime = Date.now()

    // Notify backend (fire-and-forget)
    API.post(this.config.sessionEndpoint, {
      session_id: this.sessionId,
      action: "start",
      started_at: new Date().toISOString(),
    }).catch(() => {})
  }

  end() {
    if (!this.sessionId) return
    const duration_ms = Date.now() - (this.lastActivityTime || Date.now())

    API.post(this.config.sessionEndpoint, {
      session_id: this.sessionId,
      action: "end",
      duration_ms,
    }).catch(() => {})

    this.sessionId = null
  }

  getSessionId() {
    this.touch()
    return this.sessionId
  }

  touch() {
    this.lastActivityTime = Date.now()
  }

  addScreen(screenName) {
    if (!this.sessionId) return
    API.post(this.config.sessionEndpoint, {
      session_id: this.sessionId,
      action: "update",
      screen_name: screenName,
    }).catch(() => {})
  }

  destroy() {
    this.appStateSubscription?.remove()
    this.end()
  }
}
```

---

## Step 2.5: Automatic Screen View Tracking

**File to modify:** `src/navigation/AppNavigatorContainer.js`

Add `onStateChange` listener to the `NavigationContainer`:

```javascript
import Analytics from "../utils/Analytics"

// Helper to extract active route name from navigation state
const getActiveRouteName = (state) => {
  if (!state) return undefined
  const route = state.routes[state.index]
  if (route.state) return getActiveRouteName(route.state)
  return route.name
}

// Inside the component:
const previousRouteRef = useRef(null)

const onNavigationStateChange = (state) => {
  const currentRoute = getActiveRouteName(state)
  if (previousRouteRef.current !== currentRoute && currentRoute) {
    Analytics.screen(currentRoute, {
      previous_screen: previousRouteRef.current,
    })
    previousRouteRef.current = currentRoute
  }
}

// In JSX:
;<NavigationContainer onStateChange={onNavigationStateChange}>
  {/* ... existing navigators */}
</NavigationContainer>
```

---

## Step 2.6: Auth Integration

**File to modify:** `src/store/slices/auth.js`

In `loginUser` thunk (after successful login):

```javascript
import Analytics from "../../utils/Analytics"

// After: dispatch(authenticate({ ... }))
Analytics.identify(resData.user._id, {
  role: resData.user.role,
  companyId: resData.user.co_id,
})
Analytics.track("auth_login_success", { category: "auth" })
```

In `logoutUser` thunk:

```javascript
Analytics.track("auth_logout", { category: "auth" })
Analytics.reset()
```

---

## Step 2.7: Axios Interceptor Enhancement

**File to modify:** `src/utils/API/axiosReqRes.js`

In `requestHandler`:

```javascript
// Generate request correlation ID
const requestId = crypto.randomUUID()
config.headers["X-Request-ID"] = requestId
config._requestId = requestId
config._requestStartTime = Date.now()
```

In `responseHandler` (optional — track slow requests):

```javascript
const duration = Date.now() - (response.config._requestStartTime || 0)
if (duration > 3000) {
  Analytics.track("api_slow_request", {
    category: "system",
    url: response.config.url,
    duration_ms: duration,
    status: response.status,
  })
}
```

---

## Step 2.8: Initialize Analytics at App Entry

**File to modify:** `App.js`

```javascript
import Analytics from "./src/utils/Analytics"

// Initialize before Provider renders
Analytics.init()

// In App component, ensure cleanup:
useEffect(() => {
  return () => Analytics.destroy()
}, [])
```

---

## Step 2.9: Verification Checklist

- [ ] Run app in dev mode, verify `session_start` sent on app open
- [ ] Navigate between 3-4 screens, verify `screen_view` events queued and flushed every 30s
- [ ] Enable airplane mode, perform actions, verify events persist to AsyncStorage
- [ ] Disable airplane mode, verify queued events flush automatically
- [ ] Log in, verify `Analytics.identify` called — subsequent events include `user_id`
- [ ] Log out, verify `session_end` event and identity reset
- [ ] Kill and restart app, verify unflushed events from AsyncStorage are recovered
- [ ] Check batch sizes — confirm max 20 events per POST
- [ ] Background app for 31+ minutes, verify new session created on resume

---

## Files Summary

| Action | File                                                            |
| ------ | --------------------------------------------------------------- |
| CREATE | `src/utils/Analytics/config.js`                                 |
| CREATE | `src/utils/Analytics/index.js`                                  |
| CREATE | `src/utils/Analytics/queue.js`                                  |
| CREATE | `src/utils/Analytics/session.js`                                |
| MODIFY | `src/navigation/AppNavigatorContainer.js` — add screen tracking |
| MODIFY | `src/store/slices/auth.js` — add identify/reset calls           |
| MODIFY | `src/utils/API/axiosReqRes.js` — add correlation ID             |
| MODIFY | `App.js` — initialize Analytics                                 |

## No New Dependencies Required

- Uses existing: `AsyncStorage`, `NetInfo`, `DeviceInfo`, Axios instance
- `crypto.randomUUID()` is native to Hermes engine (React Native 0.81+)
