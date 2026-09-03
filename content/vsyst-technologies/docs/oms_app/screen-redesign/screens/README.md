# Screens index

One row per screen, updated at every gate (see [[../03-per-screen-playbook#Tracking]]). The spec's status line and this table are the only two places status lives.

| Screen                               | Size | Spec agreed | API PR | Design agreed | App PR | Shipped in | Old screen removed | Notes                                                                                                                                                                  |
| ------------------------------------ | ---- | ----------- | ------ | ------------- | ------ | ---------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [[01-customers\|Customers]] (dealer) | S    | 2026-09-03  | —      | —             | —      | —          | —                  | Step 1 closed 2026-09-03 (eight rounds, 35 decisions in spec §4); one read model (page constant 12, tri-state filters Verified/Has Trans./Blacklisted, six sorts incl. Name, totals follow the filter) + prefs command; credit sheet from row data; folder `src/screens/v2/Dealer/Customers/`; O‑2 ("Latest Order wise" date source) deferred to `01b` by agreement; both frames in `designs/customers/`; build waits for Phases 0–2 |
| `01b` Customers filter sheet (sub-spec) | — | — | — | — | — | — | — | Not started; frame `designs/customers/02-filter-sheet.png`; must close O‑2 before "start API for customers" |
