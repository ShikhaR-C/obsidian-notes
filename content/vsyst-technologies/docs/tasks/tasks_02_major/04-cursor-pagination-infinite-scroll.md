# 04 — Cursor-Based Pagination + RTK Query Infinite Scroll

> Originally deferred as **Phase 3D** in the learning docs.
> Target: replace offset-based (`skip/limit`) pagination with cursor-based pagination on the API, and wire the existing (but unused) RTK Query pagination helpers to FlashList's `onEndReached` so every list becomes an infinite-scroll experience.

---

## TL;DR

Today: every list endpoint uses `skip` + `limit`. `skip` drifts when items are inserted or deleted between page loads (duplicates and missed rows), and `skip(n)` becomes O(n) on Mongo — every subsequent page is slower. Worse, the default limit is **0**, which means a missing `limit` query param returns the entire collection. This is a latent bug.

The app has a pagination helper (`src/store/apis/paginationHelpers.js`) with `serializeQueryArgs` and `merge` already written for infinite scroll, but **no screen actually wires `onEndReached`** — so every list is a single-page fetch today and FlashList's virtualization is underutilized.

Target: (1) API exposes `cursor` + `limit` on all list endpoints, with a sane `limit=25` default and `limit ≤ 100` cap. (2) App wires `onEndReached` on every FlashList, using the existing `paginationHelpers` + new cursor support, for smooth infinite scroll. (3) Old `page/limit` still works (dual-mode) for back-compat.

Net effect: (a) drift bug goes away, (b) deep-page latency drops from hundreds of milliseconds to ~20ms, (c) the app feels like a modern mobile app instead of a paginated grid.

---

## 1. Current State (from code research)

### 1.1 API side

| Concern                     | File                                     | Notes                                                            |
| --------------------------- | ---------------------------------------- | ---------------------------------------------------------------- |
| Pagination helper           | `helpers/advancedResults.js:46-58`       | `const limit = parseInt(reqlimit, 10) \|\| 0` — **zero default** |
| Default page                | `helpers/advancedResults.js:48`          | `const page = parseInt(reqpage, 10) \|\| 1`                      |
| Paginated endpoints (major) | `api_v3/services/users.js:173-176`       | Users list, uses advancedResults                                 |
|                             | `api_v3/services/dealer_custs.js`        | Dealer customer relations                                        |
|                             | `api_v3/services/order_msts.js`          | `getPSOrdersPagination`, `getPSOrdersFilter`                     |
|                             | `api_v3/services/cust_msts.js:143-160`   | `getMultipleWithPSFilters`                                       |
|                             | `api_v3/services/dealer_msts.js:173-212` | Dealer masters list                                              |
|                             | `api_v3/services/dvr_msts.js:154-209`    | Driver masters list                                              |
|                             | `api_v3/services/invs.js`, `voc_msts.js` | Invoices + vouchers lists (all POST-filter variants)             |
| Sort field default          | `-createdAt`                             | Almost every endpoint. Consistent, convenient.                   |
| Total count                 | Returned by every paginated endpoint     | Used by the client for "X of Y" displays                         |

### 1.2 App side

| Concern                 | File                                                         | Notes                                                                               |
| ----------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| Pagination helper       | `src/store/apis/paginationHelpers.js`                        | `createPaginatedQueryConfig()`, `paginatedQueryConfig` — merge + serializeQueryArgs |
| Merge strategy          | `paginationHelpers.js:28-45`                                 | Merges results, dedupes by `_id`, handles `refresh` flag                            |
| Cache key serialization | `paginationHelpers.js:12-27`                                 | Omits `page` and `refresh` from cache key (so all pages share one cache)            |
| POST-endpoint nesting   | `paginationHelpers.js`                                       | Supports `nestedPageIn: 'filterProps'` for POST bodies that nest page inside        |
| Order list query config | `src/store/apis/dzzlooms/order_msts.js:40, 76-78`            | **Already uses** `paginatedQueryConfig` — ready for infinite scroll!                |
| FlashList usage         | `src/screens/Dealer/Customers/index.js:10, 297` (and others) | FlashList present from `tasks_01/APP-8`                                             |
| `onEndReached`          | **Not wired on any screen**                                  | This is the gap                                                                     |
| Refetch on focus        | Manual `useIsFocused()` + `onRefresh` in screens             | No `refetchOnFocus` at the store level                                              |

### 1.3 Key observation

The **client-side infrastructure is ready**. The pagination helper was built (probably in a previous session) with infinite scroll in mind, but nobody has wired `onEndReached` to increment the page parameter. Half the work is done. This initiative is mostly API changes + hooking up `onEndReached`.

---

## 2. Problem Statement

### 2.1 Offset pagination is broken under inserts

Scenario: a user is on page 1 of Orders, sorted by `-createdAt`. Before they request page 2, a new order arrives.

```
page 1 (time T):         page 2 (time T+1, after new order inserted):
[#100, #99, #98,          [#99, #98, #97, #96, #95, ...]
 #97, #96, ...]           ^^^ DUPLICATE — #99 was on page 1 already
```

The client's "load more" fetch re-shows items already seen. Conversely, if an item is deleted between loads, a row gets silently skipped.

At DZZLO's current scale this is minor, but as order volume grows and users keep lists open longer, it becomes noticeable. The pagination helper's `_id` dedup papers over the duplicate case but can't recover the skip case.

### 2.2 `skip()` is O(n) in Mongo

Mongo must scan `skip` documents to reach the offset. On page 50 with `limit=20`, that's `skip=980`. Each page is slower than the last. Cursor pagination is O(1) regardless of depth because it uses an indexed range query (`_id > cursor` or `createdAt < cursor`).

### 2.3 `limit = 0` default is a bug

`helpers/advancedResults.js:49` does `parseInt(reqlimit, 10) || 0`. If a caller forgets to pass `limit`, `limit = 0`, which in Mongoose means **no limit** — the entire collection is fetched. On a 50k-document collection this is a disaster. This is explicitly called out in the research as a latent bug.

### 2.4 No infinite scroll

Users see a fixed page of items and have no visible affordance to load more. The existing FlashLists are just rendering the first page and stopping. The `paginationHelpers` merge logic is waiting to be called.

---

## 3. Research & Technical Deep-Dive

### 3.1 Cursor pagination: what is it?

A **cursor** is a serialized pointer to a position in a sorted stream. Instead of "give me page 5 of the results", the client says "give me the next 25 items **after** cursor X". The server decodes X, runs an indexed range query, returns the next 25, and returns a new cursor pointing to the last item it sent.

```
Client:  POST /orders/list  body: {limit: 25}
Server:  {items: [...25 items...], nextCursor: "eyJjcmVhdGVkQXQiOiIyMDI2LTA0LTExVDEyOjAwOjAwWiIsIl9pZCI6IjY2N..."}

Client:  POST /orders/list  body: {limit: 25, cursor: "eyJjcmVhdGVkQXQiOiIyMDI2LTA0LTExVDEyOjAwOjAwWiIsIl9pZCI6IjY2N..."}
Server:  {items: [...next 25...], nextCursor: "eyJjcmVhdGVkQXQiOiIyMDI2LTA0LTExVDExOjU5OjQ3WiIsIl9pZCI6IjY2N..."}
```

### 3.2 Cursor encoding

A cursor encodes the sort key(s) of the last item on the previous page. For DZZLO:

- **Sort:** `-createdAt, -_id` (`-_id` as tiebreaker — two docs can share a `createdAt` in rare edge cases, so we include `_id` to break ties deterministically).
- **Cursor content:** `{createdAt, _id}` — tiny JSON, base64url encoded for URL safety.
- **Query:** `{createdAt: {$lt: cursor.createdAt}} OR {createdAt: cursor.createdAt, _id: {$lt: cursor._id}}` — the "tuple comparison" idiom.

Mongoose translation:

```js
const cursorFilter = cursor
  ? {
      $or: [
        { createdAt: { $lt: cursor.createdAt } },
        { createdAt: cursor.createdAt, _id: { $lt: cursor._id } },
      ],
    }
  : {};

Model.find({ ...baseFilter, ...cursorFilter })
  .sort({ createdAt: -1, _id: -1 })
  .limit(limit + 1) // fetch one extra to detect "has more"
  .lean();
```

Return the first `limit` items as `items`. If there was an extra item, set `hasMore: true` and build a new cursor from the last returned item.

### 3.3 Why `_id` tiebreaker matters

Without a tiebreaker:

```
Documents:
  {_id: A, createdAt: 2026-04-11T10:00:00Z}
  {_id: B, createdAt: 2026-04-11T10:00:00Z}   ← same timestamp
  {_id: C, createdAt: 2026-04-11T09:59:00Z}

Page 1 (limit=1):  returns A. Cursor = {createdAt: 10:00:00}.
Page 2 query:      createdAt < 10:00:00
                   → returns C.
                   → B IS SKIPPED.
```

With the `_id` tiebreaker, page 1 cursor is `{createdAt: 10:00:00, _id: A}`. Page 2 query correctly returns B before C.

Because DZZLO uses `new Date()` for `createdAt` and batch creates (e.g. SMS OTP notification → multiple rows at once) can land in the same millisecond, this is not theoretical.

### 3.4 Indexes required

For each collection with cursor pagination, ensure a compound index on `{createdAt: -1, _id: -1}`. Mongo already has `_id` as primary; we need to add the `createdAt` index.

```js
OrderMstsSchema.index({ createdAt: -1, _id: -1 });
```

If the endpoint also filters by a field (e.g. `co_id`), we need a compound index including that field:

```js
OrderMstsSchema.index({ co_id: 1, createdAt: -1, _id: -1 });
```

The existing `tasks_01/DB-1..DB-4` already added compound indexes for major query paths. Extending them for cursor pagination is a small additive change.

### 3.5 `createdAt` vs `_id` as the sort key

Alternative: sort purely by `_id` descending (since Mongo `ObjectId` is roughly chronological by default — the first 4 bytes are a timestamp).

| Approach                    | Pros                               | Cons                                                                                                    |
| --------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `-_id` only                 | No extra index (primary key sort)  | Not monotonic if `_id` is manually set, client-supplied, or migrated. Not intuitive when showing dates. |
| `-createdAt, -_id` (chosen) | Explicit, matches user expectation | Requires a secondary index per collection                                                               |

Since DZZLO already sorts by `-createdAt` everywhere and has user-facing timestamps, we stick with `-createdAt, -_id`. The extra index is small and justified.

### 3.6 Cursor opacity

**Rule:** the client must treat the cursor as an opaque blob. It's encoded/decoded only by the server.

**Why:** if the server ever needs to change the encoding (e.g. add a new field to break another tie), clients holding old-format cursors would break. By making it opaque, the server can version the cursor internally:

```js
// v1 cursor: {v: 1, createdAt, _id}
// v2 cursor: {v: 2, createdAt, _id, tenancy}
// The server decodes, branches on `v`, and handles both.
```

Base64url encoding + a version byte is enough. Don't expose the internal shape in docs.

### 3.7 Total count: keep, drop, or estimate?

Total count is expensive on large collections (`countDocuments` scans the index). With cursor pagination, the client doesn't strictly need total count — infinite scroll just loads until `hasMore === false`.

**Options:**

1. **Always return count.** Simple. Slow on 100k+ collections.
2. **Never return count.** Fastest. But the app has UI that shows "42 of 1,234" on some screens, so this is a user-facing regression.
3. **Return count only on the first page** (no cursor passed). Subsequent paged requests skip it. This matches what the UI actually needs — the count only changes when filters change, which also invalidates the cursor chain.

**Choice:** option 3. First-page response has `{items, nextCursor, hasMore, totalCount}`. Subsequent pages have `{items, nextCursor, hasMore}` (no totalCount).

### 3.8 Dual-mode: cursor + offset during migration

We don't want to break every existing caller atomically. The API supports both:

```
POST /order_msts/a/poso
Body (old):  {page: 1, limit: 20, ...filters}    → offset mode
Body (new):  {cursor: "...", limit: 25, ...filters}  → cursor mode
Body (new, first page): {limit: 25, ...filters}  → cursor mode, no cursor yet
```

The controller branches on the presence of `cursor`. If `cursor` is undefined but `page` is defined, it's old-mode. Otherwise it's new-mode.

This means the client can migrate screens one at a time without any coordinated big-bang release.

### 3.9 RTK Query `merge` and `serializeQueryArgs` — how they work

The client-side half of infinite scroll relies on two RTK Query features:

**`serializeQueryArgs`** — tells RTK Query "all these different arg combinations should share the same cache entry". Without it, every new page is a separate cache entry and old pages get garbage-collected. With it, all pages go into one cache entry.

```js
serializeQueryArgs: ({endpointName, queryArgs}) => {
  const {cursor, page, refresh, ...rest} = queryArgs;
  return `${endpointName}-${JSON.stringify(rest)}`;
},
```

**`merge`** — called when new data arrives for an existing cache entry. Default behavior is to replace. For infinite scroll, we want to append.

```js
merge: (currentCache, newItems, {arg}) => {
  if (arg.refresh || !arg.cursor) {
    // Fresh load or pull-to-refresh — replace
    return newItems;
  }
  // Pagination — append, dedupe by _id
  const existingIds = new Set(currentCache.items.map(i => i._id));
  const newOnes = newItems.items.filter(i => !existingIds.has(i._id));
  return {
    items: [...currentCache.items, ...newOnes],
    nextCursor: newItems.nextCursor,
    hasMore: newItems.hasMore,
    totalCount: currentCache.totalCount ?? newItems.totalCount,
  };
},
```

**`forceRefetch`** — tells RTK Query to re-run the query even though the cache key is the same. Required because RTK Query would otherwise think "same cache key → nothing to do". We force it when `arg.cursor` changes.

```js
forceRefetch: ({currentArg, previousArg}) => {
  return currentArg?.cursor !== previousArg?.cursor
      || currentArg?.refresh === true;
},
```

The existing `paginationHelpers.js` has most of this for the page/offset case. The change is to (a) swap `page` for `cursor` as the pagination parameter and (b) update `forceRefetch`.

### 3.10 FlashList `onEndReached` specifics

FlashList's `onEndReached` is called when the user scrolls within `onEndReachedThreshold` of the end. Defaults and best practices:

- `onEndReachedThreshold={0.5}` — fire when scrolled to 50% of the remaining list. Gives time to load before the user actually hits the bottom.
- **Guard against repeated fires:** `onEndReached` can fire multiple times during a fast scroll. Gate with `if (!isLoading && hasMore) { loadMore(); }`.
- **Empty list fix:** FlashList fires `onEndReached` on empty lists. Guard with `if (items.length === 0) return;`.
- **Pull-to-refresh coexistence:** `onRefresh` → pass `{refresh: true}` to the query, which causes `merge` to replace instead of append.

---

## 4. Target Architecture

### 4.1 API response shape

```json
{
  "success": true,
  "items": [ {...}, {...}, ... ],
  "nextCursor": "eyJ2IjoxLCJjcmVhdGVkQXQiOiIyMDI2LTA0LTExVDEyOjAwOjAwWiIsIl9pZCI6IjY2N..." ,
  "hasMore": true,
  "totalCount": 1234
}
```

- `items` is always present (empty array if none).
- `nextCursor` is present if `hasMore === true`, otherwise `null`.
- `totalCount` is present only on the first page (request without a cursor).

### 4.2 Client query arg shape

```js
{
  // pagination
  cursor: string | null,       // null/undefined on first page
  limit: number,                // default 25
  refresh: boolean,             // true = replace cache, false = append

  // filters (endpoint-specific)
  ...filterProps,
}
```

### 4.3 FlashList usage pattern

```jsx
const [cursor, setCursor] = useState(null);
const [refresh, setRefresh] = useState(false);

const { data, isFetching, refetch } = useGetOrdersQuery({
  cursor,
  limit: 25,
  refresh,
  ...filters,
});

const handleEndReached = useCallback(() => {
  if (isFetching || !data?.hasMore) return;
  setCursor(data.nextCursor);
  setRefresh(false);
}, [isFetching, data]);

const handleRefresh = useCallback(() => {
  setCursor(null);
  setRefresh(true);
  // RTK Query will re-fetch and merge will replace the cache
}, []);

<FlashList
  data={data?.items ?? []}
  renderItem={renderItem}
  onEndReached={handleEndReached}
  onEndReachedThreshold={0.5}
  refreshing={isFetching && refresh}
  onRefresh={handleRefresh}
  ListFooterComponent={isFetching && cursor ? <ActivityIndicator /> : null}
/>;
```

This pattern is copy-pasted across every list screen with only `filters` and `renderItem` changing.

---

## 5. Phased Rollout

### Phase 1 — API: Cursor helper + indexes + default limit fix

**Goal:** lay the groundwork. No endpoints migrated yet.

#### Step 1.1 — Create cursor helper

- New file: `helpers/cursorPagination.js`
- Exports:
  - `encodeCursor({createdAt, _id})` → base64url string (with version byte)
  - `decodeCursor(str)` → `{createdAt, _id}` or throws
  - `buildCursorFilter(cursor, direction)` → Mongoose filter
  - `buildCursorSort(direction)` → `{createdAt: -1, _id: -1}` or inverse
  - `extractNextCursor(items, limit)` → returns `{items, nextCursor, hasMore}` — consumes one extra fetched item

#### Step 1.2 — Fix the `limit = 0` bug (proactively)

- File: `helpers/advancedResults.js:49`
- Change `parseInt(reqlimit, 10) || 0` → `Math.min(parseInt(reqlimit, 10) || 25, 100)`.
- Default 25, max 100.
- **Caveat:** some callers may intentionally pass `limit=0` to mean "all". Grep for `limit: 0` in both codebases before changing to confirm no callers rely on this. If any do, migrate them to explicit large limits first.

#### Step 1.3 — Add indexes

- For each collection planned to get cursor pagination (orders, invoices, vouchers, customers, dealers, users, drivers, dealer_custs):
  - Add `Schema.index({createdAt: -1, _id: -1})`.
  - If the queries filter by `co_id`, `dealer_id`, or similar, add compound indexes like `{co_id: 1, createdAt: -1, _id: -1}`.
- Let Mongo build them in the background on Atlas. Monitor via Atlas UI.
- Cross-check with `tasks_01/DB-1..DB-4` — don't duplicate existing indexes.

#### Step 1.4 — Unit tests for cursor helper

- `test/api_v3/helpers/cursorPagination.test.js`:
  - `encode → decode` round-trip
  - Unknown cursor format → throws
  - Version mismatch → throws cleanly
  - `buildCursorFilter` produces the tuple-comparison filter correctly

**Definition of Done:**

- Helper exists, tests pass, indexes built, `advancedResults.js` default fixed. No endpoints changed yet.

---

### Phase 2 — API: Migrate one endpoint (orders list)

**Goal:** pilot on the heaviest list: `order_msts`. Dual-mode (accepts both old and new).

#### Step 2.1 — Update the controller

- File: `api_v3/controllers/collections/order_msts.js` (lines 66-74 area)
- Branch logic:
  ```js
  if (req.body.cursor !== undefined || req.body.page === undefined) {
    return getOrdersCursor(req, res);
  }
  return getOrdersOffset(req, res); // existing
  ```

#### Step 2.2 — Implement `getOrdersCursor` in the service

- File: `api_v3/services/order_msts.js`
- New function `getPSOrdersCursor({tenancyFilter, filters, cursor, limit})`.
- Body:

  ```js
  const cursorFilter = cursor ? buildCursorFilter(decodeCursor(cursor)) : {};
  const query = { ...tenancyFilter, ...filters, ...cursorFilter };

  const items = await OrderMsts.find(query)
    .sort({ createdAt: -1, _id: -1 })
    .limit(limit + 1)
    .select(fieldProjection)
    .lean();

  const result = extractNextCursor(items, limit);

  if (!cursor) {
    result.totalCount = await OrderMsts.countDocuments(query);
  }

  return result;
  ```

#### Step 2.3 — Integration tests

- Seed 100 orders with known `createdAt` values.
- Call first page (`{limit: 25}`) → 25 items, `hasMore: true`, `totalCount: 100`, `nextCursor: "..."`.
- Call second page (`{limit: 25, cursor}`) → next 25 items.
- Walk all 4 pages → last page has `hasMore: false, nextCursor: null`.
- Call with old-mode `{page: 1, limit: 25}` → still works.
- Concurrent insert test: fetch page 1, insert a new order, fetch page 2 — assert no duplicates.

**Definition of Done:**

- Both cursor mode and old-mode work on `order_msts` list.
- Tests pass.
- No app changes yet.

---

### Phase 3 — App: Upgrade paginationHelpers for cursor mode

**Goal:** extend the existing `paginationHelpers.js` to support cursors alongside pages.

#### Step 3.1 — Add `createCursorPaginatedQueryConfig`

- File: `src/store/apis/paginationHelpers.js` (extend, don't break)
- New export: `createCursorPaginatedQueryConfig({tagType})` returns an object with `serializeQueryArgs`, `merge`, `forceRefetch`, `providesTags`.
- Keep the old `paginatedQueryConfig` and `createPaginatedQueryConfig` for endpoints still in offset mode.

#### Step 3.2 — Helper hook for screens

- New file: `src/hooks/useCursorList.js`
- Signature: `useCursorList(queryHook, filters, {limit = 25})`
- Returns: `{items, isLoading, isFetching, hasMore, refresh, loadMore, error}`
- Internal state: `cursor`, `refreshKey`
- Fires the query, handles `onEndReached` and `onRefresh` logic.
- This encapsulates all the boilerplate from the "FlashList usage pattern" sketch above. Screens use the hook and don't touch cursor state directly.

#### Step 3.3 — Unit tests for the hook

- Jest + React Testing Library.
- Mock the query hook.
- Assert:
  - First render → fetches with `cursor: null`
  - `loadMore()` → fetches with `cursor: responseNextCursor`
  - `refresh()` → resets cursor to null and sets `refresh: true`
  - `hasMore: false` → `loadMore()` is a no-op

**Definition of Done:**

- Helpers and hook exist with tests. No screens migrated yet.

---

### Phase 4 — App: Migrate the Orders list screen

**Goal:** wire the first screen end-to-end. Validates the whole pipeline.

#### Step 4.1 — Update the RTK Query endpoint

- File: `src/store/apis/dzzlooms/order_msts.js`
- For `fetch_order_so_POST`, replace `createPaginatedQueryConfig({nestedPageIn: 'filterProps'})` with `createCursorPaginatedQueryConfig({tagType: 'order_msts'})`.
- The endpoint now takes `{cursor, limit, refresh, filterProps}`.

#### Step 4.2 — Migrate the screen

- File: `src/screens/Common/Orders/index.js` (and Dealer / Customer variants that share the hook)
- Replace the current `useLazyFetch_order_so_POSTQuery` call with:
  ```js
  const { items, hasMore, isFetching, loadMore, refresh } = useCursorList(
    useFetch_order_so_POSTQuery,
    filterProps,
    { limit: 25 },
  );
  ```
- Wire `onEndReached={loadMore}` and `onRefresh={refresh}` on the FlashList.

#### Step 4.3 — Manual test

- Open Orders screen → 25 items loaded, "scroll me" UX is present.
- Scroll → more items appear at ~50% scroll position.
- Scroll to end → spinner → more items → eventually hasMore = false.
- Pull to refresh → list replaced with latest 25.
- Toggle a filter → list resets, totalCount updates.

**Definition of Done:**

- Orders list is fully infinite-scrolling with cursor pagination. Users notice only a smoother UX (but product/support should be alerted in advance).
- Old offset mode remains in the API for any non-migrated callers.

---

### Phase 5 — API: Migrate remaining high-traffic list endpoints

**Goal:** apply the Phase 2 pattern to the next batch of endpoints.

For each endpoint below, repeat the Phase 2 recipe (dual-mode branching, service function, tests):

1. `api_v3/services/invs.js` — invoice list
2. `api_v3/services/voc_msts.js` — voucher list
3. `api_v3/services/dealer_custs.js` — dealer-customer relations
4. `api_v3/services/cust_msts.js` — customer masters
5. `api_v3/services/dealer_msts.js` — dealer masters
6. `api_v3/services/users.js` — users list
7. `api_v3/services/dvr_msts.js` — driver masters

**Definition of Done per endpoint:**

- Both modes work, integration tests updated, indexes verified.

---

### Phase 6 — App: Migrate remaining list screens

**Goal:** wire `useCursorList` into every screen that renders a list.

Per-screen checklist (copy once, apply per screen):

- [ ] Endpoint updated to use `createCursorPaginatedQueryConfig`
- [ ] Screen swapped to `useCursorList`
- [ ] FlashList has `onEndReached`, `onEndReachedThreshold={0.5}`, `onRefresh`
- [ ] Footer spinner for "loading more"
- [ ] Empty-state handling ("no items" vs. "no more to load")
- [ ] Filter-change resets the cursor chain
- [ ] Manual QA: scroll, refresh, filter, search

**Screens to migrate:**

| Module      | Screen                                  | Priority                                                                                                                                       |
| ----------- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Orders      | `Common/Orders/index.js`                | P0 (pilot)                                                                                                                                     |
|             | `Dealer/Orders/index.js`                | P1                                                                                                                                             |
|             | `Customer/Orders/index.js`              | P1                                                                                                                                             |
| Invoices    | `Common/Invoices/index.js`              | P1                                                                                                                                             |
|             | `Dealer/Invoices/index.js`              | P1                                                                                                                                             |
|             | `Customer/Invoices/index.js`            | P1                                                                                                                                             |
| Payments    | `Common/Payments/index.js`              | P1                                                                                                                                             |
|             | `Dealer/Payments/index.js`              | P1                                                                                                                                             |
|             | `Customer/Payments/index.js`            | P1                                                                                                                                             |
| Customers   | `Dealer/Customers/index.js`             | P1                                                                                                                                             |
| Dealers     | `Customer/Dealers/index.js`             | P1                                                                                                                                             |
| Users       | `Common/CompanyUsers/index.js`          | P2 — but this one gets a BFF in `03`, so cursor pagination for its users list becomes part of the BFF response. Coordinate ordering with `03`. |
| Drivers     | `Customer/Drivers/index.js` (if exists) | P2                                                                                                                                             |
| Vehicles    | `Common/Vehicles/index.js`              | P2                                                                                                                                             |
| Sister cos. | `Common/SisterCompanies/index.js`       | P2 — same caveat (BFF)                                                                                                                         |

Ship 2-3 screens per PR. Don't batch them all or QA becomes unmanageable.

---

### Phase 7 — Monitoring and retirement of offset mode

#### Step 7.1 — Telemetry

- Log every list call with `{endpoint, mode: 'cursor'|'offset'}`.
- Dashboard: count of offset-mode calls per hour. Watch it trend toward zero as screens migrate.

#### Step 7.2 — Retirement of offset mode

When offset-mode calls drop below 1% of traffic **and** that 1% is from known old-app versions (check User-Agent), remove the offset branch from the controllers. This is a T+60-day cleanup PR.

- The `advancedResults.js` helper stays (it's used by admin tooling too), but the new default of 25 and cap of 100 remain.

---

## 6. Benefits

| Benefit                                     | Before                    | After                            |
| ------------------------------------------- | ------------------------- | -------------------------------- |
| Page 50 latency on 50k docs (orders)        | ~200-500 ms (skip scan)   | ~20 ms (indexed range query)     |
| Duplicate rows on concurrent inserts        | Yes (drift)               | No                               |
| Silently-skipped rows on concurrent deletes | Yes                       | No                               |
| Default limit protection                    | `limit=0` returns all (!) | `limit=25`, cap 100              |
| User-visible: infinite scroll UX            | No                        | Yes                              |
| User-visible: pull to refresh on all lists  | Partial                   | Yes                              |
| List screen first-paint time (cached)       | Same                      | Same                             |
| List screen deep-scroll time                | Degrades linearly         | Constant                         |
| Additional Mongo indexes                    | —                         | ~1 compound index per collection |
| Extra client-side LoC per screen            | —                         | ~5 (thanks to `useCursorList`)   |

---

## 7. Risks & Rollback

| Risk                                                                      | Likelihood | Impact | Mitigation                                                                          |
| ------------------------------------------------------------------------- | ---------- | ------ | ----------------------------------------------------------------------------------- |
| Cursor gets corrupted / mismatched across app versions                    | Low        | Low    | Version byte in cursor; unknown versions → 400 → client falls back to first page    |
| Indexes not yet built when deploying (Mongo backfilling)                  | Medium     | High   | Build indexes 24h before deploying cursor code; verify via Atlas UI                 |
| Some legacy caller relies on `limit=0` = all                              | Medium     | High   | Grep first; migrate those callers to explicit `limit=10000` before changing default |
| Filter-change bug: cursor from old filter set used with new filters       | Medium     | Medium | `useCursorList` resets cursor whenever filters change (shallow compare)             |
| FlashList `onEndReached` fires on mount (empty list)                      | High       | Low    | Guard with `items.length > 0`                                                       |
| Infinite scroll goes infinite (server always says hasMore)                | Low        | High   | Server-side safety: cap at 1000 items per paginated session                         |
| User-perceived lag because cursor loads are slower than simple cache hits | Low        | Low    | Show footer spinner. Pre-fetch at 50% threshold.                                    |

### Rollback plan

**Per-endpoint rollback:** revert the controller branch to `return getOrdersOffset(req, res)` (drop the cursor path). Client's `useCursorList` will still call with `cursor` set, but the server responds with offset-style payload → the response shape mismatch will fail loudly rather than silently corrupt data. Better: add a kill switch `CURSOR_PAGINATION_ENABLED=false` that makes the controller fall back to offset mode.

**Client-side:** the old `paginatedQueryConfig` is still exported. Revert the endpoint file to use it, and the old page/offset mode resumes.

---

## 8. Testing Strategy

### 8.1 API tests

Per endpoint:

- Happy-path walk: page 1, 2, 3, ..., last. Verify no duplicates, no skips, correct total on page 1 only.
- Concurrent insert: fetch page 1, insert a record with a `createdAt` ≥ the first item on page 1, fetch page 2, verify no duplicate.
- Concurrent delete: similar.
- Tiebreaker: insert two records with identical `createdAt`, paginate with `limit=1`, verify both appear.
- Filter change: fetch with filter A, then fetch with filter B — both should return their own full chains.
- Limit cap: request `limit=500`, assert server returns `limit=100`.
- Legacy: `{page: 2, limit: 20}` still works.

### 8.2 App tests

- Jest test for `useCursorList` hook covering all state transitions.
- Integration test with a mocked endpoint returning multi-page data.

### 8.3 Manual QA checklist

- [ ] Fresh app launch → orders list loads 25 items
- [ ] Fast scroll → pages load ahead of the viewport (no blank rows)
- [ ] Pull to refresh → list jumps to latest 25
- [ ] Apply a filter → list resets
- [ ] Scroll to absolute end → footer spinner disappears, no "hasMore" indicator
- [ ] Offline mid-scroll → error state, resumeable on reconnect
- [ ] Same user on two devices: insert on A, refresh on B → no duplicates on B's next scroll

---

## 9. Interaction with Other `tasks_02` Initiatives

- **`02-websocket-realtime.md`:** when a socket event invalidates a list's tag (e.g. `order:created`), RTK Query re-fetches **only the first page** (by resetting the cursor chain via `refresh: true`). New items appear at the top. Implementation note: the socket handler should dispatch `refresh` on the hook, not naïvely `invalidateTags`, because `invalidateTags` would re-fetch with the current cursor and miss the new items. Build a helper `refreshCursorList(tagType)` that clears the cache entry and re-fetches fresh.
- **`03-bff-composite-endpoints.md`:** BFF responses don't paginate internal lists. If a BFF's internal list grows, link out to the cursor-paginated endpoint. Don't try to paginate inside a BFF.
- **`05-cicd-github-actions.md`:** no direct interaction. Tests run in CI.

---

## 10. Open Questions

1. **Should list endpoints support a `prevCursor` for backwards pagination?** Not for infinite scroll. Add only if/when a paginated table UI is built.
2. **Sort orders other than `-createdAt`?** Most screens sort by date. If a specific screen needs `-totalAmount` or similar, the cursor must encode that field instead. Defer until a real use case appears. Keep the cursor helper extensible (`encodeCursor({keys})`).
3. **Should totalCount be estimated (e.g. via `estimatedDocumentCount` for no-filter cases)?** Only if `countDocuments` becomes a hotspot. Not a launch concern.
4. **What about very cold deep scrolls (user scrolls to page 100)?** Cursor pagination is constant-time, but the user will hit the ~1000-item session cap first. Design decision: cap is fine; if a user needs to search something far back, they should use search/filters instead of scrolling.
5. **Interaction with offline cache:** if the user scrolls page 1-5 offline from cache, then scrolls to page 6 online, does it work? Yes — RTK Query serves the cached merged list and fetches the next cursor from the server. As long as the cache isn't garbage-collected between sessions (RTK Query's `keepUnusedDataFor` is 300s — long enough for normal use), this works.
