# Business Model

## In one line

DZZLO OMS is a vertical SaaS platform on which petrol pump dealers run their credit sales to transport companies. VSYST Technologies operates the software. It does not sell fuel, and it does not receive, hold, or route any customer money.

## Parties

| Party                              | What they do on DZZLO                                                        | Relationship with VSYST                                                         |
| ---------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Petrol pump dealer (retail outlet) | Sells fuel on credit, raises GST invoices, receives payment                  | Platform user; expected subscriber; sub-merchant under VSYST's merchant account |
| Transport company (customer)       | Orders fuel, takes delivery at the outlet, pays invoices                     | Platform user; free                                                             |
| VSYST Technologies                 | Builds and runs the platform; master merchant for payment-gateway onboarding | —                                                                               |

## What is transacted

Fuel (diesel or petrol) dispensed at the dealer's outlet into the customer's vehicle against a verified order. The dealer raises a GST-compliant invoice in the platform, and the customer pays that invoice. Product prices are provided by the oil marketing companies; the platform records and settles the sale, it does not price it. There is no shipping — delivery happens at the outlet at the time of dispensing.

## How VSYST earns

- **Today: nothing.** The platform is free and in referral-only rollout to build adoption. VSYST is pre-revenue.
- **Expected:** a subscription charged to dealer companies, per GSTIN, billed on the platform. Customer companies and all users stay free.
- **Not from payments.** VSYST takes no commission or charge on payments passing through the gateway, earns nothing from transaction value, and holds no float. Settlement goes from the gateway directly to each dealer's own bank account.

## Scale — current and expected

| Measure           | Current (Aug 2026)                                       | Expected                                                                   |
| ----------------- | -------------------------------------------------------- | -------------------------------------------------------------------------- |
| Dealer outlets    | ⟨2⟩                                                      | ⟨10–15⟩ in the first phase, added by referral                              |
| Users             | ⟨130+⟩                                                   | —                                                                          |
| Transactions/day  | ⟨130+⟩                                                   | —                                                                          |
| Volume per dealer | ₹10–20 lakh/month, paid by bank transfer outside the app | up to ₹1 crore+/month per outlet, excluding oil-company loyalty-card flows |

The expected figures are assumptions drawn from observed throughput at the outlets already on the platform. They are projections, not commitments.

## Why a payment gateway

Every other step of the sale — order, delivery, invoice, ledger — already runs inside DZZLO and optimised to be errorless and effortless. Payment is the one step still outside it. As a startup we want to provide an common ERP platform for petrol pump dealer and their customers to ease their transactions in affordable and efficient way through our platform. See _Use Case of the Payment Gateway_.
