# 04 — Background Sync (Offline Mutations Queue) — FUTURE

> Phase 4 of the PWA initiative. Lets technicians submit forms (inspections, meter reads, decants) while offline; the requests queue locally and replay automatically when connectivity returns.
> **Future work.** Tracked here so the design isn't lost. Highest-risk phase — do not start until Phase 1 + 2 are stable in production and there is a clear user demand.

---

## TL;DR

This is the killer feature for a field-inspection app. A technician walks into a basement utility room with no signal, fills out a 20-field inspection form, hits submit, walks back to the truck — and the inspection is automatically uploaded as soon as LTE returns, with no user intervention.

The mechanics are straightforward (Workbox `BackgroundSyncPlugin` + IndexedDB queue). The hard parts are:

- **Idempotency** — replays may double-submit if the original `POST` actually reached the server but the response was lost
- **Conflict resolution** — what if the customer was reassigned while the form was queued?
- **Auth token expiry** — a token valid at form-submit time may have expired by replay time
- **UX honesty** — the user must understand "this will sync later" vs "this is saved on the server"

Estimated effort: **5 days** including conflict-resolution design and idempotency on the API side.

---

## 1. Why This Is High Risk

Background sync silently re-fires `POST`/`PUT`/`DELETE` requests minutes or hours after the user originated them. Every unhandled edge case becomes a **data integrity bug**:

- User-friendly look: "the form submitted later." User-hostile reality: "I submitted the form, walked away, and now there are two duplicate inspections charged to the customer."
- Or: "I submitted the form, then the customer was reassigned to another technician, then sync ran and overwrote the new technician's data."
- Or: "I submitted the form, my token expired, sync replayed with an expired token, request failed silently, data is lost forever."

This is why Phases 1–3 must be stable first and why this design has a 5-day budget rather than 1–2.

---

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         dip-web (browser)                           │
│                                                                     │
│  RTK Query mutation                                                 │
│  ┌────────────────────┐                                             │
│  │ useUpdate_insp()   │                                             │
│  └─────────┬──────────┘                                             │
│            │ fetch(POST /api/insps, body)                           │
│            ▼                                                        │
│  ┌────────────────────┐                                             │
│  │ Service worker     │                                             │
│  │ (BackgroundSync    │                                             │
│  │  plugin)           │                                             │
│  └─────────┬──────────┘                                             │
│            │                                                        │
│      online?                                                        │
│       ├─ yes ─► forward to network ─► response ─► RTK Query         │
│       └─ no  ─► enqueue in IndexedDB                                │
│                  │                                                  │
│                  │  on `sync` event (fired when                     │
│                  │  network returns):                               │
│                  ▼                                                  │
│            replay queued requests                                   │
│            ─► server response ─► postMessage to app                 │
│                                  │                                  │
│                                  ▼                                  │
│                          UI shows "synced" state                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Tasks

### 3.1 Frontend (`dip-web`)

- [ ] Add Workbox `BackgroundSyncPlugin` to mutation routes in `vite.config.js`
- [ ] Decide: which mutations are sync-eligible? Only POST/PUT for transactions (insps, decants, meter_reads), not master CRUD
- [ ] RTK Query interceptor: when a mutation fails due to offline, return a synthetic "queued" response so optimistic updates persist visually
- [ ] IndexedDB schema for the queue: { id, url, method, headers, body, createdAt, attemptCount, idempotencyKey }
- [ ] Generate `idempotencyKey` (UUID) at submit time, attach as header
- [ ] UI affordances:
  - "Pending sync (3)" indicator in the header
  - Per-record sync state badge in transaction lists
  - "Retry" / "Discard" actions on a pending-sync drawer
- [ ] On successful replay: postMessage from SW → main thread → invalidate relevant RTK Query tags
- [ ] On permanent failure (4xx): surface to user with original payload for re-edit
- [ ] Token-expiry handling: before replay, check expiry; if expired, attempt refresh (depends on `tasks_02_major/01-token-refresh.md` being done)

### 3.2 Backend (`dzzlo_oms_api`)

- [ ] Implement `Idempotency-Key` header support on all sync-eligible endpoints
  - Cache `idempotencyKey → response` for 24h in Redis (or Mongo TTL collection)
  - Return cached response on duplicate key, never re-process
- [ ] Add `clientCreatedAt` to mutation payloads so the server can detect stale writes
- [ ] Conflict-resolution policy per entity:
  - Inspections: last-write-wins per technician scope
  - Meter reads: append-only, never overwrite
  - Decants: same as inspections
- [ ] Audit log: record `replayedAfterMs` so we can monitor sync delay distributions

### 3.3 UX

- [ ] Submit-while-offline flow:
  - Form shows "Saved locally — will sync when online" toast
  - Record appears in the list with a "pending sync" badge
  - Cannot edit a pending-sync record (enforce at form-open time)
- [ ] Replay flow:
  - Badge changes to "syncing…" then "synced" then disappears after 2s
  - On 4xx: badge becomes "sync failed — tap to fix"
- [ ] Discard flow: explicit user action, with confirmation, removes from queue without replay

---

## 4. Open Questions

1. **Mutation eligibility.** Which RTK Query mutations are safe to queue? Master CRUD probably isn't — if a user creates a customer offline, the local optimistic ID won't match the server-assigned ID, and any subsequent transactions referencing that customer will fail to replay.
2. **Photo uploads.** Inspections include photos. IndexedDB can store blobs, but Workbox `BackgroundSyncPlugin` replays the original Request, which means the photo blob must still be in memory or referenceable. May need a custom plugin instead.
3. **Queue lifetime.** How long do we keep failed replays? 24h? 7 days? Forever until user discards?
4. **Per-device queue persistence.** If user logs out, queue should... persist? Wipe? Surface to next user? Probably wipe — but that loses unsynced field data.
5. **Multi-tab.** If two tabs of the app are open and both queue mutations, the SW handles them — but the UI in tab A must reflect tab B's queue state. BroadcastChannel?
6. **Dependency on Phase 01 (token refresh) of tasks_02_major.** Background sync replaying with an expired token is broken. Either ship token-refresh first, or replays with auth failures are surfaced as "sync failed — log in again."

---

## 5. Acceptance Criteria (Tentative)

- [ ] User can submit an inspection form while offline; UI shows "queued" state
- [ ] On reconnect, request replays automatically within 30 seconds
- [ ] Duplicate request (same idempotency key) does not create duplicate records
- [ ] Stale-write detection works: replay attempted on data modified by another user shows a clear conflict UI
- [ ] Token refresh happens transparently on replay if needed
- [ ] User can manually discard a queued mutation
- [ ] Failed replays (4xx) surface to user with editable payload
- [ ] Photo uploads succeed via the queue (or alternative photo-handling path)
- [ ] No silent data loss in any failure scenario

---

## 6. Why This Should Wait

- **Phase 2 must prove stable in real field use first.** If users are happy with offline reads, that's already the 80% win. The other 20% (offline writes) is 80% of the engineering risk.
- **Token refresh (`tasks_02_major/01-token-refresh.md`) should ship first.** Replaying mutations with stale tokens is a known minefield.
- **API-side idempotency is a meaningful change** that benefits other clients (mobile app) too — better to design once than retrofit twice.

---

## 7. References

- Workbox BackgroundSync: https://developer.chrome.com/docs/workbox/modules/workbox-background-sync/
- IndexedDB queue patterns: https://developer.chrome.com/docs/workbox/managing-fallback-responses/
- RFC: HTTP idempotency keys (Stripe-style): https://stripe.com/docs/api/idempotent_requests
- `tasks_02_major/01-token-refresh.md` — soft prerequisite
- `dip-web/src/store/apis/createApi.js` — RTK Query base
- `00-overview.md` — phase context
