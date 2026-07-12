# Release Notes — v1.78

**Build:** Android versionCode 103 (versionName 1.78) · iOS build 8
**Range:** v1.77 → v1.78 (2026-05-08 → 2026-06-23) · 70 commits

---

## 📱 End-User Release Notes

### ✨ New: Advance Deposits

- Record and track **advance deposits** with a dedicated voucher type and a full ledger.
- View advance-deposit balances right from the **Accounts** balance header, and open the ledger from there.
- Each ledger entry shows the **counterparty name** and any **linked on-account voucher**; balances refresh automatically after an adjustment.
- New **Payment Acknowledgement** screen for confirming payments, available to users with the right access.
- "On Account" payments are now handled through the unified voucher flow, with payment details shown only after you pick a payment mode.

### 💳 Smarter Credit Limits

- Credit limits now support **three states**: _Unlimited_, _Limit Credit_, and _Capped_.
- A **credit-utilization bar** and a shared **Credit Summary** make it easy to see how much credit is used at a glance.
- Tap to **restore your last cap**, with the limit field always mirroring the real value.
- Advance deposits now count toward available **spending power** in credit utilization.

### 🚚 Faster Vehicles List

- Vehicles now load with **server-side pagination, search, and filters** plus smooth infinite scroll.
- Significantly faster scrolling and lower memory use thanks to list recycling.
- Search is streamlined to **registration number**, and the list jumps back to the top on a new search.
- When you add a new vehicle in an order, it's now **auto-selected** for you.

### 🏷️ Discounts

- Discount editing is consolidated into a single **bottom-sheet editor** that saves reliably on _Done_.
- The product and relation lists stay visible while data refreshes in the background — no more disappearing content.
- Clearer messaging when no rate is set.

### 📅 Product Rates

- The product calendar now shows the **carried-forward effective rate on every day**, even when no new rate was set that day.

### 🧰 Polish & Fixes

- Smoother bottom sheets — no more accidental **drag-to-dismiss** when scrolling lists or searching (iOS & Android).
- The bottom tab bar is now **hidden on create/edit screens** (orders, invoices, payments, vouchers) for a cleaner, more focused view.
- Pull-to-refresh only triggers on a **real pull**, and lists no longer flicker while loading more.
- Compact dates (e.g. `24 Jun'26`) and truncated long names in Payments.
- Fixed a stuck spinner when a PromptPay approval failed.
- Emergency OTP sheet now stays open after generating an OTP.
- Company name is now **required and trimmed** before saving.
- Various scroll-position, layout, and navigation fixes across Dealers, Vehicles, Orders, and the Error screen.

---

## 🛠️ Developer Release Notes

### Features

- **Advance Deposit module** (`advdep`)
  - New Advance Deposit voucher type, ledger view, and account-balance adjustment (`5e0ee266`).
  - New Payment Ack screen with scope-gated entry and advdep ledger UI (`1bd79d55`).
  - Advance Deposits entry surfaced in the Accounts balance header (`baf9f37e`); `AdvDepLedger` now opens on the current stack from Accounts (`98a60246`).
  - Consolidated "On A/c" payment into the voucher flow; removed standalone `PayOnAc` (`c5e87820`).
  - Payment details gated behind pay-mode selection (`607621b5`); adjustment flow & `NewPayAck` inputs reworked (`f0f6f790`).
  - Ledger header shows counterparty name; linked on-account voucher shown with ledger refetch after adjust (`733b8b5d`, `fc7b4e3a`, `6e1eb996`).

- **Credit limits & utilization**
  - Three-state credit limit model: unlimited / blocked / capped (`fdd9d3a8`).
  - Credit-utilization bar + shared Credit Summary sheet on relation settings (`687d4ff7`).
  - Tap-to-restore last cap; limit field mirrors real value (`9bc0ef3d`).
  - "Blocked" relabeled to "Limit Credit" (`a8a0edbf`); credit-usage % formatting unified via `formatCreditPct` (`8f3325bc`).
  - Advance deposit treated as spending power in utilization (`6a8109a8`); 0/empty amount handled on blur (`d662622b`); relation-credit balance fetched only when dealer+customer ids present (`953ab5fa`).

- **Vehicles — pagination & performance**
  - Paginated `veh_trns` endpoint with infinite scroll (`41eaa1df`); server-side pagination, search & filters (`169d9f02`).
  - `BottomSheetFlatList` → `FlashList` with recycling (`c02d257f`); dedicated req-count endpoint with parallelized fetches (`5d3d76ea`).
  - Scroll-to-top on result change; search simplified to reg-no (`7290e46e`); page-fetch dedupe + query-abort swallowing (`a297894b`).
  - NewOrder uses paginated `veh_trns` with targeted fetch (`066609c8`); query scoped to new `reg_no` to auto-select on add (`1f7ef15b`).
  - Cached vehicle lists patched in place instead of invalidating LIST (`fe947901`); list scroll handling reworked around FlashList v2 MVCP (`20615d06`); vehicle-type filter relation mapping fixed (`7d500be1`).

### Fixes

- **Discounts:** centralized edits in bottom sheet with cache/state-sync fixes (`d5448486`); single add/edit/remove mutation persisted on Done (`667e9bbd`); editor re-seeded on open & no-rate state clarified (`29ba2f62`); product list & relation kept visible during background refetch (`2d4ef5c3`, `1d1e7744`); error state cleared on category-sheet close (`3310415a`); relation refetched on pull-to-refresh (`0e03889c`).
- **Bottom sheets:** content panning kept enabled on Android (`0c85f8c4`); content panning disabled to prevent drag-to-dismiss on more sheets (`ec5a652a`); iOS drag-to-dismiss prevented on list-with-search sheets (`66bb55eb`).
- **Navigation:** tab bar hidden on order/invoice/payment create & edit (`d2fcce66`); bottom tab removed from new-voucher screen (`de8f7913`).
- **Hooks crash:** guard returns moved below hooks to fix "rendered fewer hooks" crash (`bab10574`).
- **Lists/refresh:** pull-to-refresh driven by real user pulls only (`766e1444`); pagination-fetch flicker stopped (`a4b51578`); detail screen no longer sticks at scale 0.8 on close (`abcf3dab`); Error menu offset, Dealers scroll restore & product reset (`ef824002`); saved scroll position reset before navigating to AddDealers (`b35f5f09`).
- **Orders:** zero-product orders prevented before rates load (`f49b482c`); totals gated on product selection + product picker refined (`8c4a7667`).
- **Payments:** stuck spinner cleared on PromptPay approve failure (`f34434ba`); compact `DD MMM'YY` date format & long-name truncation (`941a4aff`); emergency OTP sheet kept open after generating OTP (`1d3fcfc1`).
- **Product dates:** carried-forward effective rate shown on each calendar day (`7dd23348`, `435ad746`).
- **Forms/validation:** InviteUser autofill no longer leaks into background form (`5ae4662f`); company name validated as required & trimmed (`2a17273a`); local selection cleared when parent deselects dealer (`1aa35f71`); dealer-customer fetch skipped when ids missing + select-sheet formatting (`337c90b0`).
- **Error screen:** drawer menu surfaced when error screen hides navigator header (`8a84df1e`).
- **Vehicles UI:** green success text + InfoVehicle layout/typo fix (`12ba73be`).
- **Misc:** new-voucher add-driver error text color corrected (`de8f7913`).

### Chore / Docs

- iOS code signing cert & provisioning profile workflow documented (`48a53e58`); Ruby/CocoaPods toolchain documented, pods pinned to `bundle exec` (`5ba4abcb`).
- Release build bump: Android 102, iOS 8 (`d802e88e`) → current Android 103.

### PRs merged in this range

- #41 — veh_trns server-side vehicle pagination + NewOrder vehicle select
- #42 — Advance Deposit voucher, ledger & New Payment Ack
- #43 — centralize discount edits in bottom sheet, fix cache & state sync
- #44 — May 26 batch of UI and validation fixes
- #45 — credit max-limit handling on blur
