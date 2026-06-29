# Phase 1 — Register `AdvDep` & add the On-Account vs Advance-Deposit selector

**Goal:** A customer can pick "Advance Deposit" on the `PayOnAc` screen and create a voucher with `voc_type: 'AdvDep'`. The new type renders with a proper label/icon everywhere and appears in payment filters. **Purely additive — no behaviour change to existing on-account payments.**

**Depends on:** nothing. **Required by:** Phase 2 (approval). Ship Phase 1+2 together as the MVP — until Phase 2 lands, an AdvDep voucher is created but **cannot be approved**.

**Risk:** Low.

---

## Step 1.1 — API: add the `AdvDep` label to `voc_text()`

`voc_text()` feeds notification/receipt wording. Without a case it returns `""`.

**File:** `dzzlo_oms_api/api_v3/services/voc_msts.js` (~L36–57)

```js
const voc_text = ({ voc_type }) => {
  switch (voc_type) {
    case "PRODUCT":
      return "Product Invoice";
    case "CASH_REIMBURSE":
      return "Payment Advice";
    case "PInv":
      return "Product Invoice";
    case "PAdvice":
      return "Payment Advice";
    case "CrNote":
      return "Credit Note";
    case "DrNote":
      return "Debit Note";
    case "TCS":
      return "TCS Voucher";
    case "TDS":
      return "TDS Voucher";
    case "AdvDep": // ← ADD
      return "Advance Deposit"; // ← ADD
    default:
      return "";
  }
};
```

> Note: `models/voc_msts.js` needs **no change** — `voc_type` has no enum. Appending `AdvDep` to the type comment at `models/voc_msts.js:65` is optional and is a `models/` edit (see overview §6).

---

## Step 1.2 — App: add `AdvDep` to the payment constants

**File:** `dzzlo_oms_app/src/constants/payments.js`

```js
export const VOC_TYPE = {
  DRNOTE: "DrNote",
  CRNOTE: "CrNote",
  PINV: "PInv",
  PADVICE: "PAdvice",
  TCS: "TCS",
  TDS: "TDS",
  ADVDEP: "AdvDep", // ← ADD
};

export const VOC_TYPE_LABELS = {
  PInv: "Product Invoice",
  PAdvice: "Payment Advice",
  DrNote: "Debit Note",
  CrNote: "Credit Note",
  TCS: "TCS Voucher",
  TDS: "TDS Voucher",
  AdvDep: "Advance Deposit", // ← ADD
};

export const VOC_TYPES_ARRAY = [
  VOC_TYPE.DRNOTE,
  VOC_TYPE.CRNOTE,
  VOC_TYPE.PINV,
  VOC_TYPE.PADVICE,
  VOC_TYPE.TCS,
  VOC_TYPE.TDS,
  VOC_TYPE.ADVDEP, // ← ADD (makes AdvDep selectable in payment filters)
];
```

This is enough for AdvDep to appear in the payments filter bottom sheet (`src/screens/Common/Payments/bottomsheet/vocTypes.js`, which iterates `VOC_TYPES_ARRAY`).

---

## Step 1.3 — App: add `AdvDep` to the display maps

**File:** `dzzlo_oms_app/src/utils/Conditional/VoucherType.js`

Add an `AdvDep` case to **all three** switches, using the existing `payment-cash` glyph (decision §6.5 — a dedicated `advance-deposit` glyph can replace it later with no other call-site changes).

```js
// In Voucher_type({ voc_type }) — the icon used in payment list rows:
    case 'AdvDep':
      voucherText = <VsystIcons name={'payment-cash'} size={25} />; // payment-cash for now (decision §6.5)
      break;

// In Voucher_text({ voc_type }) — the label:
    case 'AdvDep':
      voucherText = 'Advance Deposit';
      break;

// In Voc_Inv_type({ type, colors, dark }) — icon for combined invoice/voucher lists:
    case 'AdvDep':
      voucherText = <VsystIcons name={'payment-cash'} size={25} />; // payment-cash for now (matches Voucher_type)
      break;
```

After this, `PaymentHeader` (`src/screens/Common/Payments/components/index.js`) and the voucher detail view render AdvDep correctly with no further changes.

---

## Step 1.4 — App: add the selector to `PayOnAc`

**File:** `dzzlo_oms_app/src/screens/Customer/Dealers/DealerSettings/PayOnAc/index.js`

### 1.4a — Import the constant (top of file, with the other imports)

```js
import { VOC_TYPE } from "../../../../../constants/payments";
```

### 1.4b — Add category state (near the other `useState`s, e.g. after `pay_mode`, ~L69)

```js
// 'ONAC' = On Account payment (existing) | 'ADVDEP' = Advance Deposit (new)
const [payCategory, setPayCategory] = useState("ONAC");
```

### 1.4c — Render the category selector

Place it **above** the existing "Select Payment Mode" pressable (i.e., just before the `<Pressable onPress={() => toggleCrBillPrd()} ...>` block at ~L329). Reuse the existing local `UnitChip` component (defined at the bottom of this file) so styling matches the pay-mode chips.

```jsx
<View style={{ marginTop: 8, marginBottom: 4, paddingHorizontal: 10 }}>
  <Text style={{ fontSize: 12, color: colors.text }}>Payment Type</Text>
  <View
    style={{
      flexDirection: "row",
      justifyContent: "space-around",
      marginVertical: 8,
    }}
  >
    <UnitChip
      selectedUnit={"On Account"}
      unit={payCategory === "ONAC" ? "On Account" : ""}
      setUnit={() => setPayCategory("ONAC")}
    />
    <UnitChip
      selectedUnit={"Advance Deposit"}
      unit={payCategory === "ADVDEP" ? "Advance Deposit" : ""}
      setUnit={() => setPayCategory("ADVDEP")}
    />
  </View>
</View>
```

> `UnitChip` compares `` `${unit}` === `${selectedUnit}` `` for the active style, so passing the matching label when active (and `''` otherwise) lights up the selected chip without touching `UnitChip` itself.

### 1.4d — Drive `voc_type` + `remarks` from the category in `handleSubmit` (~L108–127)

```js
const isAdvDep = payCategory === "ADVDEP";

await add_cust_on_acc_voc_msts({
  dealer_id: dealerId,
  cust_id: customerId,
  inv_id: undefined,
  invs_adj: undefined,
  order_id: undefined,
  cust_user_id: custUserId,
  dealer_user_id: undefined,
  chq_no: chq_no,
  pay_mode: pay_mode,
  pay_dt: pay_dt,
  bank_name: bank_name,
  tds_amt: undefined,
  amount: amount,
  pay_type: "CREDIT", // CREDIT or DEBIT
  voc_type: isAdvDep ? VOC_TYPE.ADVDEP : "PInv", // ← was hardcoded 'PInv'
  pay_status: false,
  // IMPORTANT: keep the exact "On account payment." string for the on-account
  // path — the dealer approval cascade (PromptPay.js) string-matches it.
  remarks: isAdvDep
    ? `Advance deposit.${!!remarks ? ` ${remarks}` : ""}`
    : `On account payment.${!!remarks ? ` ${remarks}` : ""}`,
  notify: true,
}).unwrap();
```

### 1.4e — (Optional polish) reflect the category in the header/labels

- The screen header title is `'On A/c Payment'` (`src/navigation/Customer/Main.js:215-224`). Optionally make the in-screen "Payment for ₹X" caption read "Advance Deposit for ₹X" when `isAdvDep`. Low priority.

---

## Acceptance criteria (Phase 1)

- [ ] Selecting **Advance Deposit** + amount + pay mode and tapping **Create Payment** creates a voucher with `voc_type: 'AdvDep'`, `pay_type: 'CREDIT'`, `pay_status: false`, `remarks` starting with `"Advance deposit."`.
- [ ] Selecting **On Account** reproduces the **exact** previous payload (`voc_type: 'PInv'`, `remarks` starting with `"On account payment."`). No regression.
- [ ] In the customer/dealer Payments list, an AdvDep voucher shows the "Advance Deposit" label and an icon (not blank).
- [ ] AdvDep appears as a filter option in the payments filter sheet.
- [ ] `voc_text({ voc_type: 'AdvDep' })` returns `"Advance Deposit"` (API).

## Verification (simulator)

1. Customer → Dealer → On A/c Payment → toggle **Advance Deposit**, enter ₹1000, pick NEFT, submit.
2. Confirm navigation to Payments tab and the new row shows "Advance Deposit".
3. Repeat with **On Account** and confirm identical-to-before behaviour.
4. (DB check) The created doc has `voc_type:'AdvDep'`, `pay_status:false`.

> ⚠️ Until Phase 2, do **not** try to approve the AdvDep voucher from the dealer side — it will hit `alert('No conditions matched')` in `PromptPay.js`. That branch is added in Phase 2.
