# The Problem We Want to Solve

Working file. Subject: the problem VSYST/DZZLO needs an Internet Payment Gateway to solve, the kind of IPG servicing that would actually solve it, and where the Bank's offer falls short of that.

Content for every topic is supplied by the user — nothing here is to be invented or carried over unverified. Prior fact base: `20260708/proposalplan.md` (all 10 bank questions answered) and `20260708/IPG_Proposal_UBI_VSYST.md` (§3 problem framing, §5 architecture, §7 asks). Workflow: `CLAUDE.md`.

## Status

- [x] Topic 1 — Why we need an IPG — _drafted 2026-07-16; all flags and open questions resolved_
- [x] Topic 2 — What kind of IPG servicing is required — _drafted 2026-07-16; open points settled 2026-07-19; verification APIs added 2026-07-19_
- [x] Topic 3 — The problem with the offer provided by the Bank — _drafted 2026-07-16; revised 2026-07-19 (Easebuzz-cost argument dropped, dealer margin figures removed, UPI reason answered, capability questions turned into asks); extended 2026-07-19 (pilot at one pump as the counter-offer, HPCL eDFS rollout ask, dealer deposits and interest split, aggregator-structure question). Volume projections for 10–15 dealers awaited — they go in last._

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

**Verification APIs alongside the payment rails.** Easebuzz offers verification services as well as collection, and we want them enabled on this account and priced along with the gateway — bank account verification first among them. The reason runs through this whole document: **the accounts on DZZLO are credit accounts.** Before a firm is given a limit, and before a dealer is set up to receive settlement, we have to establish that the entity is what it says it is and that the account is genuinely its own — checked at onboarding by API, not by collecting documents and reading them by hand. We ask the Bank to avail this from the aggregator and to negotiate its commercials on the same footing as the gateway charges.

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

**If what the Bank needs is an estimate before it commits on net banking, that estimate is something we can hand over directly** — built from observed throughput at the outlets, and set out at the end of this section — rather than inferred from a pilot run on rails our customers do not use. And if the Bank would rather see the number than be handed it, there is a pilot that would actually produce it.

### What we propose instead: one pump, on net banking

The Bank's instinct is to start small and read the result before committing further. We have no quarrel with it. Our disagreement is only about what the pilot is run on. **Start with a single petrol pump, on net banking, with the charge waived for that one outlet.**

One outlet is a contained exposure: one merchant, one settlement account, a known set of customers, and a waiver granted on a volume the Bank can see the size of before it begins. And unlike a UPI-and-RuPay start, it measures the thing actually in question — firm-to-firm transfers, at real ticket sizes, made in the app by the customers who pay this way.

What we would put on the table at the end of it, jointly with the Bank: transaction count and value, what the waiver costs on a real month's volume, how the payment flow performed for customers end to end, and how the market responded — how many of that outlet's customers moved off their own net banking and onto paying in-app, and how quickly they did it. That is the reading the Bank wants before it prices a waiver, and one pump on net banking produces it where a UPI pilot cannot.

**We are asking to be measured — on the rail we say this business runs on.** If the volumes do not appear, the Bank has learned that at the cost of one outlet.

### And then the Bank's own dealers: HPCL on eDFS

Where the program goes after the pilot is a question the Bank is better placed to answer than we are, because the answer is already on its books. **Union Bank of India extends the eDFS facility to HPCL dealers** — a ready set of petrol pump dealers who are already the Bank's customers, already onboarded, already known to it. Those are the outlets we would like to take this to next.

For the Bank it is the cheapest expansion available: no customer to acquire, no fresh onboarding risk, and IPG throughput added to accounts it already holds. For us it is a warm introduction instead of a cold approach.

**We therefore ask the Bank to help us reach them** — by sharing the list of HPCL eDFS dealers banking with UBI where it is able to, or, where customer confidentiality does not allow that, by putting the program to them itself or approaching them jointly with us. Any of those forms works. **What we are asking for is the Bank's channel, not its data.**

### What we are asking, and what we will meet

On net banking, in order of preference:

1. **A waiver of the charge**, recorded in the terms and conditions rather than held as an informal concession.
2. Failing that, **a flat fee per transaction** — any reasonable amount, so long as it is not a percentage of the transfer. The Bank sets the level; we ask only that it not scale with the value of the payment.

**And if the waiver is governed by a threshold, we ask the Bank to state it.** If there is a minimum number of onboarded dealers, a committed monthly transaction count or value, or a balance to be maintained, we would far rather meet a stated condition than argue against a rate. Every dealer we bring onto this program is a current account with Union Bank of India, with the outlet's settlement and its float running through it — that is the side of the trade the waiver is priced against, and it is the side we can grow.

**And there is more we can put on that side than throughput.** Every dealer joining this program opens a current account with Union Bank of India, and we are prepared to make a deposit with the Bank part of joining — so that what the waiver is priced against is not only money passing through, but balances that stay. That is a commitment we can actually hold to, because it is asked of the dealer at onboarding rather than hoped for afterwards.

On those deposits we would want an arrangement that works on both sides of the table: **the interest they earn shared between the Bank and VSYST**, structured as the Bank sees fit. The Bank gains deposits it did not have to go out and acquire; we gain a line that helps carry the cost of running the program that brings them in. We raise it here because it belongs to the same trade as the waiver — the Bank is being asked to give up a charge, and this is what we are offering to put on the other side of it.

### What we ask the Bank to confirm

Before the product is settled, we ask the Bank to confirm with the aggregator that the gateway can actually carry the payments this platform runs on:

1. **Net banking — NEFT, RTGS and IMPS — can be enabled on this merchant account**, on Android, iOS and web alike.
2. **A single transaction of ₹5 lakh completes** through the net-banking flow. Our transfers average ₹1 lakh and reach ₹5 lakh, and we need to know where the ceiling sits and whether it is set by the aggregator or by the customer's own bank.
3. **A current account operating on maker–checker can complete the payment.** Our customers are transport firms, and their accounts commonly need a second authoriser who is not sitting in the payment session. If the flow cannot be completed from such an account, the gateway does not reach the customers it is meant to serve — the very constraint described in Topic 1 would reappear inside the solution.
4. **UPI, debit card and credit card are available alongside**, so that no customer is turned away for want of a method he holds.
5. **The verification services described in Topic 2 can be enabled on this account and priced alongside the gateway** — and which of them the aggregator in fact offers.

These are questions of capability rather than commercials, and the answers decide what we are asking to be built. We would rather have them confirmed now than discover a limit after onboarding.

### A question of structure we want the Bank's view on

One question we would like to put to the Bank directly, because its answer shapes how this is built rather than what it costs. **Should VSYST collect the payments and settle out to the dealers, instead of the aggregator settling to each dealer directly?**

We can see what that would give us. One collection point, one reconciliation, settlement timed by the platform rather than by the aggregator's cycle, and a single account through which the whole program's flow is visible — including, in time, an order drawing fuel from more than one outlet.

We can also see that it would ask a good deal of us, and that is the part we want the Bank's reading on: what such a structure requires under the RBI's payment aggregator framework, what it would mean for the accounts involved, and whether the Bank would be comfortable with it at all. **We are not proposing it — we are asking whether it is the right shape**, and the Bank sees far more of these arrangements than we do.

The default stands as it is today: the aggregator settles to each dealer's own account on T+1, and VSYST touches no customer money.

### Projected volumes

_(to be added — data being gathered; collection template: `dealer-volume-data.xlsx`)_

Projected transaction volumes across **10–15 dealers**, built from observed throughput at the outlets, so the Bank can price the ask against real numbers. Three things this must carry when it is written:

- **Transaction count alongside value.** A flat fee is priced on the number of payments, so the count is the figure the ask actually turns on — value alone does not let the Bank price what we are requesting.
- **The current-account side.** Every dealer on this program is a Union Bank of India current account, with the outlet's settlement and float running through it. That is what a waiver is priced against on the Bank's own books, so the projection should give expected accounts and balances, not only throughput.
- **The deposit side.** If a deposit with the Bank is part of joining the program, the projection should carry the expected deposit per dealer and in aggregate. A balance that stays is priced differently from float that merely passes through, and it is the harder half of the offer to argue against.

This projection sits **alongside** the pilot offer above, not in place of it: the Bank can have the estimate on paper and verify it on one outlet before it commits any further.

### ⚠ Points to settle before this reaches the Bank

- **Why the Bank wants to start with UPI and RuPay — answered.** _(2026-07-19)_ The Bank wants an estimate of the volume the platform will carry, taken first on the modes that carry no MDR. The reply is now written into the section above: the free modes are not the modes our customers pay on, so the reading would be taken off the wrong population — and the estimate itself is something we can hand over directly rather than have it inferred from a pilot.
- **Easebuzz's charge to the Bank is unknown, and the case no longer rests on it.** _(2026-07-16 confirmed unknown; argument reframed 2026-07-19.)_ The ask now stands entirely on our own side of the trade — a percentage cannot work at these ticket sizes, a flat fee can, and here is the volume we bring. Nothing waits on knowing the Bank's cost. **Do not speculate about the Bank's cost or margin in the meeting**; if the Bank volunteers it, listen, but the ask does not change.
- **Hold the virtual-account fallback in reserve.** If the confirmations we are asking for come back negative on the ₹5 lakh ticket or the maker–checker account, the product that fits may be **bank-transfer collection over virtual accounts** — the customer pushes a real NEFT/RTGS from their own channel to a per-invoice virtual account, and the aggregator auto-matches it and confirms back to DZZLO. That carries any ticket size, works from a maker–checker account, and is typically priced flat per collection. It closes the ledger and removes reconciliation, but it keeps beneficiary management — a partial answer to Topic 1, not a full one. **Do not raise it until the confirmations come back**, or the Bank may take it as the ask and leave net banking where it is.
- **Decide whether Topic 2 needs the same trim as §3.** §2 no longer has any figures, but paragraphs 3–4 still describe the dealer's commission as a thin slice against which an MDR is large. That is qualitative, not a calculation — but if the rule is that the dealer's economics stay out of the Bank's view altogether, those paragraphs need reducing to "a charge that scales with value cannot be carried at these ticket sizes" and nothing further.
- **The deposit and the interest split need a defined mechanism before this is raised.** _(2026-07-19)_ The intent is clear — dealers place deposits with UBI, and the interest is shared between the Bank and VSYST — but a bank will ask three questions in the first minute: whose money is the deposit, what does it secure, and whose interest is being split. If the deposit is the dealer's own, the interest is ordinarily the dealer's too, and a share going to VSYST needs a structure the dealer has agreed to. **Settle which of these it is** — a security deposit VSYST collects and places with UBI, a minimum balance the dealer maintains in his own account, or a term deposit lien-marked to the program — **and the amount per dealer**. Raising it undefined invites the Bank to say no to a shape we never meant.
- **Asking for the eDFS dealer list runs into customer confidentiality.** _(2026-07-19)_ A bank generally cannot hand a third party a list of its customers. The ask is written so the Bank can say yes in whatever form it is able to — share what it can, introduce the program itself, or approach the dealers jointly with us. **Do not press for the list as such** if the Bank hesitates; the channel is what we actually need, and the joint-approach form gets it without asking the Bank to do something it cannot. Separately, **confirm the eDFS description before submission** — the document asserts only that UBI extends the facility to HPCL dealers, which is what we were told and nothing beyond it.
- **Name the verification APIs we want.** _(2026-07-19)_ §2 asks for verification services with bank account verification as the lead use. If PAN, GST or Aadhaar verification are also wanted, list them — the Bank has to carry a specific list to the aggregator before it can negotiate anything, and a category is not something it can price.
- **Know the RBI payment-aggregator position before asking the aggregator question.** _(2026-07-19)_ Whether VSYST should collect and settle out is a fair question, but the answer sits in the RBI's PA framework and the Bank will hear it that way. Go in knowing that the present model — aggregator settles to each dealer directly, VSYST touches no customer money — is the clean default and that the question is forward-looking. The section says so in as many words; **keep that line in the room too**, so it does not sound like we are describing something we already do.
- **The pilot offer and the projection must arrive together.** _(2026-07-19)_ §3 now offers both: here is our estimate, and here is one outlet on which the Bank can verify it. The pairing is strong only if the estimate is ready — **if the volume data is not gathered in time, the pilot becomes the whole ask, and the Bank prices a waiver against nothing.** Settle which outlet runs the pilot, and propose how long it runs before net banking opens wider rather than leaving that open for the Bank to set. Note also that the pilot's outputs are worded so that "cost" means what the waiver costs on a real month's volume — the Bank's own number, useful to it — and not a probe into the aggregator's pricing. Keep it that way, per the point above.
- **The volume data is a projection — write it as one.** A bank reads whatever number it is handed as a commitment, and a missed commitment is how a waiver gets withdrawn and a relationship sours. Show the basis (observed throughput per outlet, dealers signed vs. in pipeline), label it a projection, and offer a **review at 12 months against actuals** — a normal banking construct that reads as confidence rather than hedging. This is the counterweight to promising volume in the prose: **claim the scale qualitatively, quantify it only inside the labelled projection.**

---

## Inbox (raw points — unsorted)

### 2026-07-19 — five points for the Bank (verbatim as supplied)

> 1. we can start in trial basis for one petrol pump for IPG net banking. wavier off for one bank so that we can analyse transactions, volume, cost, customer experience, market response accordingly. 2. as Union bank of india provides eDFS account for HPCL dealers we would like to start with HPCL dealer with edfs account after we trial with one petrol pump. we would want a list of dealers assosiated with HPCL edfs account at UBI so that we can approach them already. 3. we would like union bank to also avial and negotiate for verification API provided by easebuzz. 4. "can and should vsyst (we) become aggregator of payments and then distribute settlements to dealers? what pro and cons would that come with?" we want to ask this question to bank. 5. we would also ask dealers opening new account in UBI for IPG to deposit amount. we would like to split the interest with bank taking care of finances of both vsyst and the bank.

Where each point was placed:

| #   | Point                                                                                    | Placed in                                                                                     |
| --- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| 1   | Trial at one pump on net banking, charge waived, to read volume/cost/experience/response | §3 → new _What we propose instead: one pump, on net banking_                                  |
| 2   | Start next with HPCL eDFS dealers at UBI; ask the Bank for the list                      | §3 → new _And then the Bank's own dealers: HPCL on eDFS_                                      |
| 3   | Bank to avail and negotiate Easebuzz verification API                                    | §2 → _Verification APIs alongside the payment rails_; echoed as confirmation #5 in §3         |
| 4   | Should VSYST aggregate and distribute settlements?                                       | §3 → new _A question of structure we want the Bank's view on_                                 |
| 5   | Dealers to deposit; interest split between VSYST and the Bank                            | §3 → _What we are asking, and what we will meet_; deposit bullet added to _Projected volumes_ |
