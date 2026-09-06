# 01b — Customers · filter sheet (sub-spec of [[01-customers]])

> **SUPERSEDED 2026-09-06** by the parent spec's decisions 52–55: the sheet is replaced by two always-visible tri-state chips (Verified, Has Trans.) under the search, a sort chip (direction toggle), a react-native-paper `Menu` on the sort button, and a header reset behind a confirmation. Kept for the record of O‑2 (decision 36) and the tri-state semantics, which survive in the chips.


> Parent: [[01-customers]] (spec agreed 2026-09-03). Frame: `../designs/customers/02-filter-sheet.png`. Scope: the in-screen filter/sort bottom sheet of the dealer Customers screen — layout, states, copy, the tri-state control, and the one contract item the parent left open (**O‑2 "Latest Order wise"**). This sub-spec cannot change the parent's §5.1 except O‑2, and it does not.
>
> **Status line:** Session held **2026-09-04** (four decisions, all on the recommended option) → **O‑2 closed 2026-09-04** and copied into the parent's §5.1 → built with the parent screen (no separate API or PR).

## 1. Purpose

One sheet, opened from the filter icon in the Customers header, that sets the three tri-state status filters and the sort (key + direction) the list is fetched with, and saves them as the user's preference for this company (parent §5.2). It sends nothing itself: **Done** hands `{ filters, sort, dir }` to the screen, which refetches the read model and issues the one `PUT /users/prefs/dealer_customers`.

## 2. What the user sees (top to bottom, from the frame)

| #   | Element                                                                                                                     | Source                                                                                                          | Rule                                                                                                                                                                                                                                                                                                      |
| --- | --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Header: **Close** (left, error colour) · **Filters** (title) · **Done** (right, primary)                                    | —                                                                                                               | Close discards the sheet's edits; Done applies them (§3)                                                                                                                                                                                                                                                  |
| 2   | "Select Customer by Status :"                                                                                               | copy                                                                                                            | —                                                                                                                                                                                                                                                                                                         |
| 3   | Three tri-state status controls: **Verified · Has Trans. · Blacklisted**                                                    | `filters.verified` / `filters.hasTrans` / `filters.blacklisted` (parent §5.1, tri-state: absent · true · false) | Rendering as drawn: blank box = **any** (key absent), box + ✓ badge = **only** (`true`), box + ✕ badge = **exclude** (`false`). Tapping the control cycles any → only → exclude → any (**A‑1**, visual detail for the design session). Three controls; the third wraps to a second line on narrow widths. |
| 4   | "Select sorting Type"                                                                                                       | copy                                                                                                            | —                                                                                                                                                                                                                                                                                                         |
| 5   | Radio list, in this order: **Creation Date · Customer Name · A/c Balance · Daily Total · Credit Total · Latest Order wise** | `sort` = `createdAt` · `name` · `balance` · `daily` · `credit` · `latestOrder`                                  | Exactly one selected; the selected row is highlighted and carries the direction arrow (6). "Customer Name" is second (decided 2026-09-04).                                                                                                                                                                |
| 6   | Direction arrow on the selected row                                                                                         | `dir`                                                                                                           | ↓ = `desc`, ↑ = `asc`. Tapping the arrow flips `dir`. Selecting a **different** sort sets that sort's natural direction (**A‑2**): `createdAt` desc · `name` asc · `balance` desc · `daily` desc · `credit` desc · `latestOrder` desc.                                                                    |
| 7   | ~~"\* Atleast one required"~~                                                                                               | —                                                                                                               | **Removed** (decided 2026-09-04): a radio list always has one selection and every toggle state is valid, so nothing can be "required". Done is always enabled.                                                                                                                                            |
| 8   | **Reset to Default** (full-width primary)                                                                                   | —                                                                                                               | Sets the sheet to `{ sort: "createdAt", dir: "desc", filters: {} }`, applies immediately (refetch + the PUT with those defaults — parent §5.2) and closes the sheet.                                                                                                                                      |

Not in the sheet: search (lives in the header), the count badge (on the filter icon, parent §2 row 2: `activeFilterCount`).

## 3. What the user can do

| Action                        | Precondition              | Effect                                                                                                                                                                                  |
| ----------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Open the sheet                | list loaded at least once | pre-filled from the list response's `meta.applied` (`sort`, `dir`, `filters`) — no request                                                                                              |
| Tap a status control          | —                         | cycles its state (row 3); local sheet state only                                                                                                                                        |
| Tap a sort row                | —                         | selects it and sets its natural direction (row 6); local                                                                                                                                |
| Tap the arrow                 | on the selected row       | flips `dir`; local                                                                                                                                                                      |
| **Done**                      | always                    | closes; the screen refetches with the sheet's `{ filters, sort, dir }` and sends one `PUT /users/prefs/dealer_customers` with the same body; the badge updates from `activeFilterCount` |
| **Close** / swipe down / back | —                         | discards edits; reopening shows the applied values again                                                                                                                                |
| **Reset to Default**          | always                    | row 8                                                                                                                                                                                   |

Offline: Done still applies locally and the refetch fails through the list's existing error state; the PUT's failure is silent (a lost preference is not an error the user can act on) and is retried on the next Done. No optimistic write is undone.

## 4. Decisions (session 2026-09-04)

1. **O‑2 — "Latest Order wise" = newest sales order.** Key `latestOrder` sorts by the newest `so_msts.on_dt` per customer (the dealer's own sale record, whether raised from an app order or directly). Not the order request (`order_msts`) and not invoices/payments (the ledger buckets carry no per-document dates; both would cost extra queries). Zero extra queries: it comes from the grouped `so_msts` query Has Trans. already needs.
2. **All-time, not FY-bounded.** The same single aggregate drops the FY bound on `on_dt` and computes the FY count Has Trans. needs as a conditional sum — no extra cost — so the sort is meaningful in the first days of April and a customer who last ordered in March sorts by that date while still reading `hasTrans: false`.
3. **"\* Atleast one required" removed** from the sheet (row 7).
4. **Name sort = "Customer Name", second in the list** (row 5).

Assumptions Fable fixed for the build (override in the design session if the frame says otherwise):

- **A‑1** tri-state interaction = tap-to-cycle, rendered as drawn (blank / ✓ / ✕).
- **A‑2** selecting a sort applies its natural direction; the arrow flips it; the direction is remembered per sheet session only (the saved preference carries whatever was applied).
- **A‑3** Reset applies immediately and closes (one refetch, one PUT); it is not a "clear the form" button.
- **A‑4** `activeFilterCount` (parent §6) = number of status controls not in **any** + 1 if `sort ≠ createdAt` or `dir ≠ desc`.

Proposal for the design session (Step 3), **not** a decision — it would change the parent's §2/§5.1 and must go spec → test → code in one PR per [[../01-tdd-workflow#1.4 How discussion sessions feed the tests|01 §1.4]]: **P‑1** when the list is sorted by Latest Order wise, show a subtle "Last order 12 Aug" line in each row (would add `lastOrderAt` to the row contract).

## 5. API contract — what this sub-spec fixes in the parent

`sort: "latestOrder"` — key = newest `so_msts.on_dt` per `cust_id` over **all time**; customers with no sales order ever sort **last in both directions**; ties by `cust_id` ascending (parent rule). Composition item 5 of the parent becomes one aggregate over `so_msts` filtered by `dealer_id` (tenant) and `cust_id ∈ relations`, grouped by `cust_id`: `{ lastOnDt: max(on_dt), fyCount: sum(on_dt in current FY ? 1 : 0) }` — `hasTrans` reads `fyCount > 0`, `latestOrder` reads `lastOnDt`. Indexes `{ dealer_id: -1, on_dt: -1 }` and `{ cust_id: 1, on_dt: -1 }` exist on `so_msts`.

API tests (replace the parent's `it.todo`):

- [ ] `sort: "latestOrder", dir: "desc"` → the customer with the newest sales order first; `asc` → oldest first; pinned against seeded `on_dt` values
- [ ] a relation with **no** sales order ever sorts last under both directions
- [ ] all-time: a relation whose only sales order is dated in the previous FY sorts by that date **and** still reads `hasTrans: false`
- [ ] two relations with the same newest `on_dt` → `cust_id` ascending
- [ ] keyset paging on `latestOrder`: pages disjoint, order stable after a new SO is inserted for a customer already on page 1
- [ ] mutation smoke: drop the `$max` (use the FY-bounded date) → the all-time test goes red

## 6. Screen build plan (with the parent screen — same folder, same PR)

- `components/FilterSheet.js` inside `src/screens/v2/Dealer/Customers/`, rendered from a `BottomSheetModal`; strings in the screen's `strings.js` (`filters.title`, `filters.close`, `filters.done`, `filters.statusHeading`, `filters.sortHeading`, `filters.reset`, the six sort labels, the three status labels).
- **Tier 1 (red first):** `src/helpers/Filters/`: `cycleTriState(current) → undefined | true | false`, `defaultDirFor(sort)`, `activeFilterCount({ sort, dir, filters })` (A‑4), `SORT_OPTIONS` (order + labels + natural dir). One test per rule.
- **Tier 3 (decision-only, `renderScreen`):** opening pre-fills from `meta.applied`; tapping a control cycles through the three states; selecting Latest Order wise shows ↓ and Done sends `{ sort: "latestOrder", dir: "desc" }`; tapping the arrow flips to `asc`; Done triggers exactly one list refetch and one PUT with the same body; Close discards (reopen shows the applied values); Reset refetches + PUTs the defaults and closes; the badge equals `activeFilterCount`.
- Mutation smokes: break `cycleTriState` (skip the exclude state) → the cycle tests red; drop the PUT from Done → the prefs test red.

## 7. Definition of done

- [x] Session held, four decisions recorded (2026-09-04)
- [x] O‑2 copied into the parent §5.1 (sort table, composition item 5, test list) — same day
- [ ] A‑1…A‑4 confirmed or overridden in the design session (Step 3)
- [ ] Built and shipped with the parent screen (its DoD applies)
