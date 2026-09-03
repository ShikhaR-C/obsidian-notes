# Screen spec — `Customers` (dealer)

> Screen slug `customers` · route name `Customers` (unchanged) · folder `src/screens/v2/Dealer/Customers/` · registry key `Dealer/Customers` · toggle `screen_v2_dealer_customers` · size **S** (one read model + one preference command; the filter sheet gets its own sub-spec `01b`) — see [[../03-per-screen-playbook]] and [[../templates/screen-spec]].
>
> **Status line:** Spec draft 2026-09-03 (eight rounds) → **Spec agreed 2026-09-03** (user; O‑2 "Latest Order wise" explicitly deferred to sub-spec `01b`, which must close before "start API for customers") → API red → API green (PR #) → Design agreed (date) → Screen red → Screen green (PR #) → Shipped in app vX.Y → Old screen removed (PR #)
>
> **Next gate:** Phase 0 closed 2026-09-03 (tasks_12 PRs merged into `slave`/`slave_dev`, fixtures on seed `v3_2026-09-03`, gate PASS). The build now waits for "start phase 1" and "start phase 2" per [[../02-foundations]], then the `01b` filter-sheet session. Nothing in either repo changes for this screen before "start API for customers".
>
> Facts without a marker were read from the code on 2026-09-03 (paths inline). Former assumptions **A‑1…A‑8** are all decided (see §4). **O‑2** is the only open definition and it belongs to the filter-sheet sub-spec, which must close before "start API for customers". From here on, any change to §2, §3 or §5 follows [[../01-tdd-workflow#1.4 How discussion sessions feed the tests|01 §1.4]]: spec first, then the test, then the code, in one PR.

## 1. Purpose ⛔

- **One sentence:** a dealer user sees every customer company the dealer serves — today's orders, account balance and credit utilisation per customer, plus the totals for the customers currently shown — and jumps from a row to that customer's settings, daily summary, ledger or credit summary.
- **Replaces:**
  - `src/screens/Dealer/Customers/index.js` (list, client-side search/sort/filter, on-focus fetch, header refresh hack `navigation.replace('Customers')`)
  - `src/screens/Dealer/Customers/RelationFilterBS.js` (filter/sort bottom sheet — its v2 replacement is planned in the sub-spec `01b-customers-filter-sheet.md`, session to be scheduled)
  - the dealer use of `src/components/Balance/Components.js` (`Card_balance_helpers` row — **shared** with `Customer/Dealers`, so the file stays until that screen ships)
  - the dealer-list use of `src/screens/Common/RelationList/RelationCreditBS.js` (still imported by `CustSettings`, `Customer/Dealers`, `DealerSettings`, `Customer/NewOrder` — **not** deleted by this screen)
  - Not touched: `CustSettings.js` (1,962 lines), `Discount.js`, `SetDiscBS.js`, `Common/DailySummary`, `Common/Accounts`, `Common/AdvDepLedger` — they stay on v3 and remain the exit points.
- **Roles:** dealer only; superadmin out of scope (D5). Decided 2026-09-03:
  - list, summary strip, tiles and donut: **every** dealer scope (`DPrimary`, `DAdmin`, `DOrder`, `DAccount`, `DOrderAccount`, `DView`) — "everyone can view balances"
  - Settings strip and avatar tap → `CustSettings`: `DPrimary`, `DAdmin` only (as v1, `index.js:333`)
  - credit % label and the credit sheet: only when the user's company entry has `amend_prem.allow ∋ "credit.read"` (as v1, `Components.js:38`; default for `DPrimary`/`DAdmin` per `api_v3/services/users.js:60`, editable per user from the Users screen)
- **No "Add Customer" flow on the dealer side** (decided 2026-09-03, twice). The "Add Dealer" button in the shared frame belongs to the customer-side Dealers screen, which is a future screen.
- **Entry points:** Drawer → "Customers" (`navigation.navigate('dealerCustomer', { screen: 'Customers' })`, `DrawerContent.js:487`). Header: menu left, title "Customers", refresh icon right (kept from the frame; v2 refetches instead of re-mounting).
- **Exit points (params exactly as v1 sends them, because the target screens stay v3):**
  - `CustSettings` `{ dealer_custID: { dealer_id, cust_id } }` — also the **only** place a customer is blacklisted or un-blacklisted (A‑8)
  - `DailySummary` `{ companyID: cust_id, companyName, ID_FIELD: 'cust_id' }`
  - `Accounts` `{ companyID, companyName, companyAdvance: adv_dep, ID_FIELD: 'cust_id', previous_screen: 'Customers' }`
  - v2 credit sheet (in-screen, rendered from the tapped row — no navigation, no request)
  - v2 filter sheet (in-screen; sub-spec `01b`)

## 2. What the user sees ⛔

Layout mirrors the customer-side "Dealers" frame shared 2026-09-03 (see §4) with the dealer-side substitutions: title "Customers", search placeholder "Search Customer name" (as the filter frame shows), **no Add button**, avatar = customer image/initials instead of the oil-company logo, summary label "Customer". **Row = the Dealers frame's row** (donut + %, no numbered badge) — decided round 7.

### 2a. List screen

| #   | Element                             | Data (source collection · field)                                                                                                                                                          | Derived? (formula)                                                                                                                                                                                                                                                                                                                                                                 | Role-visible                             | Loading / empty / error state |
| --- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- | ----------------------------- |
| 1   | Search field                        | client state → body `q`                                                                                                                                                                   | debounced 300 ms; page reset in the same commit as the text change; list scrolls to top on a new search (the `SelectVehicle.js` pattern)                                                                                                                                                                                                                                           | all                                      | —                             |
| 2   | Filter button + count badge         | client state (`sort`, `dir`, `filters`)                                                                                                                                                   | `activeFilterCount({ sort, dir, filters })` = number of settings that differ from the defaults (`createdAt` / `desc` / no filters) — new Tier 1 helper; badge hidden at 0                                                                                                                                                                                                          | all                                      | —                             |
| 3   | Summary · "Customer m / n"          | server `summary.matching` / `summary.all`                                                                                                                                                 | **two numbers** (round 6): `matching` = relations passing the current `q` + `filters`; `all` = every relation of the dealer, blacklisted included                                                                                                                                                                                                                                  | all                                      | skeleton                      |
| 4   | Summary · "Daily total"             | server `summary.dailyTotal`                                                                                                                                                               | Σ of `today.amount` over the **matching** relations — all of them, not just the pages loaded so far; follows filter and search — decided round 5                                                                                                                                                                                                                                   | all                                      | skeleton                      |
| 5   | Summary · "Total Balance"           | server `summary.totalBalance`                                                                                                                                                             | Σ of `credit.boip` over the **matching** relations — same universe as row 4 — decided round 5                                                                                                                                                                                                                                                                                      | all                                      | skeleton                      |
| 6   | Row · tags `CR` `DR` `OTP`          | `dealer_custs.cs_reimb` · `dealer_custs.products[]` × `prod_msts.categories[]` · `dealer_custs.dvr_otp`                                                                                   | server booleans: `tags.cr` = `cs_reimb`; `tags.dr` = the relation has a `products[]` entry with `disc_type !== "none"` and `disc_val > 0` whose `dealer_prod_id` is a dealer product whose PRIMARY category is **Diesel** (`prod_msts.categories ∋ { group_name: "PRIMARY", name: "Diesel" }` — the same rule `so_msts.js:210-213` uses to stamp `p_ctgy`); `tags.otp` = `dvr_otp` | all                                      | —                             |
| 7   | Row · avatar                        | `cust_msts.cust_img`, `cust_msts.cust_name`                                                                                                                                               | image when `img` present, else `initials(name)` (first letter of the first two words, upper-case — the filter frame shows "CO", "CT") — new Tier 1 helper — decided round 5 (A‑2)                                                                                                                                                                                                  | all                                      | —                             |
| 8   | Row · unverified dimming            | `dealer_custs.dealer_verified`                                                                                                                                                            | `opacity 0.6` when `false` (as v1)                                                                                                                                                                                                                                                                                                                                                 | all                                      | —                             |
| 9   | Row · "Settings" strip under avatar | user scope (auth store)                                                                                                                                                                   | `canOpenSettings(scope)` = scope ∈ {DPrimary, DAdmin} — new Tier 1 helper                                                                                                                                                                                                                                                                                                          | DPrimary, DAdmin                         | —                             |
| 10  | Row · customer name                 | `cust_msts.cust_name`                                                                                                                                                                     | 1 line, tail ellipsis                                                                                                                                                                                                                                                                                                                                                              | all                                      | —                             |
| 11  | Row · daily tile (green)            | `so_msts` of the relation with `on_dt` inside the **IST calendar day** of the request: `Σ ptotal + Σ cs_reimb` (`getPtSum`/`getCsSum`)                                                    | server `today.amount` (2 dp); window computed on the server (decided 2026-09-03), no dates in the body. Label copy ("Daily Total" in the filter frame, "Daily Orders" in v1) is a design-session item                                                                                                                                                                              | all                                      | `₹ 0.00` when none            |
| 12  | Row · balance tile (blue)           | `dealer_custs.cust_bal` FY opening (`yearBalance`) + `month_crdrs` FY cumulative (the `calcFYCumulativeBal` rule)                                                                         | server `credit.boip` (2 dp); ledger rule lives in `api_v3/services/ledger_window.js` — v4 composes, never copies                                                                                                                                                                                                                                                                   | all                                      | skeleton                      |
| 13  | Row · credit donut + % label        | `dealer_custs.max_cr_lmt`, `dealer_custs.adv_dep`, `credit.boip`, `credit.pendingPOs` (`order_msts` PENDING/PROCESSING), `credit.uninvoicedSOs` (`so_msts` without `inv_id`/`gst_inv_id`) | `creditUtilization({ maxCrLmt, adv_dep, maxOut: boip + pendingPOs + uninvoicedSOs })` — exists and is tested in `src/helpers/Credit/`; UNLIMITED → flat bar; ratio > 0.85 → error colour (frame: 90 % red, 85 % and 65 % primary)                                                                                                                                                  | donut: all · % label: `credit.read` only | —                             |
| 14  | Row · "Blacklisted" chip            | `dealer_custs.hidden` — the **Blacklist** switch in Customer Settings (`CustSettings.js:1816-1824`)                                                                                       | shown when `blacklisted` is true; row dimmed like unverified; blacklisted customers stay in the list whenever they pass the filter — **decided round 7 (A‑8)**                                                                                                                                                                                                                     | all                                      | —                             |
| 15  | List end                            | `page.hasMore`                                                                                                                                                                            | footer spinner while the next page loads; nothing when `hasMore` is false                                                                                                                                                                                                                                                                                                          | all                                      | —                             |
| 16  | List empty                          | —                                                                                                                                                                                         | "No customers" (no filter) / "No customers match" (filter or search active) — strings in `strings.js`                                                                                                                                                                                                                                                                              | all                                      | illustration + retry          |
| 17  | List loading (first page)           | —                                                                                                                                                                                         | row skeletons ×12                                                                                                                                                                                                                                                                                                                                                                  | all                                      | —                             |
| 18  | Screen error                        | `errorRTK` message                                                                                                                                                                        | —                                                                                                                                                                                                                                                                                                                                                                                  | all                                      | full-screen error with retry  |
| 19  | Offline                             | —                                                                                                                                                                                         | design session decides (v1 has nothing)                                                                                                                                                                                                                                                                                                                                            | all                                      | banner, last data stays       |

### 2b. Credit sheet (opens on donut tap, `credit.read` only)

Decided 2026-09-03 (round 4): **rendered from the tapped row's `credit` object — no request on open, no refresh button.** The list's refresh paths (screen focus, pull-to-refresh, header refresh icon, return from a settings edit) are the sheet's refresh paths, so the sheet always agrees with the donut it opened from. Every element below is pure presentation of row data through `creditSummary(credit)` (Tier 1).

| #   | Element                         | Data                             | Derived? (formula)                                                                                                        | Loading / error                                                               |
| --- | ------------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 20  | Title "Credit Summary" + name   | row `cust.name`                  | —                                                                                                                         | —                                                                             |
| 21  | Utilisation bar + % + available | row `credit`                     | `creditUtilization(...)`; available = `pool − maxOut`; UNLIMITED → flat bar and no available                              | —                                                                             |
| 22  | Advanced Deposits               | `credit.adv_dep`                 | —                                                                                                                         | —                                                                             |
| 23  | Credit Limit by Dealer          | `credit.max_cr_lmt`              | hidden when UNLIMITED; "0" when BLOCKED (as v1)                                                                           | —                                                                             |
| 24  | Maximum Credit Limit            | —                                | `max_cr_lmt + adv_dep` (hidden when UNLIMITED)                                                                            | —                                                                             |
| 25  | Unpaid Invoices                 | `credit.boip`                    | —                                                                                                                         | —                                                                             |
| 26  | Unbilled Sales Orders           | `credit.uninvoicedSOs`           | —                                                                                                                         | —                                                                             |
| 27  | Pending Orders                  | `credit.pendingPOs`              | —                                                                                                                         | —                                                                             |
| 28  | Total Credit used               | —                                | `boip + uninvoicedSOs + pendingPOs`                                                                                       | —                                                                             |
| 29  | Balance Credit                  | —                                | `pool − maxOut` (hidden when UNLIMITED)                                                                                   | —                                                                             |
| 30  | "Updated HH:MM" footer          | list response `meta.generatedAt` | `formatUpdatedAt(iso)` → IST time of the list load (new Tier 1 helper) — decided round 5 (A‑7), replaces a refresh button | shown always; the design session decides whether ages > 5 min are highlighted |

### 2c. Filter sheet — **sub-spec `01b-customers-filter-sheet.md`, session to be scheduled**

Frame: `../designs/customers/02-filter-sheet.png` (shared 2026-09-03). What it fixes for **this** spec's API contract (round 7): three tri-state status toggles (Verified · Has Trans. · Blacklisted), five sorts in the frame (Creation Date · A/c Balance · Daily Total · Credit Total · Latest Order wise) plus Name (added round 8, not yet drawn) with one direction arrow on the selected sort, "\* At least one required", "Reset to Default". Everything about its layout, states and copy is planned in `01b`; the API keys it needs are already in §5.1 so the sheet session cannot change the contract except O‑2.

Fields v3 returns that **no element uses** and v4 therefore does not return: `dealer_id.{dealer_name, oil_do, dealer_img}`, `cust_id.otp_mgr`, `cust_code` (search is by name only — decided 2026-09-03), `ftank_amt`, `cust_verified`, `monthly`, `unapproved` (badge dropped 2026-09-03, confirmed round 7), `createdAt` (sort happens on the server), `closed` (a model field nothing writes — round 6), `hasTrans` (a filter input, never displayed), raw `cs_reimb`/`dvr_otp`/`products` (folded into `tags`).

Rule: **if it is not in this table, the API does not return it.**

## 3. What the user can do ⛔

| #   | Action                                                                                                            | Trigger                               | Precondition (business rule)                                      | API command / call                                                              | Optimistic? | Success feedback                                          | Failure feedback               |
| --- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------- | ----------- | --------------------------------------------------------- | ------------------------------ |
| 1   | Search by customer **name**, matching anywhere, case-insensitive                                                  | typing (debounced)                    | —                                                                 | read model body `q`                                                             | n/a         | list replaced from page 1, scrolled to top; totals follow | screen error                   |
| 2   | Status filters, each tri-state any / only / exclude: **Verified · Has Trans. · Blacklisted**                      | filter sheet → Done                   | —                                                                 | read model body `filters` **+** `PUT /api/v4/users/prefs/dealer_customers`      | n/a         | list refetches from page 1; badge and totals update       | screen error; pref save silent |
| 3   | Sort: **Creation Date** (default) · Name · A/c Balance · Daily Total · Credit Total · Latest Order wise, asc/desc | filter sheet → Done                   | —                                                                 | read model body `sort`, `dir` **+** `PUT /api/v4/users/prefs/dealer_customers`  | n/a         | list refetches from page 1                                | as above                       |
| 4   | Reset to Default                                                                                                  | filter sheet button                   | —                                                                 | read model with defaults **+** `PUT …/prefs/dealer_customers` with the defaults | n/a         | badge disappears; list refetches                          | as above                       |
| 5   | Load next page (infinite scroll, 12 rows per page)                                                                | end reached                           | `page.hasMore`                                                    | read model with `cursor`                                                        | n/a         | rows appended                                             | footer retry                   |
| 6   | Refresh                                                                                                           | pull-to-refresh · header icon · focus | —                                                                 | refetch page 1 (cache invalidated)                                              | n/a         | spinner                                                   | screen error                   |
| 7   | Open customer settings                                                                                            | avatar / Settings strip               | scope ∈ {DPrimary, DAdmin} (client-side; `CustSettings` stays v3) | navigate `CustSettings`                                                         | n/a         | —                                                         | —                              |
| 8   | Open daily summary                                                                                                | daily tile                            | —                                                                 | navigate `DailySummary`                                                         | n/a         | —                                                         | —                              |
| 9   | Open ledger                                                                                                       | balance tile                          | —                                                                 | navigate `Accounts`                                                             | n/a         | —                                                         | —                              |
| 10  | Open credit summary                                                                                               | donut                                 | `credit.read` in the user's `amend_prem.allow`                    | none — v2 sheet rendered from the row's `credit` object (§2b)                   | n/a         | sheet                                                     | —                              |

**One command** (`PUT /api/v4/users/prefs/dealer_customers`, §5.2). Every other precondition is a client-side visibility rule and becomes a Tier 1 helper with a test. Server-side rules: tenancy (dealer from token), role (`authorize("dealer")`), and the prefs write touching only the caller's own document for the addressed company.

## 4. Design references ◌

- **Frames** (both 1× exports, 414 × 896; re-export at 2× before the design session if text is hard to read):
  - `../designs/customers/01-default.png` — the customer-side **"Dealers"** frame (shared 2026-09-03): header with search + Add Dealer + filter badge; summary strip Dealer 4/4 · Daily total · Total Balance; rows with CR/DR/OTP tags, oil-company logo, Settings strip, name, green daily tile, blue balance tile, credit donut with %, flat bar for unlimited. **Customers is designed "the same way"** with the substitutions at the top of §2. The row in this frame is the Customers row (round 7).
  - `../designs/customers/02-filter-sheet.png` — the **Customers filter sheet** (shared 2026-09-03): Close / Filters / Done; "Select Customer by Status" with Verified (✓) and Has Trans. (✕) toggles; "Select sorting Type" radio list Creation Date (selected, direction arrow) · A/c Balance · Daily Total · Credit Total · Latest Order wise; "\* Atleast one required"; "Reset to Default". The rows visible behind the sheet (initials avatar, "Daily Total"/"Balance" tiles, a numbered purple badge) are an older iteration — the badge is **not** part of the row (round 7).
  - If a live Figma file exists, add its URL to `../designs/README.md`.
- Design-system tokens: `src/theme/` does not exist yet (foundation F-APP-3, Phase 2). Colours seen in the frames — green daily tile, blue balance tile, primary purple, error red — map to tokens in the design session, not here.
- States that need their own frame: default, empty (no filter / with filter), first-page loading skeleton, next-page footer spinner, error, offline, unverified row, blacklisted row (chip), UNLIMITED row (flat bar), blocked row (`max_cr_lmt = 0`), credit sheet (capped / unlimited / blocked, with the "Updated" footer), font-scale 200 %. Filter-sheet states belong to `01b`.
- **Discussion-session notes (dated):**
  - **2026-09-03 — Step 1 session, round 1 (user + Fable).** Decisions:
    1. **Sequencing:** foundations first — Phase 0 → 1 → 2 per [[../02-foundations]], then Customers as screen 01. Spec agreed now, build waits for the foundations gate.
    2. **Location:** `src/screens/v2/Customers/` behind the registry and `screen_v2_customers` (D10 as written); the v1 path named in the request is what gets **retired**, not edited. _Superseded by 20 (round 3): the folder carries the role._
    3. **Roles:** everyone can view balances; Settings only DPrimary/DAdmin; credit % and sheet keep the `credit.read` gate.
    4. **Row actions:** Settings, daily tile, balance tile, credit sheet. The unapproved-payments badge (disabled in v1) is dropped — `unapproved` leaves the contract.
    5. **Credit sheet:** new v2 component (not `RelationCreditBS`).
    6. Closed/hidden excluded by default with an `includeClosed` body key. _Superseded by 28 (round 6): `closed` is a dead field and `hidden` means blacklisted._
    7. **Paging × sort:** all sorts server-side; infinite scroll with **12 rows per page**; status filters server-side.
    8. **Search:** server-side, matches **anywhere** (case-insensitive) — built like the vehicle search in `Customer/NewOrder/BSheets/SelectVehicle.js` / `api_v3/services/veh_trns.js:343-355` (escaped regex over the search field).
    9. **Preferences:** sort + dir + filters saved **per user per company**; the read model applies them when the body omits those keys.
    10. **Daily tile window:** server computes the IST day.
    11. **Tags:** `CR` = `cs_reimb`, `DR` = a discount set on a Diesel product, `OTP` = `dvr_otp`.
    12. **Summary strip:** count = matching / all; Daily total and Total Balance over **all** relations. _Totals part superseded by 24 (round 5)._
    13. **No Add Customer** on the dealer side; the customer-side Dealers screen is a future screen that will reuse this one's components.
    14. **Branches:** `api_v4_foundations` (from `api_tdd` @ `ecdd3ae`) and `app_v4_foundations` (from `app_tdd` @ `8b6831df`) created 2026-09-03; per-screen branch layout decided later.
  - **2026-09-03 — round 2 (user's follow-up).** Amendments: 15. **Search by name only**, not code (`cust_code` leaves the contract; placeholder "Search Customer name"). 16. **`DR` tag** is driven by the product's **PRIMARY category = "Diesel"** (`prod_msts.categories`), not by a product named HSD — a dealer can have several Diesel products; any of them with a discount on the relation sets the tag. 17. Credit sheet fetches fresh data on every tap via a second read model. _Superseded by 22 (round 4)._ 18. **Preferences storage:** the user asked whether a new collection is better than `users.companies[]`. Fable recommended **a new collection `user_prefs`**, one document per user × company, unique index `{ user_id: 1, co_id: 1 }` — structure and reasoning in §5.2. _Confirmed in round 5 (A‑5)._ 19. **Largest live dealer has 130 relations** → O‑1 resolved: the per-request pass over all relations (constant round trips) is acceptable; no cached balance needed. A perf test pins the round-trip count and the PR records the staging p95 for that dealer.
  - **2026-09-03 — round 3 (user's follow-up).** 20. **Location (supersedes 2):** the screen belongs to the dealer app, so the folder carries the role like the rest of the app: **`src/screens/v2/Dealer/Customers/`**, registry key **`Dealer/Customers`**, toggle **`screen_v2_dealer_customers`**. D10, the template, the foundations and the playbook now read `src/screens/v2/<Role>/<Name>/`, registry key `<Role>/<Route>`, toggle `screen_v2_<role>_<slug>` — required anyway because `Orders`, `Invoices` and `Payments` are route names in both role trees, so a bare route name cannot key the registry. 21. **`user_prefs` structure** requested — written out in §5.2 (one doc per user × company; `screens.dealer_customers` key named after the toggle; enums guarded by the v4 route schema, not the model). The command path follows the key: `PUT /api/v4/users/prefs/dealer_customers`.
  - **2026-09-03 — round 4 (user's follow-up).** 22. **Credit sheet = row data (A‑6 decided; supersedes 17).** User: "if we are efficient with single endpoint we will go with it." No second read model, no request on open; the per-customer credit endpoint, its test file and its store query are removed from this spec. Size returns to **S**. 23. **Refresh button in the sheet — no** (user asked; Fable recommended against: a refresh needs either the endpoint just removed or a page-1 refetch of the list, which recomputes all relations, resets the infinite-scroll pages and may drop the tapped row off page 1). Instead the sheet shows **"Updated HH:MM"** from the list response's `meta.generatedAt` (A‑7). _Confirmed in round 5._
  - **2026-09-03 — round 5 (user's follow-up: "keep page constant to 12 for api as well. total counts all relations but the filtered relation updates the daily total and total balance sum. rest is all ok").** 24. **Summary totals follow the filter (supersedes the totals part of 12):** `summary.all` still counts every relation of the dealer; `summary.matching`, `summary.dailyTotal` and `summary.totalBalance` are computed over the relations that pass the current `q` + `filters` — across all pages, not only the rows loaded so far. 25. **Page size is a constant 12 on the API too (A‑4 changed):** the read model has no `limit` key; `PAGE_SIZE = 12` is the endpoint's constant and `meta.limit` echoes 12. D6's "default 25, max 100" stays the general rule for other v4 lists; this screen's endpoint is fixed by spec. 26. **"Rest is all ok" → A‑1** (count universe), **A‑2** (avatar = `cust_img` with initials fallback), **A‑5** (`user_prefs` collection as written in §5.2), **A‑7** ("Updated HH:MM" footer) — **confirmed**. A‑3 (hidden rows never shown) was also confirmed, but on a wrong premise — reopened as A‑8 in round 6.
  - **2026-09-03 — round 6 (user: "count as two numbers. one filtered count and one total all relation count. what are hidden rows?").** 27. **Count = two numbers** — the spec's row 3: `summary.matching` (after filter + search) and `summary.all` (every relation). Confirmed. 28. **What `hidden` is (found in the code, supersedes 6 and A‑3):** `dealer_custs.hidden` is the **Blacklist switch** in Customer Settings (`CustSettings.js:1816-1824` writes `{ hidden: !blackListed }`); the order service refuses that customer's orders with "Please contact Dealer" (`api_v3/services/order_msts.js:265`). It is not a "soft delete". `dealer_custs.closed` ("transaction ended") has **no writer anywhere** in the API, the app or the web — a dead field. Consequences: `closed` leaves the contract; blacklist becomes a filter.
  - **2026-09-03 — round 7 (user: "a-8 is good we show blacklisted customer if filter pass. also added image for filter" + answers on the filter frame).** 29. **A‑8 decided:** blacklisted customers are shown whenever they pass the filters, with the chip and dimming (row 14); they count in `all`, and in `matching` and the totals when they pass. A third status toggle **Blacklisted** joins Verified and Has Trans. in the sheet. 30. **Filter frame read** (`02-filter-sheet.png`): status toggles are **tri-state** (blank = any, ✓ = only, ✕ = exclude), three of them; sorts are **Creation Date (default) · A/c Balance · Daily Total · Credit Total · Latest Order wise**; one direction arrow on the selected sort; "Reset to Default". The `name` sort Fable had proposed is **dropped** (not in the frame). _Re-added by the user in round 8 (35)._ 31. **"Has Trans." = any sales order, invoice or payment in the current financial year.** Correction to Fable's "no extra query" claim, on the user's challenge ("this screen does not pull ledger screen data"): the list read model does read the **ledger buckets** — `credit.boip` (the balance tile) is the FY opening plus the FY `month_crdrs` buckets, fetched once for all customers in one grouped aggregate — so _invoices and payments this FY_ are already known per customer (a customer with any FY bucket has them). _Sales orders this FY_ are **not** already loaded (only today's and the unbilled ones are), so one extra grouped query over `so_msts` for the FY is needed: `{ cust_id, count, lastOnDt }` per customer. That single query also serves "Latest Order wise" if O‑2 lands on sales orders. Round trips stay constant (≈ 9). 32. **"Latest Order wise" definition deferred (O‑2):** user: "by default use creation date. then we have options to sort in image. we will plan the bottom sheet separately." The key `latestOrder` is reserved in the sort enum now; its date source (newest sales order `on_dt`, newest order request, or newest of any transaction) is fixed in the filter-sheet session and recorded here before "start API for customers". Its API test is `it.todo` until then. 33. **Row = the Dealers frame's row:** donut + %, **no numbered badge**; the rows behind the filter sheet are an older iteration. `unapproved` stays out of the contract. 34. **Filter sheet gets its own sub-spec** `01b-customers-filter-sheet.md` (per the playbook's L-screen rule applied to one sheet): layout, states, copy and the tri-state control. It cannot change §5.1 except O‑2.
  - **2026-09-03 — round 8 (user: "ok add name sort as well").** 35. **`name` sort added** (supersedes the drop in 30): key `name`, `cust_name` lower-cased, `asc` = A → Z. Six sorts in the contract; the filter sheet (`01b`) gains a "Customer Name" option — its position in the list and its label are `01b` decisions.
  - **2026-09-03 — "spec agreed"** (user, after round 8). O‑2 stays open by agreement and is owned by `01b`. Step 1 closed.

## 5. API contract (v4) ⛔

### 5.1 Read model — the list

```
POST /api/v4/screens/customers                       (body carries filters → POST, per D2)
Auth: Bearer (protect) · Roles: authorize("dealer") · Tenant: dealer_id = tenantOf(req).dealer_id — never from the body
Page size: PAGE_SIZE = 12, an endpoint constant (round 5) — there is no `limit` key; sending one is an unknown key → 400
Body (house DSL, unknown keys rejected at every level):
  {
    q?:       string, 1–60 chars, trimmed                                   // matches anywhere, case-insensitive, on cust_msts.cust_name only
    filters?: {                                                             // omitted ⇒ saved pref ⇒ {} (no filter); each key tri-state:
      verified?:    boolean,                                                //   absent = any · true = only verified · false = only unverified
      hasTrans?:    boolean,                                                //   absent = any · true = has FY transactions · false = has none   (round 7)
      blacklisted?: boolean                                                 //   absent = any · true = only blacklisted · false = exclude       (A‑8)
    },
    sort?:    "createdAt" | "name" | "balance" | "daily" | "credit" | "latestOrder"  // omitted ⇒ saved pref ⇒ "createdAt"; latestOrder pending O‑2
    dir?:     "asc" | "desc",                                               // omitted ⇒ saved pref ⇒ "desc"
    cursor?:  string                                                        // opaque, from page.next
  }
200:
  {
    success: true,
    data: {
      summary: {
        all:          number,   // every relation of the dealer (blacklisted included) — never changes with q/filters
        matching:     number,   // relations passing q + filters
        dailyTotal:   number,   // Σ today.amount over the matching relations, all pages   (round 5)
        totalBalance: number    // Σ credit.boip  over the matching relations, all pages   (round 5)
      },
      customers: [
        {
          id:          { dealer_id: string, cust_id: string },                           // exit-point params
          cust:        { id: string, name: string, img: string|null },
          verified:    boolean,                                                          // dealer_custs.dealer_verified
          blacklisted: boolean,                                                          // dealer_custs.hidden (A‑8)
          tags:        { cr: boolean, dr: boolean, otp: boolean },
          today:       { amount: number },                                               // IST day, 2 dp
          credit:      { max_cr_lmt: number|null, adv_dep: number, boip: number, pendingPOs: number, uninvoicedSOs: number }   // also feeds the credit sheet (§2b)
        }
      ]
    },
    page: { next: string|null, hasMore: boolean },
    meta: { generatedAt: ISO, limit: 12, applied: { sort, dir, filters }, prefsSource: "body" | "saved" | "default" }   // generatedAt is shown in the credit sheet
  }
Errors: 400 VALIDATION (details[] with every path) · 401 UNAUTHENTICATED · 403 FORBIDDEN_ROLE (customer or superadmin bearer)
Partial failure policy: nothing optional — summary, today and credit are the screen's purpose; any sub-query failure fails the request.
```

**Filter definitions** (all evaluated on the server, per relation):

| `filters` key | true means                                                                                                                                                                                  | false means            |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| `verified`    | `dealer_custs.dealer_verified === true`                                                                                                                                                     | `=== false`            |
| `hasTrans`    | the relation has **at least one** of: a `month_crdrs` bucket in the current FY with `drttl` or `crttl` ≠ 0 (an invoice or a payment this FY), or a `so_msts` with `on_dt` in the current FY | none of those          |
| `blacklisted` | `dealer_custs.hidden === true`                                                                                                                                                              | `=== false` (or unset) |

**Sort keys** (ties broken by `cust_id` ascending; cursor = base64url `{ k, id }`, `PAGE_SIZE + 1` probe, no `countDocuments`):

| `sort`        | key                                                                                                                                                                                                                                                                         |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `createdAt`   | `dealer_custs.createdAt` — **default**, `desc`                                                                                                                                                                                                                              |
| `name`        | `cust_name` lower-cased (added round 8; `asc` = A → Z)                                                                                                                                                                                                                      |
| `balance`     | `credit.boip`                                                                                                                                                                                                                                                               |
| `daily`       | `today.amount`                                                                                                                                                                                                                                                              |
| `credit`      | utilisation ratio: UNLIMITED → 0; `max_cr_lmt + adv_dep` ≤ 0 → 1; else `(boip + pendingPOs + uninvoicedSOs) / (max_cr_lmt + adv_dep)` — the pool rule the v3 order check already applies; the read model reuses that exported helper (found in Step 2), never a second copy |
| `latestOrder` | **O‑2 — defined in the filter-sheet session.** Candidate: newest `so_msts.on_dt` per customer (comes free from the `hasTrans` query); alternatives: newest `order_msts.createdAt`, newest of any transaction. Customers with none sort last in both directions              |

Because `balance`, `daily`, `credit` and `latestOrder` are computed, and the totals need every matching relation anyway, the read model does **one pass** per request: load the dealer's relations (≤ 130 today) → `summary.all` → compute `today`, `credit`, `hasTrans` and `lastOrderAt` for all of them in constant round trips → filter (`filters`, `q`) → `summary.matching`, `dailyTotal`, `totalBalance` over the filtered set → sort → keyset slice of 12. Rows can shift between pages when a payment lands mid-scroll; accepted for this screen.

**Composition rule** (from [[../00-overview#Risks|00 §Risks]]): the read model must **not** call `dlrCusts` or `allRelationCurrBal` (3 awaits × N relations). Constant round trips regardless of N, all `$in`/grouped by `cust_id`, run through `runParallel` after `dealer_custs.find`:

1. one `month_crdrs` aggregate for the FY grouped by `cust_id` → balance (must equal `calcFYCumulativeBal` per relation — the oracle test) **and** the invoice/payment half of `hasTrans`
2. `pendingPOlist({ dealer_id })` (already grouped)
3. `uninvoicedSOlist({ dealer_id })` (already grouped)
4. the two `so_msts` IST-day aggregates (`getCsSum`, `getPtSum`) → `today.amount`
5. **one `so_msts` FY aggregate** grouped by `cust_id` → `{ count, lastOnDt }` → the sales-order half of `hasTrans` and (pending O‑2) `latestOrder`
6. `prod_msts.find({ dealer_id, categories: { $elemMatch: { group_name: "PRIMARY", name: "Diesel" } } })` projected to `_id` → `tags.dr`
7. `cust_msts.find({ _id: { $in } })` projected to `cust_name cust_img`
8. the caller's `user_prefs` doc, only when the body omits `sort`/`dir`/`filters`

`yearBalance` (opening) is pure and runs per row. Any change needed inside `ledger_window.js` is a separate test-first PR (D13).

### 5.2 Commands

```
PUT /api/v4/users/prefs/dealer_customers        (route param is an enum of screen keys — one entry per shipped v2 screen, each with its own body schema)
Auth: Bearer · authorize("dealer") · targets the caller (req.loggedInUser._id) and tenantOf(req).co_id — no ids in the body
Body: { sort: <sort enum>, dir: "asc"|"desc", filters: { verified?: boolean, hasTrans?: boolean, blacklisted?: boolean } }   (sort, dir, filters required; filters may be {}; unknown keys → 400)
200: { success: true, data: { prefs: { sort, dir, filters } } }
Idempotency: full replace by nature (PUT) — no Idempotency-Key
Write: UserPrefs.findOneAndUpdate({ user_id, co_id }, { $set: { "screens.dealer_customers": { ...body, updatedAt: now } } }, { upsert: true, returnDocument: "after" })
Side effect on Mongo (assert in test): exactly one user_prefs doc for { user_id, co_id }; screens.dealer_customers equals the body; a second company's doc untouched; other keys under screens untouched
Invalidation: none. The app sends explicit sort/dir/filters after a change; the list read model reads prefs only when the body omits them (one indexed findOne inside runParallel).
"Reset to Default" = this PUT with { sort: "createdAt", dir: "desc", filters: {} }.
```

**Storage — `models/user_prefs.js` (confirmed round 5; additive file, listed for approval in the brief). One document per user × company:**

```js
const UserPrefsSchema = new Schema(
  {
    user_id: { type: ObjectId, ref: "users", required: true }, // from the bearer, never from the body
    co_id: { type: ObjectId, required: true }, // from tenantOf(req) (the x-co-id company), never from the body
    screens: { type: Object, default: {} }, // Mixed on purpose — see rules below
  },
  { timestamps: true, minimize: false, strict: true },
)
UserPrefsSchema.index({ user_id: 1, co_id: 1 }, { unique: true })
```

As stored, after one save from this screen:

```json
{
  "_id": "…",
  "user_id": "6a4e…",
  "co_id": "6a4ec1673fafcaa9084668ce",
  "screens": {
    "dealer_customers": {
      "sort": "balance",
      "dir": "asc",
      "filters": { "verified": true, "hasTrans": false },
      "updatedAt": "2026-09-03T12:50:00.000Z"
    }
  },
  "createdAt": "…",
  "updatedAt": "…"
}
```

Rules:

- **Key naming:** `screens.<role>_<slug>`, the toggle name without its `screen_v2_` prefix (`dealer_customers` ↔ `screen_v2_dealer_customers`). A dealer company's doc holds only dealer-screen keys; a customer company's doc holds keys such as `customer_dealers`. No clash, no role field needed — the company decides the role.
- **`screens` is `Mixed` on purpose.** The route's v4 schema (D7 house validator, unit-tested) is the single guard for each key's enums. A new screen adds a route-param entry and a schema file; the model never changes again. `minimize: false` keeps `screens: {}` on a fresh doc.
- **Read path:** `UserPrefs.findOne({ user_id, co_id }, { "screens.dealer_customers": 1 }).lean()` inside the list read model's `runParallel`; a missing doc or key ⇒ defaults and `prefsSource: "default"`. Each key carries its own `updatedAt` so a stale pref can be diagnosed without the doc's timestamps.
- **Isolation:** nothing else reads the collection — auth, `check_user_company_status`, the 30-second user cache and the login/updaterx fixtures are untouched. Orphan docs after a user or company is removed are harmless and out of scope.

Why a separate collection rather than `users.companies[].prefs` (Fable, 2026-09-03): the users document is the auth document — `api_v3/auth.js` loads it on every request and caches it for 30 s, `check_user_company_status` reads `companies[]` on every request, and every login/`updaterx` fixture pins its shape. Preferences are high-write, low-value data; putting them there means every preference save invalidates the auth cache and grows the object attached to `req.loggedInUser`, and the schema change is a gated edit to the most sensitive model in the repo. A `user_prefs` doc per user × company is additive, indexed for a single upsert, invisible to auth, and future screens add a key under `screens` instead of another model change.

### 5.3 Test list — API (write these first, watch them fail)

`test/api_v4/screens/customers.test.js`

- [ ] happy path: dealer bearer, empty body → 200; `summary`, every row key in §5.1 present; numbers are numbers (2 dp); `max_cr_lmt: null` preserved (not coerced to 0); `meta.applied` = `{ sort: "createdAt", dir: "desc", filters: {} }`, `prefsSource: "default"`, `meta.limit === 12`; `meta.generatedAt` is a valid ISO instant
- [ ] tenancy: rows are only the token dealer's relations; `dealer_id` in the body → 400 VALIDATION (unknown key); customer bearer → 403 FORBIDDEN_ROLE; superadmin bearer → 403
- [ ] validation: `filters.verified: "yes"` → 400 with path `filters.verified`; `filters.closed: true` → 400 (unknown key); `limit: 100` in the body → 400 (unknown key — page size is a constant); `sort: "code"` → 400; `q` of 61 chars → 400; every failure listed in `details[]`
- [ ] filter `verified`: `true` returns only `verified: true`, `false` only `verified: false`, absent both; `summary.matching`, `dailyTotal` and `totalBalance` follow; `summary.all` does not change
- [ ] filter `hasTrans`: a relation with only a FY invoice → true; only a FY payment → true; only a FY sales order (no invoice yet) → true; a relation whose only activity is in the previous FY → false; a brand-new relation → false
- [ ] filter `blacklisted` (A‑8): a relation with `hidden: true` is returned when the filter is absent, with `blacklisted: true`; `true` returns only such rows; `false` excludes them; it counts in `summary.all` always and in `matching`/totals when it passes
- [ ] filters combine with AND: `{ verified: true, blacklisted: false }` returns verified, non-blacklisted rows only
- [ ] search: `q: "ust"` matches "Customer One" anywhere, case-insensitive; `q: "2"` does **not** match a customer whose `cust_code` is 2 (name only); regex metacharacters in `q` are literal (`"a.b"` matches nothing); `dailyTotal`/`totalBalance` cover only the matches
- [ ] sort: `createdAt`, `name`, `balance`, `daily`, `credit` — both directions, pinned against the seeded values; `name` is case-insensitive ("alpha" sorts before "Beta"); ties resolve by `cust_id`
- [ ] `it.todo("latestOrder sort — O‑2, defined in the filter-sheet session")` — the only todo; must be resolved before the API PR
- [ ] pagination: 13 seeded relations → page 1 has exactly 12 rows and `hasMore: true`; page 2 has 1 row, disjoint from page 1, `next: null`; `summary` identical on both pages; malformed cursor → 400
- [ ] `today.amount`: a SO at 23:30 IST yesterday is excluded, one at 00:30 IST today is included (server IST window; no dates accepted in the body)
- [ ] `credit.boip` equals v3 `getCurrBalance().boip` for the same relation (v3 ledger rule is the oracle — no second implementation); `pendingPOs` / `uninvoicedSOs` likewise
- [ ] `summary.dailyTotal` = Σ `today.amount` and `summary.totalBalance` = Σ `credit.boip` over the **matching** relations across all pages (assert against page 1 + page 2 rows), and both equal the all-relations sums when no filter is set
- [ ] tags: `cr` mirrors `cs_reimb`; `otp` mirrors `dvr_otp`; `dr` true only with a `products[]` discount (`disc_type !== "none"`, `disc_val > 0`) on a product whose PRIMARY category is Diesel; a discount on a Petrol product does not set `dr`; a Diesel product with `disc_type: "none"` does not set `dr`
- [ ] prefs applied: after `PUT /users/prefs/dealer_customers { sort: "balance", dir: "asc", filters: { verified: true } }`, an empty-body read returns rows in that order, verified only, `meta.applied` echoing it and `prefsSource: "saved"`; a body key overrides (`prefsSource: "body"`)
- [ ] no fan-out: query count for a dealer with 30 seeded relations equals the count for 3 (spy on the driver; constant round trips); PR records the staging p95 for the 130-relation dealer
- [ ] contract fixture captured: `yarn fixtures:export --set v4` → `fixtures/api_v4/screens_customers.json` (a seed with ≥ 13 relations so `hasMore` is exercised, at least one blacklisted, one without FY transactions)
- [ ] mutation smoke recorded in PR: remove `scopeFilter` → tenancy tests red; remove the IST window → day test red; drop the Diesel category match → `dr` tests red; sum totals before filtering → the two totals tests red; drop the SO half of `hasTrans` → the "only a FY sales order" case red

`test/api_v4/commands/users_prefs.test.js`

- [ ] green: 200, Mongo side effect — a `user_prefs` doc for `{ user_id, co_id }` with `screens.dealer_customers` equal to the body; a second company's doc untouched; a second PUT replaces (one doc, not two); `filters: {}` is stored as `{}` (not dropped)
- [ ] red: customer bearer → 403; missing `dir` → 400; `sort: "boip"` → 400; `filters.hasTrans: "yes"` → 400; unknown key → 400
- [ ] replay: same PUT twice → identical doc (idempotent)
- [ ] read-through: covered by the "prefs applied" test above

## 6. Screen build plan ⛔

- **Folder:** `src/screens/v2/Dealer/Customers/` (round 3: the role segment mirrors `src/screens/Dealer/`) — `index.js`, `useScreenModel.js`, `strings.js`, `components/{CustomerRow,SummaryStrip,FilterSheet,CreditSheet,Tags}.js`, `__tests__/Customers.test.js`. `FilterSheet` is built to the `01b` sub-spec. New shared UI that other screens will reuse (the customer-side Dealers screen first): `src/components/v2/{MoneyTile,CreditDonut,SearchField,TriStateToggle}` — final list in the design session.
- **Pure logic to extract first (Tier 1, TDD):**
  - `initials(name)` → `src/utils/Text/initials.js`
  - `canOpenSettings(scope)`, `canReadCredit(user, co_id)` → `src/helpers/Permissions/`
  - `activeFilterCount({ sort, dir, filters })` → `src/helpers/Filters/` (a `Filters` folder already exists) — counts a non-default sort/dir as one and each present `filters` key as one
  - `creditSummary(credit)` → `src/helpers/Credit/` — pool, available, maxOut, the UNLIMITED/BLOCKED display flags for the sheet (extends the existing tested module)
  - `formatUpdatedAt(iso)` → `src/utils/Dates/` — IST "HH:MM" for the sheet footer
  - `creditUtilization` — exists in `src/helpers/Credit/`, reused, not re-tested; `formatCurrency`/`formatwosign`/`formatCreditPct` — exist in `src/utils/Currency`
- **RTK Query endpoints (Tier 2, MSW):** `src/store/apis/v4/customers.js` —
  - `getScreen_Customers` as a **query** with infinite-scroll merge (`serializeQueryArgs` ignoring `cursor`, `merge` appends, `forceRefetch` on cursor change — the pattern already in `src/store/apis/paginationHelpers.js`), `providesTags: ['relations']` so the v3 `update_dealer_custs` mutation fired from `CustSettings` (including the Blacklist switch) still refetches the list (D9 shared tags); the latest page's `summary` and `meta` replace the cached ones on merge
  - `putPrefs_Customers` mutation, no tags
  - Tests: URL `<API_URL>/api/v4/screens/customers`, POST body carries exactly the keys set (no `undefined` placeholders, **no `limit`**, `filters` only with the keys the user set), bearer + `x-co-id`, page 2 appended and de-duplicated, a new `q` resets to page 1, 403 → `errorRTK` path; prefs URL `…/users/prefs/dealer_customers` as PUT
- **Screen test (Tier 3, RNTL, decision cases only)** — uses the pulled `v4_screens_customers.json`:
  - one row per fixture customer; name, daily amount, balance formatted
  - summary strip shows `matching / all`, daily total, total balance from the fixture; after a filter change the strip shows the new fixture's totals
  - Settings strip shown for `DPrimary`, hidden for `DView`
  - credit % label shown with `credit.read`, hidden without; donut in both cases
  - tags render per fixture booleans; unverified row dimmed; blacklisted row shows the chip
  - UNLIMITED row shows the flat bar, not a donut
  - loading skeleton / empty (two strings) / error states
  - tapping the tiles and the avatar navigates with the exact v1 params (§1 exit points); avatar tap does nothing for `DView`
  - filter sheet Done → refetch with the chosen `filters`/`sort`/`dir` **and** one `PUT /users/prefs/dealer_customers`; Reset to Default → refetch with defaults **and** one PUT with defaults; badge count matches `activeFilterCount`
  - end reached with `hasMore: true` → second request carries `cursor`; rows appended
  - typing in search → one request after the debounce with `q`, list back at page 1
  - donut tap with `credit.read` → the sheet shows the row's five numbers, the derived totals and "Updated HH:MM" from `meta.generatedAt`, and **no request was made** (MSW `onUnhandledRequest: "error"` proves it); donut tap without `credit.read` → nothing opens
- **Cutover:** route name `Customers` unchanged; registered in `src/navigation/screenRegistry.js` under the key `Dealer/Customers` behind `screen_v2_dealer_customers` (default on); `src/navigation/Dealer/Main.js:141` switches to `resolveScreen`; old component and `RelationFilterBS.js` deleted the release after.

## 7. Definition of done

- [x] Spec agreed and dated (2026-09-03); both PNGs in `designs/customers/`
- [ ] O‑2 closed in `01b` and copied into §5.1 (before "start API for customers")
- [ ] API PR: tests first (red commit → green commit), fixture exported, flow-map rows added in `docs/testing.md`, `yarn test:full` green; `models/user_prefs.js` approved in the brief; staging p95 for the 130-relation dealer recorded
- [ ] App PR: Tier 1 → Tier 2 → Tier 3 tests, `yarn fixtures:pull`, `yarn test` green, no-network guard intact
- [ ] Manual: one request on screen open (v4), none on credit-sheet open, old screen still works on v3 for a v1.78 build
- [ ] Release gate green; screen listed in the release notes; `screens/README.md` row updated
