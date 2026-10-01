# Phase 2 — Version gate & maintenance, driven by settings

**Repo:** `dzzlo_oms_api` (Phase 0 merged tree, on top of Phase 1)
**Goal:** Make the **app version floor**, the **store-update messages**, and a **maintenance switch** superadmin-controllable — the single highest-value lever, because with no OTA ([[app-ota-and-version-gating]]) this middleware is the only release-free control over fielded apps. The compiled-in `1.68` stays as a hard floor so a bad write can never lock everyone out or let everyone in.

> **Order-sensitive — read before deploying.** The version middleware runs on *every* request. It must (a) read from the Phase 1 **cached** `settingsCache` (never a per-request DB query) and (b) fall back to the compiled constant if settings are absent. Deploy this middleware *before* anyone sets `min_app_version`; seed the `app_settings` doc; only then raise the floor.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). ⬜ Not built on master — the gate is still `Number(1.68)` with the test-build exemption and two literal store messages (`helpers/middlewares.js:112-141`, mounted `dzzlo_oms.js:75`), pinned by `test/api_v3/features/version_gate/index.test.js`; 0 of 8 acceptance items hold. An unmerged alternative sits on API PR #34 (`387072a`, OPEN, CONFLICTING, untouched since 2026-06-29): a `version_gate` counters doc (`minVersion`, `latestVersion`, `testVersion`) and soft-update headers, but no compiled-floor guard, no maintenance switch, no custom messages and no tests — `X-APP-5`. dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

---

## 1. Make the compiled floor explicit — `helpers/middlewares.js`

**Status (2026-10-01):** ⬜ `COMPILED_MIN_VERSION` is absent (git grep: 0); PR #34 names its fallback `DEFAULT_MIN_VERSION = 1.68` but accepts a write below it.

Today (`slave`, line ~123): `const allowedVersion = Number(1.68);`. Promote it to a named export so the Phase 1 write-guard (`update_settings`) can reference it as the minimum settable floor.

At module top:

```js
// Compiled hard floor. settings.min_app_version may RAISE this but never lower it.
exports.COMPILED_MIN_VERSION = 1.68;
```

---

## 2. Read floor + messages from settings — `check_user_version` (~line 112)

**Status (2026-10-01):** ⬜ unchanged on master (`helpers/middlewares.js:112-141`); PR #34 reads a cached doc here instead (unmerged). Both compare `Number(version)`, which breaks on a three-digit minor — `T09-N4` in the overview.

Replace the hardcoded `allowedVersion` and the two literal store messages with settings-backed values, each falling back to the current compiled behavior.

```js
const { getAppSettings } = require("./settingsCache");

exports.check_user_version = () => async (req, res, next) => {
  let meta = null;
  try {
    meta = req.headers.meta ? JSON.parse(req.headers.meta) : null;
  } catch {}
  const version = !!meta && !!meta.version ? meta.version : null;
  const deviceBrand = !!meta && !!meta.deviceBrand ? meta.deviceBrand : null;

  let settings = {};
  try {
    settings = await getAppSettings(); // cached; never throws on cache hit
  } catch {
    settings = {}; // DB blip → fall back to compiled behavior, never 403 the fleet
  }

  // Floor: settings may only RAISE above the compiled constant (defense-in-depth;
  // update_settings already rejects lower writes).
  const settable = Number(settings.min_app_version);
  const allowedVersion =
    Number.isFinite(settable) && settable >= exports.COMPILED_MIN_VERSION
      ? settable
      : exports.COMPILED_MIN_VERSION;

  const testVersion = "1.510";
  const isntTestv = `${version}` !== testVersion;

  const message = "This version of DZZLO-OMS is too old to function.";
  const conditionMSG = "Please update your app from";
  const iosMsg = settings.update_msg_ios || `${message} ${conditionMSG} Apple App Store`;
  const androidMsg = settings.update_msg_android || `${message} ${conditionMSG} Google Play Store`;

  // Maintenance: hard stop for everyone (superadmin app traffic still carries a version;
  // exempt only if you give superadmin a bypass header — out of scope here).
  if (settings.maintenance_mode === true) {
    return res.status(503).json({
      error: settings.maintenance_msg || "DZZLO-OMS is under maintenance. Please try again shortly.",
      maintenance: true,
    });
  }

  if (!!version && isntTestv && Number(version) <= allowedVersion) {
    return res
      .status(403)
      .json({ error: `${deviceBrand}` === "Apple" ? iosMsg : androidMsg });
  }

  next();
};
```

Notes:

- **`503` for maintenance vs `403` for version** lets the app distinguish "update me" from "come back later" (Phase 3 reads `maintenance` / the 503 to show a non-dismissable maintenance screen rather than a store-update prompt).
- Reads `getAppSettings()` from the in-process cache (Phase 1). A cold cache does **one** DB read then serves from memory for `TTL_MS`. A DB error degrades to the compiled floor — the gate never hard-fails closed on the whole fleet.
- The `"1.510"` test bypass is preserved exactly.

---

## 3. Seed & rollout order

**Status (2026-10-01):** ⬜ nothing to seed on master.

1. **Deploy Phase 1 + Phase 2 code.** Behavior is identical to today: no `app_settings` doc yet → `getAppSettings()` returns `{}` → `allowedVersion` = compiled `1.68`, default messages, no maintenance. **Zero behavior change on deploy.**
2. **Seed the doc** via `PUT /api/v3/sadmin/settings` (superadmin), e.g. `{ "min_app_version": 1.68, "maintenance_mode": false }`. Still no behavior change (floor equals compiled).
3. **Operate.** Raise `min_app_version` (e.g. to `1.77` when forcing the maxcrlmt/advdep build), edit `update_msg_*`, or flip `maintenance_mode` — each takes effect within `settingsCache` TTL (≤60s), no redeploy.

> Never delete the compiled `COMPILED_MIN_VERSION`. It is the safety floor for the case where the `app_settings` doc is wiped or the DB is unreachable.

---

## 4. dip-web confirm guard (cross-ref Phase 4)

**Status (2026-10-01):** dip-web — not re-assessed.

The Settings form (Phase 4) must, before writing `min_app_version`, **show which app versions would be blocked** and require explicit confirmation (e.g. "Setting floor to 1.78 will block all 1.77 and older devices until they update — continue?"). This is the human guard against an accidental fleet lockout; the server guard (only-raise) is the machine guard.

---

## 5. Phase 2 acceptance

**Status (2026-10-01):** ⬜ 0 of 8 against settings. The compiled behaviour these items keep (1.67 and 1.68 → 403, 1.69 passes, the test-build exemption, the Apple / Google messages) is pinned today, for the hardcoded gate, by `test/api_v3/features/version_gate/index.test.js`.

- [ ] Fresh deploy, **no `app_settings` doc**: a `version: 1.67` request → `403` with the default iOS/Android store message (unchanged from today).
- [ ] `version: 1.68` → `403` (boundary `<=` unchanged); `version: 1.69` → passes.
- [ ] `version: "1.510"` → passes regardless of floor (test bypass intact).
- [ ] Set `min_app_version = 1.77`: a `1.76` request → `403`; a `1.78` request → passes (within TTL of the write).
- [ ] `update_settings` with `min_app_version = 1.50` (below compiled `1.68`) → `400` (server only-raise guard).
- [ ] Set `maintenance_mode = true`: any request → `503` with `maintenance_msg`; flip back → normal within TTL.
- [ ] Simulate `getAppSettings()` throwing (DB down): version gate still enforces compiled `1.68`, does **not** 503/500 the fleet.
- [ ] Custom `update_msg_ios` set → an Apple device below floor sees the custom text.
