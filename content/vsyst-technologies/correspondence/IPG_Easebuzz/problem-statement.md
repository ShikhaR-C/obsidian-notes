# The Problem We Want to Solve

Working file. Subject: the problem VSYST/DZZLO needs an Internet Payment Gateway to solve, the kind of IPG servicing that would actually solve it, and where the Bank's offer falls short of that.

Content for every topic is supplied by the user — nothing here is to be invented or carried over unverified. Prior fact base: `20260708/proposalplan.md` (all 10 bank questions answered) and `20260708/IPG_Proposal_UBI_VSYST.md` (§3 problem framing, §5 architecture, §7 asks). Workflow: `CLAUDE.md`.

## Status

- [x] Topic 1 — Why we need an IPG — _drafted 2026-07-16; all flags and open questions resolved_
- [ ] Topic 2 — What kind of IPG servicing is required — _awaiting content_
- [ ] Topic 3 — The problem with the offer provided by the Bank — _awaiting content_

---

## 1. Why We Need an IPG

Payment is the one leg of the loop that still sits outside DZZLO. The customer leaves the app, opens their own net banking, and pushes the transfer by hand. Every problem below follows from that gap.

| Today, without an IPG                                                                                                                                                                                                                                                   | With the IPG inside DZZLO                                                                                                                                                |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Beneficiary management is the customer's burden.** The dealer must be set up and maintained as a beneficiary in the customer's own banking channel — outside the platform, unlinked to any invoice, and subject to an activation wait before the first payment.       | No beneficiary management at all. The dealer is already there on the payment screen.                                                                                     |
| **Everything is typed by hand.** The payer selects the destination account and enters the amount manually. On transfers that average ₹1 lakh and reach ₹5 lakh, one mistyped digit is a serious incident.                                                               | The payment screen opens with the invoice selected, the dealer selected, and the amount auto-filled from the invoice. **No entry required, so no room for human error.** |
| **A payment sends nothing back.** Money moves in the bank's system while the invoice stays open in the dealer's books. Acknowledgment is manual, late, and disputable.                                                                                                  | The payment is made against a specific invoice and reflects in the shared ledger the moment it is made — one closed entry, seen identically by both sides.               |
| **Paying is bound to the working day — and so is the next order.** A customer at their credit limit must pay to free it, but the transfer is recognised only once the dealer's staff read the bank statement. Someone must be at the terminal, and a firm's account with maker–checker needs its authoriser available.                                                  | The customer pays the aggregator **24×7**, unattended, and the invoice is confirmed on the spot. The limit frees immediately and the next order can be placed at any hour. Easebuzz settles to the dealer on T+1.                                  |
| **UPI does not fit the business.** UPI is built for small amounts. A petrol pump's customers are firms paying firms, and those transfers run on NEFT and RTGS. Our own ticket profile says it: bank transfers average ₹1 lakh and reach ₹5 lakh, against ₹5,000 on UPI. | The gateway carries the rails firms actually use — NEFT and RTGS alongside UPI. _(specified in Topic 2)_                                                                 |

**What the credit limit gates — and why the clock matters.** DZZLO checks credit at order time, not at the nozzle. A customer sees their available limit while placing the order, and without limit the order cannot be placed at all. That is why a vehicle arriving against an order is always fuelled — the argument that today happens at the pump simply cannot arise. But it moves the constraint upstream to the order itself. A customer at their limit at 2 a.m. must pay to place the next order, and today that payment is not recognised until the dealer's staff read the bank statement in the morning: the order waits, the trip waits, and the dealer does not make the sale that night. With the gateway, the customer pays in-app at 2 a.m., the aggregator confirms the invoice on the spot, the limit frees, and the order goes through. **The dealer sells fuel at 2 a.m. that today he does not sell at all** — and that incremental volume moves on the Bank's rails.

**Credit opens on the gateway's confirmation of payment, not on settlement into the dealer's account.** That is precisely what makes the loop work round the clock, and it does not ask the dealer to extend trust one day further. At the moment the gateway confirms, the customer's money has already left their account and sits in the aggregator's escrow under RBI payment-aggregator authorisation — T+1 settlement is a regulated cycle, not a counterparty risk. The dealer's alternative today is to release credit against a chat-app screenshot he has no way to verify. **The gateway replaces an unverifiable promise with a confirmed receipt.**

**Why the integration matters, not just the gateway.** A payment gateway on its own only moves money — the payment still has to be found, matched, and reconciled against a bill afterwards. **No platform in this market carries a common ledger like DZZLO's**, and that is why an IPG integrated here reaches a potential it cannot reach anywhere else: payment is made against a selected invoice, lands in a ledger the dealer and customer already share, and closes on both sides at once. **Reconciliation is not reduced — it is removed as a whole.**

---

## 2. What Kind of IPG Servicing Is Required

_The specific gateway capabilities the problem demands: how it must behave, what it must support, and what it must not do. The features without which the problem above stays unsolved even with an IPG in place._

_(content to be provided)_

---

## 3. The Problem with the Offer Provided by the Bank

_Where the Bank's offer does not meet what Topic 2 requires — the gaps, limits, or conditions in it that leave the problem in Topic 1 unsolved._

_(content to be provided)_

---

## Inbox (raw points — unsorted)

_Drop fragments here as they come; they get moved under the topic they belong to._

**2026-07-16 — Topic 1 (verbatim):**

> no beneficary management, no manual entry form to select account to be transfered and manual amount entry that leads to human mistakes, no response action against payemnt made that could be reflected in account as no common ledger. no 24x7 transfers. the UPI payemnts are for small amounts, the customers of petrol pump need firm to firm transfers which is supported by NEFT and RTGS not UPI. without IPG are the problems. IPG solves all of these.

**2026-07-16 — Topic 1 clarifications (verbatim):**

> 24x7 transfers lets user make payment to aggregator. which is actually settled on t+1 day. so it is possible right? we are saying there exists no common ledger like dzzlo currently where we see full potential of IPG integration. IPG with DZZLO is remove reconiciliations as whole. DZZLO provides payment screen with invoices selected, their dealer selected and amount auto filled. no entry required eliminating human error

_Resolved: (1) 24×7 = the customer can pay the aggregator at any hour and have the invoice confirmed on the spot; settlement is T+1. Never claim NEFT/RTGS are not 24×7 — they have been since Dec 2019 / Dec 2020 and a UBI officer knows it. (2) "No common ledger" = **no other platform has one like DZZLO's** — no contradiction with §3 of the 8 July proposal; it is the reason the IPG reaches full potential here._

**2026-07-16 — credit limit mechanics (verbatim):**

> yes dealer stops fuelling at credit limit. but customer can know in advance if they have limit while placing order. if limit not present they could not place order. so ordered vehicle will always get filled in petrol pump.

_Key correction: the credit block lands at **order time**, not at the nozzle — so there is no stranded-vehicle story to tell. The loss is an **order that cannot be placed** until a payment is manually recognised. Use this framing, not "truck waiting at the pump"._

**2026-07-16 — credit release timing (verbatim):**

> credit opens once payment gateway confirms payment not when amount is settled in bank account. so it works 24x7

_Resolved: credit release is **T+0 on gateway confirmation**, not T+1 on settlement — this is what makes the round-the-clock loop close. Framing for the Bank: this is not extra dealer exposure, because at confirmation the customer's funds are already in the aggregator's RBI-authorised escrow. T+1 is a regulated settlement cycle, not counterparty risk — unlike today's release-against-a-screenshot._
