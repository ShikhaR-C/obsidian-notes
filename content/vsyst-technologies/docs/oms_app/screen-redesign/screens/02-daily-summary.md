# Screen spec — `Daily Summary` (common: dealer + customer)

> Screen slug `daily-summary` · route name `DailySummary` (unchanged, in both role navigators) · folder `src/screens/v2/…/DailySummary/` (**open — Q1**) · registry key(s) `Dealer/DailySummary` / `Customer/DailySummary` (**open — Q1**) · toggle `screen_v2_<role>_daily_summary` · size **S, proposed** (one read model, no commands; the actions are switch segment, change day, refresh) — see [[../03-per-screen-playbook]] and [[../templates/screen-spec]].
>
> **Status line:** **Spec draft 2026-09-15** (Step 0: this file opened from the template alongside app PR #52 — the branch `app_screen_daily_summary`, stacked on #51, whose only commit is the runbook stub `docs/screens/daily-summary-v2.md`) → Spec agreed (date) → API red → API green (PR #) → Design agreed (date) → Screen red → Screen green (PR #) → Shipped in app vX.Y → Old screen removed (PR #)
>
> **Next gate:** the Step 1 session — the user's brainstormed design canvas (to be linked in §4) and the questions Q1–Q6 below. Until "spec agreed", nothing changes in either repo beyond the runbook stub.
>
> Facts without a marker were read from the code on 2026-09-15 (paths inline). Nothing in §2, §3 or §5 is agreed yet.

## 1. Purpose ⛔

- **One sentence:** a dealer user opens one customer's day — or a customer user opens one dealer's day — and sees that company's sales orders and purchase orders for the day, today by default, switching the day when they need another.
- **Replaces** (all v3, all in `src/screens/Common/DailySummary/`):
  - `index.js` (136 lines) — the two-half segment pill (Purchase Orders / Sales Orders, Sales Orders default), the day range held in state (`moment().startOf('day')` → `endOf('day')` on the **device clock**), the header title = `companyName`, the header reset glyph that `navigation.replace('DailySummary', params)`, and the on-focus reset of range + segment.
  - `SalesOrders/index.js` (265) — `useLazyFetch_so_msts_DRQuery` (v3 `so_msts`), sort fixed `descending`.
  - `PurchaseOrders/index.js` (285) — `useLazyFetch_order_so_POSTQuery` (v3 `order_msts`), sort fixed `descending`.
  - `Component/index.js` (1,176) and `components.js` (571) — the row and list pieces; their fields are the input to §2.
  - Shared, **not** deleted by this screen: `src/components/DatePicker/DTBS` (the date-picker sheet — re-grep its importers before Step 6).
- **Roles:** dealer and customer, one screen. The dealer opens it for a customer (`ID_FIELD: 'cust_id'`), the customer for a dealer (`ID_FIELD: 'dealer_id'`); the sub-lists pass `ID_FIELD` into the v3 queries. Whether the two roles see different pieces is **Q1**.
- **Entry points (params exactly as the callers send them — the v2 Customers exit is already tested against them):**
  - v2 Customers daily tile, `src/screens/v2/Dealer/Customers/index.js` → `navigate(PARENT, { screen: 'DailySummary', params: { companyID: row.cust.id, companyName: row.cust.name, ID_FIELD: 'cust_id' } })`
  - v1 Customers, `src/screens/Dealer/Customers/index.js` → same route, same three params
  - customer-side Dealers, `src/screens/Customer/Dealers/index.js:334` → `navigate('customerDealer', { screen: 'DailySummary', params: { companyID: item.dealer_id._id, companyName: item.dealer_id.dealer_name, ID_FIELD: 'dealer_id' } })`
- **Exit points:** **none in v1** — no `navigate` / `push` anywhere in the folder besides the header reset; a row does not open anything, and there are no mutations. The only sheet is the date picker (in-screen). Whether a v2 row opens the order (and with what params) is **Q5**.

## 2. What the user sees ⛔

To be filled in the Step 1 session from the brainstormed design (§4) and the v1 row fields in `Component/index.js`. Skeleton:

| #   | Element                              | Data (source collection · field)          | Derived? (formula)                                        | Role-visible | Loading / empty / error state           |
| --- | ------------------------------------ | ----------------------------------------- | --------------------------------------------------------- | ------------ | --------------------------------------- |
| 1   | Header title                         | route param `companyName`                 | —                                                         | both         | —                                       |
| 2   | Day (default today) + the way to change it | —                                    | **Q3:** device clock (v1) or the server's IST day          | both         | —                                       |
| 3   | Segment: Sales Orders / Purchase Orders | —                                      | Sales Orders default (v1)                                 | both         | —                                       |
| 4   | Sales-order rows                     | `so_msts` · fields **to fill**            | **to fill**                                               | **Q1**       | skeleton / "No sales orders today" / banner |
| 5   | Purchase-order rows                  | `order_msts` · fields **to fill**         | **to fill**                                               | **Q1**       | skeleton / "No purchase orders today" / banner |
| 6   | Day totals (if the design keeps them) | **to fill**                              | must equal the Customers daily tile's amount for the same day (**Q3**) | both | —                                  |

Rule: **if it is not in this table, the API does not return it.**

## 3. What the user can do ⛔

| #   | Action                    | Trigger              | Precondition (business rule) | API command                           | Optimistic? | Success feedback | Failure feedback |
| --- | ------------------------- | -------------------- | ---------------------------- | ------------------------------------- | ----------- | ---------------- | ---------------- |
| 1   | Switch segment            | tap the pill half    | —                            | none (both lists in one read — **Q2**) | —           | list swaps       | —                |
| 2   | Change the day            | date picker          | —                            | none — refetch the read model         | —           | lists refetch    | banner           |
| 3   | Refresh                   | header glyph / pull  | —                            | none — refetch (**Q4:** not `replace`) | —           | scroll to top    | banner           |

No commands: v1 carries no mutation and none is planned.

## 4. Design references ◌

- Figma / canvas frames: `../designs/daily-summary/*.png` — **nothing dropped yet.** The user has a brainstormed design canvas for this screen; its link goes here when shared, and the frames are exported into the folder per [[../designs/README]].
- Design-system tokens used: the v2 primitives (`AppText`, `Box`, `Container`, `Screen`), the type roles and palette tokens — never literals (`AI.md`).
- States that need their own frame: loading, empty per segment, error per segment, Hindi, font-scale 200 %, landscape / wide window ([[../06-all-screen-shapes-plan]]).
- **Discussion-session notes (dated):** —

### Questions for the Step 1 session

1. **Q1 — one screen, two roles.** v1 lives in `Common/`. One v2 folder with one registry key, or two keys (`Dealer/DailySummary`, `Customer/DailySummary`) over one component so each role has its own toggle and rollback? Do the roles see different pieces?
2. **Q2 — one read model.** Does `POST /api/v4/screens/daily-summary` return both lists and the day's totals in one envelope (the Customers precedent), or one list per segment?
3. **Q3 — whose day.** v1 uses the device clock; the Customers daily tile is the server's IST day. They must agree when the user taps through.
4. **Q4 — reset.** Scroll-to-top + refetch on the request key (Customers decision 65), not `navigation.replace`.
5. **Q5 — row taps.** v1 rows open nothing. Does a v2 row open the order, and with what params?
6. **Q6 — empty and error states** per segment, English and Hindi written together.

## 5. API contract (v4) ⛔

Proposed, **not agreed** — written so the Step 1 session has something to strike out:

### 5.1 Read model

```
POST /api/v4/screens/daily-summary
Auth: Bearer (protect) · Roles: authorize(dealer roles, customer roles — Q1) · Tenant: derived from token, never from body
Body (validated, unknown keys rejected):
  { companyId: ObjectId, idField: 'cust_id' | 'dealer_id', day?: 'YYYY-MM-DD' (IST; default = server today — Q3), cursor?: string }
200:
  { success: true, data: { salesOrders: [...], purchaseOrders: [...], totals: {...} — per §2 }, page?: { next, hasMore }, meta: { generatedAt, day } }
Errors: 400 VALIDATION · 401 UNAUTHENTICATED · 403 FORBIDDEN / FORBIDDEN_ROLE · 404 NOT_FOUND
Partial failure policy: each list is an optional sub-query → null + `errors.<key>`; totals critical
```

### 5.2 Commands

None.

### 5.3 Test list — API (write these first, watch them fail)

`test/api_v4/screens/daily-summary.test.js`

- [ ] happy path: seeded world → every §2 key present, shape pinned by helper
- [ ] tenancy: a user of company B gets 403/404 and zero foreign fields for `companyId`
- [ ] validation: bad ObjectId / unknown key / bad `day` → 400 VALIDATION with field name
- [ ] role: dealer with `cust_id`, customer with `dealer_id`; the crossed pairs refused
- [ ] day boundary: an order at 23:59:59 IST and one at 00:00:00 IST the next day land on different days regardless of server TZ
- [ ] pagination: `limit+1` probe, stable cursor across an insert (if the lists page)
- [ ] partial failure: one list's sub-query throws → 200 with `errors.<key>`
- [ ] contract fixture captured (`yarn fixtures:export` → `fixtures/api_v4/screens_daily-summary.json`)
- [ ] mutation smoke recorded in PR

## 6. Screen build plan ⛔

- **Folder:** `src/screens/v2/<Role>/DailySummary/` — `<Role>` per **Q1**; `index.js`, `useScreenModel.js`, `strings.js` (`{ en, hi }`), `components/`, `__tests__/`.
- **Pure logic to extract first (Tier 1, TDD):** the IST day bounds and the `day` string (`src/utils/Dates`), the segment default, the totals formatting (`formatCurrency`), any row derivation §2 settles on.
- **RTK Query endpoint (Tier 2, MSW):** `getScreen_DailySummary` in `src/store/apis/v4/daily_summary.js`, `providesTags` per §5; fixtures pulled, never hand-rolled.
- **Screen test (Tier 3, RNTL) — decision cases only:** segment default; empty per segment; error per segment; the day change refetches with the new `day`; refresh scrolls to top and refetches (Q4); role differences if Q1 says there are any; the three entry params accepted unchanged.
- **Cutover:** route name `DailySummary` stays; `register(<key>, { v1, v2 })` per Q1 in `src/navigation/screenRegistry.js`, `resolveScreen` on the one route in each role navigator, behind `screen_v2_<role>_daily_summary` (absent = on); the v1 folder stays as the rollback until the toggle has ridden a release.

## 7. Definition of done

- [ ] Spec agreed and dated; discussion notes captured in §4
- [ ] API PR: tests first (red commit → green commit), fixtures exported, flow-map row added in `docs/testing.md`, `yarn test:full` green
- [ ] App PR (#52): Tier 1 → Tier 2 → Tier 3 tests, `yarn fixtures:pull`, `yarn test` green, no-network guard intact
- [ ] Manual: one request on screen open (v4), old screen still works on v3 for a v1.78 build
- [ ] Release gate green; screen listed in the release notes; index row updated
