# 02 — The Two-Sided Problem: Sell to the Dealer, Seed the Customer

_Phase 1 · Understand · Week 0. After this lesson you can explain why DZZLO needs two kinds of user but sells to only one, list what works for a dealer with zero customers linked and what genuinely needs the customer, say in each segment's own words why the customer says yes, run the dealer → customer seeding sequence in order, and state the one activation number that decides whether a dealer counts._

## Explain-it-like-I'm-5

Think of a mobile-recharge-and-general shop in a Raipur mohalla. The owner keeps a khata — a notebook of who took what on udhaar. It is useful to him the day he buys it: he stops forgetting, he stops losing money. Nobody had to convince his customers to buy a notebook.

Now he starts sending each customer a one-line SMS every time he writes an entry. Month-end arguments stop. The customer bought nothing, installed nothing, learned nothing — and yet the customer is the reason the shop's biggest headache disappeared. **The shopkeeper paid. The customer benefited. And the only person who could ever get the customer's attention was the shopkeeper himself.**

That is DZZLO. The pump dealer buys the notebook. His credit customers — transporter, factory, crusher, hospital — are the other half of every argument he wants to end. Our marketing job is to sell one side and let that side pull the other in.

## 1. What "two-sided" actually means, and why it is dangerous

A **two-sided product** is one where value comes from two groups interacting through it, not from one group using a tool. The failure mode is the **cold start problem** — an empty network is worth nothing to either side, so neither joins, so it stays empty. The canonical treatment is Andrew Chen's _The Cold Start Problem_, written out of a decade at Uber and a16z ([coldstart.com](https://www.coldstart.com/); [a16z](https://a16z.com/books/the-cold-start-problem/), 2021).

Three of Chen's ideas do all the work for us:

- **The hard side.** "A minority of users that will create disproportionate value and as a result… have disproportionate power" — and "the hardest problem to solve in creating the first atomic network is, well, the hard side" ([Andrew Chen — Solve a Hard Problem](https://andrewchen.com/solve-a-hard-problem-cold-start-problem/), 2021). YouTube's hard side is creators, not viewers; Uber's is drivers, not riders.
- **The easy side** follows once the hard side is dense enough to be reliable.
- **The atomic network** — "the smallest network needed that can stand on its own," and "probably smaller and more specific than you think" ([Lenny Rachitsky — The Atomic Network](https://www.lennysnewsletter.com/p/atomic-network), 2021). That is HC3, and why we saturate Raipur district before touching a second one.

The trap most founders fall into: **assuming the hard side is the side that pays.** For DZZLO it is the opposite. Map it honestly.

| | **Dealer** (petrol pump owner, bulk-diesel operator, lubricant distributor) | **Customer** (transport fleet, factory, contractor/mine, hospital) |
| --- | --- | --- |
| Pays? | **Yes** — owns the tenant, pays per GSTIN ([[08-dzzlo-subscription-strategy\|subscription strategy]], 2026-07-29) | **No** — rides free on the dealer's tenant for core trading |
| Uses it daily? | Yes — morning rates to evening reconciliation | Occasionally — a rate confirmation, an order, a ledger check |
| Direct benefit | High. His business, his money, his GST notice | Real but quieter: no rate disputes, ledger visibility, proof |
| Digital comfort | Medium–high; already runs OMC portal, GST filing, DU software | Variable; the munshi and fleet manager, not the owner |
| Hard or easy side? | **Easy side for us** — motivated, reachable, one address | **Hard side** — no payment relationship, no reason to learn a new app |
| Who can reach them cheaply? | Us: referral, OMC territory manager, association, pump visit | **Only their dealer.** Nobody else has their attention |

The last row is the whole lesson. The side that pays us is the only cost-effective channel to the side that doesn't. That is HC2: **sell to the dealer, seed the customer.** The analysis behind this table is [[11_EDUCATION_GAP|the dealer-customer dependency gap]] §1–§4; read it once and don't re-derive it.

## 2. Single-player value: what the dealer gets with zero customers linked

The escape from a cold start is to be useful before the network exists. Chris Dixon called it **"come for the tool, stay for the network"** — "the tool helps get to initial critical mass. The network creates the long term value… think of single-player tools as kindling" ([cdixon.org](https://cdixon.org/2015/01/31/come-for-the-tool-stay-for-the-network), 2015).

DZZLO has real kindling. Know it cold — it is what you sell on the first visit ([[00_OVERVIEW|product overview]] §3–§4).

| What the dealer gets | Works with zero customers linked? | How he says it himself |
| --- | --- | --- |
| GST invoicing — three-tier PRODUCT / CASH_REIMBURSE / GST | **Yes** — the customer is just a name and a phone number | "Bill se bill milta hai. CA ko file ready milti hai." |
| TCS auto-added past ₹50L per customer per FY | **Yes** — computed from his own sales/receipt ledger | "TCS ka tension khatam — system khud pakad leta hai." |
| Credit ledger, per-customer balance, ageing, credit limits | **Yes** | "Kiska kitna baaki hai, abhi ke abhi pata hai." |
| DIP module — tank dips, density, decants, inspection log | **Yes** — purely his own tank | "Stock aur bikri ka farak roz milta hai, mahine ke aakhir mein nahi." |
| Driver OTP dispatch | **Mostly** — OTP reaches the driver; customer confirmation is the upgrade | "Gaadi kis ne li, kab li — proof hai." |
| Vouchers, payment allocation, month-end credit/debit roll-up | **Yes** | "Cheque, NEFT, fleet card — sab ek jagah." |

Say it plainly at the pump: **"Aap akele bhi kal se chala sakte hain."** You can run it alone from tomorrow. That removes the biggest objection before it is raised, and it is honest — the only kind of claim worth making to a three-year customer.

## 3. What genuinely needs the customer — and the honest state of it today

Three things do not work single-player — and they are the three the dealer wants most.

| Needs the customer | Why both sides | Value released when both are live |
| --- | --- | --- |
| **Rate confirmation window** — dealer sets next-day rates; customer confirms 10 PM–6 AM; unconfirmed rates auto-lock at 6 AM | A confirmation with nobody to confirm is just a rate list | Kills the "hum ne yeh rate maana hi nahi tha" dispute for good |
| **Customer-placed orders** | Otherwise the dealer keys in WhatsApp messages himself | Order-desk load drops; fewer wrong quantities and vehicles |
| **Shared ledger and voucher settlement** | Two ledgers become one only when both parties read the same one | Month-end goes from days of phone calls to one screen |

**The honest bit, and you must say it out loud.** Today the customer joins by **phone-OTP invite into the same React Native app**, with scoped roles — CPrimary, CAdmin, COrder, CAccount, CView — so a firm's owner, order-placer and accountant can be three different people. That works. The **WhatsApp-first, zero-install customer flow** in [[11_EDUCATION_GAP|the education-gap doc]] §7–§8 — one-tap confirm link, invoice PDF, payment link, no account — is the **intended direction and is not built yet**. Do not sell it, demo it, or put it on the landing page. When a dealer asks: "Aaj customer ko app par OTP se jodna hota hai. WhatsApp-only version roadmap par hai." Its running cost is real too — Meta's India rate card is roughly **₹0.8631 per marketing message and ₹0.115 per utility/authentication message, plus 18% GST** ([WhAutomate](https://whautomate.com/whatsapp-business-api-pricing-india), 2026) — **VERIFY LIVE** against Meta's pricing page and a BSP quote (Wati / AiSensy / Gupshup).

## 4. HC2 in practice: the dealer is the buyer *and* the channel

The customer-side pitch exists. It is just not delivered by us.

- **We market to dealers.** Referral, OMC territory manager / IOCL relationship, dealer association, CA, pump visit — in that order (HC4, [[12_OWNER_ACQUISITION|Owner Acquisition]] §5).
- **The dealer markets to his customers**, using material we write for him: a WhatsApp message, a one-page Hindi leaflet for the office wall, a two-minute video. He sends it. It lands as "my supplier asked me" — a request no transporter ignores — instead of "some Raipur software company messaged me," which every transporter ignores.
- **Never** run customer-side campaigns where no dealer is live. A transporter who signs up and finds none of his four pumps on the platform has learned that DZZLO is useless, and that is expensive to unteach.
- Direct customer-side marketing unlocks **only** once several dealers in one district are live — the flywheel in §7.

The seed message is a marketing asset, not an afterthought. A first draft, finished in exercise 2 and stored in [[M08-onboarding-and-activation-checklist|M08]]:

> नमस्ते [नाम] जी। हमारा पंप अब **DZZLO** पर है। कल का रेट आपको रात में फ़ोन पर दिख जाएगा — एक बार confirm कर दीजिए, सुबह कोई बहस नहीं। कितना डीज़ल लिया, कितना बाकी है — पूरा हिसाब कभी भी देख सकते हैं। आपके लिए **बिल्कुल फ्री** है, इसी नंबर पर OTP आएगा। जोड़ दूँ?

> Namaste [Name] ji — our pump is now on DZZLO. You'll see tomorrow's rate on your phone tonight; confirm once and there's no argument at delivery. Litres taken, amount outstanding, statements — all visible any time. **Free for you**, OTP comes to this same number. Shall I add you today?

## 5. Why the customer says yes — in their words, by segment

Three reasons repeat across every segment: **no more rate disputes**, **ledger visibility without asking**, and **one place for all their fuel suppliers** — the multi-dealer support in `dealer_custs`, where one customer firm carries a separate credit line with each dealer. The wording changes; the reason doesn't. Persona depth is [[03-who-exactly-icp-personas-and-the-target-list|lesson 03]] and the field cards in [[M02-icp-and-persona-field-cards|M02]]; the ICP method is [[C09-icp-and-customer-discovery-guide|C09]].

| Segment | Who taps the phone | Their sentence | What the dealer says back |
| --- | --- | --- | --- |
| **Transport fleet** (5–50 trucks — the core) | Owner or munshi; driver at the pump | "Parchi kho jaati hai, aur mahine ke aakhir mein 15 din bahas mein jaate hain." | "Har litre ka digital proof, driver ke OTP ke saath. Aapka hisaab aur mera hisaab ek." |
| **Factory / plant** (DG sets, boilers, captive fleet) | Purchase officer + accounts | "Rate approval chahiye aur GST input match hona chahiye." | "Rate raat mein aata hai, aap approve karte ho — record ban jata hai. GST invoice turant." |
| **Contractor / mine / crusher** | Site supervisor; owner signs | "Site par kitna diesel gaya, kis machine mein — pata hi nahi chalta." | "Site aur vehicle ke hisaab se khapat, roz. Chori ka rasta band." |
| **Hospital / institution** (DG backup, ambulances) | Administrator; audit pressure | "Audit mein har purchase ka document maangte hain." | "Har delivery ka OTP-verified invoice, statement PDF ek click mein." |

Note what is missing from every row: our features. The customer never hears "multi-tenant OMS." He hears the end of a monthly argument. That is HC5, applied to the free side.

## 6. Four Indian companies where the seller brought the buyer

We are not inventing this motion; it is the default shape of Indian SMB software.

| Company | The move | What it teaches DZZLO |
| --- | --- | --- |
| **Khatabook** | Digital udhaar khata sold to the shopkeeper, who adds his customers by phone number; 5 crore+ downloads, 5 crore registered merchants, 12 languages ([Khatabook](https://khatabook.com/about/), 2026) | Single-player first; the counterparty is a record before he is a user |
| **OkCredit** | Same wedge, explicit about the counterparty's interface: _"Customer ko app ki zaroorat nahi. Usse SMS se hisaab milta rahega… Har entry par customer ko SMS, pakka proof"_ ([OkCredit](https://okcredit.in/blog/steps-to-use-okcredit-app-for-kirana-business/), 2026) | The hard side's touchpoint should be the lightest thing that works — the WhatsApp direction, validated |
| **Udaan** | Field agents, live demos, first-order support, embedded credit; 3M+ active retailers, 6M+ orders/month. Co-founder Sujeet Kumar on the resistance: merchants "have seen many startups come to them before"; they "placed small orders, but slowly as they saw the benefits, became more reliant on us" ([TechCrunch](https://techcrunch.com/2020/03/26/inside-udaans-push-to-digitize-indias-b2b-retail-market/), 2020; [EQMint](https://eqmint.com/how-udaan-became-indias-fastest-b2b/)) | Trust is earned by one small transaction, not a pitch |
| **Dukaan** | Seller builds a store on a phone in minutes and shares the **link** on WhatsApp — the buyer installs nothing; 98%+ of traffic mobile ([Inc42](https://inc42.com/startups/how-dukaans-mobile-first-approach-led-to-building-a-shopify-rival-for-indian-smbs/), 2022) | Distribution to the buyer is a link the seller forwards, not a campaign we run |

The thread across all four — and the reason [[09_PRODUCT_VS_SALES|product vs sales]] says DZZLO cannot be pure product-led — is **distribution-first plus single-player product**, never customer-side subscription ([Strategy Boffins](https://www.strategyboffins.com/start_up_strategy/mybillbook-vs-okcredit-vs-khatabook/)).

## 7. The sequence — and the traveling-customer flywheel

Order matters more than effort. The how-to is [[07-onboarding-and-activation-getting-both-sides-live|lesson 07]] and [[M08-onboarding-and-activation-checklist|M08]].

1. **Dealer live** — tenant created, products and rates set, first real invoice issued. Days 0–3.
2. **Dealer invites his top 3 credit customers** — biggest outstanding, most disputes, most trusting. Not all forty. Three. He sends the §4 message from his own number; we sit beside him for the first one.
3. **Both sides active** — one rate confirmed in the 10 PM–6 AM window, one invoice settled against a voucher. This is where the dealer stops evaluating and starts depending.
4. **Ask for the referral, move to the next dealer** — a named pump, not a category (lesson 08).

Then the compounding part. A transporter buying from four Raipur pumps, live on DZZLO with one, becomes an unpaid salesman for the other three: his driver shows the DZZLO record at Pump Y, whose owner hears the same from a second and third customer and asks us to onboard. That is the **traveling-customer flywheel** — warm inbound at zero acquisition cost, worked out in [[05_Beachhead_and_Expansion|the beachhead and expansion doc]] §6, with transporter economics in [[04_Target_Customer_Transporters|transporters 04]]. It only spins at density, which is the mechanical reason HC3 says saturate one district first. **Instrument it from day one**: every pump a customer asks about goes on the target list ([[M03-target-list-builder|M03]]) with that customer's name in the "referred by" column.

## 8. The number that decides it, and the four ways this goes wrong

An **activation metric** is the trackable event proving a new user reached real value, and it must be time-boxed, because "activation without a deadline is just eventual usage" ([Appcues](https://www.appcues.com/blog/product-activation-metric), 2026). Our definition, HC8, is deliberately two-sided:

> **A dealer counts as activated only when ≥1 customer firm is linked to his tenant AND ≥1 invoice has flowed within 14 days of tenant creation.**

Signups are not the number. Downloads are not the number. Trials are not the number. This row goes on the weekly marketing scorecard ([[M13-marketing-scorecard-and-cac-calculator|M13]], [[11-metrics-budget-and-the-marketing-scorecard|lesson 11]]) and feeds the company scorecard the COO keeps ([[T05-kpi-scorecard|T05]]).

| Failure mode | What it looks like | Why it kills you | The fix |
| --- | --- | --- | --- |
| **Dealer-only ghost tenants** | 20 signed dealers, invoices flowing, zero customers linked | You sold a billing tool. Renewal gets judged against a one-time desktop licence, not against dispute-free trading | Step 2 of §7 is not optional; no dealer is "done" without three invites sent |
| **Customer-side cold marketing** | Ads or WhatsApp blasts to transport nagars before dealers are live | Burns the segment's goodwill and our ₹30–50k month for nothing (HC7) | HC2 — every customer touch is delivered by a live dealer |
| **Waiting for the WhatsApp flow** | "We'll start selling once zero-install is ready" | Engineering is weeks-to-months away and demand rots. The app invite works today | Sell now; WhatsApp is an upgrade that raises activation, not a gate |
| **Pumps with no B2B credit customers** | A pure retail/highway pump, 95% cash-and-UPI walk-ins | Nothing to link, confirm or reconcile — it can never activate | Qualify on visit one: "Udhaar par kitni parties hain?" Under five regular credit customers → deprioritise ([[M02-icp-and-persona-field-cards\|M02]]) |

## 9. At VSYST — applying this now

Three people, no marketing budget spent yet, one district. This week:

- **Domain director (fuel distribution)** — write the §2 single-player list in a dealer's own Hindi, one line each, from how his own pump talks. Thirty minutes. It becomes the spine of the pump-visit script in [[M05-pitch-scripts-and-objection-handling|M05]] and [[06-founder-led-sales-the-pump-visit-demo-and-close|lesson 06]].
- **CEO (technical)** — confirm in the code what genuinely works with zero linked customers, so §2 is verified rather than remembered; and give the WhatsApp-flow status in one sentence the other two can repeat verbatim. No date is a fine answer; a wrong date is not.
- **Third director** — own the activation row: say where the two numbers (customers linked, first invoice date) are read from today, even if that is a Mongo query pasted into a Sheet.
- **All three** — agree HC2 out loud, and write it into the charter in [[M01-marketing-charter-and-90-day-plan|M01]]: no customer-side marketing in any district until a dealer there is live.

Everything downstream assumes this. [[03-who-exactly-icp-personas-and-the-target-list|Lesson 03]] names who to visit, [[04-the-message-positioning-and-the-one-line-pitch|lesson 04]] writes what to say, [[07-onboarding-and-activation-getting-both-sides-live|lesson 07]] gets both sides live. If in doubt: **both sides live, or it doesn't count.**

## 10. Exercises

**10.1 — The single-player list, in the dealer's words (30 min).** Take the six rows of §2. For each, write one sentence a Raipur pump owner would actually say, in Hindi or Chhattisgarhi, with a rupee number or a time saving where you can honestly attach one. Kill any row you cannot defend on a live tenant. **Artefact:** a six-line list pasted into [[M05-pitch-scripts-and-objection-handling|M05]] under "single-player openers," read aloud once to the domain director for the wince test.

**10.2 — The dealer → customer invite message (45 min).** Start from the §4 draft. Produce three variants — transporter, factory, hospital — each in Hindi and English, under 60 words, ending in a question answerable with "haan". Send the transporter variant to one real credit customer of a pump you know and note the reply verbatim, including silence. **Artefact:** the six messages plus that reply, saved into [[M08-onboarding-and-activation-checklist|M08]] as the "customer seed message" block.

**10.3 — Write the activation row into the scorecard (20 min).** Add one row: metric name `Dealers activated (≥1 customer linked + ≥1 invoice in 14 days)`, owner, source of the number, weekly target for four weeks, and today's actual — which may well be zero. Zero written down beats a good feeling. **Artefact:** the row live in [[T05-kpi-scorecard|T05]] and mirrored in the workbook's Marketing Scorecard tab, ready for [[M13-marketing-scorecard-and-cac-calculator|M13]].
