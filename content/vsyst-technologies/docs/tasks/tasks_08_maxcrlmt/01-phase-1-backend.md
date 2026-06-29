# Phase 1 — Backend (v3 only): enforcement, write normalization, create default

**Repo:** `dzzlo_oms_api`
**Goal:** Make the server treat `0 = blocked`, `null`/unset = unlimited, `>0 = capped` — on the order-credit check, on writes, and on new-relationship creation.

> Do NOT deploy this phase until you've read **Phase 2 (migration & rollout)**. Deploying before migration step 1 will instantly block every currently-unlimited (`0`) customer.

---

## 1. Order enforcement — `api_v3/services/order_msts.js`

Two near-identical blocks: **create** (~`781`) and **edit/process** (~`920`). In each, (a) drop `&& Number(...) !== 0` from the outer guard and (b) drop `!!dealer_cust.max_cr_lmt &&` from the inner `if`.

### 1a. Create block (~`781-799`)

**Current:**

```js
if (
  typeof dealer_cust.max_cr_lmt === "number" &&
  Number(dealer_cust.max_cr_lmt) !== 0
) {
  const [OrderSum, SOsum, invSum] = await Promise.all([
    currentOrderOutstanding(dealer_cust),
    currentSOOutstanding(dealer_cust),
    currentInvoiceBalance({ dealer_cust, providedDate: new Date() }),
  ]);
  const AdvanceDeposit = dealer_cust.adv_dep ? +dealer_cust.adv_dep : 0;
  const prevBal = +OrderSum + +SOsum + +invSum;
  const balSum = +prevBal + +finalAmount - +AdvanceDeposit;
  if (
    !!dealer_cust.max_cr_lmt &&
    Number(dealer_cust.max_cr_lmt) < Number(balSum)
  ) {
    throw new ErrorResponse(`Credit Limit Exceeded`, 404);
  }
}
```

**New:**

```js
// max_cr_lmt: null/unset = unlimited (skip) ; 0 = blocked ; >0 = capped.
if (typeof dealer_cust.max_cr_lmt === "number") {
  const [OrderSum, SOsum, invSum] = await Promise.all([
    currentOrderOutstanding(dealer_cust),
    currentSOOutstanding(dealer_cust),
    currentInvoiceBalance({ dealer_cust, providedDate: new Date() }),
  ]);
  const AdvanceDeposit = dealer_cust.adv_dep ? +dealer_cust.adv_dep : 0;
  const prevBal = +OrderSum + +SOsum + +invSum;
  const balSum = +prevBal + +finalAmount - +AdvanceDeposit;
  if (Number(dealer_cust.max_cr_lmt) < Number(balSum)) {
    throw new ErrorResponse(`Credit Limit Exceeded`, 404);
  }
}
```

### 1b. Edit/process block (~`920-938`)

Same two edits. Note this block's `prevBal` subtracts `oldAmt` — **keep that line unchanged**:

```js
if (typeof dealer_cust.max_cr_lmt === "number") {
  const OrderSum = await currentOrderOutstanding(dealer_cust);
  const SOsum = await currentSOOutstanding(dealer_cust);
  const invSum = await currentInvoiceBalance({
    dealer_cust,
    providedDate: new Date(),
  });
  const AdvanceDeposit = dealer_cust.adv_dep ? +dealer_cust.adv_dep : 0;
  const prevBal = +OrderSum + +SOsum + +invSum - +oldAmt; // unchanged
  const balSum = +prevBal + +finalAmount - +AdvanceDeposit;
  if (Number(dealer_cust.max_cr_lmt) < Number(balSum)) {
    throw new ErrorResponse(`Credit Limit Exceeded`, 404);
  }
}
```

**Why this is correct (decision 1 — advance deposit):** for a blocked customer (`0`), `0 < balSum` throws **unless** `balSum ≤ 0`, which happens exactly when advance deposit (and any credit balance) covers the order. So a blocked customer can still spend prepaid advance — the confirmed behavior — with no extra code.

**Boundary unchanged:** strict `<` means an order that lands `balSum` exactly on the limit is allowed (capped customers can reach their limit; blocked customers can place a `balSum ≤ 0` order).

**Enforcement is intentionally NOT version-gated.** It reads the _stored_ value, and after migration + the write-gate (§2/§3) every stored `0` is a deliberate `>= 1.78` block — so a `0` must enforce as blocked regardless of which app version places the order (a v1.77 customer ordering against a blocked relationship should still be blocked). The version gate lives only on the **write** funnels, where it prevents old apps from _creating_ a `0`.

---

## 2. Write normalization + v1.77 compatibility — `updateDealerCust` (~`1450`)

This funnel must do two things: (a) normalize the new contract, and (b) **stay compatible with the v1.77 app still in users' hands**. The old app's bare `TextInput` writes `0` to mean _unlimited_, so a `0` from a `<= 1.77` client must be mapped to `null` (unlimited) — never stored as blocked. Use the same `meta`→`version` gate already used across the API (e.g. `order_msts.js:743`, `email.js:36`).

### 2a. Pass `meta` from the controller

`api_v3/controllers/collections/dealer_custs_v1.js` → `UpdateDealerCust` (~`34`):

```js
exports.UpdateDealerCust = asyncHandler(async (req, res) => {
  let meta = null;
  try {
    meta = req.headers.meta ? JSON.parse(req.headers.meta) : null;
  } catch {}
  const data = await updateDealerCust({ body: req.body, params: req.params, meta });
  res.status(200).json({ success: true, data });
});
```

### 2b. Service: signature + gated normalization

`api_v3/services/dealer_custs.js` → change the signature to `exports.updateDealerCust = async ({ body, params, meta }) => {` and insert this **after** the `allow !== "permit"` / `cust_type` guards and **before** the `findOneAndUpdate` (~line `1483`):

```js
// v1.77-compat gate (same idiom as order_msts.js): old apps mean "0 = unlimited".
const version = !!meta && !!meta.version ? meta.version : null;
const testVersion = "1.510";
const isntTestv = `${version}` !== testVersion;
const legacyCredit =
  !!version && isntTestv && Number(version) <= Number(1.77); // <= 1.77 = legacy

// Normalize credit limit: '' / null -> unlimited (null) ; 0 -> blocked ; >0 -> capped (2dp).
// hasOwnProperty (not `!== undefined`) so we only touch it when the client actually sends it.
if (Object.prototype.hasOwnProperty.call(body, "max_cr_lmt")) {
  const raw = body.max_cr_lmt;
  if (raw === null || raw === "" || raw === undefined) {
    body.max_cr_lmt = null; // unlimited
  } else {
    const n = Number(raw);
    if (!Number.isFinite(n) || n < 0) {
      throw new ErrorResponse(`Invalid credit limit`, 400);
    }
    if (n === 0) {
      body.max_cr_lmt = legacyCredit ? null : 0; // old app: 0 = unlimited; new app: 0 = blocked
    } else {
      body.max_cr_lmt = Math.round(n * 100) / 100;
    }
  }
}
```

Notes:

- **A `<= 1.77` client can therefore never store a `0` (blocked)** — its `0`s become `null` (unlimited), exactly the old meaning. Only `>= 1.78` clients create blocks. This is precisely what makes the uniform enforcement in §1 safe.
- `version === null` (web admin / unknown client) → **not** legacy → new contract. `dip-web` is moved to the new contract in Phase 4, so this is correct.
- **Known limitation (inherited from the existing idiom):** `Number(version)` compares numerically, so it assumes 2-segment versions (`"1.77"` → `1.77`). A future 3-segment string (`"1.77.1"`) or a "1.100"-style bump would misparse. The whole codebase already uses this comparison (`order_msts.js` etc.), and `versionName` is currently 2-segment, so it's consistent — just don't switch to 3-segment `versionName` without revisiting every `Number(version)` gate.
- **Client must send `null` (never `undefined`) for Unlimited** — `JSON.stringify` drops `undefined` keys, so an `undefined` would never reach the body and the old value would persist. Phase 3 sends `null`.
- `runValidators: true` is already set; `null` is valid (optional field).
- `updateDealerCustAdvFilters` shares this risk **only if** its route is revived — currently commented out in `routes/collections/dealer_custs_v1.js:29`, so skip it.

---

## 3. New-relationship default (v1.77-gated) — `createDC` (~`1332`)

New rows default to **blocked** (decision 2) — **but only for `>= 1.78` clients.** A `<= 1.77` client creating a relationship expected the old _unlimited_ default; keep that for them so old apps behave exactly as before.

### 3a. Pass `meta` from the controller

`dealer_custs_v1.js` → `CreateDC` (~`29`):

```js
exports.CreateDC = asyncHandler(async (req, res) => {
  let meta = null;
  try {
    meta = req.headers.meta ? JSON.parse(req.headers.meta) : null;
  } catch {}
  const data = await createDC({ body: req.body, meta });
  res.status(200).json({ success: true, data });
});
```

### 3b. Service: signature + gated default

Change the signature to `exports.createDC = async ({ body, meta }) => {` and insert immediately **before** `const dealer_cust = await DC.create(body);` (~line `1360`):

```js
// New relationships: >= 1.78 default to BLOCKED (0); <= 1.77 keep the old UNLIMITED default.
if (
  body.max_cr_lmt === null ||
  body.max_cr_lmt === undefined ||
  body.max_cr_lmt === ""
) {
  const version = !!meta && !!meta.version ? meta.version : null;
  const legacyCredit =
    !!version && `${version}` !== "1.510" && Number(version) <= Number(1.77);
  body.max_cr_lmt = legacyCredit ? null : 0;
}
```

This is the single create funnel (`POST /dealer_custs` → `CreateDC` → `createDC`). The app's "add dealer" flows (`AddDealers.js:147`, `BSheets/AddDealer.js:224`) send `max_cr_lmt: undefined`, which JSON-drops to absent → this sets `0` for v1.78 apps, `null` for v1.77. ✅ No client change required for the default.

> **Do NOT use a Mongoose schema `default: 0`.** Migration step 1 (`0 → $unset`) leaves unlimited rows field-less; a schema default would be re-applied by any future full-document `.save()` on those rows, silently turning unlimited back into blocked. Defaulting in the service avoids this entirely.

---

## 4. Model doc only — `models/dealer_custs.js:84`

No behavioral change. Update the comment to record the contract:

```js
    max_cr_lmt: { type: Number }, // null/unset = unlimited ; 0 = blocked ; >0 = capped (rupees, 2dp)
```

(Optional hardening: `{ type: Number, min: 0 }` — redundant with the service-level `< 0` reject, and would surface as a Mongoose ValidationError instead of the clean `400`. Leave off unless you want belt-and-suspenders.)

---

## 5. Decision 3 — v1/v2 left untouched (residual risk)

`api_v1/controllers/App/order_msts.js:234,409` and `api_v2/controllers/collections/order_msts.js:342,530` still use the old `!!max_cr_lmt` / `!== 0` pattern, so **on those paths `0` still means unlimited** — a blocked customer ordering through a v1/v2 endpoint would NOT be blocked. The app's live order path is v3 (`order_msts/a/poso`, `/process/:id`), so this is acceptable per decision. **Before deploy, confirm no client build still posts orders to v1/v2.** If one does, either patch those four lines (same edit as §1) or retire the route.

---

## 6. Phase 1 acceptance

- [ ] Order create/process: customer with `max_cr_lmt = 0` and no covering advance → "Credit Limit Exceeded".
- [ ] Same customer with advance deposit ≥ order → order succeeds (decision 1).
- [ ] Customer with `max_cr_lmt = null`/unset → orders unrestricted.
- [ ] Customer with `max_cr_lmt = 50000` → blocked only past 50000.
- [ ] `PUT dealer_custs` with `max_cr_lmt: "-5"` or `"abc"` → `400 Invalid credit limit`.
- [ ] `PUT` with `"50000.999"` → stored `50001` (2dp); `null` → stored `null`.
- [ ] **v1.77 compat (write):** `PUT` with `max_cr_lmt: 0` and `meta` header `{"version":"1.77"}` → stored **`null`** (unlimited, old meaning). Same `PUT` with `{"version":"1.78"}` → stored **`0`** (blocked).
- [ ] **v1.77 compat (create):** `POST dealer_custs` without `max_cr_lmt`, `meta {"version":"1.77"}` → row `max_cr_lmt: null`; with `{"version":"1.78"}` (or no `meta`) → row `max_cr_lmt: 0`.
- [ ] `meta` header `{"version":"1.510"}` (test bypass) is treated as **new** contract (`0` → blocked).
