# Phase 2 — Advance-deposit balance posting & dealer approval

**Goal:** When a dealer approves an `AdvDep` voucher, the amount is added to the customer's advance-deposit balance (`dealer_custs.adv_dep`) and is **kept out of** the running invoice-outstanding ledger (`month_crdrs`). The dealer can actually approve AdvDep vouchers from the app.

**Depends on:** Phase 1. **Together with Phase 1 = the MVP.**

**Risk:** Medium — edits the shared `updateVocStatus` approval path. Mitigated by branching strictly on `voc_type` and leaving the existing path byte-for-byte unchanged for non-AdvDep.

---

## Background (the exact code we change)

`api_v3/services/voc_msts.js` → `exports.updateVocStatus` (~L295). On approval (`pay_status` truthy) it currently **always** does:

```js
// ~L297-299  — current select (note: voc_type is NOT selected)
const voc_mst = await VoucherMaster.findById(id)
  .select("amount pay_mode chq_no pay_dt dealer_id cust_id invs_adj tds_amt")
  .lean();

// ~L315-323  — current credit posting (always month_crdrs CREDIT)
if (!!pay_status) {
  await updateCrDr({
    dealer_id: finalVoucher.dealer_id,
    cust_id: finalVoucher.cust_id,
    cd: "CREDIT",
    amt: finalVoucher.amount,
    dt: finalVoucher.pay_dt,
  });
}

// ~L325-334 — invoice resolution + on-account skip
const vocInvsAdj = voc_mst?.invs_adj?.map((v) => v.inv_id);
const invoices = vocInvsAdj.length > 0 && (await Invoices.find(...));
if (!isOnAcPay) {
  if (!invoices) throw new ErrorResponse(`Invoices not found`, 404);
}
```

`DealerCustomer` (the `dealer_custs` model) is already imported at the top of this file (`L7`). `month_crdrs` at `L8`.

---

## Step 2.1 — Add an `updateAdvDep` helper

Place it next to `updateCrDr` (~L286) in `api_v3/services/voc_msts.js`.

```js
// Adds (or, for adjustments, subtracts) to the customer's advance-deposit balance.
// delta > 0 on AdvDep approval; delta < 0 on adjustment approval (Phase 3).
const updateAdvDep = async ({ dealer_id, cust_id, delta }) => {
  if (!delta || !Number(delta)) {
    console.log(`No advance-deposit delta`);
    return;
  }
  const dc = await DealerCustomer.findOne({ dealer_id, cust_id })
    .select("_id adv_dep")
    .lean();
  if (!dc) throw new ErrorResponse(`Dealer-customer relation not found`, 404);

  const current = Number(dc.adv_dep || 0);
  const next = Number((current + Number(delta)).toFixed(2));
  if (next < 0) {
    // Guardrail (matters for Phase 3 adjustments): never overdraw the deposit.
    throw new ErrorResponse(
      `Adjustment exceeds available advance deposit`,
      400,
    );
  }
  await DealerCustomer.findByIdAndUpdate(dc._id, { adv_dep: next });
};
```

> Implementation note: an atomic `$inc` is tempting, but the `next < 0` guardrail needs the read first. Volume on this path is low (manual dealer approvals), so read-then-write is acceptable. If you prefer atomicity, use a conditional update: `findOneAndUpdate({ dealer_id, cust_id, adv_dep: { $gte: -delta } }, { $inc: { adv_dep: delta } })` and throw if no doc returned.

---

## Step 2.2 — Branch the approval posting on `voc_type`

In `updateVocStatus`:

**(a)** Add `voc_type` to the select (~L297-299):

```js
const voc_mst = await VoucherMaster.findById(id)
  .select(
    "amount pay_mode chq_no pay_dt dealer_id cust_id invs_adj tds_amt voc_type",
  ) // ← + voc_type
  .lean();
```

**(b)** Replace the credit block (~L315-323) with a type-aware branch:

```js
const isAdvDep = voc_mst.voc_type === "AdvDep";

if (!!pay_status) {
  if (isAdvDep) {
    // Advance Deposit: post to the separate advance-deposit balance, NOT month_crdrs.
    await updateAdvDep({
      dealer_id: finalVoucher.dealer_id,
      cust_id: finalVoucher.cust_id,
      delta: +finalVoucher.amount,
    });
  } else {
    await updateCrDr({
      dealer_id: finalVoucher.dealer_id,
      cust_id: finalVoucher.cust_id,
      cd: "CREDIT",
      amt: finalVoucher.amount,
      dt: finalVoucher.pay_dt,
    });
  }
}
```

**(c)** Skip invoice resolution/validation for AdvDep (it has no invoices), reusing the existing `isOnAcPay` escape (~L325-334):

```js
const skipInvoices = isOnAcPay || isAdvDep; // ← AdvDep behaves like on-account here

const vocInvsAdj = voc_mst?.invs_adj?.map((v) => v.inv_id) || [];
const invoices =
  vocInvsAdj.length > 0 &&
  (await Invoices.find({ _id: { $in: vocInvsAdj } })
    .select("_id inv_no inv_dt inv_total_amt inv_status inv_type")
    .lean());

if (!skipInvoices) {
  if (!invoices) throw new ErrorResponse(`Invoices not found`, 404);
}
```

The downstream FULLPAID/PARTPAID block already no-ops when `invoices` is falsy, so no further change is needed there.

> ⚠️ Do **not** change the `pay_type` handling or the `updateCrDr` signature — other callers (`createDealerVoucher`, `invs.js`) depend on it.

---

## Step 2.3 — App: let the dealer approve an AdvDep voucher

**File:** `dzzlo_oms_app/src/screens/Dealer/Payments/components/PromptPay.js` (`handleDialogFCPaymentLogic`, ~L93-141)

The cascade currently falls through to `alert('No conditions matched')` for AdvDep (no `inv_id`/`order_id`/`invs_adj`, remarks ≠ "On account payment."). Add an AdvDep branch **before** the `else`. Branch on `voc_type` (present on the order — `PaymentHeader` already reads `isSelectedOrder.voc_type` at L396).

```js
        } else if (
          !!order.remarks &&
          String(order.remarks).includes('On account payment.')
        ) {
          await updateVocStatus({
            _id: order._id,
            pay_status: true,
            pay_dt: pay_dt,
            chq_no: trnNo,
            isOnAcPay: true,
            notify: true,
          }).unwrap();
        } else if (order.voc_type === 'AdvDep') {          // ← ADD THIS BRANCH
          await updateVocStatus({
            _id: order._id,
            pay_status: true,
            pay_dt: pay_dt,
            chq_no: trnNo,
            isOnAcPay: true, // skip invoice validation; backend routes to adv_dep via voc_type
            notify: true,
          }).unwrap();
        } else {
          alert('No conditions matched');
        }
```

> `isOnAcPay: true` only tells the backend "this voucher has no invoices to validate." The backend decides where the money posts purely from `voc_type === 'AdvDep'` (Step 2.2), so we don't need a new flag on the wire. (If you prefer an explicit signal, add `isAdvDep: true` and read it in the service — optional.)

No RTK changes: `useUpdateVocStatusMutation` already forwards the whole body.

---

## Step 2.4 — Make the manual `adv_dep` editor read-only (decision §6.1)

Approval now mutates `adv_dep`, so the dealer's manual editor must stop writing it — otherwise the manual and voucher-driven paths double-count. Make the input **read-only**.

**File:** `dzzlo_oms_app/src/screens/Dealer/Customers/CustSettings.js`

Change the Advance Deposits `TextInput` (~L706-716) to display-only — drop the write handlers and mark it non-editable:

```jsx
<Text>Advance Deposits</Text>

<TextInput
  value={`${advDep}`}
  editable={false}                       // ← read-only: adv_dep is now voucher-driven
  ref={advdepInput}
  style={[styles.textInputItem, stateStyles.textInputItem, { opacity: 0.7 }]}
  // onChangeText / onBlur={handleAdvanceDeposits} / keyboardType removed — no manual writes
/>
```

Then retire the now-unused writer `handleAdvanceDeposits` (~L378-387) and its `update_dealer_custs({ adv_dep })` call, leaving a breadcrumb so it isn't "fixed" back later:

```js
// adv_dep is voucher-driven (AdvDep approval / Phase 3 adjustment). Do NOT write it here.
// See docs/tasks/tasks_07_advdep/02-phase-2-balance-and-approval.md §2.4
```

> Existing stored `adv_dep` values are preserved and continue as the starting balance; all future changes flow through voucher approval (Step 2.2) and adjustments (Phase 3).

---

## Acceptance criteria (Phase 2 — the MVP gate)

- [ ] Dealer approves an AdvDep voucher → `dealer_custs.adv_dep` increases by the amount.
- [ ] After that approval, `month_crdrs` for that customer is **unchanged** (outstanding not affected).
- [ ] The "Advance Deposits" column on the Accounts screen reflects the new balance; "Outstanding Bal." is unchanged; "Final Bal." drops by the amount (per `opening + outstanding − advance`).
- [ ] Approving a normal **On-Account** payment still posts a CREDIT to `month_crdrs` exactly as before (regression check).
- [ ] Approving the AdvDep voucher no longer shows "No conditions matched".

## Verification (simulator + DB)

1. Create an AdvDep voucher (Phase 1). Note customer's `adv_dep` and current month `month_crdrs`.
2. As dealer: Payments → Unapproved → open the AdvDep voucher → Approve.
3. DB: `dealer_custs.adv_dep += amount`; `month_crdrs` row for the month **unchanged**.
4. Accounts screen: "Advance Deposits" up by amount; "Outstanding" same; "Final Bal." down by amount.
5. Regression: create + approve a normal On-Account payment → `month_crdrs.crttl` increases; `adv_dep` unchanged.
