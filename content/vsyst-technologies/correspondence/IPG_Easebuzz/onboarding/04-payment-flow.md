# Payment Flow

Two flows are described: the one live in the DZZLO app today, where no payment gateway is involved, and the one we intend to build once the Easebuzz gateway is enabled. Part B is a design intent, not a description of working software.

## A. Current flow — live today, no gateway

Money moves outside the app; the app records it. Every payment is a **voucher** raised against one or more invoices and is entered into the common ledger only when the dealer approves it.

| #   | Who      | Where in the app                         | What happens                                                                                                                                                                                                                                                                                                             |
| --- | -------- | ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | Customer | Orders → New Order                       | Places a fuel order against its credit limit with the dealer. Without available limit the order cannot be placed.                                                                                                                                                                                                        |
| 2   | Dealer   | Orders → dispense                        | Fuel is dispensed at the outlet into the verified vehicle; the sales order is closed.                                                                                                                                                                                                                                    |
| 3   | Dealer   | Invoices → New Invoice                   | Raises the invoice for the delivery. Invoice status: **UNPAID**.                                                                                                                                                                                                                                                         |
| 4   | Customer | — (outside the app)                      | Pays the dealer by NEFT / RTGS / cheque / cash / fleet card / card from its own bank or at the counter.                                                                                                                                                                                                                  |
| 5   | Customer | Invoices → select invoices → New Payment | Records the payment: invoices paid, amount, payment mode (NEFT, RTGS, Cheque, Cash, Fleet Card, Debit/Credit Card), bank name, cheque or transaction number, date, optional TDS, remarks. A voucher is created **pending**; the selected invoices move to **UNAPPROVED**; dealer users get a "New Payment" notification. |
| 6   | Dealer   | Payments → voucher → Approve             | Checks the bank statement or cash, then approves. The voucher becomes **approved**, stamped with the approving dealer user; the invoices become **FULLPAID** (or **PARTPAID** if the amount falls short); the month's ledger is rebuilt; customer users get a "Payment Approved" notification.                           |
| 7   | Both     | Accounts / Ledger                        | The common ledger shows the same entry to dealer and customer. Available credit is computed from the ledger, so the customer's limit is freed by the approval and the next order can be placed.                                                                                                                          |

Also recorded through the same voucher path: **on-account payments** and **advance deposits** from the customer (Payments → New Payment Acknowledgement: On Account / Adv. Deposit / TDS Note), and dealer-raised **debit notes, credit notes, TDS vouchers** (Dealer → New Voucher), which enter the ledger on creation.

**What can be changed.** A pending voucher can be deleted by the customer (the invoices return to UNPAID from PROCESSING). An approved voucher cannot be deleted. The ledger is rebuilt from the documents, never edited by hand.

**The gap.** Step 4 is manual and blind: the customer types the dealer's account number and the amount by hand, and step 6 waits for a person to read a bank statement. Between the two, the invoice is open, the credit limit is blocked, and nothing in the app can confirm the money arrived.

The manual acknowledgement in step 5 is the weak link. The platform's rule is that each process is initiated by the party responsible for it, so the transport customer records the payment it has made. In practice, customers rarely see why a payment already made must be entered again: the acknowledgement looks like paying twice, and its purpose — keeping the account current and freeing the credit limit — is not obvious to them. When a transfer or its reconciliation is delayed, the usual response is to ask the dealer for a higher credit limit rather than to record the payment, so a delay turns into more credit exposure. And the amount keyed into the acknowledgement often differs from the amount actually transferred — a human error that creates exactly the reconciliation the platform exists to remove.

## B. Expected flow — with the Easebuzz gateway (to be built)

| #   | Who       | Where                                    | What happens                                                                                                                                                                                                     |
| --- | --------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1–3 | as today  |                                          | Order, dispensing, invoice — unchanged.                                                                                                                                                                          |
| 4   | Customer  | Invoices → select invoices → **Pay now** | Invoices pre-selected, amount pre-filled. The DZZLO API creates a pending voucher and an Easebuzz payment request keyed to the voucher id, and opens the Easebuzz checkout in the app (net banking, UPI, cards). |
| 5   | Customer  | Easebuzz checkout                        | Authenticates with its own bank or UPI app. No account numbers are typed; no card or bank credentials touch DZZLO.                                                                                               |
| 6   | Easebuzz  | → DZZLO API                              | Sends the payment result (success / failure / pending) to a DZZLO webhook; DZZLO stores the gateway transaction id and status against the voucher and confirms with a status check.                              |
| 7   | DZZLO API | automatic                                | On success, approves the voucher exactly as a dealer would today — invoices FULLPAID/PARTPAID, ledger rebuilt, both sides notified, credit limit freed — at any hour, with no dealer action.                     |
| 8   | Easebuzz  | settlement                               | Settles to the dealer's own bank account on T+1 as a sub-merchant settlement. VSYST receives no part of the money.                                                                                               |

- **Failed or abandoned:** the voucher stays pending, the invoices stay open, and the customer can retry; a pending voucher with no successful gateway result is cleared automatically after ⟨24 hours⟩.
- **Pending at the bank:** DZZLO polls the status API until it resolves; nothing is posted to the ledger until success is confirmed.
- **Refund:** raised only by the dealer in DZZLO against the original voucher, executed through the Easebuzz refund API to the original instrument, and recorded as a reversing entry in the ledger. See the Cancellation and Refund Policy.
- **Reconciliation:** Easebuzz's settlement report is matched daily against vouchers by gateway transaction id.

## C. Data held by VSYST

Voucher, invoice and ledger records; the gateway transaction id and its status; the payer's name, phone and email as already registered on the platform. VSYST stores no card numbers, bank credentials or UPI PINs — those stay within Easebuzz's RBI-authorised scope.
