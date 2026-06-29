# 02 — Offline Caching Strategy (Workbox Runtime Caching + RTK Query)

> Phase 2 of the PWA initiative. Adds runtime caching of API responses, fonts, and other cross-origin assets so the app stays useful when offline or on flaky networks.
> **Depends on Phase 1** (`01-pwa-base-setup.md`) being merged.

---

## TL;DR

Phase 1 caches the **app shell** (HTML/JS/CSS/icons) so the UI loads offline. Phase 2 caches the **data** so users see the last-known list of customers, masters, and transactions when there's no signal — instead of empty screens.

The tricky part is not "how do I cache" — Workbox handles that with one config block. The tricky part is **multi-user safety** (cached data from User A must not be visible to User B who logs in on the same device) and **cache freshness** (technicians must not act on 3-day-old company data thinking it's current).

End state: Workbox caches `GET` API responses with a `NetworkFirst` strategy, RTK Query keeps doing its tag-based invalidation as before (Workbox is invisible to it), and the auth slice clears Workbox caches on logout.

Estimated effort: **2 days** including auth/multi-user testing.

---

## 1. Current State (after Phase 1)

| Concern         | State                                                                                                           |
| --------------- | --------------------------------------------------------------------------------------------------------------- |
| Service worker  | Registered, precaching app shell (`sw.js` from Phase 1)                                                         |
| Runtime caching | _none_ — Workbox `runtimeCaching` array is empty                                                                |
| RTK Query       | Single `createApi` in `src/store/apis/createApi.js`. Tag-based invalidation. Token from `localStorage.userData` |
| Auth flow       | Login stores `userData` in localStorage. Logout clears localStorage but **does not clear browser caches**       |
| API origin      | TBD — see Decision D1 in `00-overview.md`                                                                       |

---

## 2. Caching Strategies — When to Use What

Workbox ships five named strategies. We only need three.

| Strategy               | Behavior                                                            | Use For                                                          |
| ---------------------- | ------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `CacheFirst`           | Return cache; fetch only on miss                                    | Immutable assets (fonts, hashed JS — though precache handles JS) |
| `NetworkFirst`         | Try network with timeout; fall back to cache on failure             | API responses (we want fresh data when online)                   |
| `StaleWhileRevalidate` | Return cache immediately; fetch network in background; update cache | Optional: master data that rarely changes (palettes, dropdowns)  |
| `NetworkOnly`          | Always go to network; no cache                                      | Mutations, login, anything we must not cache                     |
| `CacheOnly`            | Cache only; no network                                              | Not used                                                         |

For an inspection app where stale data is **dangerous** (a technician might log a meter read against a customer that was reassigned yesterday), the default for API responses is `NetworkFirst` with a short timeout.

---

## 3. Implementation

### 3.1 Update `vite.config.js` — add `runtimeCaching`

Replace the `workbox` block from Phase 1 with:

```js
workbox: {
  globPatterns: ["**/*.{js,css,html,ico,png,svg,woff,woff2}"],
  navigateFallback: "/index.html",
  navigateFallbackDenylist: [/^\/api\//, /^\/_/],
  cleanupOutdatedCaches: true,
  runtimeCaching: [
    // 1. Google Fonts — immutable, cache aggressively
    {
      urlPattern: /^https:\/\/fonts\.(googleapis|gstatic)\.com\/.*/i,
      handler: "CacheFirst",
      options: {
        cacheName: "google-fonts",
        expiration: { maxEntries: 20, maxAgeSeconds: 60 * 60 * 24 * 365 },
        cacheableResponse: { statuses: [0, 200] },
      },
    },
    // 2. API GET requests — network-first with offline fallback
    //    TODO D1: replace API_ORIGIN with the real prod/staging origin(s)
    {
      urlPattern: ({ url, request }) =>
        request.method === "GET" &&
        (url.origin === "https://API_ORIGIN_PLACEHOLDER" ||
          url.pathname.startsWith("/api/")),
      handler: "NetworkFirst",
      options: {
        cacheName: "api-cache",
        networkTimeoutSeconds: 5,
        expiration: {
          maxEntries: 200,
          maxAgeSeconds: 60 * 60 * 24,            // 24 hours hard ceiling
        },
        cacheableResponse: { statuses: [200] },   // never cache 4xx/5xx
      },
    },
    // 3. Images served from API (avatars, attachments)
    //    Tighter expiration; use stale-while-revalidate for snappy UX
    {
      urlPattern: ({ url, request }) =>
        request.destination === "image" &&
        url.origin !== self.location.origin,
      handler: "StaleWhileRevalidate",
      options: {
        cacheName: "external-images",
        expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 7 },
      },
    },
  ],
},
```

**Why `networkTimeoutSeconds: 5`:** if the user is online but the network is slow, we'd rather serve cached data after 5 seconds than spin forever. If the user is fully offline, the fetch fails immediately and the cache is hit instantly.

**Why `cacheableResponse: { statuses: [200] }` on the API rule:** we must not cache 401/403/500. Caching a 401 would log the user out repeatedly when they come back online with a valid token.

### 3.2 Decision D2 — multi-user cache safety

Decision matrix from `00-overview.md`:

| Option                        | Tradeoff                                                                                                      |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------- |
| (a) Skip API caching entirely | Safest. No cross-user leakage risk. **But:** zero offline data.                                               |
| (b) Cache + clear on logout   | Recommended. Caches survive login (good for repeat-user case), wiped on explicit logout.                      |
| (c) Cache only `GET` masters  | Compromise. Reference data (`useDealerData`) is low-sensitivity. Transactions (with customer PII) skip cache. |

**Recommendation: (b).** Implement by clearing Workbox caches inside the existing logout thunk.

#### 3.2.1 Add cache clearing to logout

In `src/store/slices/auth.js` (or wherever `logoutUser` is defined), after the existing localStorage cleanup:

```js
async function clearPwaCaches() {
  if (!("caches" in window)) return;
  const names = await caches.keys();
  await Promise.all(
    names
      .filter(
        (n) => n.startsWith("api-cache") || n.startsWith("external-images"),
      )
      .map((n) => caches.delete(n)),
  );
}

// inside logoutUser thunk, after AsyncStorage / localStorage removal:
await clearPwaCaches();
```

**Do not delete the `workbox-precache-*` cache.** That's the app shell — clearing it forces a re-download on next launch and breaks the offline experience for the next user.

#### 3.2.2 Forced cache clear on user-id change

If a user logs in as a different account without explicitly logging out (e.g. token swap from URL, deep link), watch for `userData.userId` changes in the auth slice and call `clearPwaCaches()` when it differs from the previous value. This is belt-and-suspenders for the (b) strategy.

### 3.3 RTK Query interaction — what changes, what doesn't

**RTK Query is not aware of the service worker.** `fetch` calls go through the SW transparently, so the cached response is served back to RTK Query as if it were a normal network response.

This means:

- ✅ Tag-based `invalidatesTags` / `providesTags` keep working
- ✅ Optimistic updates keep working
- ✅ `useFetch_*` hooks behave identically online
- ⚠️ **Offline + tag invalidation:** if a mutation is attempted offline, it will fail (Phase 4 handles this). The optimistic update won't roll back to "fresh" data because there is no fresh data to fetch.
- ⚠️ **Cache headers:** RTK Query's own RAM cache (`keepUnusedDataFor`) is independent of Workbox. A response served from Workbox is still subject to RTK Query's TTL.

### 3.4 What must NOT be cached

Add explicit `NetworkOnly` rules for these (or rely on the `request.method === "GET"` filter in the API rule, which already excludes them):

- `POST`, `PUT`, `PATCH`, `DELETE` requests — Workbox does this by default
- `/auth/login`, `/auth/otp`, `/auth/refresh` — never cache auth flows
- Any endpoint returning real-time data (sockets are excluded automatically; they don't go through fetch)

If you want belt-and-suspenders, add:

```js
{
  urlPattern: ({ url }) => url.pathname.startsWith("/auth/"),
  handler: "NetworkOnly",
},
```

### 3.5 Cache size budgets

Workbox enforces `maxEntries` per cache, evicting LRU. Set conservatively:

| Cache              | Max Entries | Max Age         | Rationale                                                      |
| ------------------ | ----------- | --------------- | -------------------------------------------------------------- |
| `workbox-precache` | unbounded   | until SW update | App shell; a few MB max                                        |
| `api-cache`        | 200         | 24 hours        | Last-seen list pages and details. ~50 KB each → ~10 MB ceiling |
| `google-fonts`     | 20          | 1 year          | Tiny — but cap it anyway                                       |
| `external-images`  | 100         | 7 days          | Avatars, attachment thumbnails                                 |

If users start hitting the 200-entry limit and missing important cached data, increase to 500 — but watch device storage usage on low-end Android.

### 3.6 Offline indicator (UX)

When the SW serves cached responses or fetches fail, the user should know. Add a thin offline banner:

```jsx
// src/components/OfflineBanner.js
import { useEffect, useState } from "react";

export function OfflineBanner() {
  const [online, setOnline] = useState(navigator.onLine);
  useEffect(() => {
    const on = () => setOnline(true);
    const off = () => setOnline(false);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => {
      window.removeEventListener("online", on);
      window.removeEventListener("offline", off);
    };
  }, []);
  if (online) return null;
  return (
    <div
      role="status"
      style={
        {
          /* inline styles per CLAUDE.md */
        }
      }
    >
      You are offline — showing last-known data.
    </div>
  );
}
```

Render it in `App.js` near the top of the layout. Style with `useTheme()` per project conventions.

`navigator.onLine` is unreliable (it reflects the OS-level network connection, not whether your API is reachable). For a more accurate indicator, also dispatch an event from the RTK Query `baseQuery` when a fetch fails. Phase 4 will need this anyway.

---

## 4. Testing Checklist

### 4.1 Online behavior unchanged

- [ ] Login, dashboard, masters all load and behave identically to pre-PWA build
- [ ] RTK Query tag invalidation still works (mutate something, see list refresh)
- [ ] No new console errors

### 4.2 Offline behavior

- [ ] Load the app online; navigate around to populate caches
- [ ] DevTools → Network → Offline
- [ ] Reload the app — app shell loads (Phase 1)
- [ ] Navigate to a page visited online — **cached API data is shown** (this phase)
- [ ] Navigate to a page never visited online — graceful empty state (no infinite spinner)
- [ ] Offline indicator banner is visible

### 4.3 Slow network

- [ ] DevTools → Network → "Slow 3G"
- [ ] Reload: cached data shows within `networkTimeoutSeconds`
- [ ] When network returns, fresh data replaces cached data on next refetch

### 4.4 Multi-user safety (Decision D2 verification)

- [ ] Log in as User A; navigate to populate cache
- [ ] Log out
- [ ] DevTools → Application → Cache Storage → `api-cache` is **empty**
- [ ] Log in as User B → no User A data visible anywhere

### 4.5 Auth edge cases

- [ ] Token expires while offline → next online action triggers re-auth flow (no cached 401s)
- [ ] Login response is **never** cached (DevTools → Cache Storage shows no `/auth/*` entries)
- [ ] Logout response is **never** cached

### 4.6 Cache size

- [ ] Load 200+ different list/detail pages
- [ ] DevTools shows `api-cache` capped at 200 entries (oldest evicted)

---

## 5. Rollback

To remove runtime caching while keeping Phase 1's installable behavior:

1. Remove the `runtimeCaching` array from `vite.config.js`
2. Remove the `clearPwaCaches()` call from logout
3. Remove `<OfflineBanner />` from `App.js`
4. Rebuild and deploy
5. Existing users get the new SW on next visit; old caches are cleaned up by `cleanupOutdatedCaches: true`

---

## 6. Known Limitations

- **POST/PUT/DELETE offline:** these will fail. Phase 4 (background sync) addresses this.
- **`navigator.onLine` lies:** reports `true` if any network connection exists, even captive portals or routers without internet. The offline banner can show a false negative.
- **Cache poisoning on logout-skip:** if a user closes the tab without logging out, caches persist for the next person who opens the browser. The 24h max-age limits the blast radius. For shared-device scenarios, prefer Decision D2(a) — no API caching.
- **iOS Safari storage quotas:** ~50 MB before eviction without explicit user permission. Watch this for image-heavy inspections.

---

## 7. Acceptance Criteria

- [ ] Phase 1 acceptance criteria still pass
- [ ] Offline navigation to previously-visited pages shows cached data
- [ ] Logout clears `api-cache` and `external-images`; `workbox-precache` survives
- [ ] No 4xx/5xx responses are cached
- [ ] No `/auth/*` responses are cached
- [ ] Cache sizes stay within budget after a 30-min usage session
- [ ] Lighthouse PWA audit still passes

---

## 8. References

- Workbox runtime caching: https://developer.chrome.com/docs/workbox/caching-strategies-overview/
- `vite-plugin-pwa` runtime caching: https://vite-pwa-org.netlify.app/workbox/generate-sw.html#runtimecaching
- `dip-web/src/store/apis/createApi.js` — RTK Query base
- `dip-web/src/store/slices/auth.js` — logout thunk (cache-clear hook target)
- `01-pwa-base-setup.md` — prerequisite phase
- `00-overview.md` — decisions D1, D2
