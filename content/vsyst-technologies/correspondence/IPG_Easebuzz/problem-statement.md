# The Problem We Want to Solve

Working file. Subject: the problem VSYST/DZZLO needs an Internet Payment Gateway to solve, the kind of IPG servicing that would actually solve it, and where the Bank's offer falls short of that.

Content for every topic is supplied by the user — nothing here is to be invented or carried over unverified. Prior fact base: `20260708/proposalplan.md` (all 10 bank questions answered) and `20260708/IPG_Proposal_UBI_VSYST.md` (§3 problem framing, §5 architecture, §7 asks). Workflow: `CLAUDE.md`.

## Status

- [x] Topic 1 — Why we need an IPG — _drafted 2026-07-16; all flags and open questions resolved_
- [x] Topic 2 — What kind of IPG servicing is required — _drafted 2026-07-16; all open points settled 2026-07-19_
- [x] Topic 3 — The problem with the offer provided by the Bank — _drafted 2026-07-16; revised 2026-07-19 (Easebuzz-cost argument dropped, dealer margin figures removed, UPI reason answered, capability questions turned into asks). Volume projections for 10–15 dealers awaited — they go in last._

---

## 1. Why We Need an IPG

Payment is the one leg of the loop that still sits outside DZZLO. The customer leaves the app, opens their own net banking, and pushes the transfer by hand. Every problem below follows from that gap.

| Today, without an IPG                                                                                                                                                                                                                                                                                                  | With the IPG inside DZZLO                                                                                                                                                                                         |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Everything is typed by hand.** The payer selects the destination account and enters the amount manually. On transfers that average ₹1 lakh and reach ₹5 lakh, one mistyped digit is a serious incident.                                                                                                              | The payment screen opens with the invoice selected, the dealer selected, and the amount auto-filled from the invoice. **No entry required, so no room for human error.**                                          |
| **A payment sends nothing back.** Money moves in the bank's system while the invoice stays open in the dealer's books. Acknowledgment is manual, late, and disputable.                                                                                                                                                 | The payment is made against a specific invoice and reflects in the shared ledger the moment it is made — one closed entry, seen identically by both sides.                                                        |
| **Paying is bound to the working day — and so is the next order.** A customer at their credit limit must pay to free it, but the transfer is recognised only once the dealer's staff read the bank statement. Someone must be at the terminal, and a firm's account with maker–checker needs its authoriser available. | The customer pays the aggregator **24×7**, unattended, and the invoice is confirmed on the spot. The limit frees immediately and the next order can be placed at any hour. Easebuzz settles to the dealer on T+1. |
| **UPI does not fit the business.** UPI is built for small amounts. A petrol pump's customers are firms paying firms, and those transfers run on NEFT and RTGS. Our own ticket profile says it: bank transfers average ₹1 lakh and reach ₹5 lakh, against ₹5,000 on UPI.                                                | The gateway carries the rails firms actually use — NEFT and RTGS alongside UPI. _(specified in Topic 2)_                                                                                                          |
| **Beneficiary management is the customer's burden.** The dealer must be set up and maintained as a beneficiary in the customer's own banking channel — outside the platform, unlinked to any invoice, and subject to an activation wait before the first payment.                                                      | No beneficiary management at all. The dealer is already there on the payment screen.                                                                                                                              |

**What the credit limit gates — and why the clock matters.** DZZLO checks credit at order time, not at the nozzle. A customer sees their available limit while placing the order, and without limit the order cannot be placed at all. That is why a vehicle arriving against an order is always fuelled — the argument that today happens at the pump simply cannot arise. But it moves the constraint upstream to the order itself. A customer at their limit at 2 a.m. must pay to place the next order, and today that payment is not recognised until the dealer's staff read the bank statement in the morning: the order waits, the trip waits, and the dealer does not make the sale that night. With the gateway, the customer pays in-app at 2 a.m., the aggregator confirms the invoice on the spot, the limit frees, and the order goes through. **The dealer sells fuel at 2 a.m. that today he does not sell at all** — and that incremental volume moves on the Bank's rails.

**Credit opens on the gateway's confirmation of payment, not on settlement into the dealer's account.** That is precisely what makes the loop work round the clock, and it does not ask the dealer to extend trust one day further. At the moment the gateway confirms, the customer's money has already left their account and sits in the aggregator's escrow under RBI payment-aggregator authorisation — T+1 settlement is a regulated cycle, not a counterparty risk. The dealer's alternative today is to release credit against a chat-app screenshot he has no way to verify. **The gateway replaces an unverifiable promise with a confirmed receipt.**

**Why the integration matters, not just the gateway.** A payment gateway on its own only moves money — the payment still has to be found, matched, and reconciled against a bill afterwards. **No platform in this market carries a common ledger like DZZLO's**, and that is why an IPG integrated here reaches a potential it cannot reach anywhere else: payment is made against a selected invoice, lands in a ledger the dealer and customer already share, and closes on both sides at once. **Reconciliation is not reduced — it is removed as a whole.**

---

## 2. What Kind of IPG Servicing Is Required

**Net banking is the core requirement — NEFT, RTGS and IMPS.** The customers ordering fuel on DZZLO are transport firms, and a firm paying a firm moves money by bank transfer. That is the rail this business actually runs on, and a gateway that does not carry it does not solve anything in Topic 1. The three rails map cleanly onto our ticket profile: IMPS and NEFT carry the everyday ₹5,000–₹2 lakh range, and RTGS carries ₹2 lakh and above, where our transfers reach ₹5 lakh.

**Also required, in support:** UPI, debit card and credit card — so that no customer is turned away for want of a payment method they hold.

**Why UPI cannot be the answer on its own.** Two separate reasons, and both matter. It does not fit the transaction: our bank-transfer tickets average ₹1 lakh and reach ₹5 lakh, past what UPI is built to carry, and firm-to-firm settlement is not what it was designed for. And it is not where a bank wins: **the UPI market is already captured by Paytm and PhonePe.** Net banking for firm-to-firm fuel payments is still an open rail — it is where Union Bank of India owns the relationship rather than renting it, and it is precisely the rail this platform brings.

**QR codes and POS machines do not solve this.** They are not interconnected with DZZLO. A payment taken on a QR or a POS terminal is never acknowledged back to the platform, so the invoice stays open, the ledger does not close, and the credit limit does not free. That is the same disconnection Topic 1 describes: the money moves in one system while the business record sits in another, and a human has to bridge the two. **An integrated IPG is not a more convenient QR code — it is the only form that closes the loop.**

**App and web, across every option.** DZZLO runs on Android, iOS and the web. Every payment option the gateway offers has to work on all of them.

**The commercials: charges have to be waived.** Neither the dealer nor the customer can absorb IPG charges, and the reason is structural rather than a matter of preference. Pump prices are set by the oil marketing companies and the dealer's commission is a fixed amount per litre — **the dealer cannot raise his price to absorb a transaction charge** — and the customer will not pay a fee to settle a bill he already owes.

It is simply not feasible for the dealer to bear IPG charges. The dealer's commission is a fixed rupee amount per litre, set by the OMC, and it is a very thin slice of the sale value — while a percentage-based charge scales with the full transaction amount. On this platform the tickets are large, running from tens of thousands of rupees to ₹5 lakh, so even a modest MDR becomes a huge sum on each payment — large enough to consume most of, or exceed, what the dealer earns on the entire order. And that commission is _gross_, before the cost of operating the outlet. **A per-transaction percentage charge is one this business structurally cannot carry**, and the burden grows, not shrinks, as ticket sizes rise.

We therefore request the Bank to **waive the charges on this program**, and to record that waiver in the **terms and conditions** rather than leave it as an informal concession. What we cannot carry is a _percentage_ of the transfer; a minimal flat fee per transaction is a basis we are willing to discuss. See §3.

_Scope note: UPI and RuPay debit already carry zero MDR by regulation, so this ask concerns net banking and cards, where charges do apply. **Verify current RBI/NPCI position before submission.**_

---

## 3. The Problem with the Offer Provided by the Bank

The Bank's offer has two parts, and each on its own leaves Topic 1 unsolved:

- **Net banking priced at 1.8% per transaction.**
- **The program to start with UPI and RuPay debit only**, net banking to follow.

### The charge is on the wrong axis

The difficulty with 1.8% is the axis it sits on rather than the number itself. A percentage grows with the size of the transfer, and the tickets on this platform are large — ₹1 lakh on average, reaching ₹5 lakh. Nothing on the dealer's side moves with them: pump prices are set by the oil marketing companies and his margin is a fixed amount per litre, so there is no price he can raise to absorb a charge that scales with the value of the payment. The customer will not carry it either, since he is settling a bill he already owes. **At these ticket sizes, a charge that scales with value is not one this trade can carry, whatever the rate.**

**A flat fee is a different proposition, and one the dealer can work with.** It is a known amount per payment, it does not grow when the ticket does, and it can be planned for like any other cost of doing business. What makes a charge unworkable here is the scaling, not the paying — which is why a flat fee is a basis we can genuinely commit to if a waiver is not possible.

And a flat fee is priced on exactly what this platform brings: **transactions, in number and in size.** Every fuel order placed on DZZLO ends in a payment, the tickets are large, and the customers pay again and again — a transport firm fuels its vehicles continuously, not occasionally. Across 10–15 dealers that is a substantial and recurring flow of high-value transactions onto the Bank's rails, along with the current accounts they settle into. The projection is set out at the end of this section.

### Net banking is the rail we need — and the safest one the Bank can give

If risk sits alongside price in the Bank's thinking, net banking is the strongest instrument on the list. **Net banking carries no chargeback.** The payer authenticates inside their own bank and pushes the money; there is no reversal right to be exercised against the merchant afterwards. Debit cards, by contrast, do carry chargeback exposure. And the dispute itself barely arises here: the payment is made by an identified firm against a specific invoice, for fuel dispensed at a physical outlet into a vehicle that was present. There are no goods to return and no delivery to contest.

The rail we are asking for is the lowest-risk instrument in the offer — enabling it early adds less exposure for the Bank, not more.

### A UPI-and-RuPay start would measure the wrong customer

We understand what the Bank is after here: an estimate of the volume this platform will carry, taken first on the modes that carry no MDR. The intent is sound — the Bank should not price a waiver blind. The difficulty is that **the free modes are not the modes this platform's customers pay on**, so the reading would not describe the business it is meant to size.

UPI fits a **cash customer** — the walk-in who pays at the pump for the fuel going into his tank. That customer is real, but he is not who DZZLO carries. **The accounts on this platform are credit accounts, and a credit customer is a firm.** The firm pays from the firm's account, on the firm's authorisation, against an invoice already raised — by bank transfer, ₹1 lakh on average and reaching ₹5 lakh. It does not pay from a proprietor's UPI handle, and one firm does not settle with another on a debit card.

A UPI-and-RuPay pilot therefore does not measure a smaller version of this business. It measures a different set of customers — the cash counter rather than the credit book — and it would read low precisely because the rail carrying the value was switched off while the reading was taken.

The consequence on the ground is not that we launch smaller. It is that we launch and nothing moves. The customers go on doing exactly what they do today — open their own net banking and transfer by hand, outside the platform — because the app cannot offer them the rail they pay on. The gateway records near-zero volume, and the program reads as having failed for want of demand when it was never given the rail its demand runs on.

**If what the Bank needs is an estimate before it commits on net banking, that estimate is something we can hand over directly** — built from observed throughput at the outlets, and set out at the end of this section — rather than inferred from a pilot run on rails our customers do not use.

### What we are asking, and what we will meet

On net banking, in order of preference:

1. **A waiver of the charge**, recorded in the terms and conditions rather than held as an informal concession.
2. Failing that, **a flat fee per transaction** — any reasonable amount, so long as it is not a percentage of the transfer. The Bank sets the level; we ask only that it not scale with the value of the payment.

**And if the waiver is governed by a threshold, we ask the Bank to state it.** If there is a minimum number of onboarded dealers, a committed monthly transaction count or value, or a balance to be maintained, we would far rather meet a stated condition than argue against a rate. Every dealer we bring onto this program is a current account with Union Bank of India, with the outlet's settlement and its float running through it — that is the side of the trade the waiver is priced against, and it is the side we can grow.

### What we ask the Bank to confirm

Before the product is settled, we ask the Bank to confirm with the aggregator that the gateway can actually carry the payments this platform runs on:

1. **Net banking — NEFT, RTGS and IMPS — can be enabled on this merchant account**, on Android, iOS and web alike.
2. **A single transaction of ₹5 lakh completes** through the net-banking flow. Our transfers average ₹1 lakh and reach ₹5 lakh, and we need to know where the ceiling sits and whether it is set by the aggregator or by the customer's own bank.
3. **A current account operating on maker–checker can complete the payment.** Our customers are transport firms, and their accounts commonly need a second authoriser who is not sitting in the payment session. If the flow cannot be completed from such an account, the gateway does not reach the customers it is meant to serve — the very constraint described in Topic 1 would reappear inside the solution.
4. **UPI, debit card and credit card are available alongside**, so that no customer is turned away for want of a method he holds.

These are questions of capability rather than commercials, and the answers decide what we are asking to be built. We would rather have them confirmed now than discover a limit after onboarding.

### Projected volumes

_(to be added — data being gathered; collection template: `dealer-volume-data.xlsx`)_

Projected transaction volumes across **10–15 dealers**, built from observed throughput at the outlets, so the Bank can price the ask against real numbers. Two things this must carry when it is written:

- **Transaction count alongside value.** A flat fee is priced on the number of payments, so the count is the figure the ask actually turns on — value alone does not let the Bank price what we are requesting.
- **The current-account side.** Every dealer on this program is a Union Bank of India current account, with the outlet's settlement and float running through it. That is what a waiver is priced against on the Bank's own books, so the projection should give expected accounts and balances, not only throughput.

### ⚠ Points to settle before this reaches the Bank

- **Why the Bank wants to start with UPI and RuPay — answered.** _(2026-07-19)_ The Bank wants an estimate of the volume the platform will carry, taken first on the modes that carry no MDR. The reply is now written into the section above: the free modes are not the modes our customers pay on, so the reading would be taken off the wrong population — and the estimate itself is something we can hand over directly rather than have it inferred from a pilot.
- **Easebuzz's charge to the Bank is unknown, and the case no longer rests on it.** _(2026-07-16 confirmed unknown; argument reframed 2026-07-19.)_ The ask now stands entirely on our own side of the trade — a percentage cannot work at these ticket sizes, a flat fee can, and here is the volume we bring. Nothing waits on knowing the Bank's cost. **Do not speculate about the Bank's cost or margin in the meeting**; if the Bank volunteers it, listen, but the ask does not change.
- **Hold the virtual-account fallback in reserve.** If the confirmations we are asking for come back negative on the ₹5 lakh ticket or the maker–checker account, the product that fits may be **bank-transfer collection over virtual accounts** — the customer pushes a real NEFT/RTGS from their own channel to a per-invoice virtual account, and the aggregator auto-matches it and confirms back to DZZLO. That carries any ticket size, works from a maker–checker account, and is typically priced flat per collection. It closes the ledger and removes reconciliation, but it keeps beneficiary management — a partial answer to Topic 1, not a full one. **Do not raise it until the confirmations come back**, or the Bank may take it as the ask and leave net banking where it is.
- **Decide whether Topic 2 needs the same trim as §3.** §2 no longer has any figures, but paragraphs 3–4 still describe the dealer's commission as a thin slice against which an MDR is large. That is qualitative, not a calculation — but if the rule is that the dealer's economics stay out of the Bank's view altogether, those paragraphs need reducing to "a charge that scales with value cannot be carried at these ticket sizes" and nothing further.
- **The volume data is a projection — write it as one.** A bank reads whatever number it is handed as a commitment, and a missed commitment is how a waiver gets withdrawn and a relationship sours. Show the basis (observed throughput per outlet, dealers signed vs. in pipeline), label it a projection, and offer a **review at 12 months against actuals** — a normal banking construct that reads as confidence rather than hedging. This is the counterweight to promising volume in the prose: **claim the scale qualitatively, quantify it only inside the labelled projection.**

---

## Inbox (raw points — unsorted)
