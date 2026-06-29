# Quick Wins — Zero-Risk, Immediate Impact

> Tiny changes that improve the codebase with zero chance of breaking anything.
> Each task is independent. Do them in any order. Verify API + App after each.

---

## QW-1: Add `.lean()` to all read queries (API)

**Size:** XS (find-and-replace pattern)
**Files:** All service files in `api_v3/services/`, `helpers/advancedResults.js`, `helpers/auth.js`

**What:** Add `.lean()` to every `find()`, `findOne()`, `findById()` call that doesn't need `.save()` or Mongoose document methods afterward.

**Why:** `.lean()` returns plain JS objects instead of full Mongoose documents. 3-5x faster deserialization, lower memory. This is free performance — no behavior change, no API contract change.

**How to verify:**
- API: Hit any GET endpoint before/after. Response shape is identical.
- App: No change needed. App receives the same JSON.

**Discussion:** Mongoose documents carry change tracking, validators, and methods. For read-only queries (which is 90%+ of your reads), you never use any of that. The plain object is what gets serialized to JSON anyway.

**What Mongoose documents carry (and when you need them):**

1. **Change tracking** — Mongoose watches every field you modify so `.save()` only sends the diff to MongoDB. Example: `order.status = 'delivered'; await order.save()` sends `{$set: {status: 'delivered'}}`, not the entire document.

2. **Validators** — Schema-level rules that run on `.save()`. This project uses them in `users.js` (phone: 10-digit regex), `cust_msts.js` (email regex), `contact_us.js` (role enum). These only matter when writing data.

3. **Instance methods** — Custom functions on documents. This project uses them heavily in `users.js`: `matchPassword()`, `getSignedJwtToken()`, `getOTPToken()`, `matchOTP()`. Also `order_msts.js` has `getOTPToken()`.

**The rule:**
- Reading data to send as JSON? → use `.lean()` (skip all overhead, 3-5x faster)
- Modifying and saving? Using `matchPassword()` or `getSignedJwtToken()`? → don't use `.lean()`

**Current state in this project:**
- `api_v3/services/` already uses `.lean()` systematically — good.
- `api_v1/` and `api_v2/` mostly return full Mongoose documents — opportunity for improvement.
- `helpers/advancedResults.js` already uses `.lean()` — good.

**Does this create MongoDB dependency?**
The project is already deeply committed to MongoDB — Mongoose schemas, pre/post hooks, aggregation pipelines, sub-documents, Mixed types, multiple DB connections. This is the right call: the data model (orders with nested line items, dealers with products/tanks/nozzles) fits documents naturally. Adding `.lean()` doesn't increase lock-in — it just uses what's already there more efficiently.

---

## QW-2: Share `loggedInUser` across middleware (API)

**Size:** XS (~5 lines changed)
**File:** `helpers/middlewares.js`

**What:** In `logging()` middleware, attach the result of `getUserFromToken()` to `req.loggedInUser`. In `check_user_company_status()`, reuse `req.loggedInUser` instead of calling `getUserFromToken()` again.

```js
// In logging():
const loggedInUser = await getUserFromToken(req.headers);
req.loggedInUser = loggedInUser; // ADD THIS LINE

// In check_user_company_status():
const loggedInUser = req.loggedInUser || await getUserFromToken(req.headers);
```

**Why:** Every request currently calls `getUserFromToken()` **twice** — once in logging, once in company status check. Each call does JWT decode + MongoDB query. This eliminates ~5-10ms and 1 DB call per request.

**How to verify:**
- API: Any authenticated request. Same response, one fewer DB call.
- App: No change needed.

**Discussion:** This is the simplest possible optimization. Zero new dependencies. The user object is the same in both middleware. We're just avoiding fetching it twice.

---

## QW-3: Add `keepUnusedDataFor` to RTK Query (App)

**Size:** XS (1 line)
**File:** `src/store/apis/createApi.js`

**What:** Add `keepUnusedDataFor: 300` (5 minutes) to the `createApi()` config.

**Why:** Currently, when a user navigates away from a screen and comes back, RTK Query refetches the data. With `keepUnusedDataFor`, the cached data stays alive for 5 minutes. Screens that are revisited within that window show data instantly.

**How to verify:**
- App: Navigate to order list, go to another screen, come back within 5 min. Should show data instantly (no loading spinner).
- API: You'll see fewer duplicate requests in logs.

**Discussion:**

RTK Query already caches data while a component is mounted. `keepUnusedDataFor` extends that cache to survive unmounting. 5 minutes is conservative — screens revisited within that window show data instantly (no spinner).

**This does NOT cause stale data.** All three order screens (Common, Dealer, Customer) already call `onRefresh()` with `refresh: true` inside a `useIsFocused()` effect — this makes a fresh API call every time the user navigates back, regardless of cache TTL. Pull-to-refresh on the FlatList also lets the user manually refetch. `keepUnusedDataFor` only controls how long unsubscribed cache entries stay in memory; it never blocks a new fetch.

**Freshness audit across order screens:**

| Screen | Focus refetch | Pull-to-refresh | Dep array issue |
|---|---|---|---|
| `Common/Orders/index.js:445` | `onRefresh()` on focus | Yes (line 569) | Missing `onRefresh` in deps |
| `Dealer/Orders/index.js:506` | `onRefresh()` on focus | Yes (line 623) | Missing `onRefresh`, `isSearchOpen` in deps; also calls both `DispatchOrder()` and `onRefresh()` when search is open (redundant) |
| `Customer/Orders/index.js:446` | `onRefresh()` on focus | Yes (line 619) | Missing `onRefresh` in deps |

**Without sockets**, the current focus-based refetch + pull-to-refresh pattern is the correct approach. The missing dependencies in `useEffect` should be fixed to avoid stale closures if `comp_id` or `role` change between navigations.

---

## QW-4: Add response compression middleware (API)

**Size:** XS (install + 5 lines)
**Files:** `dzzlo_oms.js`

**What:**
```bash
yarn add compression
```
```js
const compression = require('compression');
app.use(compression({ threshold: 1024 }));
```

**Why:** JSON compresses 70-85%. A 100KB order list response becomes ~15-20KB. Significant on mobile data connections. Express has zero compression by default.

**How to verify:**
- API: `curl -H "Accept-Encoding: gzip" <endpoint> -v` — check for `Content-Encoding: gzip` header.
- App: No change needed. `fetch` handles decompression automatically.

**Discussion:** This is a standard Express best practice that's been missing. The `threshold: 1024` means only responses >1KB get compressed — small responses aren't worth the CPU.

**Why not binary formats (MessagePack, Protobuf) instead of JSON?**
- Binary JSON (e.g., MessagePack) is ~35% smaller than raw JSON, but after compression (gzip/brotli) both converge to nearly the same size (~85% reduction). The difference is ~1KB on a 100KB payload.
- Binary formats add complexity: extra encode/decode libraries on both client and server, can't inspect payloads in browser devtools, opaque blobs make debugging harder.
- `URLSearchParams` (query string format) is the lightest option for flat key-value data — zero parsing overhead, built into every runtime — but doesn't support nesting or typed values.
- **Verdict:** JSON + compression is the industry standard because it gives 85%+ size reduction with zero client-side changes. Binary formats only win meaningfully at extreme throughput (millions of req/sec) or severely bandwidth-constrained environments (IoT).

---

## QW-5: Fix `express.json()` missing size limit (API)

**Size:** XS (1 line change)
**File:** `dzzlo_oms.js`

**What:** Change `app.use(express.json())` to `app.use(express.json({ limit: '1mb' }))`.

**Why:** Without a limit, an attacker can send a 100MB JSON body, consuming all server memory. The default is 100KB in newer Express versions, but explicitly setting it is defense in depth.

**How to verify:**
- API: Send a request with a body larger than 1MB. Should get 413 Payload Too Large.
- App: Normal requests are well under 1MB. No impact.

**Discussion:** This is a one-line hardening change. No real-world request to your API should ever be >1MB.

---

## QW-6: Add `trust proxy` setting (API)

**Size:** XS (1 line)
**File:** `dzzlo_oms.js`

**What:** Add `app.set('trust proxy', 1)` before any middleware.

**Why:** Your API runs behind an ALB (or Nginx). Without `trust proxy`, `req.ip` returns the ALB's IP, not the client's real IP. This breaks rate limiting (everyone looks like the same IP) and logging (all logs show the proxy IP).

**How to verify:**
- API: Check `req.ip` in logging middleware. Should now show real client IPs.
- App: No change needed.

**Discussion:** Required prerequisite for rate limiting to work correctly. Without this, rate limiting by IP is useless behind a proxy.

---

## QW-7: Wrap `JSON.parse(req.headers.meta)` in try/catch (API)

**Size:** XS (3 lines)
**File:** `helpers/middlewares.js` (logging middleware)

**What:** The `meta` header is parsed with `JSON.parse()` without error handling. If the app sends malformed JSON, the entire request crashes.

```js
// BEFORE
const metaData = req.headers.meta ? JSON.parse(req.headers.meta) : null;

// AFTER
let metaData = null;
try { metaData = req.headers.meta ? JSON.parse(req.headers.meta) : null; } catch {}
```

**Why:** Defensive coding. A single malformed header shouldn't crash the request. This is especially important during app updates where the meta format might change.

**How to verify:**
- API: Send a request with `meta: "not-json"`. Should not crash.
- App: No change needed.

---

## Summary

| Task | Size | Impact | Risk |
|------|------|--------|------|
| QW-1: `.lean()` on reads | XS | 3-5x faster query deserialization | Zero |
| QW-2: Share loggedInUser | XS | -1 DB call per request | Zero |
| QW-3: `keepUnusedDataFor` | XS | Instant screen revisits | Zero |
| QW-4: Response compression | XS | 70-85% bandwidth savings | Zero |
| QW-5: JSON body size limit | XS | Prevent memory exhaustion | Zero |
| QW-6: `trust proxy` | XS | Correct client IP detection | Zero |
| QW-7: Safe meta parse | XS | Prevent crash on bad header | Zero |
