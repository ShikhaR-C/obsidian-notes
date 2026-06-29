# App Performance

> React Native and RTK Query optimizations.
> Each task is independent. Test the specific screen after each change.

---

## APP-1: Add `useCallback` to all `renderItem` functions (App)

**Size:** XS per screen (2 min each, many screens)
**Files:** All screens with `FlatList`

**What:** Wrap `renderItem` functions in `useCallback`:

```js
// BEFORE — new function every render
const renderItem = ({ item }) => <OrderItem item={item} />;

// AFTER — memoized
const renderItem = useCallback(({ item }) => <OrderItem item={item} />, []);
```

**Why:** Without `useCallback`, every parent re-render creates a new function reference, which tells FlatList every item has "changed" and needs re-rendering. With `useCallback`, the function reference is stable — FlatList only re-renders items whose data actually changed.

**How to verify:**

- App: Open a list screen. Scroll up and down. Should feel the same or smoother. No visual change.
- API: No change needed.

**Discussion:** Start with the 5 highest-traffic screens: Orders, Customers, Payments, Dealers, Vouchers. Then expand to all screens with FlatList.

---

## APP-2: Add `React.memo()` to list item components (App)

**Size:** XS per component (1 line each)
**Files:** All list item components (e.g., `OrderItem`, `CustomerItem`, etc.)

**What:**

```js
// BEFORE
const OrderItem = ({ item }) => <View>...</View>;

// AFTER
const OrderItem = React.memo(({ item }) => <View>...</View>);
```

**Why:** Without `React.memo`, every item in a FlatList re-renders when the parent state changes (e.g., new data loads, filter changes). With `React.memo`, items only re-render when their props change. Combined with APP-1, this prevents cascade re-renders.

**How to verify:**

- App: Same screens. No visual change. Enable React DevTools profiler to verify fewer re-renders.

---

## APP-3: Add FlatList virtualization props (App)

**Size:** S (create shared component or add props to each FlatList)
**Files:** Screens with long lists (Orders, Customers, Payments, Dealers)

**What:** Add performance props to all FlatList components:

```jsx
<FlatList
  removeClippedSubviews={true} // Unmount off-screen items (Android)
  maxToRenderPerBatch={10} // Render 10 items per frame
  updateCellsBatchingPeriod={50} // Batch updates every 50ms
  windowSize={5} // Render 5 screens worth of items
  initialNumToRender={10} // First render: 10 items
/>
```

**Optionally create a shared wrapper:**

```js
// src/components/OptimizedFlatList.js
const DEFAULTS = { removeClippedSubviews: true, maxToRenderPerBatch: 10, ... };
export const OptimizedFlatList = React.forwardRef((props, ref) => (
  <FlatList ref={ref} {...DEFAULTS} {...props} />
));
```

**Why:** Default FlatList renders all items immediately, causing high memory usage and slow initial render for long lists (50+ items). Virtualization ensures only visible items are rendered.

**How to verify:**

- App: Open a list with 50+ items. Initial load should be faster. Scrolling should be smooth.
- Use `adb shell dumpsys meminfo <package>` on Android to check memory before/after.

---

## APP-4: Create fine-grained auth selectors (App)

**Size:** S (new file + update screens gradually)
**Files:** New `src/store/selectors/auth.js`, then update screens

**What:** Replace broad `useSelector(state => state.auth)` with specific selectors:

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

**Why:** When you select the entire `auth` object, ANY change to auth state (even unrelated fields like notification flags) re-renders the component. Fine-grained selectors mean the component only re-renders when the specific field it uses changes.

**How to verify:**

- App: All screens should work identically. No visual change. Fewer unnecessary re-renders.

**Discussion:** Do this incrementally — update one screen at a time. Start with the most frequently rendered screens (order list, dashboard).

---

## APP-5: Add RTK Query retry with exponential backoff (App)

**Size:** S (20 min)
**File:** `src/store/apis/createApi.js`

**What:** Wrap the base query with RTK Query's built-in `retry()`:

```js
import { retry } from '@reduxjs/toolkit/query/react';

const rawBaseQuery = fetchBaseQuery({...});

const baseQueryWithRetry = retry(rawBaseQuery, {
  maxRetries: 3,
  backoff: async (attempt) => {
    await new Promise(resolve => setTimeout(resolve, Math.min(1000 * 2 ** attempt, 8000)));
  },
});
```

Skip retry on 4xx errors (client errors):

```js
const baseQueryWithSmartRetry = async (args, api, extraOptions) => {
  const result = await baseQueryWithRetry(args, api, extraOptions);
  if (result.error?.status >= 400 && result.error?.status < 500)
    retry.fail(result.error);
  return result;
};
```

**Why:** Currently, any network blip causes an immediate failure with no retry. Mobile networks are unreliable. Exponential backoff (1s, 2s, 4s) gives transient errors time to resolve without overwhelming the server.

**How to verify:**

- App: Temporarily break the API URL. The app should retry 3 times before showing an error. With a working API, no behavior change.
- API: Check logs — retried requests will show up as normal requests.

**Discussion:** The "skip 4xx" logic is important — you don't want to retry bad requests (invalid data, unauthorized). Only retry network errors and 5xx server errors.

- **Does the app keep retrying if network never comes back?** No. `maxRetries: 3` caps it — the app tries the original request + 3 retries (1s, 2s, 4s backoff, ~7s total), then gives up and surfaces the error to the UI. It does NOT poll indefinitely. If you want auto-refetch on reconnect, that's a separate concern (e.g. `NetInfo` + `refetch()`).

- **`baseQueryWithRetry` vs `baseQueryWithSmartRetry`:** These are two layers. `baseQueryWithRetry` wraps `rawBaseQuery` with the retry engine (retry up to 3x with backoff on any error). `baseQueryWithSmartRetry` wraps that and adds intelligence — it calls `retry.fail()` on 4xx errors to stop retrying immediately (retrying a 401 or 400 is pointless). `baseQueryWithSmartRetry` is the one passed to `createApi`, so all endpoints get smart retry automatically.

---

## APP-6: Unify GET/POST cache tags for order endpoints (App)

**Size:** S (15 min)
**Files:** `src/store/apis/dzzlooms/order_msts.js` (or equivalent)

**What:** Both `fetch_order_msts_so` (GET) and `fetch_order_so_POST` (POST) should provide the same tag type. Currently they may have different tags, causing cache fragmentation.

```js
// Both should use:
providesTags: (result) => [
  ...(result?.data?.map(({ _id }) => ({ type: 'orders', id: _id })) || []),
  { type: 'orders', id: 'LIST' },
],
```

And mutations should invalidate the same tags:

```js
invalidatesTags: [{ type: 'orders', id: 'LIST' }],
```

**Why:** When the app creates an order (mutation), it needs to invalidate the order list cache. If GET and POST variants have different tags, the invalidation might miss one variant, showing stale data.

**How to verify:**

- App: Create an order. Go back to the order list. The new order should appear immediately (no manual refresh needed).

---

## APP-7: Remove Axios — consolidate to RTK Query only (App)

**Size:** M (2-3 hours)
**Files:** `src/utils/API/index.js`, `src/utils/API/axiosReqRes.js`, `src/utils/API/retryLogic.js`, and all call sites

**What:**

1. Move logout call to an RTK Query mutation
2. Move error reporting to an RTK Query mutation
3. Find and migrate any remaining Axios calls
4. Delete the Axios utility files
5. `yarn remove axios`

**Why:** Two HTTP clients means:

- Duplicate header-setting logic
- Inconsistent error handling (Axios has retry, RTK Query doesn't — until APP-5)
- Duplicate device info collection
- Larger bundle size

After APP-5 adds retry to RTK Query, there's no reason to keep Axios.

**How to verify:**

- App: Test logout, error reporting, and any other flows that used Axios. All should work via RTK Query.
- Bundle: Run `npx react-native-bundle-visualizer` — Axios should be gone.

**Discussion:** This is the largest app task. Do it after APP-5 (retry) so RTK Query has feature parity with Axios. Map all Axios call sites first before starting the migration.

### Plan

#### Context

Two HTTP clients currently coexist:

- **Axios** instance in `dzzlo_oms_app/src/utils/API/index.js` with `requestHandler`, `responseHandler`, `errorHandler` interceptors (`axiosReqRes.js`) and manual exponential backoff (`retryLogic.js`).
- **RTK Query** `fetchBaseQuery` in `dzzlo_oms_app/src/store/apis/createApi.js` which already replicates the request handler (`prepareHeaders`) and retry (`retry` wrapper with smart 4xx short-circuit).

The Axios instance is now only used in 4 places (auth slice logout, StartupScreen logout, `GetLastInvDate`, and a stray `axios.put` inside `dzzlooms/auth.js::updateCurr_User_Comp`). Removing Axios eliminates duplicate header/device-info logic, unifies error handling, and shrinks the bundle — it is the last step in the app-perf series (APP-1…APP-6 already shipped).

#### Where do `requestHandler`, `responseHandler`, `errorHandler` live in RTK Query?

RTK Query has no interceptors. Each Axios concept maps to a specific hook on `fetchBaseQuery` or a middleware layer:

| Axios interceptor                         | RTK Query equivalent                                                                          | Location                                                         |
| ----------------------------------------- | --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `requestHandler(config)`                  | `fetchBaseQuery({ prepareHeaders })`                                                          | `createApi.js:22-35` (already done)                              |
| `responseHandler(response)`               | `fetchBaseQuery({ responseHandler })` for global parsing, or per-endpoint `transformResponse` | `createApi.js` — wire in as a stub now, to be extended in future |
| `errorHandler(error)` — 401 logout        | Redux middleware using `isRejectedWithValue` from `@reduxjs/toolkit`                          | New file, registered in `store/apis/index.js`                    |
| `errorHandler(error)` — retry 5xx/network | `retry()` wrapper from `@reduxjs/toolkit/query/react`                                         | `createApi.js:39-53` (already done via `baseQueryWithRetry`)     |
| `errorHandler(error)` — per-endpoint      | `transformErrorResponse` on each `builder.query/mutation`                                     | Per endpoint in `store/apis/dzzlooms/*`                          |

#### Alternative to `axios.create({ baseURL, timeout: 10000 })`

```js
fetchBaseQuery({
  baseUrl: API_URL_V, // replaces baseURL
  timeout: 10000, // same option name
  prepareHeaders, // replaces request interceptor
  responseHandler, // optional: replaces response interceptor
});
```

This already exists at `dzzlo_oms_app/src/store/apis/createApi.js:20-37`. Nothing new is needed — the task is to _delete_ the Axios version and migrate its remaining call sites to `api.injectEndpoints(...)`.

#### Migration Steps

**1. Add 401-logout middleware (replaces `errorHandler` 401 branch)**

Create `dzzlo_oms_app/src/store/middleware/rtkQueryErrorLogger.js`:

```js
import { isRejectedWithValue } from "@reduxjs/toolkit";
import { logoutUser } from "../slices/auth";

let _isLoggingOut = false;

export const rtkQueryErrorLogger = (storeApi) => (next) => (action) => {
  if (
    isRejectedWithValue(action) &&
    action.payload?.status === 401 &&
    !_isLoggingOut
  ) {
    _isLoggingOut = true;
    storeApi.dispatch(logoutUser());
    _isLoggingOut = false;
  }
  return next(action);
};
```

Register it in `dzzlo_oms_app/src/store/apis/index.js`:

```js
middleware: gDM =>
  gDM({ serializableCheck: false })
    .concat(api.middleware)
    .concat(rtkQueryErrorLogger),
```

**1b. Wire a `responseHandler` stub into `fetchBaseQuery`**

Keep `responseHandler` as a seam for future global response handling (e.g. Firebase Performance hooks that were commented out in the old `axiosReqRes.js:52-63`, unified response-shape normalization, etc.). Extend `dzzlo_oms_app/src/store/apis/createApi.js`:

```js
const rawBaseQuery = fetchBaseQuery({
  baseUrl: API_URL_V,
  prepareHeaders: async (headers) => {
    /* unchanged */
  },
  timeout: 10000,
  responseHandler: async (response) => {
    // Future: attach perf metrics, global response transforms, etc.
    // Default behavior — parse JSON / text like fetchBaseQuery does out of the box.
    const contentType = response.headers.get("content-type") || "";
    return contentType.includes("application/json")
      ? response.json()
      : response.text();
  },
});
```

Leave the handler body as the default JSON/text parse for now. Future work plugs perf metrics, auth-refresh, etc. into this single seam instead of scattering them across endpoints.

**2. Add logout + `invs/rel/latest_date` endpoints**

Edit `dzzlo_oms_app/src/store/apis/dzzlooms/auth.js` — add to `injectEndpoints`:

```js
auth_logout: builder.mutation({
  query: () => ({ url: 'auth/logout', method: 'GET' }),
}),
```

Extend `dzzlo_oms_app/src/store/apis/dzzlooms/invs.js` with:

```js
getLatestInvDate: builder.query({
  query: params => ({ url: 'invs/rel/latest_date', params }),
  transformResponse: res => res.data,
}),
```

Also migrate the `axios.put` inside `updateCurr_User_Comp` (`dzzlooms/auth.js:25-29`) to `fetchWithBQ` (the second arg to `queryFn`) so it flows through `fetchBaseQuery` and picks up shared headers.

**3. Update call sites**

- `dzzlo_oms_app/src/store/slices/auth.js:10` — replace `API.get('/auth/logout')` with `await dispatch(api.endpoints.auth_logout.initiate()).unwrap()` inside the `logoutUser` thunk, wrapped in try/catch so AsyncStorage cleanup still runs if the server call fails. Remove `import API from '../../utils/API'`.
- `dzzlo_oms_app/src/screens/StartupScreen.js:47` — same replacement (await the mutation before `setDidTryAL()`); drop the `API` import.
- `dzzlo_oms_app/src/screens/Dealer/NewInvoice/BSheets/GetLastInvDate.js` — replace the manual `useState/useEffect` dance with `useGetLatestInvDateQuery({ dealer_id }, { skip: !dealer_id || !refetch })`. Derive `{ status, custInvData }` from the query result.

**4. Delete Axios utility files**

- Delete `dzzlo_oms_app/src/utils/API/axiosReqRes.js`
- Delete `dzzlo_oms_app/src/utils/API/retryLogic.js`
- Rewrite `dzzlo_oms_app/src/utils/API/index.js` to export only the URL constants (no axios instance):

```js
import {
  PROJ_ENV as ENV,
  API_URL as BASE_URL,
  API_VERSION_PATH,
  API_VERSION_PATH_V1,
} from "@env";

export const PROJ_ENV = ENV;
export const API_URL = BASE_URL;
export const API_URL_V = `${BASE_URL}${API_VERSION_PATH}`;
export const API_URL_V1 = `${BASE_URL}${API_VERSION_PATH_V1}`;
```

The 10 other files importing `API_URL` / `API_URL_V` / `PROJ_ENV` keep working unchanged.

**5. Remove the dependency**

```sh
yarn remove axios
```

Grep the repo for `from 'axios'` / `require('axios')` afterwards — should be zero hits in `src/`. Delete `src/notes/Testing/apiTesting.js` scratch file as part of cleanup.

#### Critical files

- `dzzlo_oms_app/src/utils/API/index.js` — rewrite (constants only)
- `dzzlo_oms_app/src/utils/API/axiosReqRes.js` — delete
- `dzzlo_oms_app/src/utils/API/retryLogic.js` — delete
- `dzzlo_oms_app/src/store/apis/index.js` — add error-logger middleware
- `dzzlo_oms_app/src/store/apis/createApi.js` — already has the fetchBaseQuery setup (no change)
- `dzzlo_oms_app/src/store/apis/dzzlooms/auth.js` — add `auth_logout` mutation, migrate `updateCurr_User_Comp` off `axios.put`
- `dzzlo_oms_app/src/store/apis/dzzlooms/invs.js` — add `getLatestInvDate` query
- `dzzlo_oms_app/src/store/slices/auth.js` — remove Axios import, dispatch RTK mutation
- `dzzlo_oms_app/src/screens/StartupScreen.js` — same
- `dzzlo_oms_app/src/screens/Dealer/NewInvoice/BSheets/GetLastInvDate.js` — convert to `useGetLatestInvDateQuery`
- New: `dzzlo_oms_app/src/store/middleware/rtkQueryErrorLogger.js`

#### Verification

1. `yarn lint` — no unused imports of `API`, `axios`, `axiosReqRes`, `retryLogic`.
2. Grep `from 'axios'` in `dzzlo_oms_app/src` → empty.
3. Launch the app: login → navigate → logout. Confirm `GET /auth/logout` fires and `userData`/`currentUser` are cleared from AsyncStorage.
4. Force a 401 (invalidate the stored token): any RTK Query call should trigger auto-logout via the new middleware.
5. Airplane-mode a request — RTK Query `retry()` should produce the same 3-attempt backoff as the old `retryLogic.js` (`createApi.js:39-46`).
6. `NewInvoice` screen: open the last-invoice-date bottom sheet per-customer → data loads, pull-to-refresh works.
7. `npx react-native-bundle-visualizer` — confirm `axios` is absent from the bundle.

---

## APP-8: Migrate heavy FlatLists to FlashList (App)

**Size:** M (3-4 hours across 3 phases)
**Dependency:** Do after APP-3 (virtualization props). FlashList replaces FlatList's create/destroy model with cell recycling — a fundamentally different architecture that eliminates blank-cell flicker and cuts memory ~60-70%.

---

### Setup: Install @shopify/flash-list. DONE. CHECK.

```bash
yarn add @shopify/flash-list
cd ios && pod install
```

Rebuild both platforms after install. FlashList requires native modules.

---

### Phase 1 — Critical screens (Orders + Invoices) — ~1.5 hr

These are the highest-traffic, most complex lists. Users scroll these daily.

| #   | Screen            | File                                                      | estimatedItemSize | Notes                                                                           |
| --- | ----------------- | --------------------------------------------------------- | ----------------- | ------------------------------------------------------------------------------- |
| 1   | Dealer Orders     | `src/screens/Dealer/Orders/components/OneOrder.js`        | 200               | Collapsible items: 180px collapsed, 400px expanded. Use 200 as weighted average |
| 2   | Customer Orders   | `src/screens/Customer/Orders/components/OneOrder.js`      | 200               | Same pattern as Dealer Orders                                                   |
| 3   | Common Orders     | `src/screens/Common/Orders/components/ListComponents.js`  | 200               | Read-only view, same order card                                                 |
| 4   | Dealer Invoices   | `src/screens/Dealer/Invoices/components/index.js`         | 130               | Invoice card with footer calculations                                           |
| 5   | Customer Invoices | `src/screens/Customer/Invoices/components/InvoiceList.js` | 120               | Invoice card with selection state                                               |
| 6   | Common Invoices   | `src/screens/Common/Invoices/components/InvoiceList.js`   | 130               | Read-only invoice list with pagination                                          |

**Steps per file:**

1. Change import:

   ```js
   // BEFORE
   import { FlatList } from "react-native";

   // AFTER
   import { FlashList } from "@shopify/flash-list";
   ```

2. Replace `<FlatList` with `<FlashList` and add `estimatedItemSize`:

   ```jsx
   <FlashList
     data={data}
     renderItem={renderItem}
     keyExtractor={(item) => item._id}
     estimatedItemSize={200}
     // Keep existing props: onRefresh, ListHeaderComponent, ListFooterComponent, etc.
     // REMOVE these FlatList-specific props (FlashList handles them internally):
     //   removeClippedSubviews, maxToRenderPerBatch,
     //   updateCellsBatchingPeriod, windowSize, initialNumToRender
   />
   ```

3. **Keep all business logic unchanged** — renderItem, keyExtractor, onRefresh, onEndReached, ListHeaderComponent, ListFooterComponent, onScroll handlers all stay the same.

4. If the list uses `getItemLayout`, replace with `overrideItemLayout`:

   ```js
   // BEFORE (FlatList)
   getItemLayout={(data, index) => ({ length: 200, offset: 200 * index, index })}

   // AFTER (FlashList)
   overrideItemLayout={(layout) => { layout.size = 200; }}
   ```

5. If the list uses `ref` with `scrollToIndex` / `scrollToOffset`, these work the same on FlashList — no change needed.

**How to verify Phase 1:**

- Open each order/invoice list. Scroll fast up and down — should see zero or near-zero blank cells.
- Create an order, go back to list — new order appears (cache invalidation still works).
- Pull to refresh works. Pagination/onEndReached loads more items.
- Collapse/expand on order cards works exactly as before.

---

### Phase 2 — High-traffic entity lists (Customers, Dealers, Payments) — ~1 hr

| #   | Screen            | File                                                      | estimatedItemSize | Notes                        |
| --- | ----------------- | --------------------------------------------------------- | ----------------- | ---------------------------- |
| 7   | Dealer Customers  | `src/screens/Dealer/Customers/index.js`                   | 110               | Card with image + actions    |
| 8   | Customer Dealers  | `src/screens/Customer/Dealers/index.js`                   | 120               | Filtered/sorted dealer cards |
| 9   | Dealer Payments   | `src/screens/Dealer/Payments/components/index.js`         | 160               | Payment card + DividerFading |
| 10  | Customer Payments | `src/screens/Customer/Payments/components/PaymentList.js` | 150               | Payment card with selection  |
| 11  | Common Payments   | `src/screens/Common/Payments/components/PaymentList.js`   | 150               | Read-only payment view       |

**Same migration steps as Phase 1.** Additional notes:

- DividerFading between items: keep as part of renderItem, FlashList recycles the whole cell including dividers.
- Image-heavy lists (Customers/Dealers with profile pictures): FlashList recycling means the image component may flash briefly during fast scroll. If this happens, add `recyclingKey={item._id}` to prevent cell reuse across different items.

**How to verify Phase 2:**

- Search/filter works on Customers and Dealers lists.
- Payment selection and multi-select works.
- Long-press actions (if any) still trigger correctly.
- Images load correctly during normal and fast scrolling.

---

### Phase 3 — Secondary lists (Vehicles, Products) — ~45 min

| #   | Screen            | File                                                       | estimatedItemSize | Notes                                                   |
| --- | ----------------- | ---------------------------------------------------------- | ----------------- | ------------------------------------------------------- |
| 12  | Common Vehicles   | `src/screens/Common/Vehicles/components/index.js`          | 150               | Vertical vehicle list (skip the horizontal driver list) |
| 13  | Customer Vehicles | `src/screens/Customer/Vehicles/vehicleComponents/index.js` | 150               | Mirrors Common Vehicles card                            |
| 14  | Dealer Products   | `src/screens/Dealer/Products/components.js`                | 150               | Product cards with SVG icons                            |
| 15  | Common Products   | `src/screens/Common/Products/components/index.js`          | 150               | Read-only counterpart to Dealer Products                |

**Additional notes for Phase 3:**

- **Horizontal driver lists** (`Common/Vehicles` DriverList and `Customer/Vehicles/driverComponents/index.js`): deferred. FlashList horizontal requires a fixed-height wrapper and recycling gains only matter past ~20 items, which isn't typical here. Keep as FlatList for now; revisit if a specific customer reports lag.
- Customer/Common counterparts share the same card components as their Dealer versions — reuse the same `estimatedItemSize` and migration steps.

**How to verify Phase 3:**

- Vehicle/driver assignment flows unchanged (both Customer and Common screens).
- Product rate editing still works from the Dealer list; Common Products read-only view renders correctly.

---

### Props migration reference

| FlatList prop                            | FlashList equivalent                     | Action                                                                   |
| ---------------------------------------- | ---------------------------------------- | ------------------------------------------------------------------------ |
| `data`                                   | `data`                                   | Keep                                                                     |
| `renderItem`                             | `renderItem`                             | Keep                                                                     |
| `keyExtractor`                           | `keyExtractor`                           | Keep                                                                     |
| `ListHeaderComponent`                    | `ListHeaderComponent`                    | Keep                                                                     |
| `ListFooterComponent`                    | `ListFooterComponent`                    | Keep                                                                     |
| `ListEmptyComponent`                     | `ListEmptyComponent`                     | Keep                                                                     |
| `onRefresh` / `refreshing`               | `onRefresh` / `refreshing`               | Keep                                                                     |
| `onEndReached` / `onEndReachedThreshold` | `onEndReached` / `onEndReachedThreshold` | Keep                                                                     |
| `onScroll`                               | `onScroll`                               | Keep                                                                     |
| `horizontal`                             | `horizontal`                             | Keep                                                                     |
| `numColumns`                             | `numColumns`                             | Keep                                                                     |
| `contentContainerStyle`                  | `contentContainerStyle`                  | Keep (but FlashList ignores `flex: 1` — wrap in a parent View if needed) |
| `removeClippedSubviews`                  | —                                        | **Remove** (handled internally)                                          |
| `maxToRenderPerBatch`                    | —                                        | **Remove** (handled internally)                                          |
| `updateCellsBatchingPeriod`              | —                                        | **Remove** (handled internally)                                          |
| `windowSize`                             | `drawDistance`                           | **Replace** (drawDistance in px, e.g. `250`)                             |
| `initialNumToRender`                     | `estimatedFirstItemOffset`               | **Replace** (or just use `estimatedItemSize`)                            |
| `getItemLayout`                          | `overrideItemLayout`                     | **Replace** (see example above)                                          |

### Known gotchas

1. **`contentContainerStyle` with `flex: 1`** — FlashList ignores flex on the inner container. If you need the list to fill its parent, wrap FlashList in a `<View style={{flex: 1}}>`.
2. **Sticky headers** — `stickyHeaderIndices` is not supported. Use `StickyHeaderComponent` prop or move sticky headers outside the list.
3. **`CellRendererComponent`** — Not supported in FlashList. If any list uses this, keep it as FlatList.
4. **Item separator** — `ItemSeparatorComponent` works but is not recycled. For heavy separators, render them inside `renderItem` instead.
5. **Variable height items** — FlashList handles them, but `estimatedItemSize` should be the average. If heights vary wildly (e.g. collapsed vs expanded orders), recycling performance may be slightly lower — still better than FlatList.
6. **Lists inside bottom sheets** — Keep `BottomSheetFlatList` / `BottomSheetScrollView` from `@gorhom/bottom-sheet`. FlashList has no official bottom-sheet wrapper, so gesture hand-off (drag-to-dismiss when the list is at offset 0) breaks without custom glue via `createBottomSheetScrollableComponent`. Bottom-sheet lists are also short (selectors, filters, pickers), so recycling gains are negligible — not worth the risk.

---

### What NOT to migrate

Keep these as FlatList — they are short lists (<15 items) in bottom sheets/pickers where FlashList adds overhead without benefit:

- Bottom sheet selection lists (SelectPSOCBS, SelectVehicle, SelectProduct, SelectDealer, SelectCustomer, etc.)
- State/district pickers (SelectStateBS, SelectDistrict)
- Small inline lists in form screens (NewInvoice items, NewOrder items)
- NumberMeter, Prompt, and other utility components

---

## Summary

| Task                            | Size | Impact                                                  | Risk       |
| ------------------------------- | ---- | ------------------------------------------------------- | ---------- |
| APP-1: `useCallback` renderItem | XS   | Fewer re-renders                                        | Zero       |
| APP-2: `React.memo` list items  | XS   | Fewer re-renders                                        | Zero       |
| APP-3: FlatList virtualization  | S    | Lower memory, smoother scroll                           | Low        |
| APP-4: Fine-grained selectors   | S    | Fewer re-renders across screens                         | Low        |
| APP-5: RTK Query retry          | S    | Resilient to network blips                              | Low        |
| APP-6: Unify cache tags         | S    | Correct cache invalidation                              | Low        |
| APP-7: Remove Axios             | M    | Simpler codebase, smaller bundle                        | Medium     |
| APP-8: FlashList migration      | M    | Eliminates blank cells, ~60% less memory, 60 FPS scroll | Low-Medium |

**Recommended order:** APP-1 + APP-2 (together) → APP-3 → APP-8 (Phase 1) → APP-5 → APP-6 → APP-4 → APP-8 (Phase 2-3) → APP-7
