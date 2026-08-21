# Use Case of the Payment Gateway

## In one line

A transport company pays a petrol pump dealer's invoice, from inside the DZZLO app, and the payment closes that invoice in the common ledger the moment it is confirmed avoiding any reconciliations.

## Who pays whom, for what

| Role         | Detail                                                                                                                                   |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Payer        | The customer firm (transport company), paying from the firm's own bank account                                                           |
| Payee        | The dealer, onboarded as a sub-merchant — settlement goes directly to the dealer's own bank account                                      |
| Platform     | VSYST Technologies — technology layer only, master merchant for onboarding; receives, holds and routes no money                          |
| What is paid | An invoice for fuel already dispensed at the outlet against a verified order. Post-delivery settlement of a credit sale; nothing to ship |

No payment gateway is live on DZZLO today. Payments are made outside the app and acknowledged afterwards.

## Expected transaction profile

Expectations drawn from observed throughput at the outlets on the platform — projections, not commitments.

| Mode                             | Expected average ticket | Expected range     | Role                                      |
| -------------------------------- | ----------------------- | ------------------ | ----------------------------------------- |
| Net banking (NEFT / RTGS / IMPS) | ₹1,00,000               | ₹5,000 – ₹5,00,000 | Core — firm-to-firm settlement            |
| UPI                              | ₹5,000                  | ₹1,000 – ₹50,000   | Supporting                                |
| Debit / credit card              | —                       | —                  | Supporting, so no customer is turned away |

- **Frequency:** recurring. A transport firm fuels its vehicles continuously and pays invoice by invoice, not in lump sums.
- **Volume:** ₹10–20 lakh per dealer per month today, paid by bank transfer outside the app; expected to move onto the gateway as dealers are added.

## What the gateway replaces

Today the customer leaves the app, opens their own net banking, sets up the dealer as a beneficiary, types the account number and the amount by hand, and transfers. The dealer's staff read the bank statement the later on and mark the invoice paid.

With the gateway, the invoice is pre-selected and the amount pre-filled, confirmation is instant, the customer's credit limit frees at once — at any hour — and reconciliation is not reduced but removed.

## Channels

Android and iOS apps ⟨and web⟩. Every payment mode must work on all of them.

## Also requested

Verification services alongside the gateway — bank account, PAN, GSTIN, Aadhaar, vehicle RC and driving licence — to be used when dealers and customer firms are onboarded.
