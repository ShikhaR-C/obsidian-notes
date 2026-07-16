# The Problem We Want to Solve

Working file. Subject: the problem VSYST/DZZLO needs an Internet Payment Gateway to solve, the kind of IPG servicing that would actually solve it, and where the Bank's offer falls short of that.

Content for every topic is supplied by the user — nothing here is to be invented or carried over unverified. Prior fact base: `20260708/proposalplan.md` (all 10 bank questions answered) and `20260708/IPG_Proposal_UBI_VSYST.md` (§3 problem framing, §5 architecture, §7 asks). Workflow: `CLAUDE.md`.

## Status

- [x] Topic 1 — Why we need an IPG — _drafted 2026-07-16; all flags and open questions resolved_
- [x] Topic 2 — What kind of IPG servicing is required — _drafted 2026-07-16; 4 points flagged, dealer commission figure needed_
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

**Net banking is the core requirement — NEFT, RTGS and IMPS.** The customers ordering fuel on DZZLO are transport firms, and a firm paying a firm moves money by bank transfer. That is the rail this business actually runs on, and a gateway that does not carry it does not solve anything in Topic 1. The three rails map cleanly onto our ticket profile: IMPS and NEFT carry the everyday ₹5,000–₹2 lakh range, and RTGS carries ₹2 lakh and above, where our transfers reach ₹5 lakh.

**Also required, in support:** UPI, CBDC, debit card and credit card — so that no customer is turned away for want of a payment method they hold.

**Why UPI cannot be the answer on its own.** Two separate reasons, and both matter. It does not fit the transaction: our bank-transfer tickets average ₹1 lakh and reach ₹5 lakh, past what UPI is built to carry, and firm-to-firm settlement is not what it was designed for. And it is not where a bank wins: **the UPI market is already captured by Paytm and PhonePe.** Net banking for firm-to-firm fuel payments is still an open rail — it is where Union Bank of India owns the relationship rather than renting it, and it is precisely the rail this platform brings.

**QR codes and POS machines do not solve this.** They are not interconnected with DZZLO. A payment taken on a QR or a POS terminal is never acknowledged back to the platform, so the invoice stays open, the ledger does not close, and the credit limit does not free. That is the same disconnection Topic 1 describes: the money moves in one system while the business record sits in another, and a human has to bridge the two. **An integrated IPG is not a more convenient QR code — it is the only form that closes the loop.**

**App and web, across every option.** DZZLO runs on Android, iOS and the web. Every payment option the gateway offers has to work on all of them.

**The commercials: charges have to be waived.** Neither the dealer nor the customer can absorb IPG charges, and the reason is structural rather than a matter of preference. Pump prices are set by the oil marketing companies and the dealer's commission is a fixed amount per litre — **the dealer cannot raise his price to absorb a transaction charge** — and the customer will not pay a fee to settle a bill he already owes.

The arithmetic settles it. Dealer commission on diesel is **₹2.2 per litre**, set by the OMC. At a pump price of about ⟨₹93/litre — _confirm_⟩ that is roughly **2.4% of the value of the sale**. On a ₹1,00,000 fuel order:

| On a ₹1,00,000 diesel order                        |                                                    |
| -------------------------------------------------- | -------------------------------------------------- |
| Diesel dispensed                                   | ~1,075 litres                                      |
| **Dealer's gross commission** (₹2.2/litre)         | **₹2,366**                                         |
| IPG charge at 1.8% MDR (typical for net banking)   | ₹1,800 — **76% of the dealer's entire commission** |
| IPG charge at 1% MDR                               | ₹1,000 — **42% of the dealer's entire commission** |

At a typical net-banking MDR, the gateway takes roughly three-quarters of what the dealer earns for sourcing, storing and dispensing the fuel. Even at a generous 1%, it takes more than 40%. And ₹2.2 is *gross* commission, before the cost of operating the outlet — what the dealer actually retains is a fraction of it. **There is no percentage-based charge this business can carry**, and the problem gets worse, not better, as ticket sizes rise toward ₹5 lakh.

We therefore request the Bank to **waive the charges on this program**, and to record that waiver in the **terms and conditions** rather than leave it as an informal concession.

_Scope note: UPI and RuPay debit already carry zero MDR by regulation, so this ask concerns net banking and cards, where charges do apply. **Verify current RBI/NPCI position before submission.**_

### ⚠ Points to settle before this reaches the Bank

- **Confirm the diesel pump price** behind the arithmetic above — ₹93/litre is a working assumption, not your number. The conclusion is robust either way: anywhere between ₹85 and ₹100 a litre, ₹2.2 lands between 2.2% and 2.6% of sale value, so MDR still eats 40–80% of the commission. But the table should carry the real price from your outlet.
- **"FMCG" should not go in.** Fuel retail is not FMCG and a banker will notice. "Petroleum retail, on an OMC-regulated margin" is both accurate and the stronger claim, because it says the dealer is *structurally unable* to pass the cost on — not merely that margins are tight.
- **Is a full waiver the only acceptable outcome, or is a flat per-transaction fee a fallback?** A percentage charge is what breaks the economics; a small flat fee on a ₹1 lakh transfer may not. Naming a fallback tends to get a yes — an all-or-nothing ask invites a no. Worth deciding before the ask is written.
- **CBDC framing.** Retail CBDC is still at pilot stage. Asking for it "as and when the Bank's CBDC rails are available" costs nothing and reads as RBI-aligned; asking for it as a live requirement invites a pointless objection.

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

**2026-07-16 — Topic 2 (verbatim):**

> we need Internet payment gateway for netbanking that supports NEFT, RTGS, IMPS. we could also require UPI, CBDC, debit card, credit card. as the customers of petrol pump are transport firm that order fuel through DZZLO would make firm to firm bank transfer they would need net banking. UPI market is already captured by paytm, phonepe. QR code or POS machine payment are not acknowledged to DZZLO as they are not interconnected. we need app and web support for all options of IPG. also the petrol pump dealer and their customer would not be able to bear charges of IPG due to heavy amounts per transaction and low comission in FMCG business. we request bank to waive off changes. we need terms and conditions accordingly.

_Note: the QR/POS point is likely the bridge into Topic 3 — if the Bank's offer is a QR or POS-based acceptance product, "not interconnected with DZZLO" is exactly why it fails._

**2026-07-16 — dealer commission (verbatim):**

> dealer commission is ₹2.2 per litre on diesel

_Worked into the Topic 2 charges table. Ratio to remember: ₹2.2/litre ≈ **2.4% of sale value** at ~₹93/litre, so a 1.8% net-banking MDR consumes **~76%** of the dealer's gross commission and a 1% MDR consumes **~42%**. Because commission and MDR both scale with litres, the ratio holds at every ticket size — the argument does not weaken at ₹5 lakh._
