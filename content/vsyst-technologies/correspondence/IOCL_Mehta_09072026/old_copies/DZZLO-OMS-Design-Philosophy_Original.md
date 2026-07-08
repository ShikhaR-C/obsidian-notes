---
title: "DZZLO OMS — Design Philosophy"
---

<!--
DRAFT FOR REVIEW — points to confirm before we finalise:

1. Provenance: §1 says "a copy of it lies on the table as we write" (true to the photographed
   brochure). If the folder is Mr. Mehta's, or if there is a personal HAS connection (member,
   colleague, family), say the word and we will weave the true story in — it would strengthen §1.
2. HAS claims are limited to what the brochure itself states (32,000 km, 700–1,000 kiosks,
   50 km spacing, V-SAT, vehicle sets, last-5-locations, distress relay, 500 m beep, 3-year
   guarantee, sealed/tamper-proof). If you know its actual deployment history / years of
   service, we can add it — I deliberately did not invent any.
3. Naming: "Sparsh Communications Ltd., a Sanghi Group company" is credited by name in §2.
   Confirm this is desirable.
4. DZZLO facts are drawn from the UBI/IPG proposal (live since June 2021, verified order
   chain, common ledger, immutable escalated records, bill-to-bill, credit limits by amount
   and period, GST/TDS, advance deposits, no fund custody). Flag anything that shouldn't
   appear in a client-facing document.
5. Signature block names all three directors — trim if you prefer.
~2,100 words. Once you've made your edits, ask and I'll produce the formatted document.
-->

# DZZLO OMS — A Design Philosophy

_From the founders of VSYST Technologies_

## 1. Why We Wrote This

Most software documents open with a list of features. This one opens with a red cardboard folder.

A copy of it lies on the table as we write. On its cover, a satellite beams dotted lines down onto a winding highway, a roadside kiosk, a computer. Inside the flap, four questions are printed in white on red:

> _Where is your vehicle? Is your vehicle idling? Has it met with an accident? Are the goods safe?_

The folder introduced the **Highway Automation System — HAS**, conceived in the late 1990s by Sparsh Communications Ltd. of Hyderabad, a Sanghi Group company. More than a quarter of a century later, we build and operate **DZZLO OMS**, an order and credit management platform for petrol pump dealers and the transport companies they serve. The technology in our pockets today would have read as science fiction to the engineers of HAS. Yet the questions we answer every day are the same four questions on that flap — followed by the ones that come right behind them: _Was the fuel delivered? Is the invoice correct? Are the books settled? Will I be paid?_

We believe great systems are built on principles, and that principles outlive the hardware that first carried them. Ours are inherited, and we know exactly from where. So before we explain what DZZLO OMS does, we want to explain what it believes — and give proper credit to the system that believed it first.

## 2. The Legacy: What HAS Got Right

To appreciate HAS, consider what its designers had to work with. There was no GPS in a civilian truck, no mobile network worth the name outside the metros, no internet beyond a handful of offices. A vehicle that left the depot effectively vanished until it arrived — or didn't. Against that darkness, HAS proposed something audacious: network roughly **32,000 kilometres of national highways**, plus the important state highways, with **700 to 1,000 kiosks placed every 50 kilometres** — each one equipped with a V-SAT link, a computer, a telephone and a fax machine, all of them speaking to one main server through the sky. A nervous system for the Indian highway.

Every member vehicle carried a **vehicle set**: an electronic monitoring device with its own distinctive code number, PIN-protected, hermetically sealed, tamper-proof, guaranteed for three years. As the vehicle passed each kiosk, its position was logged automatically and relayed to every kiosk in the country. An owner who wanted to know where his truck was made a **local phone call** to the nearest kiosk, quoted his code number, and the operator read back the vehicle's **last five locations, with time**. Members who had a computer and modem could dial in and see it themselves, with software supplied on request. Members who had neither received a printed page. Nobody was turned away for owning too little technology.

The details still make us smile with admiration. The vehicle set carried a **distress switch**; if the vehicle was beyond a kiosk's range, the alarm kept transmitting until a _passing member vehicle_ picked it up, acknowledged it, and carried the message to the next kiosk — the network's members were each other's safety net. An owner could send his driver a message, or fax documents to a kiosk along the route; the vehicle set **beeped within 500 metres** of a waiting kiosk, telling the driver to stop and collect what home had sent. Weather, road conditions and blockades were passed down the line. Fleet movement reports came, on request, neatly printed.

Holding this folder, it is easy to understand why the idea commanded respect. And reading it closely, we can name precisely what its designers got right:

- **It asked the operator's own questions, in the operator's own words.** Not "telematics infrastructure" — _where is your vehicle, are the goods safe._
- **It moved nothing anonymously.** Every vehicle on the network had an identity: a code number, a PIN, a seal.
- **It engineered trust into the hardware.** Sealed, tamper-proof, guaranteed — the record could be believed because it could not be quietly altered.
- **It met every member at their own level of technology.** A phone call, a printed page, a fax handed to a driver, a modem login for those who wanted one.
- **It made the network itself the safety net.** A distress call was never allowed to die on the roadside.
- **It kept its scope honest.** One job — the movement of vehicles and goods — done thoroughly, end to end.

We claim no corporate lineage from HAS. We claim something we consider stronger: an inheritance of principle, accepted knowingly and carried with care.

## 3. Our Principles — Inherited and Kept

Four principles run through DZZLO OMS. Each one was demonstrated first on the highways of the 1990s; our work has been to keep them alive on new terrain.

### Principle 1 — One local call gets the answer

HAS promised that a local call to the nearest kiosk would tell an owner, in a minute, where his vehicle had last been seen. The deeper promise underneath: _an operator should never have to work hard to learn the state of his own business._

DZZLO OMS is built on that promise. A dealer or a transporter opens the app and the answer is already on screen: today's orders, deliveries in progress, invoices raised, dues outstanding, credit consumed. The kiosk is now zero kilometres away — it lives in the pocket — but the standard is the same one HAS set: speed to the answer is not a luxury; it is the point.

### Principle 2 — Nothing moves anonymously

On the HAS network, no vehicle was a stranger: every member carried its code number in a sealed set. Its designers understood that monitoring without identity is just noise.

In DZZLO OMS, every order carries a **verified company, order manager, driver and vehicle**. When a lorry arrives at the nozzle, the dealer's staff know exactly who is standing before them, on whose account, and on whose authority. No anonymous orders, no repudiated deliveries, no "who sent this truck?" The code number became a verified transaction chain — the principle did not change.

### Principle 3 — The record is sacred

HAS sealed its vehicle sets hermetically and relayed every sighting to every kiosk in the country. Tamper-proofing was not a feature; it was the foundation. A record you can quietly edit is not a record — it is a draft.

So in DZZLO OMS, dealer and customer share **one common ledger, maintained like a bank statement**, and once a record is escalated it **cannot be deleted — by either side, or by us**. Invoices are GST-compliant, TDS is handled in-platform, and payments match bill-to-bill rather than vanishing into lump sums. Disputes are settled by reading, not by arguing, because the books are authentic by construction.

### Principle 4 — No message left stranded

The most moving detail in the HAS design is the distress relay: an alarm beyond kiosk range kept transmitting until a fellow member's vehicle carried it to safety. The network simply refused to lose a message that mattered.

DZZLO OMS treats every order, payment and acknowledgement with that same stubbornness. State is visible to both sides at every step; nothing is silently lost, and nothing important waits quietly in a corner — **unpaid invoices are shown by default**, credit exposure is displayed before it becomes a problem, and every acknowledgement is recorded. _Never lose an order. Never bury a due._

## 4. What a New Era Demands

The world (generation) changed. The principles did not.

HAS was designed for an India where moving a message across 32,000 kilometres required a satellite dish, and where a computer was a destination — you travelled to it. Its designers solved that era's hardest problem, brilliantly. Today that particular problem is solved for good: there is a connected computer in every driver's pocket that outruns anything a kiosk could hold.

But the highway economy acquired new terrain that no one in the 1990s was asked to design for. The hard questions moved **from movement to money**. Diesel worth millions is sold on credit every day, and that trade still runs on chat messages and hand-keyed ledgers on both sides. Payments arrive as unallocated lump sums that take accountants days to reconcile. A transporter hesitates before typing a dealer's account number into a five-lakh transfer — one wrong digit is a serious incident — and a dealer hesitates to circulate his account details at all. GST and TDS regimes that did not exist then now govern every invoice. UPI has taught everyone that money can move in seconds, and they now expect information to move the same way. Banks, payment aggregators and oil-company programmes offer APIs where fax machines once stood. A data-protection law now governs every record a platform keeps.

None of this is a criticism of HAS — you cannot fault a system for not answering questions its era never asked. The four questions on the folder simply grew companions: _Are the books right? Is the credit under control? Will the payment come?_ New terrain, waiting for the old principles.

## 5. How DZZLO OMS Carries the Torch

Each capability of DZZLO OMS is an inherited principle, restated in today's materials.

**A kiosk every 50 kilometres → an app at zero kilometres.** The information point is no longer up the road; it is in the dealer's hand and the transporter's pocket. Orders, deliveries, ledgers and dues, live, wherever the operator stands — the local call, with the distance removed.

**A code number on the vehicle → a verified identity on the whole transaction.** HAS identified the vehicle; DZZLO identifies the company, the order manager, the driver _and_ the vehicle, on every single order. Identity was extended from the machine to the transaction it performs.

**The last five locations, with time → the whole journey of the order.** Placed, delivered, invoiced, paid — every step stamped and visible to both parties in the shared ledger. Where HAS showed you where the truck had been, DZZLO shows what it carried, what it cost, and what remains unpaid.

**A sealed, tamper-proof vehicle set → a ledger no one can quietly edit.** The hermetic seal became the immutable record; the guarantee card became bill-to-bill discipline. Trust, engineered in, exactly as before.

**The distress switch → alarms that ring before the emergency.** HAS raised the alarm when trouble struck. DZZLO raises it earlier: per-customer credit limits by amount and by period, a utilisation bar that fills before exposure becomes debt, dues visible by default. The best distress call is the one that never has to be made.

Here is what that adds up to, on an ordinary night. A transporter's lorry needs diesel at 11 p.m., four hundred kilometres from its home office. The company's order manager places the order in the app, naming the driver and the vehicle. At the outlet, the dealer's staff see a verified order — known company, known driver, known number plate — and fill the tank. The delivery becomes a digital invoice; the invoice becomes an entry in the one ledger both sides read; the customer's credit bar moves; the owner, at home, watches it happen.

(In 1999, that owner would have dialled the nearest kiosk in the morning to learn where his truck had been. He may well be the same man — only now the answer reaches him before he thinks to ask, and it includes the money. The question is answered with the same respect. Only the rails are new.)

## 6. What We Refuse to Do

HAS kept its scope honest, and discipline is part of the inheritance. So, plainly, what we will not do — even though we could:

**We refuse to touch the money.** Payments flow from the customer directly to the dealer's own bank account over regulated rails. We are the technology layer, nothing more. A scorekeeper who holds the stakes is no longer trusted as a scorekeeper.

**We refuse to let anyone rewrite the past — including ourselves.** No silent edits, no convenient deletions, not even when a customer asks nicely. The day a ledger can be rewritten is the day it stops being worth keeping.

**We refuse to become everything-software.** DZZLO OMS is an order and credit management system for the fuel and transport trade. Features earn their place by serving orders, credit and books; whatever does not, stays out. When in doubt, we leave it out.

**We refuse to break what your hands remember.** The trade has its disciplines — bill-to-bill settlement, the day-end reconciliation, the way an order is called in. We refine workflows; we do not redesign them for novelty. A tool that changes shape every season is not a tool an operator can trust.

And underneath all four: the books belong to the dealer and the customer whose trade they record. We keep them; we do not trade in them.

## 7. An Invitation

The last line of the HAS folder reads: _"And this is just the beginning."_

Its authors meant it about their own pipeline of services. We have chosen to read it as a sentence left open — an unfinished promise handed to whoever was willing to pick it up. This document is our way of saying: we picked it up, deliberately, and with both hands.

If you knew HAS — if you ever quoted a code number over a local call, or waited for the beep that meant papers from home — you will recognise this system within the first five minutes. The same four questions, answered with the same respect for the person asking, joined now by the questions of credit and payment that today's trade lives on.

Come and see it running. Watch an order travel from a lorry cab to a dealer's ledger in less time than a kiosk telephone took to ring. Nothing would please us more than to show it to the people who remember where these ideas began.

The highway is the same highway. The questions are the same questions. The torch has simply changed hands — and we intend to carry it a very long way.

_For VSYST Technologies Pvt. Ltd._
**Paresh Chawra · Shikhar Chawra · Shikha Chawra**
Raipur, Chhattisgarh — July 2026
