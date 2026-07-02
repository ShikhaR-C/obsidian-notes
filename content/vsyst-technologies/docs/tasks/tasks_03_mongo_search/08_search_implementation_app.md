# Search Implementation Plan — App (`dzzlo_oms_app`)

Scope: wire the new `/search` endpoints from `07_search_implementation_api.md`
into the React Native app for **Vehicles**, **Orders**, and **Dealers**, with a
consistent debounced `SearchBar`, a reusable `FilterSheet`, and per-entity
hooks. Existing in-memory "filter on the client" behaviour stays as a graceful
fallback when the user has no network.

---

## 1. Existing data-fetching pattern (audit)

Relevant files read:

- **Store**: RTK Query. Base API at `dzzlo_oms_app/src/store/apis/createApi.js`,
  endpoints injected in `dzzlo_oms_app/src/store/apis/dzzlooms/*.js` using
  `builder.query` / `builder.mutation` and tag invalidation.
  - `order_msts.js` — `fetch_order_msts_so` and `fetch_order_so_POST` both hit
    `/order_msts/a/poso` and accept `page/limit/order_status[in]/cust_id` etc.
    They use `createPaginatedQueryConfig` / `paginatedQueryConfig` from
    `paginationHelpers.js` to merge pages on the client.
  - `veh_msts.js` — only `add_veh_msts` + `delete_veh_msts`. No list endpoint.
  - `dealer_msts.js` — `fetch_dealer_msts` uses the `_id[nin]` pattern.
- **Screens** currently filter client-side AFTER fetching a whole page:
  - `src/screens/Dealer/Orders/index.js` — lines 243-321: `useMemo` that chains
    `.filter(status).filter(cust_id).filter(text on veh_reg_no/remarks/dealer_user_name)
    .filter(date range on on_dt).sort(on_dt)`.
    Uses `search` state + `searchFilterFunction` callback. Has an
    `isSearchOpen` toggle that swaps between the "browse" list
    (`fetch_order_msts_so`) and the "filter" list (`fetch_order_so_POST`).
    It already owns `sheetdateRef`, `sheetstatusRef`, `sheetCompRef` bottom
    sheets and passes filters into `fetch_OFP(...)`.
  - `src/screens/Customer/Vehicles/index.js` — lines 112-120: local `search`
    state driving a `useMemo` over `vTrns.data`. Uses the shared
    `src/components/Search/Search.js` bar.
  - `src/screens/Customer/Dealers/index.js` — lines 64-93: same pattern,
    local `search` state, client-side filter on `dealer_id.dealer_name`.
- **Reusable search bar**: `src/components/Search/Search.js` already exists
  (read end-to-end). It is a styled `TextInput` with an optional magnifier.
  It takes `search` + `searchFilterFunction` props and does **not** debounce.
- **Bottom sheets**: `@gorhom/bottom-sheet ^5.2.8` is in `package.json`.
  Existing sheet implementations live in
  `src/screens/Common/Orders/bottomsheet/{dateRange,orderStatus,companyList}.js`.
  `DateRangeBottomSheet` uses `@react-native-community/datetimepicker`.
- **List rendering**: `@shopify/flash-list ^2.3.1` (see Dealers `index.js`).
- **Theme**: `react-native-paper ^5.15.0` (`useTheme()` returns `{ colors }`).
- **No** `lodash` or `debounce` package present. We'll implement debouncing
  with a custom hook to avoid adding a dep.

---

## 2. Reusable components

### 2.1 `SearchBar` — extend `src/components/Search/Search.js`

Instead of creating a new component, extend the existing one so current call
sites keep working. Add (a) optional debounce, (b) clear button, (c) loading
spinner.

File: `dzzlo_oms_app/src/components/Search/Search.js` (edit)

```jsx
import React, { useRef, useEffect, useState, useCallback } from 'react';
import { View, Pressable, TextInput, ActivityIndicator } from 'react-native';
import { useTheme } from 'react-native-paper';
import Feather from '../SVG/RNVI/Feather';
import Ionicons from '../SVG/RNVI/Ionicons';

const Search_components = ({
  search,                   // controlled value (kept for back-compat)
  searchFilterFunction,     // fired for every keystroke
  onDebouncedChange,        // NEW: fired after `debounceMs` of no typing
  debounceMs = 300,         // NEW
  loading = false,          // NEW
  placeholder = 'Search',
  showIcon = true,
  marginLeft = 15,
  marginRight = 15,
  zIndex = 1,
  autoFocus = false,        // NEW
}) => {
  const { colors } = useTheme();
  const searchInput = useRef(null);
  const [local, setLocal] = useState(search || '');

  // keep local state in sync if parent pushes a new value
  useEffect(() => { setLocal(search || ''); }, [search]);

  // debounce
  useEffect(() => {
    if (!onDebouncedChange) return;
    const id = setTimeout(() => onDebouncedChange(local), debounceMs);
    return () => clearTimeout(id);
  }, [local, debounceMs, onDebouncedChange]);

  const onChange = useCallback(
    (text) => {
      setLocal(text);
      if (searchFilterFunction) searchFilterFunction(text);
    },
    [searchFilterFunction],
  );

  const clear = useCallback(() => {
    setLocal('');
    if (searchFilterFunction) searchFilterFunction('');
    if (onDebouncedChange) onDebouncedChange('');
    searchInput.current?.focus();
  }, [searchFilterFunction, onDebouncedChange]);

  return (
    <View
      style={{
        zIndex,
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}
    >
      <View
        style={{
          flex: 12,
          backgroundColor: colors.border,
          marginVertical: 5,
          borderRadius: 10,
          marginLeft,
          marginRight,
          alignItems: 'center',
          flexDirection: 'row',
        }}
      >
        {showIcon && (
          <Pressable
            style={{ flex: 0.1, paddingLeft: 8 }}
            onPress={() => searchInput.current?.focus()}
            accessibilityLabel="Focus search"
          >
            <Feather name="search" size={18} color={colors.placeholder} />
          </Pressable>
        )}

        <TextInput
          ref={searchInput}
          autoCapitalize="none"
          autoCorrect={false}
          autoFocus={autoFocus}
          onChangeText={onChange}
          value={local}
          placeholder={placeholder}
          placeholderTextColor={colors.placeholder}
          underlineColorAndroid="transparent"
          returnKeyType="search"
          accessibilityLabel={placeholder}
          style={{
            flex: 1,
            padding: 10,
            height: 40,
            color: colors.text,
          }}
        />

        {loading ? (
          <ActivityIndicator
            size="small"
            color={colors.primary}
            style={{ marginRight: 10 }}
          />
        ) : local ? (
          <Pressable
            onPress={clear}
            hitSlop={10}
            style={{ paddingHorizontal: 10 }}
            accessibilityLabel="Clear search"
          >
            <Ionicons
              name="close-circle"
              size={18}
              color={colors.placeholder}
            />
          </Pressable>
        ) : null}
      </View>
    </View>
  );
};

export default Search_components;
```

**Back-compat**: when callers pass only `search` + `searchFilterFunction`, the
new props are no-ops and behaviour is identical to today.

### 2.2 `FilterSheet` — new reusable bottom sheet

File: `dzzlo_oms_app/src/components/Filter/FilterSheet.js` (new)

A generic `@gorhom/bottom-sheet` wrapper that takes a `fields` config and an
`initialValues` object, renders checkbox / radio / token chips for each field,
and emits `onApply(values)`.

```jsx
import React, {
  forwardRef, useMemo, useCallback, useState, useEffect,
} from 'react';
import { View, Pressable, ScrollView } from 'react-native';
import {
  BottomSheetBackdrop,
  BottomSheetModal,
  BottomSheetScrollView,
} from '@gorhom/bottom-sheet';
import { Button, Text, useTheme } from 'react-native-paper';
import DateRangeFilter from './DateRangeFilter';

// fields: [
//   { key: 'status', label: 'Status', type: 'multi',
//     options: [{ value: 'PENDING', label: 'Pending' }, ...] },
//   { key: 'dateRange', label: 'Date', type: 'dateRange' },
//   { key: 'verified', label: 'Verified', type: 'bool' },
// ]
const FilterSheet = forwardRef(({ fields, initialValues, onApply }, ref) => {
  const { colors } = useTheme();
  const [values, setValues] = useState(initialValues || {});

  useEffect(() => setValues(initialValues || {}), [initialValues]);

  const snapPoints = useMemo(() => ['50%', '85%'], []);
  const renderBackdrop = useCallback(
    (p) => <BottomSheetBackdrop {...p} disappearsOnIndex={-1} appearsOnIndex={0} />,
    [],
  );

  const set = (k, v) => setValues((prev) => ({ ...prev, [k]: v }));

  const apply = () => {
    onApply(values);
    ref?.current?.dismiss();
  };
  const reset = () => {
    setValues({});
    onApply({});
  };

  return (
    <BottomSheetModal
      ref={ref}
      snapPoints={snapPoints}
      backdropComponent={renderBackdrop}
      backgroundStyle={{ backgroundColor: colors.background }}
    >
      <BottomSheetScrollView contentContainerStyle={{ padding: 16 }}>
        {fields.map((f) => (
          <View key={f.key} style={{ marginBottom: 16 }}>
            <Text style={{ fontWeight: '600', marginBottom: 8 }}>{f.label}</Text>

            {f.type === 'multi' && (
              <View style={{ flexDirection: 'row', flexWrap: 'wrap' }}>
                {f.options.map((opt) => {
                  const selected = (values[f.key] || []).includes(opt.value);
                  return (
                    <Pressable
                      key={opt.value}
                      onPress={() => {
                        const cur = values[f.key] || [];
                        set(
                          f.key,
                          selected
                            ? cur.filter((v) => v !== opt.value)
                            : [...cur, opt.value],
                        );
                      }}
                      accessibilityRole="checkbox"
                      accessibilityState={{ checked: selected }}
                      style={{
                        borderWidth: 1,
                        borderColor: selected ? colors.primary : colors.border,
                        backgroundColor: selected
                          ? colors.primary
                          : 'transparent',
                        paddingHorizontal: 12,
                        paddingVertical: 6,
                        borderRadius: 16,
                        marginRight: 8,
                        marginBottom: 8,
                      }}
                    >
                      <Text
                        style={{
                          color: selected ? colors.antiText : colors.text,
                          fontSize: 12,
                        }}
                      >
                        {opt.label}
                      </Text>
                    </Pressable>
                  );
                })}
              </View>
            )}

            {f.type === 'dateRange' && (
              <DateRangeFilter
                from={values[f.key]?.from}
                to={values[f.key]?.to}
                onChange={(range) => set(f.key, range)}
              />
            )}

            {f.type === 'text' && (
              <Text>{/* wire a TextInput here if needed */}</Text>
            )}
          </View>
        ))}

        <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
          <Button mode="text" onPress={reset}>Reset</Button>
          <Button mode="contained" onPress={apply}>Apply</Button>
        </View>
      </BottomSheetScrollView>
    </BottomSheetModal>
  );
});

export default FilterSheet;
```

### 2.3 `DateRangeFilter` — new component

File: `dzzlo_oms_app/src/components/Filter/DateRangeFilter.js` (new)

Wraps `@react-native-community/datetimepicker` (already used in
`src/screens/Common/Orders/bottomsheet/dateRange.js`). Shows two pressable
date chips ("From", "To"), opens the native picker on press.

```jsx
import React, { useState } from 'react';
import { View, Pressable, Platform } from 'react-native';
import DateTimePicker from '@react-native-community/datetimepicker';
import { Text, useTheme } from 'react-native-paper';
import { DDMM } from '../../utils/Dates';

const DateRangeFilter = ({ from, to, onChange }) => {
  const { colors } = useTheme();
  const [which, setWhich] = useState(null); // 'from' | 'to' | null

  const onPick = (_, selected) => {
    if (Platform.OS === 'android') setWhich(null);
    if (!selected) return;
    if (which === 'from') onChange({ from: selected, to });
    if (which === 'to')   onChange({ from, to: selected });
  };

  const chip = (label, value, key) => (
    <Pressable
      onPress={() => setWhich(key)}
      accessibilityLabel={`Pick ${label} date`}
      style={{
        flex: 1,
        borderWidth: 1,
        borderColor: colors.border,
        borderRadius: 8,
        padding: 10,
        marginRight: key === 'from' ? 8 : 0,
        marginLeft: key === 'to' ? 8 : 0,
      }}
    >
      <Text style={{ fontSize: 11, color: colors.placeholder }}>{label}</Text>
      <Text style={{ fontSize: 14, color: colors.text }}>
        {value ? DDMM(value) : 'Any'}
      </Text>
    </Pressable>
  );

  return (
    <View>
      <View style={{ flexDirection: 'row' }}>
        {chip('From', from, 'from')}
        {chip('To', to, 'to')}
      </View>
      {which && (
        <DateTimePicker
          value={(which === 'from' ? from : to) || new Date()}
          mode="date"
          display={Platform.OS === 'ios' ? 'inline' : 'default'}
          onChange={onPick}
        />
      )}
    </View>
  );
};

export default DateRangeFilter;
```

---

## 3. Hooks

All three hooks live under a new `src/hooks/search/` folder. They wrap RTK
Query endpoints defined in the store (Section 4), add 300 ms debouncing, and
cancel stale requests when a newer query arrives.

### 3.1 `src/hooks/useDebouncedValue.js` (new, tiny util)

```js
import { useEffect, useState } from 'react';

export default function useDebouncedValue(value, delay = 300) {
  const [v, setV] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setV(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return v;
}
```

### 3.2 `src/hooks/search/useSearchVehicles.js` (new)

```js
import { useEffect } from 'react';
import useDebouncedValue from '../useDebouncedValue';
import { useLazySearch_veh_mstsQuery }
  from '../../store/apis/dzzlooms/veh_msts';

export default function useSearchVehicles({ q, custId, from, to, page, limit }) {
  const dq = useDebouncedValue(q, 300);
  const [trigger, result] = useLazySearch_veh_mstsQuery();

  useEffect(() => {
    const promise = trigger(
      { q: dq, cust_id: custId, from, to, page, limit },
      /*preferCacheValue*/ true,
    );
    return () => promise.abort(); // cancel stale request on re-run/unmount
  }, [dq, custId, from, to, page, limit, trigger]);

  return {
    data: result.data?.data || [],
    count: result.data?.count || 0,
    pagination: result.data?.pagination || {},
    isLoading: result.isFetching || result.isLoading,
    error: result.error,
  };
}
```

### 3.3 `src/hooks/search/useSearchOrders.js` (new)

Same shape, with `{ q, status, dealerId, custId, from, to, page, limit }`.
Maps `status` array -> comma-joined string at the query layer.

### 3.4 `src/hooks/search/useSearchDealers.js` (new)

Same shape, with `{ q, city, state, verified, page, limit }`.

---

## 4. Store — new RTK Query endpoints

### 4.1 Edit `src/store/apis/dzzlooms/veh_msts.js`

```js
import { api } from '../createApi';

const vehMstsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    // ... existing add / delete ...

    search_veh_msts: builder.query({
      query: ({ q, cust_id, from, to, page = 1, limit = 20 }) => ({
        url: 'veh_msts/search',
        method: 'GET',
        params: {
          q: q || undefined,
          cust_id: cust_id || undefined,
          from: from ? new Date(from).toISOString() : undefined,
          to:   to   ? new Date(to).toISOString()   : undefined,
          page, limit,
        },
      }),
      providesTags: (result) =>
        result?.data
          ? [
              ...result.data.map((r) => ({ type: 'veh_msts', id: r._id })),
              { type: 'veh_msts', id: 'SEARCH' },
            ]
          : [{ type: 'veh_msts', id: 'SEARCH' }],
    }),
  }),
  overrideExisting: true,
});

export const {
  useAdd_veh_mstsMutation,
  useDelete_veh_mstsMutation,
  useLazySearch_veh_mstsQuery,
  useSearch_veh_mstsQuery,
} = vehMstsApi;
```

### 4.2 Edit `src/store/apis/dzzlooms/order_msts.js`

Add near the other endpoints:

```js
search_order_msts: builder.query({
  query: ({ q, status = [], dealer_id, cust_id, from, to, page = 1, limit = 20 }) => ({
    url: 'order_msts/search',
    method: 'GET',
    params: {
      q: q || undefined,
      status: status.length ? status.join(',') : undefined,
      dealer_id: dealer_id || undefined,
      cust_id: cust_id || undefined,
      from: from ? new Date(from).toISOString() : undefined,
      to:   to   ? new Date(to).toISOString()   : undefined,
      page, limit,
    },
  }),
  providesTags: (result) =>
    result?.data
      ? [
          ...result.data.map((r) => ({ type: 'order_msts', id: r._id })),
          { type: 'order_msts', id: 'SEARCH' },
        ]
      : [{ type: 'order_msts', id: 'SEARCH' }],
}),
```

Export `useLazySearch_order_mstsQuery`.

### 4.3 Edit `src/store/apis/dzzlooms/dealer_msts.js`

```js
search_dealer_msts: builder.query({
  query: ({ q, city, state, verified, page = 1, limit = 20 }) => ({
    url: 'dealer_msts/search',
    method: 'GET',
    params: {
      q: q || undefined,
      city: city || undefined,
      state: state || undefined,
      verified: typeof verified === 'boolean' ? verified : undefined,
      page, limit,
    },
  }),
}),
```

Export `useLazySearch_dealer_mstsQuery`.

---

## 5. Screen changes

### 5.1 `src/screens/Customer/Vehicles/index.js`

Currently lines 112-120 maintain a local `search` state driving a client-side
`useMemo`. Add:

```jsx
import Search from '../../../components/Search/Search';
import useSearchVehicles from '../../../hooks/search/useSearchVehicles';

// Inside the component, replace the list-building useMemo when `search` is non-empty:
const [search, setSearch] = useState('');
const [page, setPage] = useState(1);

const { data: searchHits, isLoading: isSearching } = useSearchVehicles({
  q: search,
  custId: customerId,
  page,
  limit: 20,
});

// Use searchHits when a query is present; fall back to local vTrns otherwise.
const listData = search ? searchHits : veh_trns;
```

Add the SearchBar above the existing list container:

```jsx
<Suspense fallback={null}>
  <Search
    search={search}
    searchFilterFunction={setSearch}
    onDebouncedChange={(v) => { setSearch(v); setPage(1); }}
    loading={isSearching}
    placeholder="Search vehicles (reg no / route)"
  />
</Suspense>
```

### 5.2 `src/screens/Dealer/Orders/index.js`

This screen already has a rich filter state (`status_order`, `cust_id`,
`startDateFilter`, `endDateFilter`) and an `isSearchOpen` toggle that swaps
between the plain list and the filter list. Plan:

1. **Keep** the existing toggle UI and bottom sheets.
2. **Replace** the current `fetch_OFP` POST call with
   `useLazySearch_order_mstsQuery` when the user starts typing.
3. **Replace** the client-side `filteredDataSource` text filter (lines 243-321,
   specifically the `.filter(data => { const text = search.toLowerCase(); ... })`
   block) with server results.

Concretely, inside the component:

```jsx
import useSearchOrders from '../../../hooks/search/useSearchOrders';

const comp_id = currentUser?.user?.co_id;

const {
  data: searchHits,
  isLoading: isSearching,
  pagination: searchPagination,
} = useSearchOrders({
  q: search,                // already in state
  dealerId: role === 'dealer' ? comp_id : undefined,
  custId:   cust_id,
  status:   status_order,
  from:     startDateFilter,
  to:       endDateFilter,
  page:     pageF,
  limit:    pageLimitF,
});

// Replace filteredDataSource with searchHits when isSearchOpen && !!search
const listSource = isSearchOpen && search ? searchHits : filteredDataSource;
```

> Security note: passing `dealerId` / `custId` from the client is a UX
> convenience only — the API must (and, per `07_search_implementation_api.md`
> §7, does) enforce tenant scoping server-side from the auth token. Never
> rely on the client to restrict another tenant's data.

Wire the `<Search />` component into the existing search header (around line
674 where the current `<TextInput />` lives) via `onDebouncedChange={setSearch}`
so the input is debounced without removing the inline chip row.

Hook up the existing `DateRangeBottomSheet` and `StatusBottomSheet` unchanged
— they already drive `status_order`, `startDateFilter`, `endDateFilter`. The
hook re-fires when any of those change.

### 5.3 `src/screens/Customer/Dealers/index.js`

Currently lines 64-93 filter `DC.data` client-side by lowercased `dealer_name`.
Replace with server search when `search` is non-empty:

```jsx
import useSearchDealers from '../../../hooks/search/useSearchDealers';

const {
  data: searchHits,
  isLoading: isSearching,
} = useSearchDealers({
  q: search,
  page: 1,
  limit: 20,
});

const listSource = search ? searchHits : dealer_custs;
```

Replace the existing `Search` usage (already imported at line 25) with the
debounced `onDebouncedChange` prop; keep `search` state and `setSearch`
callback unchanged so everything else works.

Add autocomplete-style suggestions UI: when `search` is non-empty AND
`searchHits` is non-empty AND the user has not yet picked a result, render the
top 5 `searchHits` as a small dropdown card above the list. On press, either
navigate to that dealer or `setSearch(dealer.dealer_name)` to commit.

---

## 6. Search results UI

### 6.1 Highlight matched terms

Add a tiny helper `src/utils/highlight.js`:

```js
import React from 'react';
import { Text } from 'react-native-paper';

export function Highlight({ text, q, style, highlightStyle }) {
  if (!q || !text) return <Text style={style}>{text}</Text>;
  const parts = String(text).split(new RegExp(`(${escapeReg(q)})`, 'ig'));
  return (
    <Text style={style}>
      {parts.map((p, i) =>
        p.toLowerCase() === q.toLowerCase() ? (
          <Text key={i} style={[style, highlightStyle, { fontWeight: '700' }]}>
            {p}
          </Text>
        ) : (
          p
        ),
      )}
    </Text>
  );
}

function escapeReg(s) {
  return s.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&');
}
```

Use inside `OneOrder` row, vehicle row, dealer row:

```jsx
<Highlight text={item.veh_reg_no} q={search} style={styles.regNo} />
```

### 6.2 Empty state

Reuse `src/components/NotFound.js` (already used by Dealers screen).
Render it when `search && !isSearching && searchHits.length === 0` with a
context-specific message: "No vehicles match <q>", etc.

### 6.3 Loading skeleton

Add `src/components/Loading/SearchSkeleton.js` — render three shimmering
`View`s using `react-native-paper`'s `Surface` + `opacity` animation
(no extra dep). Show while `isSearching && !searchHits.length`.

---

## 7. Offline / poor network

- RTK Query caches responses by arg key, so a repeated search re-renders
  instantly. Keep `refetchOnMountOrArgChange: false` for search endpoints.
- When `result.error.status === 'FETCH_ERROR'` (offline), fall back to the
  existing client-side filter over the already-fetched list
  (`veh_trns` / `allOrders` / `DC.data`). This keeps search usable on the
  highway where OMS is often used.
- Show a small banner: "Offline — searching cached data" via
  `react-native-paper` `Snackbar`.

```jsx
const offline = error?.status === 'FETCH_ERROR';
const listSource = offline
  ? clientFilter(localList, search)
  : search
    ? searchHits
    : localList;
```

---

## 8. Pagination — recommendation

**Use infinite scroll** for search results, not numbered pages:

- Vehicle and dealer lists are typically long but results are narrow after a
  query (1-30 hits). Infinite scroll feels native on mobile.
- Orders search can still return many results — infinite scroll with a
  `pageLimit` of 20 matches existing `fetch_order_msts_so` behaviour
  (`pageLimit = 15` in `Dealer/Orders/index.js` line 128 and `pageLimitF`
  line 400).
- Use the `pagination.next` field returned by the API (identical shape to
  existing endpoints via `calcPagination`) to decide whether to fetch more.

Implementation: reuse the existing `onPressNext` / `onPressNextF` pattern or
an `onEndReached={() => setPage(p => p + 1)}` on the `FlashList`. RTK Query's
`merge` inside `createPaginatedQueryConfig` (already used for
`fetch_order_so_POST`) handles concatenation.

---

## 9. State management

- **Search query string + debounce**: local `useState` on each screen.
  No need for Redux — it is ephemeral UI state.
- **Filters** (status, dates, city): also local, but persisted to
  `AsyncStorage` via a tiny helper if the team wants session continuity.
- **Results**: owned entirely by RTK Query cache. No extra slice needed.
- **Selected row/highlight**: already local in each screen.

---

## 10. API call examples (axios-less, via RTK Query)

All network IO flows through RTK Query. Direct examples for clarity:

```js
// Vehicles
trigger({ q: 'KA01', cust_id: '65fa...', page: 1, limit: 20 });
// -> GET /api/v3/veh_msts/search?q=KA01&cust_id=65fa...&page=1&limit=20

// Orders
trigger({
  q: 'diesel',
  status: ['PENDING', 'PROCESSING'],
  dealer_id: comp_id,
  from: '2026-04-01',
  to:   '2026-04-11',
});
// -> GET /api/v3/order_msts/search?q=diesel&status=PENDING,PROCESSING&dealer_id=...&from=...&to=...

// Dealers
trigger({ q: 'HP', city: 'bengaluru', verified: true });
// -> GET /api/v3/dealer_msts/search?q=HP&city=bengaluru&verified=true
```

The API-key header and auth token are already injected by
`src/store/apis/createApi.js` `baseQuery` (no per-call wiring needed).

---

## 11. Navigation — inline filter, no dedicated screen

**Recommendation**: filter inline on the existing list screen (like the
Dealer Orders screen already does via `isSearchOpen`). Reasons:

- Keeps mental model consistent: search IS the list, with filters applied.
- Avoids navigation thrash on slow devices.
- Maintains existing nav structure (drawer + tabs); no new route registration
  in `src/navigation/`.
- Users can swipe back to clear filters instantly.

For the Customer Dealers screen, keep the flat list but add a small
"suggestions" popover above the first row while typing — this gives an
autocomplete feel without a new screen.

---

## 12. Accessibility

- Every `Pressable` in the new components has `accessibilityLabel` and, for
  toggles, `accessibilityState={{ checked: selected }}`.
- `TextInput` has `accessibilityLabel={placeholder}`.
- Colors draw from `useTheme().colors` so high-contrast / dark mode work
  automatically.
- Hit slop of 10+ on close/clear buttons (matches the existing sheet style).
- `returnKeyType="search"` on the search input so the OS keyboard shows the
  Search action button.
- Announce result count for screen readers via `accessibilityLiveRegion="polite"`
  on a hidden `Text` beneath the search bar:
  `"{count} results"`.

---

## 13. Files to create / edit (quick index)

Create:
- `dzzlo_oms_app/src/components/Filter/FilterSheet.js`
- `dzzlo_oms_app/src/components/Filter/DateRangeFilter.js`
- `dzzlo_oms_app/src/components/Loading/SearchSkeleton.js`
- `dzzlo_oms_app/src/hooks/useDebouncedValue.js`
- `dzzlo_oms_app/src/hooks/search/useSearchVehicles.js`
- `dzzlo_oms_app/src/hooks/search/useSearchOrders.js`
- `dzzlo_oms_app/src/hooks/search/useSearchDealers.js`
- `dzzlo_oms_app/src/utils/highlight.js`

Edit:
- `dzzlo_oms_app/src/components/Search/Search.js` (add debounce / clear / loading)
- `dzzlo_oms_app/src/store/apis/dzzlooms/veh_msts.js`
- `dzzlo_oms_app/src/store/apis/dzzlooms/order_msts.js`
- `dzzlo_oms_app/src/store/apis/dzzlooms/dealer_msts.js`
- `dzzlo_oms_app/src/screens/Customer/Vehicles/index.js`
- `dzzlo_oms_app/src/screens/Dealer/Orders/index.js`
- `dzzlo_oms_app/src/screens/Customer/Dealers/index.js`

---

## 14. Estimated effort

| Work item                                           | Days |
|-----------------------------------------------------|------|
| SearchBar extension + debounce hook                 | 0.5  |
| FilterSheet + DateRangeFilter                       | 1.0  |
| RTK Query endpoints (3 entities)                    | 0.5  |
| useSearchVehicles / useSearchOrders / useSearchDealers | 0.5  |
| Screen integration — Vehicles                       | 0.5  |
| Screen integration — Orders (complex, many states)  | 1.5  |
| Screen integration — Dealers + autocomplete popover | 1.0  |
| Offline fallback + highlight + skeleton             | 0.5  |
| QA pass on iOS/Android                              | 0.5  |
| **Total**                                           | **~6.5 engineer-days** |
