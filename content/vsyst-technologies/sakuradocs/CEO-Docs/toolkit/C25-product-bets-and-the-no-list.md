# C25 — Product Bets, Roadmap-as-Strategy and the No-List

_Toolkit · fills §4 and §5 of [[13-product-and-technology-leadership-for-a-technical-ceo|13 — Product and Technology Leadership for a Technical CEO]] · Owner: the CEO owns the bets and the no-list; engineering owns delivery inside a bet · Cadence: bets written at quarter start and reviewed quarterly; the no-list appended the day a request is refused and read whole once a quarter · No workbook tab — the check dates go on `Board Calendar`, the bet costs on `Annual Plan & OKRs` in [vsyst-ceo-workbook.xlsx](vsyst-ceo-workbook.xlsx)._

## Purpose

Two tables that together are the product strategy. The **bet list** is what the company is spending its only scarce resource on. The **no-list** is the written record of everything it refused, and why. Neither is complete without the other: a roadmap without a no-list is a wish list, and a no-list without bets is a company that has confused refusal with strategy.

A roadmap goes wrong in a predictable way — it becomes a queue ordered by who asked most recently, most loudly, or both. Cagan's objection is that such roadmaps lock in specific _solutions_ before discovery has happened, and that a feature request is only ever a customer's theory about a solution ([SVPG — Product Roadmaps](https://www.svpg.com/product-roadmaps/)). Dated columns compound it, because every date becomes a commitment and every shift breaks one; Now / Next / Later communicates confidence instead of false precision ([ProdPad — Now-Next-Later](https://www.prodpad.com/blog/now-next-later-roadmap/)).

Calling them **bets** rather than initiatives is not vocabulary. A bet is a claim you can lose, which forces you to write what losing looks like before you build. That is the discipline that stops a lost bet from becoming a blame event — decision quality is not outcome quality, and grading decisions by their results is the standard error ([Annie Duke — _Thinking in Bets_](https://www.annieduke.com/books/)). Two mechanics make it affordable at three people: **appetite instead of estimate** — "Estimates start with a design and end with a number. Appetites start with a number and end with a design" ([Basecamp — Shape Up, Ch. 3](https://basecamp.com/shapeup/1.2-chapter-03)) — and an outcome-rooted tree of opportunities beneath it, which exists precisely to stop a team overreacting to the most recent customer interview ([Product Talk — Opportunity Solution Tree](https://www.producttalk.org/2016/08/opportunity-solution-tree/)).

The no-list is the other half, and it is where the leverage is. "It comes from saying no to 1,000 things to make sure we don't get on the wrong track," said Jobs, and the strategic version is Porter's: strategy is choosing what not to do, and a position requiring no trade-offs is one anybody can copy ([Wikiquote — Steve Jobs](https://en.wikiquote.org/wiki/Steve_Jobs); [Porter — _What Is Strategy?_, HBR 1996](https://hbr.org/1996/11/what-is-strategy)). Traynor's is the practical one for the founder actually in the room: every justification for adding a feature has a rebuttal, and real product leadership means saying "this is a really great idea" and still saying no ([Intercom — Product strategy means saying no](https://www.intercom.com/blog/product-strategy-means-saying-no/)).

**The VSYST reason it matters more here than at a funded company:** engineering capacity is one to two people and one of them is the CEO. A yes does not delay a roadmap. It deletes a quarter of the company's total capacity to do anything else.

## When to use

- **At the start of each quarter**, converting the strategy kernel into three or four bets — the roadmap is the product half of the kernel's coherent actions ([[C04-strategy-kernel-one-pager|C04]], [[05-strategy-i-diagnosis-and-the-strategy-kernel|lesson 05]]).
- **Before writing a single line of code on anything above a week of work.** If it does not have a falsification condition it is not ready to be built.
- **The same day a dealer asks for something you will not build.** Not the next planning session — the same day, while his words are still his words.
- **At every quarterly review**, one question per bet: _did the falsification condition trigger?_
- **When a founder disagreement about the roadmap has happened twice.** A repeated argument is usually two people holding different unwritten bets. Write both down and the argument becomes checkable.
- **Not** for sprint scope, ticket priority or bug triage — that is the COO's engineering operations, and one theme in flight at a time is already its rule.

## How to fill (rules)

1. **Three or four bets. Never more.** A fifth bet at this size is a lie about capacity, and it is usually the one that gets half-built.
2. **Write the falsification condition before you build, because after you build you will negotiate with it.** A number and a date. "If this happens we stop" — not "we iterate", which is the word founders use to avoid admitting a loss.
3. **Cost is stated in founder-weeks plus the thing it displaces.** "Instead of \_\_\_" is a required field. A cost with no opportunity cost named is not a cost, it is a wish.
4. **The check date goes on the calendar the day the bet is written, with the metric source named.** If nobody can say where the number will come from, the bet is unmeasurable and must be rewritten before any code is written.
5. **Do not let a build hide inside a bet, or a bet hide inside a build.** Web billing at VSYST is a _build_ — the entitlement backbone must exist for revenue to exist at all, and the per-GSTIN, web-only, users-free direction is already settled ([[app-store-economics/08-dzzlo-subscription-strategy|subscription strategy]]). Whether dealers will complete a self-serve checkout **is** a bet, and it is a separate row.
6. **Every no gets a row the same day, in the asker's own words.** Their words, not your paraphrase — the paraphrase is where the job gets lost ([_The Mom Test_](https://www.momtestbook.com/)).
7. **Record the job behind the request, separately from the request.** Two different asks often share one job, and the job is frequently buildable when neither request is ([HBR — _Marketing Malpractice_](https://hbr.org/2005/12/marketing-malpractice-the-cause-and-the-cure), 2005).
8. **A "not now" without a written trigger is a lie.** With one — "revisit at 20 live tenants" — it is a plan. The trigger is a count, a date or a revenue level, or the honest word **never**.
9. **Anything marked _never_ stays never** unless the strategy kernel changes — and then it changes as part of a strategy decision logged in [[C29-decision-journal-and-one-way-door-log|C29]], not as a favour to whoever asked most recently.
10. **The count of askers is the only number that moves a row.** Not the size of the asker. A big dealer asking once is one asker.
11. **Read the whole no-list in one sitting, quarterly.** The value is never in a row; it is in the pattern. Five refusals sharing one job are a bet you have not written yet.
12. **The founders deliver a no, never a support reply.** A no delivered by someone who cannot explain the reason is heard as a brush-off.

## Template (a) — the bet card

```
BET <n>: <one-line name>                    quarter: <Q> · status: live / won / lost

WHAT WE BELIEVE    "Because <X is true about the dealer>, doing <Y> will cause
                   <measurable Z>."  The causal claim, in his terms.
WHAT WE'LL BUILD   The smallest thing that tests the claim.
                   APPETITE: <n> weeks.  (a number first, then a design)
WHAT WOULD PROVE   The falsification condition. A number and a date, written
US WRONG           before building. "If this happens, we stop."
WHAT IT COSTS      <n> founder-weeks + ₹<x>.  INSTEAD OF: <named displacement>
WHEN WE CHECK      <date> · metric source: <where the number literally comes from>
```

## Template (b) — the no-list

| Date | Who asked · tenant | The request, **their words** | The job behind it | Category | Reason (one line, the sentence you'd say to their face) | Trigger to revisit | Askers |
| ---- | ------------------ | ---------------------------- | ----------------- | -------- | ------------------------------------------------------- | ------------------ | ------ |

**The six categories of no.** Categorising is what makes a refusal repeatable and non-personal.

| Category                           | The test                                                                     | Cost of saying yes                                                           |
| ---------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Not our customer**               | The asker is outside the ICP ([[C09-icp-and-customer-discovery-guide\|C09]]) | A customer whose renewal you cannot predict, pulling the product sideways    |
| **Not our diagnosis**              | It does not touch adoption friction, trust, or the district motion           | You have changed strategy without holding a strategy meeting                 |
| **One dealer's bespoke ask**       | Nobody else has asked, and it encodes one firm's internal process            | Configuration surface that lives forever, in every migration, for one tenant |
| **Support burden we cannot staff** | It creates recurring human work with no owner                                | You have hired a person you did not budget for, and that person is you       |
| **Weakens the moat**               | It makes leaving cheaper or the ledger less trustworthy                      | A durable advantage traded for one deal                                      |
| **Wrong sequence, not wrong idea** | Genuinely good, genuinely not now                                            | Nothing — _provided_ it carries a written trigger                            |

## Template (c) — saying no to a paying dealer, in five moves

```
1. PLAY IT BACK BETTER THAN HE SAID IT
   "So what's costing you is that your accountant re-keys our statement into
   his own format every month-end — two hours he bills you for."
2. SAY NO PLAINLY, ONCE
   "We're not going to build a custom statement format."
   Not "it's on the roadmap". Not "maybe next quarter". Not silence.
3. GIVE THE REASON IN TERMS OF HIS BENEFIT
   "We are three people. Everything we build we maintain forever. If we build
   a layout per dealer, the ledger stops being the thing we make bulletproof
   — and the bulletproof ledger is what you're paying us for."
4. SOLVE THE UNDERLYING JOB ANOTHER WAY, TODAY, FREE IF IT'S CHEAP
   A CSV his accountant can pivot. A one-time template. Ten minutes on a call
   with the accountant. The job was his two hours; the feature was his guess.
5. WRITE IT DOWN IN FRONT OF HIM, AND NAME THE TRIGGER
   "I'm putting this on our list with your name on it. If four more dealers
   ask for the same thing, it moves up."  Then go back to him when the count
   moves — even if the answer is still no.
```

Two things never to do. **Never trade a feature for a signature** — a deal won with a bespoke build costs you every quarter thereafter. And never soften a no into a maybe; a maybe is a debt you repay with interest in March. Indian SME buyers respect a straight resource answer far more than a vague one: the disrespect is in being managed, not in being refused.

## Worked example — VSYST (illustrative)

Four bets for the coming year, **illustrative and written to be attacked** in a founders' meeting. The long-form versions are in [[13-product-and-technology-leadership-for-a-technical-ceo|lesson 13]] §4.4; the compressed board of them is what actually hangs on the wall.

| #     | Bet                                                                                                                                                                                                         | Appetite | Falsification condition                                                                                                                                      | Instead of                                      | Check                                                                                                     |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| **1** | **14-day activation is a product problem, not a training problem** — assisted onboarding, bulk customer + opening-balance import, guided first-invoice flow                                                 | 6 wks    | Fewer than **6 of the next 10** dealers issue a real invoice within 14 days on the new path — or those who do are no likelier to transact at day 90          | All reporting and analytics work this quarter   | Day 90 after the 10th dealer onboards · source: onboarding checklist + first-invoice timestamp            |
| **2** | **The 22:00–06:00 rate window is the habit loop, and the habit is the moat** — guaranteed push with SMS/WhatsApp fallback, one-tap confirm, carry-forward default, a confirmation log that reads like proof | 4 wks    | Nightly confirmation stays **below 80%** after four weeks — or it rises and 90-day retention is indistinguishable between high- and low-confirmation tenants | Nothing this quarter; runs alongside bet 1      | +6 wks, then +90 days for the retention split · source: confirmation events per tenant per night          |
| **3** | **Provable correctness sells better than any feature** — per-relationship reconciliation view, idempotent posting on every balance-writing path, a monthly statement an accountant can tick against Tally   | 8 wks    | **Zero** of the next 10 dealer conversations raise correctness unprompted **and** no pilot stalls on a reconciliation dispute in the same period             | The customer-side work in bet 4 slips a quarter | Each of the next 10 conversations (log the mention) + first accountant sign-off with no manual adjustment |
| **4** | **The customer-side surface is a dealer-retention feature, not a second product** — WhatsApp-delivered statement and order-status link needing no install, plus a one-tap invite                            | 3 wks    | Dealers with **5+ activated customers** show no better 90-day retention than dealers with 0–1                                                                | Nothing; small enough to run alongside bet 1    | 90 days after 20 dealers have the invite · source: activated-customer count vs tenant activity            |

Bet 1 is bet 1 because the kernel names time-to-first-invoice as the chain's weakest link, and improving any other link changes nothing until the weak one is fixed ([[05-strategy-i-diagnosis-and-the-strategy-kernel|lesson 05]] §2.2; [Richard Rumelt](https://en.wikipedia.org/wiki/Richard_Rumelt)). Bet 4 is deliberately measured on _dealer_ retention and never on customer engagement, because the dealer's B2B customers are the hard side of the network — no incentive to onboard, lower digital literacy, infrequent interaction ([a16z — _The Cold Start Problem_](https://a16z.com/books/the-cold-start-problem/)).

**The no-list, six illustrative rows.**

| Date       | Who · tenant           | Their words                                                  | The job                                                        | Category                         | Reason                                                                                               | Trigger                                                                     | Askers |
| ---------- | ---------------------- | ------------------------------------------------------------ | -------------------------------------------------------------- | -------------------------------- | ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- | ------ |
| 2026-07-14 | Ramesh, Bhilai         | "Bill mere purane printer ke format mein aana chahiye"       | His accountant re-keys the statement monthly, two billed hours | One dealer's bespoke ask         | Every layout we build we maintain forever, in every migration                                        | 5 askers                                                                    | 2      |
| 2026-07-22 | Fleet operator, Raipur | "Can we get DZZLO directly, without going through the pump?" | Wants his own multi-dealer fuel spend in one place             | **Not our customer**             | The dealer is the paying tenant; a customer-side product is a different company                      | **Never** while the kernel stands                                           | 3      |
| 2026-08-02 | Prospect, Durg         | "GPS lagao trucks mein, tabhi lenge"                         | Wants to know a delivery actually happened                     | Not our diagnosis                | The OTP already proves delivery; telematics is a different business with different economics         | Never                                                                       | 1      |
| 2026-08-09 | Ramesh, Bhilai         | "Poora data Excel mein download kar sakein?"                 | Wants to feel un-trapped, and wants his CA to check us         | **Weakens the moat** — partially | Statement and document exports yes; a dump that reconstructs the working ledger for a competitor, no | Shipped as a scoped statement export, 2026-08-20                            | 4      |
| 2026-08-11 | Prospect, Rajnandgaon  | "Aap hi entry kar do, humara staff nahi karega"              | Does not believe his staff will adopt it                       | Support burden we cannot staff   | Data entry on his behalf is a person we have not hired, and that person is me                        | Never as a free service; revisit as a **paid** onboarding SKU at 20 tenants | 2      |
| 2026-08-18 | Both co-directors      | "Dashboards and analytics before we sell more"               | Wants proof the product is working                             | **Wrong sequence**               | Analytics on six pilots is decoration; activation is the constraint                                  | 20 live tenants **or** 10 paying GSTINs                                     | 1      |

**What the pattern says**, which no single row does: three of six rows are versions of _"I do not believe this will get used"_ — the Excel export, the data-entry request and the GPS demand are all trust-in-adoption problems wearing feature clothes. That is not six refusals. That is bet 1, confirmed from a direction the bet did not anticipate. **That is the entire reason the list is read whole, quarterly, rather than row by row.**

## Common mistakes

| Mistake                                            | What it looks like                         | Fix                                                                                                                               |
| -------------------------------------------------- | ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| **A bet with no falsification condition**          | "Improve onboarding"                       | Rule 2. A bet that cannot be lost cannot be stopped, so it consumes capacity forever                                              |
| **Negotiating with the condition after building**  | "80% was always aspirational"              | Write it before, date it, and let a third person read it back at the review                                                       |
| **"Iterate" instead of "stop"**                    | A lost bet quietly becomes v2              | Continuing is allowed — as a **new** decision, with a new condition, logged in [[C29-decision-journal-and-one-way-door-log\|C29]] |
| **Five bets**                                      | Everything is a priority                   | Three or four. The fifth is the one that gets half-built                                                                          |
| **Cost with no displacement**                      | "6 founder-weeks"                          | Rule 3. "Instead of \_\_\_" or the cost is fictional                                                                              |
| **A build labelled a bet**                         | Billing listed as a hypothesis             | Rule 5. Builds get delivery dates; bets get conditions                                                                            |
| **The no-list written from memory at quarter-end** | Three rows, all paraphrased                | Rule 6. Same day, their words                                                                                                     |
| **"Not now" with no trigger**                      | Half the list says "later"                 | Rule 8. A count, a date, a revenue level, or _never_                                                                              |
| **The biggest dealer's ask jumping the queue**     | One tenant sets the roadmap                | Rule 10. Count of askers, not size of asker                                                                                       |
| **A maybe instead of a no**                        | "It's on the roadmap"                      | Move 2. Once, plainly, then solve the job another way                                                                             |
| **Never going back when the count moves**          | He asked, four others asked, silence       | The going-back is what keeps the relationship. Even when the answer is still no                                                   |
| **Reading the list row by row**                    | Quarterly review skims for anything urgent | Rule 11. Read it whole. The pattern is the product insight                                                                        |

## Related

Lessons [[13-product-and-technology-leadership-for-a-technical-ceo|13]] (§4–§5, the long form and the four worked bets), [[05-strategy-i-diagnosis-and-the-strategy-kernel|05]] (the kernel these convert), [[06-strategy-ii-moats-positioning-and-the-business-model|06]] (what "weakens the moat" means), [[07-customers-markets-and-founder-led-sales|07]] (where the requests come from), [[19-planning-okrs-and-capital-allocation|19]] (bets as capital allocation) · Templates [[C04-strategy-kernel-one-pager|C04]], [[C07-moat-and-seven-powers-audit|C07]], [[C09-icp-and-customer-discovery-guide|C09]], [[C22-internal-comms-calendar-and-all-hands|C22]] (the no-list said out loud), [[C23-stakeholder-and-investor-update|C23]] (bets reported monthly), [[C28-annual-plan-and-ceo-okr-sheet|C28]], [[C29-decision-journal-and-one-way-door-log|C29]] · COO side: [[T09-decision-log-and-adr|T09]], [[T18-project-charter|T18]], [[T19-quarterly-plan-and-review|T19]], [[T26-release-checklist|T26]] · [[CEO-Docs/toolkit/index|CEO Toolkit]]
