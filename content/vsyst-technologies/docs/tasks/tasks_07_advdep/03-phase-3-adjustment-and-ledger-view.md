# Phase 3 (v2) — Separate advance-deposit ledger + adjustment/drawdown

**Goal:** Give advance deposits their **own ledger screen**, fully separated from the relationship ledger:

- `AdvDep` vouchers are **filtered out** of the relationship ledger (Accounts screen) — neither shown as rows nor double-counted.
- A new **Advance Deposit Ledger** screen (opened from the now-disabled "Advance Deposits" field in `CustSettings`) shows deposits (**credit** column) and drawdowns (**debit** column) with a running balance.
- A customer can **adjust** (draw down) a held deposit into the running account. On dealer approval the adjustment **decrements** `adv_dep` **and credits** `month_crdrs`, so it appears as a **DEBIT in the advance-deposit ledger** and a **CREDIT in the relationship ledger**.

**Depends on:** Phases 1 & 2. **Risk:** High — voucher→voucher linkage, two-ledger posting, overdraw guardrails, a new screen + endpoint.

---

## What changed from the v1 spec (read this if you saw the old doc)

The original Phase 3 let AdvDep + adjustment rows appear in the **main** ledger as informational rows and made the dedicated ledger an _optional_ presentation extra (old §3.5). The product decision is now:

| v1 (old)                                                   | v2 (this doc)                                                                                            |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| AdvDep rows show in the main ledger                        | AdvDep rows **filtered out** of the relationship ledger (Step 3.2)                                       |
| Dedicated advance ledger optional                          | Dedicated advance-deposit ledger is **required** (Steps 3.4–3.7), opened from `CustSettings`             |
| "Advance Deposits" advance figure = `dealer_custs.adv_dep` | Same figure, but framed as **the advance-deposit ledger's running balance** (they are equal — see below) |

**Unchanged from v1:** the `ref_voc_id` linkage decision, the pooled-cap decision, and the two-ledger posting on adjustment approval (Steps 3.1 + 3.3).

---

## Decisions (resolved 2026-05-25)

- **Accounts screen keeps netting.** `FinalBalance = opening + outstanding − advance` and the "Advance Deposits" column stay exactly as today. **No change to `components.js`.** (User decision: "Keep netting.")
- **The advance figure IS the advance-deposit ledger balance.** `dealer_custs.adv_dep` is voucher-driven (Phase 2 made the manual editor read-only; only AdvDep approval `+` and adjustment approval `−` mutate it). So the scalar **equals** the advance-deposit ledger's running total by construction. The accounts screen and credit-limit checks keep reading `adv_dep` (= the ledger balance) — nothing to recompute. (User note: "calculate adv dep from balance of new adv dep ledger.")
- **Credit-limit math unchanged.** `order_msts.js:790/792` and `:930/932` keep subtracting `adv_dep` (= ledger balance). No edit. (A held deposit legitimately offsets credit-limit consumption.)
- **Linkage field → `ref_voc_id`** (`models/voc_msts.js`). Additive optional `ObjectId` on the adjustment voucher pointing at the AdvDep voucher it draws from. The one sanctioned `models/` exception (overview §6.2). Drives both the `adv_dep` decrement **and** the ledger's debit-column classification.
- **Cap → pooled (v1).** An adjustment may draw up to the _total_ `adv_dep`; `updateAdvDep`'s guardrail (Phase 2 §2.1) blocks overdraw. Per-voucher "remaining" traceability deferred.
- **Ledger entry point → dealer side (`CustSettings`) for v1.** Customer-side entry (e.g. a tappable accounts column) can be added later with no API change.
- **Adjustment is customer-initiated** (overview §6.4). Dealer-initiated AdvDep/drawdown stays out of scope.

---

## Background — the exact code we touch (current line numbers, post-Phase-2)

- **Relationship-ledger transaction list:** `api_v3/services/dealer_custs.js` → `getDealerCustomerAccount` (L566). The voucher query `vocQueryStr` (L584-588) filters only `pay_status: true` — **no `voc_type` filter** (so AdvDep currently leaks in). Each row gets `type` (DEBIT/CREDIT), `amt`, `name` (= `voc_type`), `dt`. Returned via the `POST cust_msts/app/month` route.
- **Approval posting:** `api_v3/services/voc_msts.js` → `updateVocStatus` (L318). Select at L320-324 already includes `voc_type` (Phase 2). The `isAdvDep` branch is at L340-359. `updateAdvDep` helper at L286-309, `updateCrDr` at L243-288.
- **Voucher create (pass-through):** `createCustomerOnAcVoucher` (L602) does `VoucherMaster.create(body)` → `ref_voc_id` persists once it's in the schema. `getOneVoucher_func` select at L65.
- **App:** the `add_cust_on_acc_voc_msts` and `updateVocStatus` RTK mutations (`src/store/apis/dzzlooms/voc_msts.js:98,173`) forward the whole body — **no RTK change needed for `ref_voc_id`**.

---

## Step 3.1 — API: add `ref_voc_id` to the schema & selects

**File:** `dzzlo_oms_api/models/voc_msts.js` — add after `order_id` (~L26-30):

```js
    order_id: {
      type: ObjectId,
      ref: "order_msts",
      // for CASH Customers
    },
    ref_voc_id: {
      type: ObjectId,
      ref: "voc_msts",
      // links an adjustment voucher to the AdvDep voucher it draws down
    },
```

Add `ref_voc_id` to the two selects that need it:

- `getOneVoucher_func` select (`api_v3/services/voc_msts.js:65`) — append ` ref_voc_id` to the select string so the voucher detail view can show the link.
- `updateVocStatus` select (Step 3.3 extends this) — append ` ref_voc_id`.

> `models/voc_msts.js:65` type comment optionally gains `AdvDep` (Phase 1 note). Not required.

---

## Step 3.2 — API: filter `AdvDep` out of the relationship ledger

**File:** `dzzlo_oms_api/api_v3/services/dealer_custs.js` (`getDealerCustomerAccount`, L584-588)

```js
const vocQueryStr = {
  ...queryStr,
  pay_dt: { $gte: firstDate, $lt: lastDate },
  pay_status: true,
  voc_type: { $ne: "AdvDep" }, // ← AdvDep deposits live in their own ledger (Phase 3)
};
```

This is the **only** change to the relationship ledger. AdvDep voucher rows disappear from the Accounts transaction list. Adjustment vouchers are `voc_type: 'PInv'` (Step 3.8), so they are **not** excluded — they keep showing as a **CREDIT** row, exactly as wanted. Because Phase 2 already keeps AdvDep out of `month_crdrs`, the running-balance column was never affected.

---

## Step 3.3 — API: two-ledger posting on adjustment approval

**File:** `dzzlo_oms_api/api_v3/services/voc_msts.js` (`updateVocStatus`)

**(a)** Extend the select (L320-324) to include `ref_voc_id`:

```js
const voc_mst = await VoucherMaster.findById(id)
  .select(
    "amount pay_mode chq_no pay_dt dealer_id cust_id invs_adj tds_amt voc_type ref_voc_id",
  )
  .lean();
```

**(b)** Replace the Phase 2 posting block (L340-359) with the adjustment-aware version:

```js
const isAdvDep = voc_mst.voc_type === "AdvDep";
const isAdjustment = !isAdvDep && !!voc_mst.ref_voc_id;

if (!!pay_status) {
  if (isAdvDep) {
    // Advance Deposit: post to the separate advance-deposit balance, NOT month_crdrs.
    await updateAdvDep({
      dealer_id: finalVoucher.dealer_id,
      cust_id: finalVoucher.cust_id,
      delta: +finalVoucher.amount,
    });
  } else {
    // Normal on-account / invoice CREDIT to the running ledger.
    await updateCrDr({
      dealer_id: finalVoucher.dealer_id,
      cust_id: finalVoucher.cust_id,
      cd: "CREDIT",
      amt: finalVoucher.amount,
      dt: finalVoucher.pay_dt,
    });
    if (isAdjustment) {
      // ...and draw the same amount OUT of the advance-deposit balance.
      // Posting order matters: CREDIT first, then the decrement. If the
      // decrement throws (overdraw), the error surfaces to the dealer; for
      // this low-volume path a guard-before-write is acceptable. Wrap both
      // in a txn if your Mongo deployment supports it.
      await updateAdvDep({
        dealer_id: finalVoucher.dealer_id,
        cust_id: finalVoucher.cust_id,
        delta: -Number(finalVoucher.amount),
      });
    }
  }
}
```

Everything below (invoice resolution, FULLPAID/PARTPAID) is unchanged — the adjustment is `voc_type: 'PInv'` with no `invs_adj`, and the `skipInvoices` escape (Phase 2 §2.2c) covers `isOnAcPay`. **The `updateCrDr` signature is untouched** — other callers (`createDealerVoucher`, `invs.js`) depend on it.

---

## Step 3.4 — API: new `getAdvDepLedger` service + controller + route

### 3.4a — Service

**File:** `dzzlo_oms_api/api_v3/services/dealer_custs.js` — add near `getMonthAcc` (~L635). `DC` (DealerCustomer) and `VoucherMaster` are already imported in this file.

```js
// Advance-deposit "passbook": approved AdvDep deposits (credit) + approved
// adjustment vouchers (debit, identified by ref_voc_id), with a running balance
// that closes at dealer_custs.adv_dep. Opening = adv_dep − net(rows) so any
// pre-feature/manual balance is represented as an opening line.
exports.getAdvDepLedger = async ({ body }) => {
  const { dealer_id, cust_id, sort = "pay_dt" } = body;
  if (!dealer_id) throw new ErrorResponse("Needs dealer", 404);
  if (!cust_id) throw new ErrorResponse("Needs customer", 404);

  const dc = await DC.findOne({ dealer_id, cust_id }).select("adv_dep").lean();
  const adv_dep = dc && dc.adv_dep ? Number(dc.adv_dep) : 0;

  const vouchers = await VoucherMaster.find({
    dealer_id,
    cust_id,
    pay_status: true,
    $or: [{ voc_type: "AdvDep" }, { ref_voc_id: { $ne: null } }],
  })
    .select("_id amount pay_dt pay_mode voc_type ref_voc_id chq_no")
    .sort(sort)
    .lean();

  const rows = vouchers.map((v) => ({
    ...v,
    dep_type: v.voc_type === "AdvDep" ? "CREDIT" : "DEBIT", // deposit vs drawdown
    amt: Number(v.amount),
    dt: v.pay_dt,
    doc_no: `${v._id}`,
  }));

  const net = rows.reduce(
    (s, r) => s + (r.dep_type === "CREDIT" ? r.amt : -r.amt),
    0,
  );
  const opening = Number((adv_dep - net).toFixed(2));

  let running = opening;
  const data = rows.map((r) => {
    running = Number(
      (running + (r.dep_type === "CREDIT" ? r.amt : -r.amt)).toFixed(2),
    );
    return { ...r, bal: running };
  });

  return { data, adv_dep, opening }; // data[last].bal === adv_dep
};
```

### 3.4b — Controller

**File:** `dzzlo_oms_api/api_v3/controllers/collections/dealer_custs.js`

Add to the import alias block (L11-22 style):

```js
  getMonthAcc: svcGetMonthAcc,
  getAdvDepLedger: svcGetAdvDepLedger, // ← ADD
```

Add the handler (mirror `getMonthAcc`, L77-80 — spreads `...result` so `adv_dep`/`opening` ride along):

```js
exports.getAdvDepLedger = asyncHandler(async (req, res) => {
  const result = await svcGetAdvDepLedger({ body: req.body });
  res.status(200).json({ success: true, ...result });
});
```

### 3.4c — Route

**File:** `dzzlo_oms_api/api_v3/routes/collections/cust_msts.js`

Add `getAdvDepLedger` to the controller destructure (L23-39) and the route (after L79):

```js
router.post("/app/month", getMonthAcc);
router.post("/app/advdepledger", getAdvDepLedger); // ← ADD
```

---

## Step 3.5 — App: RTK query for the advance-deposit ledger

**File:** `dzzlo_oms_app/src/store/apis/balance/SectionalAcc.js`

Add an endpoint after `get_month_acc` (L14-21). **Do not** strip to `.data` — we need `adv_dep`/`opening` too:

```js
    get_advdep_ledger: builder.mutation({
      query: updateEntry => ({
        url: `cust_msts/app/advdepledger`,
        method: 'POST',
        body: updateEntry,
      }),
      transformResponse: response => response, // { success, data, adv_dep, opening }
    }),
```

Add the hook to the export block (L98-109):

```js
  useGet_advdep_ledgerMutation,
```

---

## Step 3.6 — App: the Advance Deposit Ledger screen

**New file:** `dzzlo_oms_app/src/screens/Common/AdvDepLedger/index.js`

Read-only passbook. Reuses the `Row`/`Cell` table primitives (`src/components/Table`). Fetches once on focus with `{ dealer_id, cust_id }` from `route.params.dealer_custID`.

```jsx
import React, { useEffect, useState, useCallback } from "react";
import { View, FlatList, RefreshControl } from "react-native";
import { Text, useTheme } from "react-native-paper";
import { useIsFocused } from "@react-navigation/native";
import { Row, Cell } from "../../../components/Table";
import { formatCurrency } from "../../../utils/Currency";
import { DD_MM_YY } from "../../../utils/Dates";
import Error from "../../../components/Error";
import { useGet_advdep_ledgerMutation } from "../../../store/apis/balance/SectionalAcc";
import { errorRTK } from "../../../store/apis/preloadedState";

const AdvDepLedger = ({ route }) => {
  const { colors } = useTheme();
  const isFocused = useIsFocused();
  const params = route.params || {};
  const dealer_id = params.dealer_custID?.dealer_id;
  const cust_id = params.dealer_custID?.cust_id;

  const [get_advdep_ledger] = useGet_advdep_ledgerMutation();
  const [rows, setRows] = useState([]);
  const [advDep, setAdvDep] = useState(0);
  const [errorText, setErrorText] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    if (!dealer_id || !cust_id) return;
    setRefreshing(true);
    try {
      const res = await get_advdep_ledger({ dealer_id, cust_id }).unwrap();
      setRows(res?.data || []);
      setAdvDep(res?.adv_dep || 0);
    } catch (err) {
      setErrorText(
        errorRTK({ err, msg: "Could not load advance deposit ledger" }),
      );
    }
    setRefreshing(false);
  }, [dealer_id, cust_id, get_advdep_ledger]);

  useEffect(() => {
    if (isFocused) load();
  }, [isFocused, load]);

  const renderItem = ({ item }) => (
    <Row>
      <Cell flexValue={1.2}>
        <Text style={{ fontSize: 12, color: colors.text }}>
          {DD_MM_YY(new Date(item.dt))}
        </Text>
      </Cell>
      <Cell alignflex={"flex-end"}>
        <Text style={{ fontSize: 12, color: colors.link }}>
          {item.dep_type === "CREDIT" ? formatCurrency(item.amt) : "-"}
        </Text>
      </Cell>
      <Cell alignflex={"flex-end"}>
        <Text style={{ fontSize: 12, color: colors.error }}>
          {item.dep_type === "DEBIT" ? formatCurrency(item.amt) : "-"}
        </Text>
      </Cell>
      <Cell alignflex={"flex-end"}>
        <Text style={{ fontSize: 12, color: colors.text }}>
          {formatCurrency(item.bal)}
        </Text>
      </Cell>
    </Row>
  );

  if (errorText) return <Error error={errorText} onRefresh={load} />;

  return (
    <View style={{ flex: 1, paddingHorizontal: 8 }}>
      <View
        style={{
          alignItems: "center",
          paddingVertical: 12,
          backgroundColor: colors.surface,
          borderRadius: 5,
          marginVertical: 8,
        }}
      >
        <Text style={{ fontSize: 12, color: colors.text }}>
          Advance Deposit Balance
        </Text>
        <Text
          style={{ fontSize: 18, color: colors.primary, fontWeight: "bold" }}
        >
          {formatCurrency(advDep)}
        </Text>
      </View>

      <Row>
        <Cell flexValue={1.2}>
          <Text style={{ fontSize: 11, color: colors.placeholder }}>Date</Text>
        </Cell>
        <Cell alignflex={"flex-end"}>
          <Text style={{ fontSize: 11, color: colors.placeholder }}>
            Deposit
          </Text>
        </Cell>
        <Cell alignflex={"flex-end"}>
          <Text style={{ fontSize: 11, color: colors.placeholder }}>
            Adjusted
          </Text>
        </Cell>
        <Cell alignflex={"flex-end"}>
          <Text style={{ fontSize: 11, color: colors.placeholder }}>
            Balance
          </Text>
        </Cell>
      </Row>

      <FlatList
        data={rows}
        keyExtractor={(item) => `${item._id}`}
        renderItem={renderItem}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={load} />
        }
        ListEmptyComponent={
          !refreshing ? (
            <Text
              style={{
                textAlign: "center",
                marginTop: 24,
                color: colors.placeholder,
              }}
            >
              No advance deposit transactions yet.
            </Text>
          ) : null
        }
      />
    </View>
  );
};

export default AdvDepLedger;
```

> Confirm the `Cell` prop names (`flexValue`, `alignflex`) against `src/components/Table/index.js` before pasting; adjust if the local API differs. Columns: **Deposit** (credit, AdvDep) and **Adjusted** (debit, drawdown). Closing `Balance` ties out to `adv_dep`.

---

## Step 3.7 — App: register the screen & wire the `CustSettings` entry

### 3.7a — Register in the dealer customer stack

**File:** `dzzlo_oms_app/src/navigation/Dealer/Main.js` — add to `DealerCustomerStack` next to the `Accounts` screen (~L170-178):

```jsx
<DealerCustomerStack.Screen
  name="AdvDepLedger"
  component={AdvDepLedger}
  options={({ navigation }) => ({
    headerTitle: "Advance Deposit Ledger",
    headerLeft: () => <BackButton navigation={navigation} colors={colors} />,
  })}
/>
```

Add the import at the top of `Main.js` (mirror how `AccountsScreen` is imported):

```js
import AdvDepLedger from "../../screens/Common/AdvDepLedger";
```

### 3.7b — Open it from the disabled "Advance Deposits" field

**File:** `dzzlo_oms_app/src/screens/Dealer/Customers/CustSettings.js` (Pressable ~L684-690)

Replace the no-op `onPress` (which only blurred the now-non-editable input) with navigation:

```jsx
<Pressable
  onPress={() => {
    navigation.navigate('dealerCustomer', {
      screen: 'AdvDepLedger',
      params: { dealer_custID: dealer_custID },
    });
  }}
  style={({ pressed }) => [
    styles.settingsItem,
    stateStyles.enabledSetting(pressed),
  ]}
>
  <Text>Advance Deposits</Text>
  {/* read-only TextInput unchanged (Phase 2 §2.4) — now also a tap target */}
```

> `dealer_custID` (`{ dealer_id, cust_id }`) is already in scope in `CustSettings` from `route.params`. The `advdepInput` ref / `keyBoardOff` blur logic can be dropped since the field is non-editable.

---

## Step 3.8 — App: "Adjust to account" action on the voucher-details bottom sheet

> **Implementation note (corrected during review).** The live voucher-details bottom sheet is **`dzzlo_oms_app/src/screens/Common/Accounts/BSheets/VoucherDetailsBSM.js`** — **not** `_Voucher_/BS/index.js`, which is dead/unused code (so is `_Voucher_/index.js`). Because AdvDep is filtered out of the relationship ledger (§3.2), an AdvDep voucher never opens from the Accounts ledger; instead the **Advance Deposit Ledger passbook rows are made tappable** (extends Step 3.6) to open `VoucherDetailsBSM` for the tapped deposit (via a `vocDtlBSMRef`, mirroring `Accounts/index.js`). The passbook is reachable from **both sides** — dealer via `CustSettings` "Advance Deposits" (Step 3.7) and customer via `Customer/Dealers/DealerSettings` "Advance Deposits" (registered in both `Dealer/Main.js` and `Customer/Main.js`). The adjustment is **customer-initiated**: the "Adjust to account" button is gated to `userRole === 'customer'`, so the dealer views deposits read-only while the customer creates the adjustment (the dealer then approves it via the normal PromptPay flow).

**Files:** `Accounts/BSheets/VoucherDetailsBSM.js` (button + inline amount form, using the already-imported `BottomSheetTextInput`) and `Common/AdvDepLedger/index.js` (tappable rows + render the BSM with `refreshData={load}`).

`VoucherDetailsBSM` already fetches the full voucher as `Vouchers` (`useFetch_one_voucherQuery`), the relation `dealer_custs` (with `adv_dep`), and `userRole`. The button renders for an **approved AdvDep voucher viewed by the customer** — `canAdjust = Vouchers.voc_type === 'AdvDep' && !!Vouchers.pay_status && userRole === 'customer'` — placed **before** the `<Render>` webview (the `BottomSheetView` does **not** scroll and `<Render>` is a fixed ~65%-height block, so a button/form appended *after* it renders off-screen). The amount form is a **screen-overlay `RNModal`** (not an inline expander, for the same reason) with a plain RN `TextInput`, Cancel, and Confirm. The code below (3.8a–d) shows the pattern; apply it to `VoucherDetailsBSM`, not `_Voucher_/BS`.

### 3.8a — Imports (top of file)

```js
import {
  selectUserRole,
  selectCompanyWorkEmail,
} from "../../../../store/selectors/auth";
import { selectUserId } from "../../../../store/selectors/auth"; // ← add (or extend the line above)
import {
  useEmail_vocMutation,
  useFetch_one_voucherQuery,
  useAdd_cust_on_acc_voc_mstsMutation, // ← add
} from "../../../../store/apis/dzzlooms/voc_msts";
```

### 3.8b — State + submit handler (inside the component)

```js
const custUserId = useSelector(selectUserId);
const [add_cust_on_acc_voc_msts] = useAdd_cust_on_acc_voc_mstsMutation();

const isAdvDep = Vouchers.voc_type === "AdvDep";
const canAdjust = isAdvDep && !!Vouchers.pay_status && userRole === "customer";
const availableAdvDep = Number(dealer_custs?.adv_dep || 0); // client-side cap

const [isAdjustBS, setIsAdjustBS] = useState(false);
const [adjustAmount, setAdjustAmount] = useState("");
const [adjustError, setAdjustError] = useState("");

const submitAdjustment = useCallback(async () => {
  const amt = Number(adjustAmount);
  if (!amt || amt <= 0) return setAdjustError("Enter a valid amount");
  if (amt > availableAdvDep)
    return setAdjustError(
      `Max available is ${formatCurrency(availableAdvDep)}`,
    );
  try {
    await add_cust_on_acc_voc_msts({
      dealer_id: Vouchers.dealer_id,
      cust_id: Vouchers.cust_id,
      cust_user_id: custUserId,
      amount: amt, // ≤ available adv_dep (server re-checks — Step 3.9)
      pay_mode: Vouchers.pay_mode || "ADJUSTMENT",
      pay_dt: new Date(),
      pay_type: "CREDIT",
      voc_type: "PInv", // it IS an on-account credit to the running ledger
      pay_status: false,
      ref_voc_id: Vouchers._id, // links this adjustment to the AdvDep voucher
      // keep the "On account payment." token so the existing PromptPay on-account
      // branch approves it; the decrement of adv_dep is driven server-side by
      // ref_voc_id (Step 3.3).
      remarks: "On account payment. Advance deposit adjusted.",
      notify: true,
    }).unwrap();
    setIsAdjustBS(false);
    setAdjustAmount("");
    onClose();
    refreshData();
  } catch (err) {
    setAdjustError(errorRTK({ err, msg: "Could not create adjustment" }));
  }
}, [
  adjustAmount,
  availableAdvDep,
  Vouchers,
  custUserId,
  add_cust_on_acc_voc_msts,
  onClose,
  refreshData,
]);
```

### 3.8c — The button (after the amount `Divider`, ~L442)

```jsx
{
  isAdvDep && (
    <Pressable
      disabled={!canAdjust}
      onPress={() => {
        setAdjustError("");
        setAdjustAmount("");
        setIsAdjustBS(true);
      }}
      style={{
        marginVertical: 8,
        paddingVertical: 10,
        borderRadius: 5,
        alignItems: "center",
        backgroundColor: canAdjust ? colors.primary : colors.disabled,
      }}
    >
      <Text style={{ color: colors.antiText, fontWeight: "bold" }}>
        Adjust to account
      </Text>
      {!canAdjust && (
        <Text style={{ fontSize: 10, color: colors.antiText }}>
          {!Vouchers.pay_status
            ? "Available after the deposit is approved"
            : "Adjusted by the customer"}
        </Text>
      )}
    </Pressable>
  );
}
```

### 3.8d — The adjust form

Open a small amount form when `isAdjustBS` — reuse the lazy bottom-sheet pattern already in this file (the `EmailBS`/`InvoiceDetailModal` `Suspense` blocks at the bottom), or a `Portal`+`Modal` with a single numeric `IconInput` (cap-validated), an error line, and a "Confirm Adjustment" button calling `submitAdjustment`. Header: "Adjust to account · Available {formatCurrency(availableAdvDep)}".

Notes:

- The button shows on **every** AdvDep voucher (per requirement); it's **enabled** only for an approved deposit viewed by the customer (the initiator), and disabled with a hint otherwise (guardrail, Step 3.9).
- `voc_type: 'PInv'` (not `AdvDep`) so the normal on-account approval path credits `month_crdrs` **and** the `$ne: 'AdvDep'` filter (Step 3.2) keeps the adjustment visible in the relationship ledger as a CREDIT.
- No RTK change — `add_cust_on_acc_voc_msts` and `updateVocStatus` forward the whole body (`ref_voc_id` included).
- On dealer approval the existing PromptPay "On account payment." branch fires (`PromptPay.js`); Step 3.3 routes the dual posting from `ref_voc_id`.
- If the server's `relations/a/dealer_cust` select omits `adv_dep`, read the available balance from the `getAdvDepLedger` response (`adv_dep`) instead, or add `adv_dep` to that select.

---

## Step 3.9 — Guardrails & UX

- **Client cap:** the adjustment amount field is capped at the current `adv_dep` (read from `dealer_cust.adv_dep`, or the ledger's `adv_dep`).
- **Server guardrail:** `updateAdvDep` (Phase 2 §2.1) throws `400 "Adjustment exceeds available advance deposit"` if the decrement would push `adv_dep` below 0 — surface that message in the dealer approval sheet.
- **Approved-only:** only offer "Adjust to account" on an **approved** AdvDep voucher (an unapproved deposit has no real balance).
- **Reconciliation:** the ledger's closing `bal` equals `adv_dep` by construction; if they ever diverge, suspect a non-voucher write to `adv_dep` (should be impossible after Phase 2 §2.4 made the manual editor read-only).

---

## Step 3.10 — Exclude AdvDep from ALL voucher-summing balance paths (invariant completion)

> Found during the Phase 3 review. Phase 2 only fixed the *write* path (`updateVocStatus`). The codebase has several **read/reconcile** paths that re-derive balances by summing approved vouchers by `pay_type`. AdvDep vouchers are `pay_type: 'CREDIT'`, so they were being counted as outstanding-reducing credits — re-introducing the deposit into invoice outstanding. Every such query must exclude AdvDep (`voc_type: { $ne: "AdvDep" }`); adjustments are `PInv` and stay counted.

The four sites (all now carry the filter):

1. **`api_v3/services/dealer_custs.js` `getInvVoc`** (the voucher query feeding `calcttl`). **Most critical:** `calcttl` → `checkMonthDRCR` **overwrites** `month_crdrs.crttl` with the recomputed total. The app's Accounts screen calls `sync_year_acc` (`cust_msts/app/checkYearMonth` → `checkYearMonthTotal` → `checkMonthDRCR`), so simply *viewing* Accounts would have injected the AdvDep amount into `month_crdrs` and reduced outstanding. Also feeds the emailed/Excel year statement (`yearAccEmail`), keeping AdvDep out of that statement too.
2. **`api_v3/services/dealer_custs.js` `bal_open_inv_pay`** (→ `allRelationCurrBal`, the relation balance lists).
3. **`api_v3/services/dealer_custs.js` `currentInvoiceBalance`** (→ `getCurrBalance` / `checkBalance`).
4. **`api_v3/services/order_msts.js` `currentInvoiceBalance`** (→ credit-limit `prevBal` at L788/926). Without the filter, AdvDep was **double-subtracted** from credit availability (the credit check already subtracts `adv_dep` explicitly via `balSum = prevBal + amount − AdvanceDeposit`).

`getDealerCustomerAccount` (Step 3.2) already had the filter. `getAdvDepLedger` intentionally includes AdvDep.

## Acceptance criteria (Phase 3 v2)

- [ ] AdvDep vouchers **do not** appear as rows in the relationship ledger (Accounts screen), and the running-balance / "Outstanding" column is unaffected by them.
- [ ] Tapping the "Advance Deposits" field in `CustSettings` opens the **Advance Deposit Ledger** screen.
- [ ] The ledger shows approved AdvDep deposits in the **Deposit (credit)** column and approved adjustments in the **Adjusted (debit)** column, with a running balance whose last value equals `adv_dep`.
- [ ] In the Advance Deposit Ledger, tapping an approved AdvDep deposit row opens the Voucher Details bottom sheet (`VoucherDetailsBSM`) with an "Adjust to account" button. Submitting for ≤ available deposit creates a linked on-account voucher (`ref_voc_id` set, `voc_type: 'PInv'`, unapproved).
- [ ] On dealer approval of the adjustment: `adv_dep −= amount` **and** `month_crdrs.crttl += amount`. The row shows as a **DEBIT** in the advance-deposit ledger **and** a **CREDIT** in the relationship ledger.
- [ ] On the Accounts screen the "Advance Deposits" column drops by the adjustment amount, "Outstanding" drops, and "Final Bal." nets unchanged (because the formula still subtracts the now-smaller advance).
- [ ] An adjustment exceeding the available deposit is rejected (client cap + server 400).
- [ ] Approving a normal On-Account payment still posts a CREDIT to `month_crdrs` exactly as before (regression).
- [ ] After approving an AdvDep deposit, opening the Accounts screen (which triggers `sync_year_acc`) leaves `month_crdrs` and outstanding **unchanged** — i.e., the sync/reconcile path no longer re-injects AdvDep (Step 3.10).
- [ ] Credit-limit checks subtract the advance deposit **once** (not twice): an approved AdvDep of ₹X frees exactly ₹X of credit room, not ₹2X (Step 3.10).

## Verification (simulator + DB)

1. Create + approve an AdvDep voucher (Phases 1–2). Note `adv_dep` and the current `month_crdrs` row.
2. Open Accounts (relationship ledger): the AdvDep voucher is **not** listed; balances unchanged by it.
3. `CustSettings` → tap "Advance Deposits" → the Advance Deposit Ledger shows the deposit as a **credit**, balance = `adv_dep`.
4. As customer: DealerSettings → "Advance Deposits" → Advance Deposit Ledger → tap an approved deposit row → "Adjust to account" (customer-only) → enter ≤ balance → submit. As dealer: approve the resulting adjustment voucher from Payments (Unapproved). (The dealer can also open the same ledger from CustSettings, read-only.)
5. DB: `dealer_custs.adv_dep -= amount`; `month_crdrs.crttl += amount`.
6. Advance Deposit Ledger: new **debit** row; balance dropped by amount. Relationship ledger: new **credit** row; "Outstanding" dropped; "Final Bal." unchanged.
7. Overdraw: attempt an adjustment > balance → blocked client-side; if forced, dealer approval surfaces the 400.
