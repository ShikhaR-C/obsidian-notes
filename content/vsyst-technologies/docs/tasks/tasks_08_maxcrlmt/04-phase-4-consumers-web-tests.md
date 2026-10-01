# Phase 4 — All other consumers: app display, web admin, tests, verification

**Repos:** `dzzlo_oms_app`, `dip-web`, `dzzlo_oms_api/test`
**Goal:** Split every `null`-vs-`0` conflation so **Unlimited (null)**, **Blocked (0)** and **Capped (>0)** render and sort distinctly. This is the part where a single missed truthiness check leaves a blocked customer looking unlimited.

> **Status review — 2026-10-01.** Checked against app `main` @ `ea7e7222` (v1.79) and API `master` @ `6d41ce5` (v1.5.5). ✅ For the app and the API: the helper exists (and gained `creditSummary` for the v2 credit sheet), all seven listed app consumers use it, the API suites pin the contract, and the grep gates find one hit — in an unused component. dip-web rows (§4) not assessed; the device and web checks (§7) are ❔ except the server-side one, flipped. 2 new tasks in 00-overview (`T08-N1`, `T08-N2`). dip-web and other repos were not re-assessed.
> Legend: ✅ done · 🟡 partly done · ⬜ to do · 🆕 new · ⏸ deferred · ❌ dropped / superseded · ❔ unverifiable from the repos

---

## 1. Shared classifier helper (app) — do this first

**Status (2026-10-01):** ✅ `src/helpers/Credit/index.js` — `creditState`, `isUnlimited` / `isBlocked` / `isCapped`, `creditUtilization` with the deposit counted in the pool (`:33-38`), and `creditSummary` for the v2 credit sheet (`:66`); 24 tests in `src/helpers/Credit/__tests__/index.test.js`.

Create `src/helpers/Credit/index.js`:

```js
export const UNLIMITED = "UNLIMITED";
export const BLOCKED = "BLOCKED";
export const CAPPED = "CAPPED";

// null / undefined / '' -> UNLIMITED ; 0 -> BLOCKED ; >0 -> CAPPED
export const creditState = (maxCrLmt) => {
  if (maxCrLmt === null || maxCrLmt === undefined || maxCrLmt === "") {
    return UNLIMITED;
  }
  return Number(maxCrLmt) === 0 ? BLOCKED : CAPPED;
};

export const isUnlimited = (m) => creditState(m) === UNLIMITED;
export const isBlocked = (m) => creditState(m) === BLOCKED;
export const isCapped = (m) => creditState(m) === CAPPED;

// Utilization for the donut/bar. percent is 0..1.
// UNLIMITED -> no bar (0, atLimit false). BLOCKED -> full (1, atLimit true). CAPPED -> ratio.
export const creditUtilization = ({ maxCrLmt, adv_dep = 0, maxOut = 0 }) => {
  const state = creditState(maxCrLmt);
  if (state === UNLIMITED) return { state, percent: 0, atLimit: false };
  if (state === BLOCKED) return { state, percent: 1, atLimit: true };
  const creditAdv = Number(maxCrLmt) + Number(adv_dep);
  const denom = creditAdv > 0 ? creditAdv : 1;
  const ratio = Number(maxOut) / denom;
  const percent = ratio > 1 ? 1 : ratio < 0 ? 0 : ratio;
  return { state, percent, atLimit: ratio >= 1 };
};
```

## 2. The standard recipe (apply in each progress component)

**Status (2026-10-01):** ✅ applied — `limitZero = isUnlimited(…)` / `blockedMaxCrLmt = isBlocked(…)` in `RelationCreditBS.js:330-331`, `DealerSettings/index.js:867-868`, `NewOrder/components.js:841-842`, `Balance/Components.js:441`, `Customer/Dealers/components.js:324`.

Each of the components below has locals shaped like `limitZero` / `blockedMaxCrLmt` / `credit_adv` / `progressCent` / `finalProgress`. Replace those definitions with helper-backed ones that **preserve existing JSX** but fix the meaning:

```js
import { isUnlimited, isBlocked, creditState, BLOCKED } from '<rel>/helpers/Credit';
...
const limitZero       = isUnlimited(maxCrLmt);   // ONLY unlimited -> the "no limit" UI
const blockedMaxCrLmt = isBlocked(maxCrLmt);     // 0 -> blocked

// blocked shows a FULL bar; capped shows the ratio; unlimited handled by limitZero branch
const credit_adv = Number(maxCrLmt) + Number(adv_dep);
const roundCr_adv = Number(credit_adv) > 0 && Number(credit_adv) < 1 ? 1 : Number(Number(credit_adv).toFixed(2));
const progressCent = blockedMaxCrLmt
  ? 1
  : (isCappedRatio); // = the file's existing (maxOut / roundCr_adv) expression
const finalProgress = Number(progressCent) > 1 ? 1 : Number(progressCent);
```

And wherever the file computes the **red/error colour** (`pbcolor`, `isRed`, etc.), include blocked:

```js
const isRed = blockedMaxCrLmt || Number(progressCent) > 0.85; // blocked always red
```

> Net effect on rendering: **Unlimited** → unchanged "no limit" visual (flat line / hidden). **Blocked** → full red bar (previously this was the rare `0.01` sentinel path; now it's `0`). **Capped** → unchanged ratio bar.

## 3. Per-file edits (app)

**Status (2026-10-01):** ✅ all seven files import `helpers/Credit`; `getProgress` uses `creditUtilization` (`src/screens/Dealer/Customers/index.js:37-47`); the text displays read "Unlimited" / "0" / amount (`DealerSettings/index.js:817-822`, `DealerSettings/components.js:290-297`, `RelationCreditBS.js:472` inside the non-unlimited branch) — blocked prints `0`, not the planned "Blocked". On the v2 Customers screen (the default) the ring is `CreditAvatar`: CAPPED arc, BLOCKED full error ring, UNLIMITED dotted (10 tests).

| File                                                    | Anchor                              | Edit                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `screens/Common/RelationList/RelationCreditBS.js`       | `76-77`, `332-333`, **`491`**       | **Stop conflating:** `const maxCrLmt = dealer_cust ? dealer_cust.max_cr_lmt : null;` (was `... ? : 0`). Apply the recipe at `332-333` + colour. **`:491`** `{formatwosign(maxCrLmt)}` is a raw-value text display → show "Unlimited"/"Blocked"/amount (state-aware).                                                                                                                                                                                                                                                                                                                                           |
| `components/Balance/Components.js`                      | `433-458`                           | Apply recipe (`blockedMaxCrLmt`, `limitZero`, `progressCent`, `finalProgress`, `pbcolor`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `screens/Customer/Dealers/components.js`                | `314-340`                           | Apply recipe (`blockedMaxCrLmt`, `credit_adv`, `progressCent`, `limitZero`, `pbcolor`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `screens/Customer/NewOrder/components.js`               | `838-855` (`CreditProgressORDER`)   | `limitZero = isUnlimited(maxCrLmt)`; add `blockedMaxCrLmt`; blocked → full bar + red `ImpNote`. The early `if (!canPress && limitZero) return <></>` now hides only for **Unlimited** (blocked will render the full bar).                                                                                                                                                                                                                                                                                                                                                                                      |
| `screens/Dealer/Customers/index.js`                     | `32-49` (`getProgress`)             | Replace body: `const { percent } = creditUtilization({ maxCrLmt: dealer_cust?.max_cr_lmt, adv_dep: dealer_cust?.adv_dep, maxOut: Number(dealer_cust?.boip ?? 0) + Number(dealer_cust?.pendingPOs ?? 0) + Number(dealer_cust?.uninvoicedSOs ?? 0) }); return percent;` (removes the `?? 0` that made unlimited and blocked indistinguishable). Note `creditUtilization` clamps `percent` to `1`, so two _over-limit_ customers tie in the "Credit Limit" sort (the old code returned an uncapped ratio). If exact over-limit ordering matters, return the raw `maxOut/creditAdv` for the `CAPPED` case instead. |
| `screens/Customer/Dealers/DealerSettings/index.js`      | `123`, `132`, `136-150`             | Preserve raw value: `const CUSTmax_cr_lmt = dealer_cust ? dealer_cust.max_cr_lmt : null;`; init `useState(null)` and `setmaxCrLmt(CUSTmax_cr_lmt)` **unconditionally** (drop the `if (CUSTmax_cr_lmt)` guard so `0` loads).                                                                                                                                                                                                                                                                                                                                                                                    |
| `screens/Customer/Dealers/DealerSettings/index.js`      | `704-727` (`MaxCreditLimit`)        | Replace the value `Text`: show **state-aware** copy — `creditState(maxCrLmt) === 'UNLIMITED' ? 'Unlimited' : creditState(maxCrLmt) === 'BLOCKED' ? 'Blocked' : formatCurrency(maxCrLmt)`. Also `{!!maxCrLmt && ...}` ftank gate (`729`) → `{isCapped(maxCrLmt) && ...}` (ftank only meaningful when capped).                                                                                                                                                                                                                                                                                                   |
| `screens/Customer/Dealers/DealerSettings/index.js`      | `771` (`CreditProgress`), **`892`** | Apply recipe. **`:892`** `{formatwosign(maxCrLmt)}` raw-value display → state-aware "Unlimited"/"Blocked"/amount.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `screens/Customer/Dealers/DealerSettings/components.js` | **`290`**                           | `<Field_Value field='Maximum Credit Limit' value={maxCrLmt} />` raw-value display → pass state-aware text instead of the raw number (shows "0" for blocked / blank for null today).                                                                                                                                                                                                                                                                                                                                                                                                                            |

> `screens/Customer/NewOrder/index.js:816` (`const maxCrLmt = searchPump?.max_cr_lmt;`) already preserves the raw value (null/0/>0) — **no change**, it just feeds the fixed components above.
>
> **Completeness note:** the recipe fixes the _progress/colour_ logic; the **bold raw-value rows above** (`:491`, `:892`, `components.js:290`, and the dip-web ones below) are separate **text** displays that the truthiness grep gate (§6) does **not** catch. They must each render the three states explicitly. `invs.js:1153` also `.select()`s `max_cr_lmt` but does **not** enforce or display it — no change needed there.

## 4. Web admin (`dip-web`)

**Status (2026-10-01):** web — not assessed.

No shared helper with the app — replicate the classifier inline (or add a local util). Replace `?? 0` / truthy conflation so blocked (`0`) ≠ unlimited (null):

dip-web is **read-only** for `max_cr_lmt` (no write/edit path — verified), so no version gate is needed here; these are all display fixes.

| File                                            | Anchor                              | Edit                                                                                                                                                                                                                            |
| ----------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `src/pages/superadmin/customers/CustDealers.js` | `122`                               | drop `?? 0` for classification; classify raw `item.max_cr_lmt`.                                                                                                                                                                 |
| ″                                               | `185`                               | `<CreditRow label="Credit Limit by Dealer" value={maxCrLmt} />` → state-aware value ("Unlimited"/"Blocked"/amount).                                                                                                             |
| ″                                               | `404`                               | `maxCrLmt: item.max_cr_lmt ?? 0` → preserve raw (`?? null`) so the consumer can tell blocked from unlimited.                                                                                                                    |
| ″                                               | `442`,`445`                         | colour + `formatNumField`: show "Unlimited" (null), "Blocked" (0), amount (>0) — not `formatNumField(0)` for both.                                                                                                              |
| `src/pages/superadmin/dealers/DlrCusts.js`      | `172`,`277`,`314`,`426`,`437`,`514` | stop `?? 0` (`:172` `modalMaxCrLmt`, `:277`); the `Number(modalMaxCrLmt) > 0 &&` gates at `:426`,`:514` and `formatCurrency` at `:314`,`:437` currently hide/zero **both** blocked and unlimited — split into the three states. |

## 5. Tests & seeds (`dzzlo_oms_api/test`)

**Status (2026-10-01):** ✅ `test/api_v3/collections/dealer_custs/index.test.js:90-178` (normalisation + v1.77 gate), `test/api_v3/features/credit/index.test.js` (enforcement incl. `0` + deposit, the inclusive cap, the presenter, `createDC` defaults), `collections/order_msts/credit_window.test.js`; the seed forces unlimited (`test/api_v3/temp/seed/v3/index.js:245`) and suites set capped or blocked per test. v4: `test/api_v4/lib/customersModel.test.js:159-206`, `test/api_v4/screens/customers.test.js:357,1068-1090,1693-1747`.

These assert the **old** "0 = no block" behavior and will now fail — update to the new contract:

- `test/api_v3/collections/dealer_custs/index.test.js`, `test/api_v3/helper/collections/dealer_custs/relations.js`
- `test/api_v3/temp/seed/v3/factories/relateDC_Cash_reimb.js` (`max_cr_lmt: options.max_cr_lmt || undefined` — fine for unlimited; add explicit `0` cases for blocked).
- `test/202405_v2/*` and `test/api_v1/collections/dealer_custs/write.test.js` only if those suites still run against current code.
- **Add** order-enforcement tests: `0` blocks (no advance); `0` + sufficient advance allows; `null` unlimited; `50000` cap boundary.

## 6. Cross-cutting grep gate (must be clean before merge)

**Status (2026-10-01):** 🟡 run 2026-10-01 on the app at `ea7e7222` (dip-web not run). Gate A — one code hit, `visible={!!maxCrLmt}` at `src/screens/Customer/Dealers/DealerSettings/components.js:165`, inside an unused `AccountDetails` copy (the screen renders its own, `DealerSettings/index.js:943`) → `T08-N2`; plus two fixture JSON lines. Gate B — four hits, each a deliberate three-state render (`CreditSheet.js:311` shows the limit only when `showLimit`).

Run **two** gates. Gate A catches truthiness conflation; Gate B catches every place the value is _rendered_ (these slip past Gate A — e.g. `formatwosign(maxCrLmt)`).

```sh
# Gate A — truthiness conflation (app + web)
grep -rn "max_cr_lmt\|maxCrLmt" dzzlo_oms_app/src dip-web/src \
  | grep -Ev "helpers/Credit" \
  | grep -E "\?\? 0|! *!?max|<= *0|: *0\b|=== 0|> *0 *&&.*< *1|\? .*: *0"

# Gate B — render sites (each must emit Unlimited/Blocked/amount)
grep -rn "maxCrLmt\|max_cr_lmt" dzzlo_oms_app/src dip-web/src \
  | grep -E "format[A-Za-z]*\(.*[mM]ax|value=\{?.*[mM]axCrLmt|CreditRow|Field_Value|>\s*\{?\`?\\\$\{?.*maxCrLmt"
```

The implementer should be able to point at a deliberate `creditState`/`isBlocked`/`isUnlimited`/`isCapped` decision for **every** hit from both gates. Anything else is a latent bug (blocked silently rendering as "no limit", or `0`/`null` rendered literally).

**Reference inventory** (every known read/display site, so nothing is missed): app — `Dealer/Customers/index.js:37`, `RelationCreditBS.js:76-77,332-333,491`, `Customer/Dealers/components.js:314-340`, `Balance/Components.js:433-458`, `NewOrder/components.js:838-855`, `NewOrder/index.js:816` (no-op), `DealerSettings/index.js:123,132,136-150,704-727,771,892`, `DealerSettings/components.js:290`. web — `CustDealers.js:122,185,404,442,445`, `DlrCusts.js:172,277,314,426,437,514`. enforce/select-only (no display) — `order_msts.js:717,782-797,872,921-937`, `invs.js:1153`.

## 7. Verification (simulator + web)

**Status (2026-10-01):** 1 ✅ (server side, flipped), 3 🟡 / ❔ device checks, 1 web — not assessed, 1 🟡 — marks at the end of each line.

- [ ] Dealer customer list: an unlimited customer shows no/empty credit ring; a blocked customer shows a **full red** ring; a capped customer shows the ratio. (`getProgress` sort by "Credit Limit" orders them sensibly.) — **2026-10-01:** 🟡 on the v2 list (default) the three states are distinct and tested, but UNLIMITED draws a dotted ring rather than none (`CreditAvatar.js:2-3`); the credit sort is pinned in v4 (`customers.test.js:1068-1090`); the look ❔.
- [ ] Customer-side `DealerSettings`: limit reads **"Unlimited" / "Blocked" / ₹amount** (not `₹0` for both null and blocked). — **2026-10-01:** 🟡 reads "Unlimited" / "0" / amount (`DealerSettings/index.js:817-822`) — blocked shows `0`, not "Blocked".
- [ ] `NewOrder` credit indicator: blocked customer shows blocked/full state, not "no limit". — **2026-10-01:** ❔ device check; the code splits the states (`NewOrder/components.js:841-842`).
- [x] Place an order as a **blocked** customer (no advance) → server rejects "Credit Limit Exceeded"; with advance covering it → succeeds. — **2026-10-01:** ✅ flipped (server side): `test/api_v3/features/credit/index.test.js:173-224`.
- [ ] `dip-web` superadmin customer/dealer tables show the three states distinctly. — **2026-10-01:** web — not assessed.
- [ ] Grep gate (§6) returns no unreviewed hits. — **2026-10-01:** 🟡 app: one hit in dead code (`T08-N2`); dip-web not run.

---

## Done =

**Status (2026-10-01):** 🟡 the phases are merged (API 1.5.4, app 1.78); the migration run ❔; the grep gate clean except one dead-code hit (`T08-N2`).

All four phases merged, migration run in the §Phase-2 order, grep gate clean, and the acceptance checklists in Phases 1–4 green.
