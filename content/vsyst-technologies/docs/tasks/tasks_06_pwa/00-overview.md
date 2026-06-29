# Task Overview — tasks_06 — Progressive Web App (PWA) for `dip-web`

> Convert `dip-web` from a regular React SPA into an installable, offline-capable Progressive Web App.
> Scoped to the `dip-web` repo only. No changes required in `dzzlo_oms_api` for Phase 1 or Phase 2.
> Phases 3 and 4 (push notifications, background sync) require API-side support and are tracked here as future work.

---

## TL;DR

Today: `dip-web` ships a leftover `public/manifest.json` from its Create-React-App origin (still says `"name": "Create React App Sample"`), no service worker, no offline support, no install prompt. A user who taps "Add to Home Screen" gets a glorified bookmark that opens Safari/Chrome with full browser chrome and breaks the moment the network drops.

Target: A real PWA. The site declares itself installable via a proper `manifest.webmanifest`, registers a Workbox-managed service worker via `vite-plugin-pwa`, caches the app shell so the app loads offline, and serves the last-seen API response when the network is unavailable. Installing the app on Android Chrome / Desktop Chrome / iOS Safari produces a standalone-window experience indistinguishable from a native app on first glance.

Net effect for field technicians using this on tablets/phones in patchy-network sites: the app keeps loading and showing data even when the connection drops. Future phases extend this to push notifications (assignment alerts) and offline-first mutations (fill out an inspection form on a roof with no signal, sync when back in the truck).

---

## Why Now

`dip-web` is the **Dzzlooms Inspection Platform** field-facing UI. The actual users are technicians performing inspections at customer sites — water systems, RO plants, meter reads. These environments routinely have:

- Concrete-walled mechanical rooms with no signal
- Roof installations with marginal LTE
- Customer Wi-Fi networks that block third-party origins
- Tablets that get backgrounded for 20 minutes between readings

A regular SPA fails outright in these conditions. A PWA degrades gracefully:

| Scenario                       | Today                                                 | After Phase 1                                             | After Phase 2                                              |
| ------------------------------ | ----------------------------------------------------- | --------------------------------------------------------- | ---------------------------------------------------------- |
| User opens app with no signal  | White screen, "no internet" error                     | App shell loads; "you are offline" indicator              | App shell loads; **last-seen list/master data is visible** |
| User taps "Add to Home Screen" | Bookmark in browser; opens with full Safari/Chrome UI | Standalone window; splash screen; looks like a native app | Same                                                       |
| User loses signal mid-session  | Next API call hangs or fails                          | Same — but app shell stays loaded                         | Cached responses returned within `networkTimeoutSeconds`   |
| New deploy goes out            | Browser caches old JS; user must hard-refresh         | SW auto-updates in the background; prompts user to reload | Same                                                       |

This is a high-leverage change: ~1 day of work for Phase 1, mostly config, with no API coordination required.

---

## Category Index

| File                                                                 | Phase                         | Scope            | Risk   | Coordination Required                                                |
| -------------------------------------------------------------------- | ----------------------------- | ---------------- | ------ | -------------------------------------------------------------------- |
| [01-pwa-base-setup.md](./01-pwa-base-setup.md)                       | Installable + auto-update     | `dip-web` only   | Low    | No — frontend only                                                   |
| [02-offline-caching-strategy.md](./02-offline-caching-strategy.md)   | Offline app shell + API cache | `dip-web` only   | Medium | No — frontend only, but requires auth/cache decisions (see §4 below) |
| [03-push-notifications-fcm.md](./03-push-notifications-fcm.md)       | Push notifications via FCM    | `dip-web` + API  | Medium | Yes — API needs subscription storage + send endpoint                 |
| [04-background-sync-mutations.md](./04-background-sync-mutations.md) | Offline-first mutations queue | `dip-web` only\* | High   | \* API doesn't change but idempotency/conflict semantics matter      |

---

## Phase Dependency Graph

```
┌────────────────────────────┐
│  01 PWA Base Setup         │ ◄──── FOUNDATIONAL. Manifest, service worker
│  (install + auto-update)   │       registration, install prompt UX.
└──────────────┬─────────────┘
               │
               ▼
┌────────────────────────────┐
│  02 Offline Caching        │ ◄──── App shell precache + runtime API cache.
│  (Workbox runtime caching) │       Requires auth/multi-user cache decisions.
└──────────────┬─────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌──────────────┐  ┌──────────────────────┐
│ 03 Push      │  │ 04 Background Sync   │
│ Notifications│  │ (offline mutations)  │
│ (FCM)        │  │                      │
└──────────────┘  └──────────────────────┘
   FUTURE              FUTURE
```

Phase 1 must ship before Phase 2 (Phase 2 attaches behavior to the SW that Phase 1 registers).
Phases 3 and 4 are independent of each other and both depend on Phase 2 being stable.

---

## Decisions Required Before Starting

These came up in the design conversation and need answers before Phase 1 / Phase 2 work begins. Owner: project lead.

| #   | Decision                                        | Options                                                                                        | Default if no answer                          |
| --- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------- |
| D1  | Production API origin (for runtime cache regex) | URL string                                                                                     | Cache only same-origin assets, no API caching |
| D2  | Cache authenticated API responses?              | (a) skip API entirely (b) cache + clear on logout (c) cache only `GET` master data             | (b) — cache + clear on logout                 |
| D3  | Theme color for manifest + status bar           | Hex value matching `PALETTES.light` primary                                                    | `#000000` (current placeholder)               |
| D4  | App icons (192/512 maskable)                    | Real branded icons OR keep CRA default for now                                                 | Keep current placeholders, swap before launch |
| D5  | Update prompt UX                                | (a) silent auto-reload on next nav (b) toast with "reload" button (c) modal blocking           | (b) — toast                                   |
| D6  | Install-prompt UX                               | (a) browser default banner only (b) custom in-app "Install" button using `beforeinstallprompt` | (b) — custom button in user menu              |

---

## What Was Intentionally Deferred

| Item                                          | Why Deferred                                                                          | Tracked In                        |
| --------------------------------------------- | ------------------------------------------------------------------------------------- | --------------------------------- |
| Push notifications                            | Requires API endpoint for subscription storage + FCM server key handling              | `03-push-notifications-fcm.md`    |
| Background sync for mutations (offline forms) | Requires careful conflict-resolution design + IndexedDB queue + RTK Query interceptor | `04-background-sync-mutations.md` |
| Periodic background sync                      | Chrome-only API, limited use case for an inspection app                               | Not tracked                       |
| File system access (save inspection PDFs)     | Out of scope; existing `<a download>` works                                           | Not tracked                       |
| Web Share API integration                     | Out of scope                                                                          | Not tracked                       |

---

## Reading Order

1. **`00-overview.md`** (this file) — context and decisions
2. **`01-pwa-base-setup.md`** — implement first, ~1 day
3. **`02-offline-caching-strategy.md`** — implement second, ~2 days
4. **`03-push-notifications-fcm.md`** — future, ~3 days when prioritized
5. **`04-background-sync-mutations.md`** — future, ~5 days when prioritized

---

## Cross-References

- `dip-web/CLAUDE.md` — architecture invariants (RTK Query, BrowserRouter, theming)
- `dip-web/vite.config.js` — current Vite 6 config
- `dip-web/public/manifest.json` — **stale CRA placeholder, will be deleted in Phase 1**
- `dip-web/src/store/apis/createApi.js` — RTK Query base; relevant for Phase 2 cache strategy
- `dip-web/src/utils/StyleSheets/index.js` — `PALETTES` registry; theme color source for manifest
- `tasks_05_firebase/FIREBASE_NOTIFICATIONS_FCM_VS_ONESIGNAL.md` — FCM decision context for Phase 3
