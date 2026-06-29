# Phase 5: App Performance

**Priority:** P1 (5B, 5E) + P2 (5A, 5C-5G) | **Timeline:** Week 3-4 + Week 9-10

---

## Research: React Native Performance Best Practices

### Key Principles

1. **Minimize bridge crossings** (old architecture) / **reduce JS thread work** (new architecture)
2. **FlatList virtualization** -- only render visible items
3. **Memoize** -- prevent unnecessary re-renders
4. **Reduce state updates** -- batch and minimize Redux dispatches
5. **Lazy load** -- defer non-critical screens and data
6. **Offline-first** -- queue writes, serve reads from cache

### RTK Query Performance Patterns

1. **`keepUnusedDataFor`** -- retain cached data during navigation
2. **`pollingInterval`** -- auto-refresh for real-time screens
3. **`selectFromResult`** -- derive data without re-renders
4. **Tag-based invalidation** -- surgical cache updates
5. **`baseQueryWithRetry`** -- resilient to flaky networks
6. **Prefetching** -- preload next-screen data

---

## Sub-Phase 5A: Migrate All HTTP Calls to RTK Query

### Problem

Two HTTP clients are in use:

1. **RTK Query** (`src/store/apis/createApi.js`) -- used for most CRUD operations
2. **Axios** (`src/utils/API/index.js` + `axiosReqRes.js`) -- used for logout, some legacy calls

This causes:

- Duplicate header-setting logic (Axios: `axiosReqRes.js:40-50` vs RTK: `createApi.js:24-37`)
- Inconsistent error handling (Axios has retry at `retryLogic.js`; RTK Query has none)
- Duplicate device info collection (Axios reads `DeviceInfo` per request; RTK caches once)

### Proposed Solution

1. **Move logout to RTK Query:**

```js
// In src/store/apis/dzzlooms/auth.js
auth_logout: builder.mutation({
  query: () => ({ url: 'auth/logout', method: 'GET' }),
  async onQueryStarted(arg, { dispatch }) {
    await secureStore.clearTokens();
    await AsyncStorage.removeItem('currentUser');
    dispatch(authSlice.actions.logout());
  },
}),
```

2. **Move error reporting to RTK Query:**

```js
report_error: builder.mutation({
  query: (errorData) => ({ url: 'errors', method: 'POST', body: errorData }),
}),
```

3. **Delete Axios files:**

- `src/utils/API/index.js`
- `src/utils/API/axiosReqRes.js`
- `src/utils/API/retryLogic.js`

4. **Remove Axios dependency:** `yarn remove axios`

---

## Sub-Phase 5B: Add Retry/Exponential Backoff to RTK Query (P1)

### Problem

**File:** `src/store/apis/createApi.js` -- no retry logic. Network blips cause immediate failure.

Meanwhile, `src/utils/API/retryLogic.js` has retry only for Axios.

### Proposed Solution

RTK Query has built-in retry support:

```js
import { createApi, fetchBaseQuery, retry } from '@reduxjs/toolkit/query/react';

const rawBaseQuery = fetchBaseQuery({
  baseUrl: API_URL_V,
  prepareHeaders: async (headers) => {
    // ... existing header logic ...
  },
  timeout: 10000,
});

// Wrap with retry (3 attempts with exponential backoff)
const baseQueryWithRetry = retry(rawBaseQuery, {
  maxRetries: 3,
  backoff: async (attempt) => {
    // Exponential backoff: 1s, 2s, 4s
    await new Promise(resolve => setTimeout(resolve, Math.min(1000 * Math.pow(2, attempt), 8000)));
  },
});

// Custom wrapper to skip retry on 4xx (client errors)
const baseQueryWithSmartRetry = async (args, api, extraOptions) => {
  const result = await baseQueryWithRetry(args, api, extraOptions);

  // Don't retry client errors
  if (result.error && result.error.status >= 400 && result.error.status < 500) {
    retry.fail(result.error); // Stop retrying
  }

  return result;
};

export const api = createApi({
  reducerPath: 'dzzlo-oms-api',
  baseQuery: baseQueryWithSmartRetry, // was: rawBaseQuery
  keepUnusedDataFor: 300,
  tagTypes: [...],
  endpoints: () => ({}),
});
```

**Impact:** Network errors auto-retry up to 3 times. 4xx errors fail immediately.

---

## Sub-Phase 5C: Implement Offline Mutation Queue

### Problem

`@react-native-community/netinfo` is installed but unused. When a user creates an order offline, the request fails silently.

### Proposed Solution

**New file:** `src/utils/offlineQueue.js`

```js
import NetInfo from "@react-native-community/netinfo";
import AsyncStorage from "@react-native-async-storage/async-storage";

const QUEUE_KEY = "offline_mutation_queue";

class OfflineQueue {
  constructor() {
    this.isOnline = true;
    this.processing = false;

    // Monitor connectivity
    NetInfo.addEventListener((state) => {
      const wasOffline = !this.isOnline;
      this.isOnline = state.isConnected && state.isInternetReachable;

      if (wasOffline && this.isOnline) {
        this.processQueue();
      }
    });
  }

  async enqueue(mutation) {
    const queue = await this.getQueue();
    queue.push({
      ...mutation,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
    });
    await AsyncStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
  }

  async getQueue() {
    const raw = await AsyncStorage.getItem(QUEUE_KEY);
    return raw ? JSON.parse(raw) : [];
  }

  async processQueue() {
    if (this.processing) return;
    this.processing = true;

    try {
      const queue = await this.getQueue();
      const remaining = [];

      for (const item of queue) {
        try {
          await store
            .dispatch(api.endpoints[item.endpoint].initiate(item.args))
            .unwrap();
        } catch (err) {
          if (err.status >= 400 && err.status < 500) {
            // Client error -- don't retry
            console.warn("Offline queue: dropping failed mutation", item);
          } else {
            remaining.push(item); // Retry later
          }
        }
      }

      await AsyncStorage.setItem(QUEUE_KEY, JSON.stringify(remaining));
    } finally {
      this.processing = false;
    }
  }
}

export const offlineQueue = new OfflineQueue();
```

**Usage in mutation hooks:**

```js
const handleCreateOrder = async (orderData) => {
  if (!isOnline) {
    await offlineQueue.enqueue({
      endpoint: "add_order_msts",
      args: orderData,
    });
    showToast("Order queued. Will submit when online.");
    return;
  }

  await addOrder(orderData).unwrap();
};
```

---

## Sub-Phase 5D: FlatList Virtualization Optimization

### Problem

List screens with 50+ items have no virtualization optimization. Every item mounts immediately, causing:

- High memory usage
- Slow initial render
- Janky scrolling

### Proposed Solution

**Apply to all FlatList components across all screens:**

```jsx
<FlatList
  data={items}
  renderItem={renderItem}
  keyExtractor={(item) => item._id}
  // Virtualization props
  removeClippedSubviews={true} // Unmount off-screen items (Android)
  maxToRenderPerBatch={10} // Render 10 items per frame
  updateCellsBatchingPeriod={50} // Batch updates every 50ms
  windowSize={5} // Render 5 screens worth of items
  initialNumToRender={10} // First render: 10 items
  // Performance
  getItemLayout={(data, index) => ({
    length: ITEM_HEIGHT, // Known height per item
    offset: ITEM_HEIGHT * index,
    index,
  })}
/>
```

**Key screens to update:**

| Screen               | File                                                 | List Type            |
| -------------------- | ---------------------------------------------------- | -------------------- |
| Customer Orders      | `screens/Common/Orders/index.js`                     | Paginated orders     |
| Dealer Customers     | `screens/Dealer/Customers/index.js`                  | Customer relations   |
| Dealer Payments      | `screens/Dealer/Payments/index.js`                   | Voucher/invoice list |
| SuperAdmin Dealers   | `screens/SuperAdmin/Dealers/AllDealers/index.js`     | Paginated dealers    |
| SuperAdmin Customers | `screens/SuperAdmin/Customers/AllCustomers/index.js` | Customer list        |

**Create a shared wrapper:**

```js
// src/components/OptimizedFlatList.js
import React from "react";
import { FlatList } from "react-native";

const DEFAULTS = {
  removeClippedSubviews: true,
  maxToRenderPerBatch: 10,
  updateCellsBatchingPeriod: 50,
  windowSize: 5,
  initialNumToRender: 10,
};

export const OptimizedFlatList = React.forwardRef((props, ref) => (
  <FlatList ref={ref} {...DEFAULTS} {...props} />
));
```

---

## Sub-Phase 5E: Memoize Selectors & Render Functions (P1)

### Problem 1: Broad Selectors

Multiple screens select the entire `auth` slice:

```js
const { user, company } = useSelector((state) => state.auth);
```

Any auth state change (e.g., `notification` flag) re-renders every screen using this selector.

### Solution: Fine-Grained Selectors

```js
// src/store/selectors/auth.js
export const selectUserId = (state) => state.auth.user?._id;
export const selectUserRole = (state) => state.auth.user?.role;
export const selectCompanyId = (state) => state.auth.user?.co_id;
export const selectCompany = (state) => state.auth.company;

// Usage in screens
const companyId = useSelector(selectCompanyId);
const role = useSelector(selectUserRole);
```

For derived state, use `reselect`:

```js
import { createSelector } from "@reduxjs/toolkit";

export const selectCompanyScope = createSelector(
  [selectUserRole, selectCompany],
  (role, company) => company?.companies?.find((c) => c.role === role)?.scope,
);
```

### Problem 2: Un-memoized Render Functions

```js
// BAD -- new function every render
const renderItem = ({ item }) => <OrderItem item={item} />;

// GOOD -- memoized
const renderItem = useCallback(({ item }) => <OrderItem item={item} />, []);
```

### Problem 3: Un-memoized List Items

```js
// BAD -- re-renders on every parent state change
const OrderItem = ({ item }) => <View>...</View>;

// GOOD -- only re-renders if props change
const OrderItem = React.memo(({ item }) => <View>...</View>);
```

### Screens to Update

Apply `React.memo()` to all list item components and `useCallback` to all `renderItem` functions.

---

## Sub-Phase 5F: Persist Pagination State

### Problem

RTK Query paginated data merges correctly via `paginationHelpers.js`, but the cache is lost when `keepUnusedDataFor` expires or on app restart.

### Solution

1. **Increase `keepUnusedDataFor`** on paginated endpoints:

```js
fetch_order_so_POST: builder.query({
  ...createPaginatedQueryConfig('data', 'pagination', { nestedPageIn: 'filterProps' }),
  keepUnusedDataFor: 600, // 10 minutes
  query: (body) => ({ url: 'order_msts/a/poso', method: 'POST', body }),
}),
```

2. **Save/restore scroll position:**

```js
const scrollOffsetRef = useRef(0);
const listRef = useRef(null);

// Save scroll position on unmount
useEffect(() => {
  return () => {
    // Position is already saved in ref
  };
}, []);

// Restore on mount
useEffect(() => {
  if (scrollOffsetRef.current > 0 && listRef.current) {
    listRef.current.scrollToOffset({
      offset: scrollOffsetRef.current,
      animated: false,
    });
  }
}, [data]); // Restore when data loads from cache

<FlatList
  ref={listRef}
  onScroll={(e) => {
    scrollOffsetRef.current = e.nativeEvent.contentOffset.y;
  }}
  scrollEventThrottle={16}
/>;
```

---

## Sub-Phase 5G: Skeleton Loading & Prefetching

### Skeleton Screens

Replace `<ActivityIndicator>` with content-shaped placeholders:

```js
// src/components/SkeletonList.js
import { MotiView } from "moti";

const SkeletonItem = () => (
  <MotiView
    from={{ opacity: 0.3 }}
    animate={{ opacity: 1 }}
    transition={{ type: "timing", duration: 800, loop: true }}
    style={{
      height: 80,
      backgroundColor: "#E0E0E0",
      marginVertical: 4,
      borderRadius: 8,
    }}
  />
);

export const SkeletonList = ({ count = 6 }) => (
  <View>
    {Array.from({ length: count }, (_, i) => (
      <SkeletonItem key={i} />
    ))}
  </View>
);
```

**Usage:**

```js
if (isLoading) return <SkeletonList count={8} />;
```

### Prefetching Next Screens

```js
// In order list screen, prefetch first order detail
import { api } from "../../store/apis/createApi";

useEffect(() => {
  if (data?.data?.[0]) {
    dispatch(
      api.util.prefetch(
        "fetch_one_order_by_so",
        { id: data.data[0]._id },
        { force: false },
      ),
    );
  }
}, [data]);

// In dealer list, prefetch first dealer's customers
useEffect(() => {
  if (dealers?.[0]) {
    dispatch(
      api.util.prefetch(
        "fetch_dealer_customers",
        { dealer_id: dealers[0]._id },
        { force: false },
      ),
    );
  }
}, [dealers]);
```

**Impact:** When user taps on an item, data is already cached -> instant screen transition.

---

## Verification

1. **Flipper profiler:** Measure render times before/after memoization
2. **React Native Performance Monitor:** Check JS thread frame rate (target: 60fps)
3. **Bundle size:** Compare before/after Axios removal (`npx react-native-bundle-visualizer`)
4. **Network waterfall:** Use Flipper Network plugin to verify single API call per screen
5. **Offline test:** Enable airplane mode, create order, re-enable -> verify auto-sync
6. **Memory:** Monitor `adb shell dumpsys meminfo <package>` for Android memory usage
