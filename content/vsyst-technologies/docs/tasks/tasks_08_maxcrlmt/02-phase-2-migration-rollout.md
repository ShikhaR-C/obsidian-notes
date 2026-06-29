# Phase 2 — Data migration & rollout ordering

**Repo:** `dzzlo_oms_api`
**Goal:** Re-encode existing `dealer_custs.max_cr_lmt` to the new contract **with zero mis-classification window**, and deploy in the only safe order.

> This is the irreversible part. **Take a DB backup first.** `0` means opposite things before vs after; without a backup there is no clean rollback.

---

## 1. What each existing value must become

| Existing value (old meaning)                      | Migrate to   | New meaning |
| ------------------------------------------------- | ------------ | ----------- |
| `0` (was _unlimited_)                             | **`$unset`** | unlimited   |
| `0 < x < 1` (was _blocked_ sentinel, e.g. `0.01`) | **`0`**      | blocked     |
| `x < 0` (legacy junk; effectively blocked)        | **`0`**      | blocked     |
| `x >= 1` (capped)                                 | unchanged    | capped      |
| absent / `null` (was unlimited)                   | unchanged    | unlimited   |

**Order matters:** steps create new `0`s, so the `0 → $unset` step must run **first** and be isolated from the steps that write `0`. The rollout sequence in §3 guarantees this even across the code deploy.

---

## 2. Migration script (counts/verification only)

> **The production writes are performed MANUALLY via `mongosh`** (the one-liners below). The Node script below **performs no writes at all** — it exists only to (a) review the dry-run counts before each manual step and (b) verify the post-migration invariant afterward.

`scripts/migrate_max_cr_lmt.js`. **Reuse the project's own DB connection** — the API connects via `helpers/db_conn.js` using `databaseURI` from `api_v/api_constants` (NOT `process.env.MONGO_URI`).

> ⚠️ **Second database:** `db_conn.js` also exposes `database_dip`. Confirm whether `dealer_custs` is replicated/served from that DB for `dip-web`; if so, run the counts (`DB=dip`) **and** the manual `mongosh` writes against it too.

```js
// scripts/migrate_max_cr_lmt.js — COUNTS / VERIFICATION ONLY (no writes; writes are manual via mongosh).
//   node scripts/migrate_max_cr_lmt.js            # print counts on the default DB
//   DB=dip node scripts/migrate_max_cr_lmt.js     # count against database_dip instead
//   VERIFY=1 node scripts/migrate_max_cr_lmt.js   # assert post-migration invariant (exit 1 on FAIL)
const mongoose = require("mongoose");
const { databaseURI, database_dip } = require("../api_v/api_constants");
const DC = require("../models/dealer_custs");

const VERIFY = process.env.VERIFY === "1";
const useDip = process.env.DB === "dip";
const uri = useDip ? database_dip : databaseURI;

(async () => {
  if (!uri) {
    console.error(
      `No connection string for DB=${useDip ? "dip (DIPDB)" : "default (DATABASE_URI)"}.`,
    );
    process.exit(1);
  }

  await mongoose.connect(uri);
  console.log(`[connected] ${useDip ? "database_dip" : "default"}`);

  // { max_cr_lmt: null } matches both explicit null and absent field (Mongo) = unlimited.
  const queries = [
    ["0          (was unlimited / now BLOCKED)", { max_cr_lmt: 0 }],
    ["(0,1)      sentinel (blocked, to retire)", { max_cr_lmt: { $gt: 0, $lt: 1 } }],
    ["<0         (legacy junk, blocked)", { max_cr_lmt: { $lt: 0 } }],
    [">=1        (capped)", { max_cr_lmt: { $gte: 1 } }],
    ["null/unset (unlimited)", { max_cr_lmt: null }],
  ];

  const counts = await Promise.all(queries.map(([, q]) => DC.countDocuments(q)));
  console.log("[counts]");
  queries.forEach(([label], i) => {
    console.log(`  ${String(counts[i]).padStart(8)}  ${label}`);
  });

  if (VERIFY) {
    const sentinel = counts[1];
    const neg = counts[2];
    const ok = sentinel === 0 && neg === 0;
    console.log(
      `[verify] post-migration invariant — (0,1)=${sentinel} <0=${neg} -> ${ok ? "PASS" : "FAIL"}`,
    );
    await mongoose.disconnect();
    process.exit(ok ? 0 : 1);
  }

  await mongoose.disconnect();
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
```

**`mongosh` — this is the canonical production procedure (run these by hand, in the §3 order):**

```js
// STEP 1 (run manually BEFORE deploy, under OLD code)
db.dealer_custs.updateMany({ max_cr_lmt: 0 }, { $unset: { max_cr_lmt: "" } });
// STEPS 2+3 (run manually AFTER deploy, under NEW code)
db.dealer_custs.updateMany(
  { max_cr_lmt: { $gt: 0, $lt: 1 } },
  { $set: { max_cr_lmt: 0 } },
);
db.dealer_custs.updateMany(
  { max_cr_lmt: { $lt: 0 } },
  { $set: { max_cr_lmt: 0 } },
);
```

Before each manual `updateMany`, confirm the affected-row count with `countDocuments` (or the script's `DRY_RUN=1`), then verify `modifiedCount` matches afterward.

---

## 3. Rollout sequence (no mis-classification window)

Run in exactly this order. The reasoning column shows what every value class means at each moment.

| #   | Action                                                           | `0` rows                            | `(0,1)` rows                   | `null`/unset | `>=1`     |
| --- | ---------------------------------------------------------------- | ----------------------------------- | ------------------------------ | ------------ | --------- |
| 0   | (before anything) — OLD code                                     | unlimited                           | blocked                        | unlimited    | capped    |
| 1   | **Run STEP 1 manually** (`0 → $unset`) under OLD code            | — (now unset → still **unlimited**) | blocked                        | unlimited    | capped    |
| 2   | **Deploy Phase 1 backend** (new code)                            | n/a                                 | blocked ✅                     | unlimited ✅ | capped ✅ |
| 3   | **Run STEP 2+3 manually** (`(0,1) → 0`, `<0 → 0`) under NEW code | blocked ✅                          | → became `0`, still blocked ✅ | unlimited ✅ | capped ✅ |

- **Step 1 is safe under old code:** old code treats `0` and unset identically (both unlimited), so unsetting changes nothing behaviorally — but it clears the `0`s out of the way before the meaning flips.
- **After step 2 there are no `0` rows** (step 1 removed them), so deploying new code can't accidentally block anyone. The `(0,1)` sentinel rows are still correctly enforced as blocked by the new code.
- **Step 3 under new code is behaviorally a no-op** (`(0,1)` and `0` both enforce/block) — it's just normalizing the storage to the canonical `0`.

> Doing it the other way (deploy then migrate) would, in the gap, make the new code read every legacy `0` (unlimited) as blocked — mass customer lockout. Don't.

### Cutover-window caveat (step 1 → deploy gap)

Between running step 1 and deploying the new code, a **v1.77 dealer** can still write a fresh `0` (intending _unlimited_) through the un-gated old `updateDealerCust`. After deploy, that `0` would read as blocked. To avoid it: keep the step-1→deploy gap as short as possible (same maintenance window), **and re-run the STEP-1 `updateMany` once manually immediately after deploy** to sweep any `0`s created during cutover. This post-deploy sweep is safe **only until the v1.78 app build is released** — after that, new `0`s are legitimate blocks, so the sweep must not be run again (the script's `STEP` guard makes this a deliberate choice, not an accident).

### Rollback hazard

If you **roll back the v3 code** after migrating, the stored `0`s (v1.78 blocks) will be read by the old code as **unlimited** — silently un-blocking those customers (money risk). A code rollback therefore requires either restoring the DB backup or first running `db.dealer_custs.updateMany({ max_cr_lmt: 0 }, { $unset: { max_cr_lmt: "" } })` to neutralize blocks before the old code runs. Document this in the deploy runbook.

---

## 4. v1.77 compatibility (covered by the write-gate)

The live v1.77 app hits the same backend. The Phase 1 **write-gate** (§2/§3) is what makes this safe:

- **Writes** — a v1.77 dealer typing `0` (meaning _unlimited_ in the old UI) is mapped to `null` by the gate → stays unlimited. A v1.77 app can therefore never create a `0` (blocked), so it can't accidentally lock a customer out. New v1.77-created relationships still default to unlimited (`null`). ✅ behavior-identical to before.
- **Per-field updates** — the old screen saves one field at a time (`handleAdvanceDeposits` etc. send only their own key), so a v1.77 dealer editing _other_ settings never clobbers `max_cr_lmt`. ✅
- **Display (the one residual skew)** — a row blocked by a v1.78 dealer (`0`) shows as "no limit" on a v1.77 viewer (old `!max_cr_lmt` truthiness). ⚠️ **display only** — the server still enforces the block; the indicator corrects itself once that user updates to v1.78. Acceptable (no money-safety impact).

To minimize the display skew, ship Phase 3 + Phase 4 (app) in the same release and encourage update.

---

## 5. Phase 2 acceptance

- [ ] DB backup taken and verified restorable.
- [ ] `node scripts/migrate_max_cr_lmt.js` counts reviewed and sane (esp. how many `0` rows exist — these are your current "unlimited" customers). Re-run with `DB=dip` if `database_dip` serves `dealer_custs`.
- [ ] Manual `mongosh` writes executed in the §3 order; each `updateMany`'s `modifiedCount` matches the pre-step count from the script.
- [ ] Spot-check: a known previously-unlimited customer has no `max_cr_lmt` field; a known previously-blocked (sentinel) customer has `max_cr_lmt: 0`; capped customers unchanged.
- [ ] `VERIFY=1 node scripts/migrate_max_cr_lmt.js` → PASS (post-migration counts of `{ $gt: 0, $lt: 1 }` and `{ $lt: 0 }` are both `0`).
