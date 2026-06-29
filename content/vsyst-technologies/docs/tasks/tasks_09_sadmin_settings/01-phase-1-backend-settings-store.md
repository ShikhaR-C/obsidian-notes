# Phase 1 — Backend settings store (v3)

**Repo:** `dzzlo_oms_api` — branch from the **Phase 0 merged tree** (`v1.5.4` + `slave`; see overview §5b). Do not branch from raw `slave` (it lacks the v1.5.4 mainline work).
**Goal:** A superadmin-writable, app-readable settings document with a cached server-side reader. No existing behavior changes — nothing consumes it yet (Phases 2–4 do). Ship-able alone.

> This phase is a near-direct generalization of `api_v3/controllers/sadmin/diesel_limit.js` + `helpers/dieselQtyLimit.js` (from the merged-in slave commits). Read those two files first — the controller/cache code below is the same shape with an allow-list and a multi-key `$set`.

---

## 1. Storage — `counters` doc `app_settings`

Reuse the proven key-value pattern: `units`/`hsncodes` (`api_v3/controllers/sadmin/units_hsns.js`) and `diesel_limit` (`helpers/dieselQtyLimit.js` → `{ doc_name: "diesel_limit", data: {...} }`, present after the Phase 0 merge) all live this way. No new model, no migration. **Use a separate `app_settings` doc** — do not co-mingle with the existing `diesel_limit` doc (overview decision 6).

The doc:

```js
// counters collection
{ doc_name: "app_settings", data: { /* keys from overview §4, all optional */ } }
```

Record it in the model doc comment only — `models/counters.js`:

```js
// doc_name "app_settings": { data: { min_app_version, update_msg_ios, update_msg_android,
//   maintenance_mode, maintenance_msg, force_update, page_size, api_timeout_ms,
//   cache_keep_unused_s, max_cached_items, feature_flags, diesel_limit } } — superadmin-managed app config
```

---

## 2. Endpoints

### 2a. Superadmin write + admin read — `api_v3/controllers/sadmin/settings.js` (new)

Mirror `units_hsns.js` style (`asyncHandler`, `counters.findOneAndUpdate`, `ErrRes`).

```js
const ErrRes = require("../../../helpers/ErrorResponse");
const asyncHandler = require("../../../helpers/async");
const counters = require("../../../models/counters");
const { bustSettingsCache } = require("../../../helpers/settingsCache");

// Allow-list: only these keys can be written. Unknown keys are rejected (no schema-less sprawl).
const ALLOWED = new Set([
  "min_app_version", "update_msg_ios", "update_msg_android",
  "maintenance_mode", "maintenance_msg", "force_update",
  "page_size", "api_timeout_ms", "cache_keep_unused_s",
  "max_cached_items", "feature_flags", "diesel_limit",
]);

exports.get_settings = asyncHandler(async (_req, res) => {
  const doc = await counters.findOne({ doc_name: "app_settings" }).select("data").lean();
  res.status(200).json({ success: true, data: doc?.data ?? {} });
});

exports.update_settings = asyncHandler(async (req, res, next) => {
  const body = req.body || {};
  const keys = Object.keys(body);
  if (!keys.length) return next(new ErrRes(`No settings provided`, 400));
  for (const k of keys) {
    if (!ALLOWED.has(k)) return next(new ErrRes(`Unknown setting: ${k}`, 400));
  }

  // Guard: min_app_version may only be RAISED above the compiled floor (overview decision 4).
  if (Object.prototype.hasOwnProperty.call(body, "min_app_version")) {
    const v = Number(body.min_app_version);
    const FLOOR = Number(require("../../../helpers/middlewares").COMPILED_MIN_VERSION); // see Phase 2 §1
    if (!Number.isFinite(v) || v < FLOOR) {
      return next(new ErrRes(`min_app_version must be a number >= compiled floor ${FLOOR}`, 400));
    }
  }

  // $set each provided key under data.* (partial update; never clobbers other keys).
  const $set = {};
  for (const k of keys) $set[`data.${k}`] = body[k];

  const doc = await counters.findOneAndUpdate(
    { doc_name: "app_settings" },
    { $set },
    { upsert: true, returnDocument: "after", strict: false },
  );
  bustSettingsCache(); // refresh the in-process cache immediately
  res.status(200).json({ success: true, data: doc?.data ?? {} });
});
```

Mount in `api_v3/routes/sadmin/index.js` (these inherit the existing superadmin protection at the sadmin mount):

```js
const { get_settings, update_settings } = require("../../controllers/sadmin/settings");
router.get("/settings", get_settings);
router.put("/settings", update_settings);
```

### 2b. App read (authenticated, NOT superadmin) — `api_v3/controllers/settings.js` (new)

**Critical (overview decision 3):** this must live *outside* the `/sadmin` guard so any dealer/customer app can read it.

```js
const asyncHandler = require("../../helpers/async");
const { getAppSettings } = require("../../helpers/settingsCache");

exports.get_app_settings = asyncHandler(async (_req, res) => {
  const data = await getAppSettings(); // cached
  res.status(200).json({ success: true, data });
});
```

Mount under the v3 collections router (same protection level as other app data routes — `protect`, but no sadmin authorize). Add `api_v3/routes/collections/settings.js`:

```js
const router = require("express").Router();
const { get_app_settings } = require("../../controllers/settings");
const { refDataCache } = require("../../../helpers/cacheMiddleware");
router.get("/", refDataCache(300), get_app_settings); // 5-min edge cache like other ref data
module.exports = router;
```

…and register it in the v3 router index alongside `cust_msts`, `dealer_msts`, etc.:

```js
router.use("/settings", require("./collections/settings"));
```

> Confirm the v3 router applies `protect` (JWT) but not `authorize("superadmin")` at this mount — match how `prod_msts`/`veh_msts` are mounted (reference data readable by all authed users).

---

## 3. Cached server-side reader — `helpers/settingsCache.js` (new)

The version middleware (Phase 2) runs on **every request** — it must never do a per-request DB read. Provide an in-process cached snapshot with a short TTL, same spirit as the existing `refDataCache`/`userCache`.

```js
const counters = require("../models/counters");

let _cache = null;
let _expiresAt = 0;
const TTL_MS = 60 * 1000; // 60s; bust on write for immediacy

async function getAppSettings() {
  const now = Date.now();
  if (_cache && now < _expiresAt) return _cache;
  const doc = await counters.findOne({ doc_name: "app_settings" }).select("data").lean();
  _cache = doc?.data ?? {};
  _expiresAt = now + TTL_MS;
  return _cache;
}

function bustSettingsCache() {
  _cache = null;
  _expiresAt = 0;
}

module.exports = { getAppSettings, bustSettingsCache };
```

> `Date.now()` is fine in app code (the no-`Date.now` rule applies only to Workflow scripts, not the API). If the API runs multiple worker processes, each holds its own cache — a write busts only the handling worker; others expire within `TTL_MS`. 60s of cross-worker staleness is acceptable for config (same tradeoff the existing 30s `userCache` makes).

---

## 4. Phase 1 acceptance

- [ ] `PUT /api/v3/sadmin/settings` with `{ "page_size": 25 }` as superadmin → `200`, doc upserted, other keys untouched.
- [ ] `PUT /api/v3/sadmin/settings` with `{ "bogus": 1 }` → `400 Unknown setting: bogus`.
- [ ] `PUT /api/v3/sadmin/settings` as a **non-superadmin** token → blocked by existing `/sadmin` guard (403/401).
- [ ] `GET /api/v3/settings` with a **dealer** token → `200` with current `data` (proves it's outside the sadmin guard).
- [ ] `GET /api/v3/settings` with **no/invalid JWT** → `401` (still requires auth).
- [ ] Two sequential `PUT`s (`{page_size:25}` then `{api_timeout_ms:8000}`) → both keys present (partial `$set`, no clobber).
- [ ] After a `PUT`, an immediate `GET /api/v3/settings` reflects the change (cache busted on write).
- [ ] No existing endpoint behavior changes (settings doc exists but is consumed by nothing yet).
