# 16 — Decisions, Delegation and Not Being the Bottleneck

_Phase 4 · Running the Company and Yourself · Months 6–24. After this lesson you can name the three mechanisms that make a founder-CEO the bottleneck and measure whether you currently are one, sort any decision on your desk by reversibility, consequence and where the information actually lives, hand a decision over with all four of the things that must transfer together — the decision, the limit, the context and the reporting expectation — using a script you can read out loud, run a delegation ladder that moves on evidence rather than mood, write escalation criteria specific enough that nobody has to guess, tell the difference between a slow decision and a careful one, and name the exit condition for each of the three bottlenecks that wear a technical costume: approving architecture, reviewing pull requests, and fixing production yourself._

## Explain-it-like-I'm-5

There is a building-materials shop on the Raipur–Bhilai road — cement, TMT bars, binding wire, a weighbridge out front. The owner has three boys working for him. On a busy morning there are four customers at the counter and all four are waiting for the same thing: the owner has to say the rate. He is the only one who knows what the last truck of rods cost him, what the mandi is doing today, which contractor is good for credit and which one is not. So the three boys stand there, and the four customers wait, and the owner is very busy indeed. Anyone watching would say he is the hardest-working man on that road, and they would be right.

Two years later, one of those boys is gone — he took a job at the shop across the road, where the owner lets him quote. The other two are still standing there. The shop has not grown. And the owner is exhausted, and slightly proud of it.

Now imagine the version where, one Tuesday, the owner writes four things on the back of a rate card and hands it to the eldest boy. **The decision:** you quote rods. **The limit:** anything up to a hundred quintals, at or above the floor rate on this card, for a customer already in the ledger. **The context:** here is what the last truck cost us, here is why we never go below the floor even for a friend, here is the contractor who still owes us from March. **And what you tell me:** every quote goes in the book, and you tell me the same evening if you went to the floor. That is not a smaller job for the owner. It is a completely different job — he now sets the floor rate instead of saying every rate, and he finds out at the end of the day instead of standing at the counter.

That is the whole lesson. **The bottleneck is not caused by having too much to do. It is caused by decisions with no owner, no limit and no report.** [[02-how-a-ceo-thinks|Lesson 02]] taught you how to make a decision well. This one is about the decisions you should not be making at all, and about the fact that the queue in front of you is your own design, not your workload.

## 1. The bottleneck is the default state, not a failure

Start with the correct baseline, because founders waste a lot of guilt on this one. **A founder-CEO being the bottleneck is not a mistake that happened. It is the state the company starts in and the state it returns to whenever nobody actively works against it.** At the beginning you genuinely were the only one who could do everything, and every process, habit and expectation in the company was built around that fact. Nobody has to do anything wrong for the queue to form. The queue is the default.

This matters because the emotional framing determines whether you fix it. Treated as a character failing — "I can't let go", "I'm a control freak" — it produces resolutions, which do nothing. Treated as a structural property of the system, it produces mechanisms, which work. This is the same sentence the COO course says about intentions and mechanisms ([[02-how-a-coo-thinks|COO 02]]), pointed at you instead of at the operating system.

### 1.1 Why it forms — three mechanisms, none of them character flaws

**You are the fastest person at almost everything, and speed is a trap.** At three people, for any given task, the founder is usually the quickest and the most accurate. Doing it yourself is locally optimal every single time — twenty minutes now against an hour of explaining. The arithmetic only inverts when you count the tenth repetition, and nobody counts the tenth repetition in the moment. Grove's framing of managerial leverage is the correction: a manager's output is the output of the organisation under them, so the right question is never "how fast can I do this?" but "what does this hour multiply?" — and a manager who becomes a queue produces **negative** leverage, because their delay is multiplied by everyone waiting ([High Output Management — notes](https://www.nateliason.com/notes/high-output-management-andy-grove)).

**Every decision that has no written owner defaults to you.** This is the mechanical cause and it is almost invisible. When decision rights are unwritten, the safe move for anyone else is to ask, because being wrong without permission is punished and asking never is. So the ambiguity converts, silently and reliably, into traffic at your desk. Eliyahu Goldratt's Theory of Constraints says the throughput of any system is set by its single tightest constraint, and that everything else you improve is wasted effort until you exploit and then elevate that one ([Theory of Constraints — the five focusing steps](https://umbrex.com/resources/frameworks/organization-frameworks/theory-of-constraints-five-focusing-steps/)). In a three-person company the constraint is a person, and you know which one.

**Growth converts a strength into a limit at a predictable point.** Larry Greiner's model of how organisations grow describes exactly this: each phase of growth ends in a crisis produced by the thing that made the previous phase work, and the crisis that ends the first phase is a **crisis of leadership** followed by a **crisis of autonomy** — the founder's direct, personal control stops scaling and the people below need decision rights the founder has not given them ([Greiner, HBR, 1998](https://hbr.org/1998/05/evolution-and-revolution-as-organizations-grow)). Greiner was writing about large firms across decades; the shape arrives at VSYST at hire number two, not hire number two hundred.

The cost of the resulting congestion is measurable at large companies and the numbers are worth having in your head as an order-of-magnitude argument. McKinsey's 2019 survey of more than 1,200 managers found that only about **20% say their organisations excel at decision making**, that a majority spend more than 30% of their working time on decisions, and that most of that time is judged ineffective — roughly **530,000 days of manager time a year wasted at a typical Fortune 500 company** ([McKinsey — Three keys to faster, better decisions](https://www.mckinsey.com/capabilities/people-and-organizational-performance/our-insights/three-keys-to-faster-better-decisions), 2019). Do not import the Fortune 500 arithmetic; import the ratio. At three people the same waste is invisible because it looks like a founder being busy.

There is one piece of direct evidence on the founder side, and it is worth citing even though it is correlational. Gallup studied 143 Inc. 500 CEOs and found that those scoring high in "Delegator" talent posted an average three-year growth rate **112 percentage points higher** than those low in it, and generated about **33% more revenue** in the study year ([Gallup — Delegating: A Huge Management Challenge for Entrepreneurs](https://news.gallup.com/businessjournal/182414/delegating-huge-management-challenge-entrepreneurs.aspx), 2015). **VERIFY LIVE** if you ever quote this externally — it is a 2014 sample of American high-growth firms, the causal direction is not established, and a company that grows fast is also a company that is forced to delegate. Treat it as a plausibility argument, not proof.

### 1.2 The observable symptoms — a diagnostic table

Do not diagnose this by feeling. Every row below is countable this week, from your own calendar, WhatsApp and repo.

| Symptom                                                       | How to count it, this week                                                                    | What it actually means                                         | The section that fixes it                                       |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------- |
| **People ask before acting on things they are allowed to do** | Count the messages asking permission for something already inside someone's remit             | Decision rights exist in your head and nowhere else            | §4, [[C03-decision-rights-matrix\|C03]]                         |
| **Work restarts when you reappear**                           | Note what moved on the two days you were unreachable versus the three you were not            | The company is running on your presence, not on its rules      | §11                                                             |
| **The same question arrives more than twice**                 | Tally repeat questions for five days                                                          | You are answering instead of publishing the rule               | §8                                                              |
| **You are in every meeting**                                  | Count meetings where you made no decision and produced no artefact                            | Attendance has become a habit, not a role                      | §7, [[15-the-ceo-operating-cadence-and-calendar\|lesson 15]] §3 |
| **Decisions age on your desk**                                | List open decisions and their age in days. Anything over 14 days is a finding                 | Slow is a decision too, and it is the one nobody logs          | §9                                                              |
| **You overrule after the fact**                               | Count the times you changed someone's already-made call in the last month                     | You delegated the task and kept the decision                   | §4.2                                                            |
| **Nothing has been given away this quarter**                  | Name one decision you genuinely stopped making since April. If you cannot, that is the answer | Delegation is being treated as a project, not a rate           | §5                                                              |
| **Merges wait for you**                                       | Median hours from PR opened to your first response                                            | You are the release gate wearing an engineer's hat             | §10                                                             |
| **You fixed production last month outside your on-call week** | Count the incidents you personally resolved                                                   | Bus factor one, permanently                                    | §10                                                             |
| **Your week is mostly doing**                                 | The calendar audit in [[C27-ceo-weekly-template-and-calendar-audit\|C27]]                     | Doing crowds out deciding, and only deciding is uniquely yours | §11                                                             |

Two of these rows deserve to be treated as red lines rather than symptoms. **"Decisions age on your desk"** is the one founders never self-report, because a decision not made produces no event. And **"you overrule after the fact"** is the one that does permanent damage, because each instance teaches the other person that the authority they were given is not real — which is precisely how a delegation programme dies without anyone noticing ([Alder Koten on the same failure from the COO's side](https://charliesolorzano.me/2026/03/17/coo-founder-led-company-failure/)).

### 1.3 The counter-argument: founder mode, honestly

There is a serious argument against everything in this lesson and it deserves to be stated at full strength before it is answered, because the fashionable version of "delegate more" has genuinely wrecked companies.

Paul Graham's _Founder Mode_ essay (September 2024) attacks the standard advice directly: "Hire good people and give them room to do their jobs. Sounds great when it's described that way, doesn't it? Except in practice… what this often turns out to mean is: hire professional fakers and let them drive the company into the ground." His account, drawn from Brian Chesky's experience at Airbnb, is that founders who followed conventional scaling advice watched their companies get worse, and that the alternative — staying deeply, unconventionally involved, as Steve Jobs did with an annual retreat for the hundred people he thought mattered rather than the hundred highest on the org chart — is under-described because almost all management literature is written by and for professional managers ([Paul Graham — Founder Mode](https://paulgraham.com/foundermode.html), 2024).

Graham himself supplies the caveat, and it is the operative half for you: once the idea has a name, "founders may use it to avoid necessary delegation", and non-founders will attempt it badly.

Three things reconcile the two positions, and none of them is a compromise.

- **Founder mode is an argument about depth, not about queues.** Chesky's version involves skip-levels, direct contact with the work, and refusing to be managed by a summary. None of that requires being the person who approves a ₹6,000 vendor renewal. **Being deeply involved in the work and being the queue for routine decisions are different things**, and founders conflate them because both feel like caring.
- **It is an argument about a stage you are nowhere near.** The essay is about companies with hundreds of employees and a professional management layer. VSYST has three people and no managers. At your size, "founder mode" is not a choice; it is a description.
- **The parts of founder mode that are real at three people are already elsewhere in this course.** Direct contact with dealers ([[07-customers-markets-and-founder-led-sales|lesson 07]]), owning the product bar personally ([[13-product-and-technology-leadership-for-a-technical-ceo|lesson 13]] §6), refusing to lead through summaries ([[17-the-numbers-a-ceo-watches|lesson 17]]). What this lesson removes is different: the ₹6,000 approvals, the copy edits, the merge gate, the 2 AM fix.

**The house call:** stay in founder mode about _what the company does_ and get ruthlessly out of the way about _how it does it_. The failure this lesson prevents is not the founder who cares too much. It is the founder whose care is spent on the cheapest available decisions.

## 2. A taxonomy of decisions — and the 3×3 that says who decides

[[02-how-a-ceo-thinks|Lesson 02]] gave you one axis: reversibility, the one-way and two-way doors from Amazon's 2015 shareholder letter, where Type 1 decisions are irreversible and deserve slow deliberation while Type 2 should be made fast by high-judgment individuals or small groups ([Amazon, 2015 letter](https://s2.q4cdn.com/299287126/files/doc_financials/annual/2015-Letter-to-Shareholders.PDF)). That axis answers _how much process_. It does not answer _who decides_, and using it for that produces the classic error of a founder who takes every one-way door personally — including the ones where somebody else knows more than he does.

Two more axes are needed.

### 2.1 The three axes

| Axis                     | The question                                                | Low end                                                                          | High end                                                                                 | Who it points to                             |
| ------------------------ | ----------------------------------------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | -------------------------------------------- |
| **Reversibility**        | What does it cost to walk back, in rupees, weeks and trust? | Two-way door: a config change, a message you can correct, a vendor you can leave | One-way door: a published price, a signed exclusivity, a migrated ledger, a fired person | Sets the **process budget**, not the decider |
| **Consequence**          | If this is wrong, what fraction of the company is damaged?  | A day of somebody's work                                                         | A district, a quarter of runway, a licence, a relationship                               | Sets **how high it escalates**               |
| **Information locality** | Where does the knowledge that settles this actually live?   | In one person's daily work — the ticket queue, the pump office, the code         | Nowhere yet; or distributed across founders; or only in your head                        | Sets **who should decide**                   |

The third axis is the one founders systematically ignore, and it is the important one. Hayek's 1945 argument is the cleanest statement of why: the knowledge that matters in practice is "the knowledge of the particular circumstances of time and place", which exists only as "dispersed bits of incomplete and frequently contradictory knowledge which all the separate individuals possess", from which it follows that "the ultimate decisions must be left to the people who are familiar with these circumstances, who know directly of the relevant changes and of the resources immediately available to meet them" ([Hayek, _The Use of Knowledge in Society_](https://www.econlib.org/library/Essays/hykKnw.html), 1945).

Read that as a management claim and it is uncomfortable, because it means **there is a whole category of decisions where you are not merely unnecessary but actively worse.** The support person who has read four hundred tickets knows which error message confuses dealers; you know which one you meant. The domain-expert director knows what a transporter will tolerate in a credit cycle; you know what the schema allows. Centralising those decisions in the CEO does not make them safer, it makes them wronger and slower at the same time. [[02-how-a-ceo-thinks|Lesson 02]] §7 said the same thing in the language of taste: taste is domain-specific and does not transfer, so decision rights should follow taste.

### 2.2 The grid

Cross consequence with information locality. Reversibility sets how much time each cell gets, not who sits in it.

|                                                                                   | **Information lives with the person doing the work**                                                                                                                                                     | **Information is split across the founders**                                                                              | **Information does not exist yet**                                                                                                             |
| --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| **Low consequence** — a day's work, one customer, reversible                      | **They decide, alone, and do not tell you.** Refund inside the limit; ticket wording; which bug first; a vendor under the DoA line. If this cell has traffic in it, you are the bottleneck by definition | **Whoever is closest decides and puts it in the weekly note.** Do not convene three people for a ₹4,000 question          | **Try the cheapest version and see.** A message worded two ways for two dealers is an experiment, not a decision                               |
| **Medium consequence** — a month, several customers, expensive to unwind          | **They decide, then tell you the same day.** Onboarding a difficult dealer; a workaround for a broken import; a discount inside the band                                                                 | **The named owner decides after a timeboxed argument, dissent logged** ([[02-how-a-ceo-thinks\|lesson 02]] §9.1)          | **Run the smallest experiment with a date and a kill criterion**, then decide ([[05-strategy-i-diagnosis-and-the-strategy-kernel\|lesson 05]]) |
| **High consequence** — a district, a quarter of runway, a licence, a relationship | **They recommend; you decide, and you say why in writing.** Their information is still better than yours — do not decide without the recommendation in front of you                                      | **You decide.** This is the seat. Kernel, pricing architecture, capital, exec hires, the values when they cost money (§6) | **You decide how much to spend finding out** — and that is the decision. Not the answer; the size of the bet                                   |

Two rules travel with the grid.

**Reversibility sets the clock, not the chair.** A one-way door in the left-hand column is still theirs to decide — it just gets a written recommendation, a night's sleep and a journal entry ([[C29-decision-journal-and-one-way-door-log|C29]]). A two-way door in the right-hand column is still yours, and should take ten minutes.

**The bottom-left cell is where founders lose the most value.** It is the cell where somebody who knows more than you needs a decision, and where the founder's instinct is to take it over because it is important. The correct move is to take the _recommendation_ over — insist on it in writing, argue with it, and then let it stand unless it violates something you wrote down in advance.

### 2.3 Fewer but larger — how the CEO's decision portfolio should change

The single most useful thing to internalise about this seat is that **the number of decisions you make should go down while their size goes up**, and that this is a deliberate act rather than a consequence of being busy.

| Company shape                    | Decisions/week you personally make | The shape of them                                     | What has changed since the previous row                                      |
| -------------------------------- | ---------------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------- |
| **3, pre-revenue** (VSYST today) | 30–60, most of them small          | Almost everything, because there is almost nobody     | Nothing yet. This is the baseline                                            |
| **5–8, first hires**             | 15–25                              | Everything above a written limit, plus all recruiting | Limits exist in writing; routine spend, support and onboarding have owners   |
| **15**                           | 8–15                               | Pricing, hires, partnerships, the plan, the money     | Function owners decide inside their functions; you decide between functions  |
| **30**                           | 4–8                                | Capital, the exec team, the bets, the story           | You are deciding through people, and most of your decisions are about people |

A.G. Lafley's formulation of the endpoint is worth having in front of you early even though you are twenty-seven people short of it: the CEO's unique work is at the boundary between the company and the outside world — deciding which businesses to be in, what the outside means for the company, and the balance between the present and the future ([HBR — What Only the CEO Can Do](https://hbr.org/2009/05/what-only-the-ceo-can-do), 2009). Everything in the top-left of §2.2's grid is inside work, and inside work is exactly what a CEO is supposed to be handing away.

The trap in this table is reading it as a schedule. It is not a schedule; it is a set of triggers. You do not go from 40 decisions a week to 20 because a year passed. You go there because a limit got written down, and then a second one, and then a person got good enough at a thing that you stopped hearing about it. **The rate of change here is the number of written limits, and nothing else.**

## 3. Frameworks that survive a small company

You will be offered several. Most of them were built for companies with thousands of people and matrix reporting, where the problem being solved is that nobody can tell who is allowed to decide anything. Two are worth knowing, one is worth using, and the honest answer for a three-person company is at the end of this section.

### 3.1 RAPID, DACI and RACI — what each is actually for

| Framework        | Letters                                                          | Built for                                                                                                                                                                                                                  | The one idea worth stealing                                                                                                                                                                                                                                                                                                | Fit at VSYST today                                                                                                                                 |
| ---------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **RAPID** (Bain) | **R**ecommend · **A**gree · **P**erform · **I**nput · **D**ecide | Large firms where a decision crosses several units and stalls ([Bain — RAPID](https://www.bain.com/insights/rapid-decision-making/); [Rogers & Blenko, _Who Has the D?_, HBR 2006](https://hbr.org/2006/01/who-has-the-d)) | The separation of **Recommend** from **Decide** — and the rule that there is only ever one D. Most founder-team arguments are two people both believing they hold the D                                                                                                                                                    | **Steal the R/D split; skip the letters.** The A (agree, a veto) is a coordination device for big firms and a poison at three people               |
| **DACI**         | **D**river · **A**pprover · **C**ontributors · **I**nformed      | A single decision that needs to be driven to a date                                                                                                                                                                        | A **Driver** who is not the Approver. Somebody has to own getting the decision made, and it need not be the person who makes it ([Routine — RACI, DACI and RAPID](https://routine.co/blog/posts/raci-daci-rapid-decision-framework); [Argumentree comparison](https://www.argumentree.com/compare/rapid-vs-daci-vs-raci/)) | **Useful, occasionally.** Reach for it when a decision has been drifting for weeks — the payment-gateway choice, the first pricing tiers           |
| **RACI**         | **R**esponsible · **A**ccountable · **C**onsulted · **I**nformed | Recurring work with several hands in it                                                                                                                                                                                    | Exactly one **A** per recurring activity                                                                                                                                                                                                                                                                                   | **The COO course owns this** — [[17-delegation-decision-rights-and-org-design\|COO 17]] §4 and [[T07-raci-matrix\|T07]]. Do not build a second one |

The one distinction that repays learning properly is **Recommend versus Decide**. In a family founding team, the most common unproductive argument is not a disagreement about the answer — it is an unspoken disagreement about whose answer counts. Naming the D before the discussion starts converts an authority contest into an information exchange, which is [[02-how-a-ceo-thinks|lesson 02]] §9's point about naming the decider first, arriving here with a vocabulary attached.

### 3.2 Disagree and commit, pointed at yourself

Amazon's leadership principle requires leaders to "respectfully challenge decisions when they disagree, even when doing so is uncomfortable or exhausting" and, once decided, to "commit wholly" ([Amazon leadership principles](https://www.aboutamazon.com/about-us/leadership-principles)). [[02-how-a-ceo-thinks|Lesson 02]] §9 covers the mechanics and the founder-team protocol, and this lesson does not repeat them.

What belongs here is the delegation-specific version, which is narrower and harder. **Disagree-and-commit is the only tool that lets you delegate a decision to someone whose answer you do not like.** Without it there are two outcomes, both bad: you take the decision back (and the delegation was fake), or you let it stand while making it clear you disagree (and the person now owns a decision without your support, which is worse than not owning it). The third path is to say the words out loud — "I would have done it the other way, I think you may be right, it is yours, go" — and then behave as though you had chosen it yourself, including when it goes wrong.

Bezos's own worked example runs in this direction, which founders rarely notice: he disagreed with a team's proposal and wrote, "Look, I know we disagree on this but will you gamble with me on it? Disagree and commit?" ([Amazon, 2016 letter](https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders)). **The first time you visibly disagree-and-commit to someone else's call is worth more than any decision-rights document you will ever sign.**

### 3.3 The honest note: three people need one page, not a framework

Here is the part the frameworks industry will not tell you. RAPID exists because a 40,000-person company cannot locate its decision-makers. VSYST can locate its decision-makers by looking up. Installing a five-role framework at this size produces vocabulary, a training session, a template nobody fills, and precisely zero decisions leaving your desk.

**What VSYST actually needs is one page listing recurring decisions, each with a name and a limit.** That page is [[C03-decision-rights-matrix|C03]], it sits above the COO's delegation-of-authority matrix ([[T22-delegation-of-authority-matrix|T22]], [[17-delegation-decision-rights-and-org-design|COO 17]] §5), and the split between the two is already settled in [[03-the-ceo-core-value-and-the-founder-contracts|lesson 03]] §5: T22 and T01 cover everything below board level; C03 extends the same levels upward to CEO alone, CEO + COO, board resolution and shareholder resolution. Do not build a third artefact. Do not rename either of them. If you find yourself designing a decision framework rather than writing limits into C03, that is avoidance wearing a consultant's jacket.

The test for whether a framework is earning its keep at your size is one question: **did a decision leave your desk this month because of it?** If not, delete it.

## 4. Handing over a decision properly

This is the section that carries the lesson. Almost everything called "a delegation problem" is a handover that transferred one or two of four things and left the rest behind.

### 4.1 The four things that must transfer together

| #     | What transfers                                                                     | What it sounds like when present                                                                                                          | What it looks like when missing                                                                                                                       |
| ----- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | **The decision** — stated as a decision, not a task                                | "You decide which dealers get onboarded in which week."                                                                                   | "Help me with onboarding." The person does the work and brings you every call. You now have the same decisions plus a colleague                       |
| **2** | **The limit** — the boundary inside which their answer stands, in numbers          | "Up to ₹10,000 of credit note, any dealer already live, no more than twice for the same dealer."                                          | "Use your judgment." Which means: guess where my line is, and be blamed when you guess wrong. People respond to this rationally, by asking every time |
| **3** | **The context** — what you know that they do not, including what you are afraid of | "Here is why the rate window closes at 6 AM. Here is the dealer who churned last year and why. Here is the number that must not go down." | The person makes a locally sensible decision that violates something invisible, and you overrule them — which teaches them the limit was fiction      |
| **4** | **The reporting expectation** — what comes back, in what form, by when             | "Every credit note in the weekly note. Anything over ₹10,000, same day, before you send it."                                              | Either silence, and you find out in month three — or a stream of updates that is just the old approval queue with different grammar                   |

The four are not a checklist to be nice about. **They are load-bearing together and useless apart**, and each pair that goes missing produces a recognisable, named failure:

- **Decision without limit** → the person freezes, or overreaches. Both get read as "not ready".
- **Decision and limit without context** → they decide correctly against the rules and wrongly against reality, and you learn the wrong lesson about their judgment.
- **Decision, limit and context without reporting** → you get surprised, and the surprise costs the trust that the whole arrangement was built on.
- **Reporting without decision** → the most common one in small companies. It is called delegation, it produces status updates, and the decisions all still happen in your head.

Molly Graham's "give away your Legos" is the emotional half of this and worth reading alongside: as the company grows you have to hand over work you built, and "if you personally want to grow as fast as your company, you have to give away your job every couple of months" — with the warning that "reacting to the emotions you're having as your team adds more people is usually a bad idea" ([First Round Review — Give Away Your Legos](https://review.firstround.com/give-away-your-legos-and-other-commandments-for-scaling-startups/), 2015). The four-part transfer is what makes that emotionally survivable, because it tells you exactly what you are still holding.

### 4.2 The classic failure: task without limit, then overrule

Watch the sequence, because it has happened to every founder and it takes about six weeks.

1. **You hand over the task.** "You handle dealer onboarding now." It feels generous, and it is meant generously.
2. **No limit is stated,** because at the moment of handover you do not know where your own line is. You have never had to say it out loud — you have simply decided each case as it came.
3. **The person makes a call.** They waive the ₹2,000 setup fee for a dealer in Bhilai who was hesitating. Inside any reasonable reading of "you handle onboarding", this is their call.
4. **You find out and reverse it,** or worse, you re-do it: you call the dealer, you restore the fee, you say "next time check with me on fee waivers."
5. **Nothing looks broken.** The dealer is fine. You were probably right about the fee. The person says "sure, understood."
6. **And the arrangement is over.** They have learned, correctly, that the boundary is undrawn and enforced retrospectively. The only safe strategy against a retrospective boundary is to ask about everything. Within a month the queue reforms — and now it arrives with an apologetic tone, which makes it feel like their diffidence rather than your design.

Three things make this recoverable, and only three.

**Write the limit before the handover, not after the first mistake.** If you cannot write it, that is the finding: you do not yet know your own rule, and the handover is premature. Spend twenty minutes recovering it from the last five cases — that is what the limit is.

**When they call it differently and it is inside the limit, it stands.** Absolutely. Even when you would have chosen otherwise, even when you are right. The cost of one waived setup fee is ₹2,000. The cost of an overrule is the entire arrangement, and you will pay it again on the next handover because they will remember. (§5.3 covers the debrief that makes this productive rather than merely tolerant.)

**When they call it differently and it is outside the limit, the limit was wrong or the context was missing — and both are yours.** Fix the document, tell them you are fixing the document, and say plainly which of the two it was. The one thing you may not do is treat a boundary you never drew as a boundary they crossed.

There is one exception, and it must be named in advance so it cannot be invented afterwards: **an emergency stop.** Anyone, including you, may halt an action to prevent harm — money about to leave wrongly, a message about to go to every dealer, a safety or legal exposure. It is declared out loud at the time, it is logged the same day, and it is followed by a written revision of the limit. Used once a year, it is a safety valve. Used monthly, it is an overrule with better branding.

### 4.3 The handover script

Read this out loud. Do not paraphrase it the first ten times — the specific sentences are doing work, and the version you improvise will drop the limit, which is the whole point.

```text
THE HANDOVER — say all five parts, in this order, in one sitting

1. THE DECISION, NAMED AS A DECISION
   "From the 1st, you decide <X>. Not 'help with' — decide. I am not the
    approver on this any more."
   [If you cannot finish that sentence with a verb like decide, choose,
    approve, set, refuse — you are handing over a task, not a decision.
    That is fine, but call it what it is.]

2. THE LIMIT, IN NUMBERS, WITH BOTH EDGES
   "Inside these bounds your answer is final and I will back it publicly:
      - up to ₹______            - for <which customers / cases>
      - up to <how often>        - not touching <the excluded thing>
    Outside them, bring it to me BEFORE you act, and I will answer within
    <same day / 48 hours>."
   [Both edges matter. A limit with only an upper bound tells them where the
    trouble is, not where the freedom is.]

3. THE CONTEXT — INCLUDING WHAT I AM AFRAID OF
   "Three things I know that you don't yet:
      - <the history: why the rule exists, who built the fence>
      - <the number that must not move, and why>
      - <the thing that scares me about this decision, said plainly>"
   [The third one is the one founders skip and it is the most valuable.
    People cannot honour a fear they have not been told about.]

4. THE REPORTING EXPECTATION — FORM, CHANNEL, DATE
   "What comes back to me: <one line in the Monday note / a row in the log>.
    What comes back same-day: <the named exceptions>.
    What never needs to come to me: <say at least one thing explicitly>."
   [Naming something that never comes back is what makes the rest credible.]

5. THE REVIEW DATE AND THE PROMISE
   "We look at this together on <date, 30 days out>. Until then, if I think
    you got one wrong and it was inside the limit, it stands and I will bring
    it to the review — I will not reverse it and I will not go around you.
    If I break that, tell me."
```

Two more sentences, said in the same sitting, that decide whether it works:

**"Here is what I am now going to stop doing."** Name it. "I will not be in the onboarding WhatsApp group." "I will not reply to dealer fee questions; I will forward them to you." A handover where the CEO's own behaviour does not change is not a handover, and everyone can see that within a fortnight.

**And then tell the other founders, in writing, the same week.** Not as an announcement of process — as a routing instruction: _fee waivers now go to X, not to me._ A delegation that only two people know about gets routed around by the third within days, entirely innocently. This is the reason the transfer is written into [[C03-decision-rights-matrix|C03]] rather than remembered.

### 4.4 What "the limit" actually looks like — five worked limits at VSYST

Limits are hard to write in the abstract and easy to write from cases. Every figure below is **illustrative** — a proposal for the founders to argue with and then ratify, not a fact — and any line touching a statutory threshold is **VERIFY LIVE** with the CA/CS before it is minuted ([[09-board-governance-and-the-directors-duties|lesson 09]]).

| The decision handed over                      | The limit, written                                                                                                         | The context that must go with it                                                                                                                                                           | What comes back, and when                                                                                     |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| **Onboarding sequence and setup-fee waivers** | Waive up to ₹2,000, twice per quarter, only for a dealer with a signed order; never for the first dealer in a new district | Why district one's pricing is a precedent everyone else will hear about; the churned dealer from last year and why                                                                         | A line per waiver in the weekly note; anything in a new district, same day, before                            |
| **Support credit notes and refunds**          | Up to ₹10,000 per tenant per month, live tenants only, never against an invoice already in a GST return                    | Which figures are legally frozen after filing and why a credit note is not an undo; the ledger-lineage rule ([[13-product-and-technology-leadership-for-a-technical-ceo\|lesson 13]] §7.2) | Weekly total plus every individual case above ₹5,000; anything touching a filed return escalates same-day     |
| **Tooling and vendor spend**                  | ≤ ₹5,000/month new commitment, no annual contract, no data-processing agreement, no auto-renew above ₹2,000                | The runway number and what a ₹5,000/month subscription costs over 24 months; why a DPA needs a legal read ([[C26-partnership-evaluation-and-mou-checklist\|C26]])                          | Monthly vendor list; anything with a lock-in or a data clause comes to the CEO before signature               |
| **What ships in a release**                   | Anything meeting the written quality bar and passing the release gate, except changes touching ledger, tenancy or money    | The bar document; why a wrong number is a company-level event and a wrong colour is not                                                                                                    | Release note to all three directors; a blocked release is same-day news                                       |
| **Which dealer gets visited this week**       | Entirely theirs, inside the district in the kernel                                                                         | The kernel's district choice and why; which two dealers are reference accounts and must not be experimented on                                                                             | The visit log; a dealer who asks for something that is on the no-list comes back with the ask, not the answer |

Notice what the middle column is doing. **The context is not background reading; it is a list of the invisible fences.** Chesterton's fence ([[02-how-a-ceo-thinks|lesson 02]] §2.4) is normally aimed at you — do not remove a fence until you know why it was built. Pointed at a handover it inverts: **if you do not tell them where the fences are, they will remove one, and it will be your fault.**

### 4.5 The first thirty days after a handover

The handover is not the event. The thirty days after it are the event, and they have a predictable shape.

**Week 1 — over-reporting.** They will tell you about things well inside the limit, because they are checking whether you meant it. Respond with the rule, not the answer: "that one is yours — what does the limit say?" Answering the question, even helpfully, restarts the queue. This is the single highest-leverage habit in the whole lesson and it costs nothing.

**Week 2 — the first call you would not have made.** It will arrive, it will be inside the limit, and your instinct will be to fix it. Let it stand. Write it in your own notes for the review. If it is genuinely serious, that is information about the limit, not about the person — go and narrow the limit in writing, and say that is what you are doing.

**Week 3 — the routing failure.** Someone — a dealer, a founder, a vendor — will come to you with a question that now belongs to them. Forward it without answering it, visibly, in the same thread. Every time you answer one of these you undo about two weeks of the handover.

**Week 4 — the review.** Thirty minutes. Three questions and nothing else: _which calls felt outside your comfort but inside the limit_ (that is where the limit should widen), _which felt inside but you wished you had asked_ (that is where the context was thin), and _what did I do that undercut this_ (ask it, and wait — the answer is always yes and it takes fifteen seconds of silence to surface). Then either widen the limit, fix the context, or move a rung on §5's ladder — and write the change into [[C03-decision-rights-matrix|C03]] with the date.

A handover is complete when three things are true, and the COO course's version of this test applies unchanged: the limit is written where the work lives, the routing has changed for everyone including the other founders, and **you have not touched the decision for two full cycles** ([[17-delegation-decision-rights-and-org-design|COO 17]] §10). Until then it is a loan.

## 5. The delegation ladder — the CEO's version

The COO course owns the five-level ladder and the task-relevant-maturity dial that sets the rung ([[17-delegation-decision-rights-and-org-design|COO 17]] §1–§2, drawn from Grove). That is the operating instrument and this course does not replace it. What belongs here is the compressed version a founder-CEO actually uses in conversation, and the two situations the ladder does not cover: moving someone up, and what to do when they call it differently from how you would have.

### 5.1 The three rungs that matter at three people

Jurgen Appelo's delegation poker splits authority into seven levels — tell, sell, consult, agree, advise, inquire, delegate — on the argument that "delegation is not a binary thing. There are plenty of 'shades of gray' between being a dictator and being an anarchist" ([Management 3.0 — Delegation Poker](https://management30.com/practice/delegation-poker/)). Seven is the right number for a workshop and too many for a Tuesday. At VSYST's size, three rungs carry almost all the traffic, and the value is entirely in **saying which rung out loud when you hand something over.**

| Rung                                | The sentence                                 | Who holds the pen      | Where the information sits        | Move up when                                                                                                      |
| ----------------------------------- | -------------------------------------------- | ---------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **1 — "Do exactly this"**           | "Do it this way, then show me."              | You                    | With you                          | They have run it clean twice from the written version                                                             |
| **2 — "Decide and tell me"**        | "Decide it, do it, and tell me in the note." | Them, inside the limit | Being built                       | Two clean cycles at rung 2, and their exception-reporting has been accurate — including once when it was bad news |
| **3 — "Decide, I'll read the log"** | "This is yours. I'll see it in the review."  | Them                   | With them, now more than with you | — (this is the destination)                                                                                       |

The missing rung between 1 and 2 is "**recommend, I decide**", and it is the one to use deliberately rather than by accident. It is how judgment gets built without risk: they do the whole analysis and hand you a recommendation, you decide, and — crucially — **you tell them what you would have decided before you read theirs, then compare.** Three or four rounds of that is worth more than a year of watching.

David Marquet's version of rung 2 is the best language available for it, and it is free to steal. On the submarine USS _Santa Fe_ he replaced permission-asking with intent-stating: the crew stopped saying "request permission to…" and started saying "**I intend to…**", followed by the reasoning, with the captain's job reduced to not objecting ([Marquet — _Turn the Ship Around!_](https://davidmarquet.com/books/turn-the-ship-around-book/); [Intent-Based Leadership resources](https://davidmarquet.com/intent-based-leadership-resources/)). Two things happen when you install that phrasing. The person has to do the thinking before speaking, because "I intend to X because Y" is a much harder sentence than "what should I do?". And **the default flips from stop to go**, which is the entire difference between rung 1 and rung 2 expressed in four words.

### 5.2 How to move someone up — the evidence, not the feeling

Rungs move on evidence, and the evidence is boringly specific: **two clean cycles.** Done from the written version, output correct, on the agreed date, with the exceptions reported accurately — including at least one occasion where the news was bad and they brought it anyway. That last clause is the real test, because rung 3 is not a judgment about competence; it is a judgment about whether you will hear about the problem in time.

Three rules keep the ladder honest.

**Rungs belong to decisions, not to people.** The same person is rung 3 on dealer onboarding and rung 1 on anything touching a GST return. Say it that way explicitly — "you're at three on onboarding and one on filings, and that is not a comment on you" — or the rung gets heard as a rating.

**Move one rung at a time.** Jumping a person from rung 1 to rung 3 is not trust, it is abandonment, and when it fails the person gets blamed for a system failure ([[17-delegation-decision-rights-and-org-design|COO 17]] §1).

**A rung with no limit attached is not a rung.** Every promotion up the ladder is a change to a written limit in [[C03-decision-rights-matrix|C03]] or [[T22-delegation-of-authority-matrix|T22]]. If nothing changed in a document, nothing changed.

### 5.3 When they call it differently from how you would have

This is the moment the whole apparatus is built for, so treat it as a procedure rather than a mood.

**Inside the limit, it stands. Publicly, immediately, without commentary.** Not "well, it's done now" — that is a reversal with a shrug. If someone asks you about it in front of others, the answer is "that's X's call and I back it." You may think it was wrong. You may be right that it was wrong. It stands.

**Then debrief afterwards, in private, and get the order right.** The order is what makes this productive:

1. **Ask for their reasoning before you give yours.** "Walk me through how you got there." Most of the time — and this is the part that surprises founders — the reasoning contains a fact you did not have, and the decision was better than yours would have been. Hayek's point arrives as a personal experience rather than an abstraction.
2. **Then say what you would have done, labelled honestly as a preference or as a rule.** "I'd have held the fee. That's taste, not a rule — you were inside the limit." Or: "I'd have held the fee, and here's the rule I never wrote down: never in a new district. That's my failure, and I'm adding it to the limit today."
3. **Change exactly one thing.** Either the limit narrows, or the context grows, or nothing changes and you say so out loud. Changing nothing, explicitly, is a real outcome and it should be the most common one.
4. **Log it if it was consequential** ([[C29-decision-journal-and-one-way-door-log|C29]]) — and score it later against what actually happened, separating decision quality from outcome quality ([[02-how-a-ceo-thinks|lesson 02]] §1.1). You will discover, over a year, that a meaningful share of the calls you would have overruled turned out fine, and that number is the single most persuasive argument available for widening limits further.

**The thing that must not happen** is the silent correction: you say nothing, and quietly stop routing that kind of decision to them. It reads as acceptance and functions as demotion, and the person finds out three months later when they notice the traffic dried up. If you are taking a rung back, say so, say why, and say what would earn it back.

### 5.4 Taking a rung back — the only legitimate reasons

There are exactly three, and none of them is "I disagreed with a call."

| Legitimate reason                   | What it looks like                                                                        | What you do                                                                                                                                 |
| ----------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **The situation changed the task**  | Volume went up tenfold; a new statutory obligation attached; the tool changed             | Say the rung is dropping because the task changed, not the person. Re-run the handover script for the new version                           |
| **The reporting failed**            | You found out late, twice. Not "they made a bad call" — you did not hear about it in time | Drop one rung, and fix the reporting expectation specifically. This is almost always a design failure in part 4 of the script               |
| **The limit was crossed knowingly** | They acted outside a limit they understood, without the emergency-stop declaration        | This is a trust conversation, not a delegation conversation, and it belongs in [[10-building-the-team-hiring-equity-and-firing\|lesson 10]] |

Everything else — a call you would not have made, an outcome that went badly, a quarter where you felt anxious — is not a reason. **A bad outcome from a decision that was inside the limit and well-reasoned is exactly the case the whole system exists to survive.** Reversing on it teaches the company that authority is contingent on luck, which is the most expensive thing you can teach.

## 6. What the CEO must never delegate

A list of things you keep is only useful if it is short. A CEO who "must be involved in" fifteen categories has written a job description for a bottleneck. Seven, and the seventh has an end date.

### 6.1 The seven

| What you keep                                                                                      | Why it cannot move                                                                                                                                                                                                                                                                                                            | What you may delegate inside it                                         | The test that catches drift                                                                                                                               |
| -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **The strategy kernel** — the diagnosis, the guiding policy, the district, the segment             | It is the one artefact everything else is derived from, and derived work cannot redefine its own source ([[05-strategy-i-diagnosis-and-the-strategy-kernel\|lesson 05]], [[C04-strategy-kernel-one-pager\|C04]])                                                                                                              | The analysis, the market map, the option write-ups — all of it          | Can each of the other two founders state the current bet in one sentence, without looking? If not, you have not been holding it; you have been storing it |
| **The capital decision** — raise or don't, from whom, at what terms; and the runway trigger ladder | Fred Wilson's third job: there is always enough cash in the bank ([AVC — What A CEO Does](https://avc.com/2010/08/what-a-ceo-does/)). Non-delegable because it is the only decision whose failure ends the company outright ([[08-capital-runway-and-fundraising\|lesson 08]], [[C13-runway-burn-and-scenario-planner\|C13]]) | The model, the data room, the scheme applications, the bank paperwork   | Can you say cash, burn and months of runway from memory, today, without opening a file?                                                                   |
| **Executive hires and fires**                                                                      | The two acts with the longest half-life in a small company. A wrong exec hire is nine months and a culture reset ([[10-building-the-team-hiring-equity-and-firing\|lesson 10]], [[C19-executive-hiring-scorecard-and-loop\|C19]])                                                                                             | The sourcing, the scheduling, the scorecard mechanics, most of the loop | Did you personally do the final conversation and at least one reference call yourself?                                                                    |
| **The values when they cost money**                                                                | A value only becomes real the first time it is expensive, and the company watches which way you go ([[11-culture-and-values-as-a-ceo-instrument\|lesson 11]])                                                                                                                                                                 | Everything about how values are written, taught and repeated            | When a value last cost the company something, was it named out loud, to everyone, with the number?                                                        |
| **The board, the signature and the filings**                                                       | A director's statutory duty is personal and cannot be contracted away ([[09-board-governance-and-the-directors-duties\|lesson 09]], [[C18-director-duties-and-governance-checklist\|C18]]). §6.2 below                                                                                                                        | Preparation, the pack, the minutes drafting, the CS's entire workflow   | Do you know what you signed last month, and what it obliges the company to?                                                                               |
| **The story** — the one sentence the company says about itself                                     | Told by the founder or it is not believed. A story delegated becomes marketing copy, and dealers can tell ([[12-communication-the-ceo-as-chief-storyteller\|lesson 12]])                                                                                                                                                      | Every channel, every schedule, every artefact except the sentence       | Would a dealer, a director and a candidate each repeat roughly the same sentence back to you?                                                             |
| **The biggest customer and the largest relationship — until each is a machine**                    | Weight asymmetry: at pre-revenue, one dealer or one OMC conversation can be a material fraction of everything ([[14-partnerships-ecosystem-and-founder-relationships\|lesson 14]])                                                                                                                                            | Day-to-day support, scheduling, the operational relationship            | **This one has an exit condition** — see below                                                                                                            |

The seventh is the only row with a date on it, and it is worth writing the date. **You stop holding a relationship personally when it survives you being away from it** — concretely: the counterparty knows a second name at VSYST and uses it; the last three commitments were made and kept without you in the thread; and there is a written account of what the relationship needs and what it must never be told. Until then the relationship is a single point of failure with your face on it, which is [[18-risk-crisis-and-the-hard-things|lesson 18]]'s problem as much as this lesson's.

Notice what is deliberately **not** on the list, and would be on most founders' versions: pricing execution (the architecture is yours, the quote is not), product design (the problem, constraints and bar are yours, the design is not — [[13-product-and-technology-leadership-for-a-technical-ceo|lesson 13]] §3), hiring below exec level, vendor selection, the roadmap's contents, and every operational decision the COO course already owns.

### 6.2 The statutory floor — what Indian company law will not let you delegate

There is a layer beneath judgment where the question is not "should you delegate this?" but "may you?" — and for a director of an Indian Private Limited company the answer is sometimes no, whatever the org chart says.

Section 179(3) of the Companies Act 2013, read with Rule 8 of the Companies (Meetings of Board and its Powers) Rules 2014, lists powers the Board may exercise **only by resolution passed at a meeting of the Board** — including borrowing monies, investing the funds of the company, granting loans, giving guarantees or providing security in respect of loans, approving financial statements, and approving amalgamations or takeovers; some of these may then be further delegated to a committee, managing director or manager only by a board resolution, and others may not ([s.179(3), Companies Act 2013](https://indiankanoon.org/doc/94052327/); [commentary on scope and limits](https://taxguru.in/company-law/powers-board-section-179-companies-act-2013-scope-limits.html)). **VERIFY LIVE** the current list, the Rule 8 items and every delegation you intend to rely on with your CS before you write any of it into [[C03-decision-rights-matrix|C03]] — this is exactly the kind of provision that moves, and getting it wrong is a compliance finding, not a management disagreement.

Three practical consequences for VSYST.

**Some rows in C03 read "board resolution" and that is not a formality you can route around.** Borrowings, guarantees, related-party matters and anything touching the cap table go to the board — which at VSYST is three people in one room, but must still be convened, minuted and filed as a board act rather than agreed over dinner ([[02-how-a-ceo-thinks|lesson 02]] §9: dinner is not a board meeting).

**The director's duty under s.166 is personal and travels with you into every delegation.** You may delegate the work and the decision; you do not delegate the duty of care or the consequences of a filing that did not happen. This is the fourth non-delegable job the whole course is built on ([[09-board-governance-and-the-directors-duties|lesson 09]]).

**The anti-bottleneck move available here is procedural, not authority-based.** A three-director company that needs board approvals quickly should get its CS to set up the routine machinery for it — a standing meeting calendar, a template resolution set, and clarity on which matters may lawfully be passed by circulation and which must be passed at a meeting. **VERIFY LIVE** with the CS: the categories differ, and the ones in s.179(3)/Rule 8 are precisely the ones that generally cannot. Done once, this converts "we need a board resolution" from a two-week delay into a three-day one, which is worth more than any delegation you could have attempted instead.

### 6.3 The test for anything not on the list

When something arrives and you are not sure whether it is yours, three questions in order — and the first "no" ends it.

1. **Is the information that settles this mostly in my head?** If it is mostly in someone else's daily work, it is theirs and your involvement makes it worse (§2.1).
2. **Is it irreversible at company scale?** Not "would it be annoying" — would it change the cap table, the licence, a filed return, a published price, a person's employment, or a relationship that cannot be rebuilt? If not, it is not a CEO decision no matter how loud it is.
3. **Would delegating it make a stated value cheap?** The only category where you keep a decision you are otherwise unqualified for, because the company is watching what you do rather than what you know.

If all three are "no", the decision is not yours, and the correct action is not to decide it well. It is to write a limit and give it away.

## 7. Escalation design — the other half of delegation

Every limit you write creates a boundary, and a boundary with no crossing rule is not a limit — it is a cliff. **Delegation without escalation design is not delegation; it is abandonment with paperwork.** The two artefacts are one artefact: the row in [[C03-decision-rights-matrix|C03]] that says "they decide up to ₹10,000" is incomplete until the next column says what happens at ₹10,001, and what happens at midnight on a Saturday, and what happens when the thing is not about rupees at all.

The failure is asymmetric, and the asymmetry should govern the design. **Over-escalation costs you an interruption. Under-escalation costs you a dealer, a filing or a month.** Design for the cheap error.

### 7.1 Why "use your judgment" is not a criterion

It is the sentence founders reach for because it sounds generous, and it is the sentence that guarantees the wrong things reach you. Three reasons, and each of them is structural rather than personal.

**It asks someone to model your risk tolerance, which they cannot do.** Your instinct about what is dangerous is built out of things they did not witness — the dealer who churned in March and why, the tax notice, the week the bank balance was lower than you told anyone. None of that is available to them. Asking for judgment is asking them to reconstruct a decade of your scar tissue from first principles, weekly, under time pressure.

**Escalating feels like an admission of failure, so people under-escalate by default.** Nobody withholds a problem out of carelessness. They withhold it because raising it says _I could not handle this_, and because the last four times they raised something it turned out to be nothing. **Written criteria remove the social cost entirely.** Escalating stops being a confession and becomes compliance: _the rule says anything touching a filed return comes to you the same day, so here it is._ That single reframe does more for information flow than any amount of "my door is always open."

**Judgment calls made under uncertainty need a default, and the default should be up.** PagerDuty's incident documentation states the rule in the cleanest available form: if you are unsure which severity level something is, **treat it as the higher one**, because the middle of an incident is not the time to litigate severities ([PagerDuty — Severity Levels](https://response.pagerduty.com/before/severity_levels/)). Import that sentence verbatim into your escalation page. It converts a judgment call into a coin-flip rule that always lands on the safe side.

### 7.2 The three buckets

Everything that could reach you goes in exactly one of three buckets, and the page that says which is which is one page long.

| Bucket               | Channel                                                                                                                                           | Timing                                                                    | The governing question                                                     | Volume you should expect at VSYST                                                                             |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Same day**         | Phone call, then a written message. Not a WhatsApp message alone — a message can sit unread for six hours and the whole point is that it does not | Within hours of the person knowing, not within hours of it being resolved | _If this is still unknown to the CEO tomorrow morning, is that a problem?_ | 0–2 a week. If it is five a week, the limits are drawn wrong; if it is zero for a month, people are filtering |
| **This week's note** | The weekly written note, one section, read before the weekly meeting ([[15-the-ceo-operating-cadence-and-calendar\|lesson 15]])                   | Batched, once                                                             | _Does the CEO need this to make a decision this week?_                     | 5–15 lines                                                                                                    |
| **Never**            | Nowhere. It is decided, done and logged where the work lives                                                                                      | —                                                                         | _Is this already inside a written limit, or answered by a written rule?_   | Everything else, and this bucket should be growing                                                            |

The third bucket is the one that gets neglected, and it is the one that makes the first two credible. **A company where anything may be escalated has no escalation criteria; it has an inbox.** Write down the "never" list explicitly — spend below the delegation-of-authority line, ticket wording, which bug is fixed first, a refund inside the limit, a visit scheduled, a vendor renewed under the threshold — and then hold the line when one arrives anyway (§4.5's week-1 discipline: answer with the rule, not the answer).

### 7.3 The same-day list — five triggers, written as tests

This is the no-surprises rule from [[03-the-ceo-core-value-and-the-founder-contracts|lesson 03]] §5 and [[03-the-coo-core-value-and-the-ceo-coo-contract|COO 03]] §5, converted from a principle into criteria somebody can apply at 7 PM without calling you to ask whether they should call you. Five categories cover it: **cash, a customer's money, a filing, a person, and the product's reputation.**

| Trigger                      | The written test — no judgment required                                                                                                                                                                                                        | Concrete at VSYST                                                                                                                                                                                                                     | Why the delay is itself the damage                                                                                                                                                                                                                                                                     |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Cash**                     | Any commitment or movement that changes the runway number by more than a week; any unexpected debit; any payment that will not be made on its date; any expected inflow that has not arrived within 3 days of its due date                     | An AWS bill that jumps; a vendor auto-renew nobody remembered; an Easebuzz settlement that has not landed; a dealer's subscription payment that failed and was not retried                                                            | Cash problems are the only ones that compound and cannot be undone by working harder. Fred Wilson's third job is not delegable and neither is knowing about it ([AVC](https://avc.com/2010/08/what-a-ceo-does/))                                                                                       |
| **A customer's money**       | Any wrong number in a live tenant's ledger, invoice, voucher, rate or statement; any figure that changed without a recoverable lineage; any credit note against an invoice already in a filed return; any dealer saying "your number is wrong" | The August ledger double-post class of event: a status transition posting a month's total twice. A rate confirmed in the 10 PM–6 AM window that shows differently in the morning. A TCS line computed against the wrong turnover base | Every hour a wrong figure stays live, more downstream documents are built on it, and the count of dealers who have seen it goes up. **A confirmed wrong stored figure in a live tenant is a SEV1 regardless of amount** ([[13-product-and-technology-leadership-for-a-technical-ceo\|lesson 13]] §7.3) |
| **A filing**                 | Anything that moves a statutory date, in either direction: a return that will be late, a challan missed, a ROC form, a notice from any department, or a discovery that something already filed was wrong                                       | GST returns, TDS, ROC annual filings, any departmental notice landing on a director's email or the registered address                                                                                                                 | The clock belongs to the state, not to you, and interest and late fees accrue daily. It is also the one category where a private company's exemptions are conditional on filing discipline ([[C03-decision-rights-matrix\|C03]] rule 5). **VERIFY LIVE** all dates and consequences with the CA/CS     |
| **A person**                 | A resignation or an offer accepted elsewhere; anything involving somebody's pay; any safety, harassment or dignity report; any founder's availability changing materially                                                                      | At three people this is rare and total: one person leaving is a third of the company                                                                                                                                                  | People problems compound silently, and by the time they are visible the decision space has already shrunk to bad options ([[10-building-the-team-hiring-equity-and-firing\|lesson 10]])                                                                                                                |
| **The product's reputation** | Anything a person outside the company has seen or will see: an outage a dealer noticed, an app-store review event, a security report from anyone at all, a complaint in a dealer WhatsApp group, anything one dealer told another              | Downtime during the rate-confirmation window; a driver-OTP failure at a pump with a truck waiting; a store rating drop; a stranger emailing about an exposed endpoint                                                                 | In a district-by-district, reference-led sales model the reputation _is_ the pipeline ([[07-customers-markets-and-founder-led-sales\|lesson 07]]). A story you hear about from a prospect is a story you have already lost control of                                                                  |

There is a sixth line, and it is a catch-all rather than a category: **anything that will appear in a public place before you hear it from us.** A review, a post, a notice board, a regulator's portal, an association WhatsApp group. The rule reads: _if it will be public, we tell each other first._ That sentence catches the cases the five categories miss.

### 7.4 The escalation message — four lines, and the fourth one is the point

Escalation that stops work is a new bottleneck wearing a helpful face. The format below prevents it, and it takes thirty seconds to write.

```
1. WHAT HAPPENED        one sentence, facts only, with the time it started
2. WHAT I HAVE DONE     already done, not planned
3. WHAT I NEED FROM YOU a decision / a phone call / nothing, and BY WHEN
4. WHAT I WILL DO IF I  the default action that executes on its own if you
   DO NOT HEAR BY <time> do not reply
```

Line 3 must contain a time, because **escalations age on your desk exactly like decisions do** (§1.2), and an escalation with no deadline becomes a thing that was technically reported.

Line 4 is the anti-bottleneck clause and the whole reason this format is worth teaching. It is Marquet's "I intend to…" pointed upward: the person states the action, the reasoning and the default, and your job shrinks to not objecting ([Marquet — _Turn the Ship Around!_](https://davidmarquet.com/books/turn-the-ship-around-book/)). With line 4 present, an unanswered escalation still moves. Without it, an unanswered escalation is a stalled company — and you _will_ be unreachable sometimes, because you are three people and one of you is on a highway to Bastar.

One corollary you must accept out loud when you install this: **if the default in line 4 executes because you did not answer in time, you do not get to complain about it.** Say that sentence when you introduce the format. It is the clause that makes people trust the format enough to use it.

### 7.5 What the CEO owes back

Escalation criteria are a two-sided contract, and the CEO's side is the half that gets skipped.

- **Acknowledge within a stated window** — two working hours is the right number at three people — even when the acknowledgement is "seen, I will come back by 9 PM." Silence is read as disapproval, and disapproval is read as _do not escalate next time._
- **Never punish a correct escalation that turned out to be nothing.** The price of a false positive is one interruption. The price of teaching people not to escalate is unbounded and you will not find out about it for months. If it met the written test, it was right to escalate, and you say that explicitly even when the answer was trivial.
- **Close the loop in public.** Say what you decided and why, in the same thread where it was raised. An escalation that disappears into the CEO teaches everyone that the channel is one-way.
- **When something reaches you that should not have, fix the criteria rather than the person.** Every misrouted item is a missing row on the page. This is Grove's exception reporting doing its job: exceptions surface, and the exceptions to the exception rule become new rules ([High Output Management — notes](https://www.nateliason.com/notes/high-output-management-andy-grove)).

Toyota's andon cord is the canonical statement of the underlying trade: any worker may stop the line when something is wrong, on purpose, because a defect caught at the station is enormously cheaper than one caught at the customer ([Toyota Production System](https://global.toyota/en/company/vision-and-philosophy/production-system/)). A founder who visibly winces when the cord is pulled has removed the cord, whatever the poster on the wall says.

### 7.6 Where the criteria live

One page, in the vault, linked from [[C03-decision-rights-matrix|C03]] as the escalation column's expansion, and pinned in the WhatsApp group everyone actually reads. Not a chat message — chat messages scroll. Reviewed at the same sitting as C03, quarterly. And every row that says "same day" gets tested once: at some point, deliberately, ask each person what would make them call you tonight. If the answers do not match the page, the page is not installed yet.

## 8. The CEO as chief editor, not chief author

There is a version of the bottleneck that survives every decision-rights document you will ever write, because it does not look like a decision at all. It looks like helping. **You give someone a task, they do it, they send it to you — and you make it better.** The deck, the dealer email, the pricing page, the onboarding SOP, the incident note, the schema. Nobody escalated anything. No limit was crossed. And the company just got slower.

The correction is a change of role rather than a change of effort. **An author's output caps at one person's throughput. An editor's output is everyone else's work made better.** Grove's leverage arithmetic (§1.1) says the second is worth more the moment there is more than one other person, and at three people that moment has already passed.

### 8.1 The rewrite trap, and why it is not a motivation problem

Watch the mechanism run, because it runs the same way every time and it takes about six weeks.

**Round one.** They send a draft. You rewrite it. It genuinely is better — you have more context, you have written forty of these, you are faster. Everyone agrees the output improved. Nothing bad has happened yet.

**Round two.** They send a draft at about seventy per cent, because there is no point polishing something that will be rewritten. You rewrite it. It is better. The gap has grown slightly.

**Round three.** They send an outline and ask what you want. This is the rational response. Effort spent on a draft that gets rewritten has a return of zero, and people stop making investments with a return of zero.

**Round six.** You are writing everything, you have more work than before you delegated, and you have concluded — sincerely, and wrongly — that you cannot find anyone who can write. What actually happened is that you ran an experiment which taught a capable person that authorship at this company is decorative, and they learned it correctly.

The diagnostic sentence is worth memorising: **"I keep having to redo it myself" is almost never a statement about their capability. It is a statement about what your last three edits taught them.**

The "make it yours" trap is the same mechanism with a compliment attached. You hand something over and say _make it yours_ — and then edit it back toward the version you would have written. The instruction and the behaviour contradict each other, and people believe the behaviour. If you are not prepared for the thing to come back different, do not say _make it yours_; say _match this template_, which is an honest instruction and a perfectly respectable one at rung 1 of §5.1's ladder.

### 8.2 How to give an edit that improves the work without taking it over

Six rules. They are not stylistic preferences; each one blocks a specific way the rewrite trap re-enters.

**1. State the brief before you state the note.** Who reads this, what must they do after reading it, what must it not say. If you find yourself unable to state the brief in two sentences, the draft is not the problem — you delegated a task without one, and the correct move is to apologise for that and re-brief, not to edit.

**2. Give notes, not orders.** Pixar's Braintrust is the strongest available model and its defining property is that it holds no power: "The Braintrust has no authority. That's the key. Remove the power dynamic, and you get honest conversation." Feedback arrives as notes — observations about what is not working — and the director decides what to do about them ([Catmull on the Braintrust](https://www.destination-innovation.com/lessons-in-candour-from-pixars-braintrust/); [HBR — How Pixar Fosters Collective Creativity](https://hbr.org/2008/09/how-pixar-fosters-collective-creativity), 2008). A note says _I lost the thread in the third paragraph._ An order says _move the third paragraph up._ The note leaves the problem with its owner, which is where the learning is; the order takes it back.

**3. Label every note with its register, out loud.** This is the highest-value rule in the section and it costs one word per comment.

| Register                  | The words                                                            | Force                                                                                         | The failure it prevents                                                                                                                      |
| ------------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Wrong**                 | "This number is wrong" / "this creates a GST exposure"               | Must change. Non-negotiable                                                                   | None — this is the legitimate case                                                                                                           |
| **Breaks a written rule** | "This misses the quality bar on error messages — see the bar doc §3" | Must change, and you must be able to point at the rule _in writing, written before the draft_ | Retroactive rules. If the rule was not written down, it is register three, and pretending otherwise is the most corrosive thing on this page |
| **Taste**                 | "I'd have said it shorter. That's taste — ignore it if you disagree" | May be ignored, and you must visibly accept it being ignored at least sometimes               | Taste delivered in the voice of a rule, which is how authors learn that everything is mandatory and stop deciding anything                   |

**4. Cap the notes at three.** Not because more would be wrong, but because fifteen notes is indistinguishable from a rewrite and is received as one. If you have fifteen, the brief was wrong: say so, fix the brief, and take one more round.

**5. Do not touch the artefact.** Comment; do not commit. The instant your hands are in the file, in the deck, in the branch, authorship has transferred back and both of you know it. This applies with special force when you are faster — and you are.

**6. Ship at eighty-five per cent when the remaining gap is taste.** Two questions decide it: _will a dealer notice?_ and _will it cost money or create an exposure?_ If both are no, it ships as written. You will be surprised how much of your editing energy has been spent on things that fail both tests.

### 8.3 The two places you still author

This is not a general licence to keep writing; it is a short, closed list, and everything outside it is edited rather than authored.

- **The sentence.** The one-line story of what VSYST is and who it is for. Told by the founder or it is not believed, and a story delegated becomes marketing copy ([[12-communication-the-ceo-as-chief-storyteller|lesson 12]], §6.1's list). You may delegate every channel and every artefact; the sentence itself is yours.
- **One-way-door text.** A position in a term sheet, a clause in the founders' agreement, a pricing architecture announcement, a statement to dealers during an incident ([[C24-crisis-comms-and-statement-kit|C24]]). These are documents where a word choice is a commitment, and the person who will live with the commitment writes it.

Everything else — the deck body, the onboarding email, the SOP, the release note, the roadmap page, the support macro — is edited. If your author list is longer than these two categories, it is not a list, it is a habit.

### 8.4 The tests that tell you which role you are actually in

**The read-back test.** After your edit, can the person explain why each change was made _without referring to you_? If the honest answer is "because that is how the CEO wanted it", you gave orders and taught nothing. Real notes survive being explained by the author.

**The ratio test.** Over a month, count the pieces of work you edited versus the pieces you rewrote. A CEO whose rewrites outnumber edits is a chief author with a CEO's title, and it will show up two quarters later as a team that has stopped proposing things.

**The disappointment test.** When a piece comes back different from how you would have done it and it is inside the bar, do you feel disappointed? That feeling is the signal, not the person's work. It is the same signal §5.3 handles for decisions, and it has the same answer: it stands, publicly, immediately, and you debrief afterwards.

### 8.5 When the draft is genuinely not good enough

Sometimes it is not a taste gap. The rule is still not to rewrite, and the alternative has four steps: **name the gap in one sentence** (not five), **show one example of the target** — an old artefact, a competitor's page, a paragraph you wrote once — **set a timebox**, and **take exactly one more round**. If a second round with a good brief and a concrete example still misses, you have a capability finding rather than an editing problem, and capability findings belong in [[10-building-the-team-hiring-equity-and-firing|lesson 10]] and in the 90-day review, not in your evenings.

And when it comes back better than your version — which happens more often than founders expect once the brief is good — **say precisely what worked, not that it was good.** Teresa Amabile's research on inner work life found that of all the things that lift motivation and creative output on a given day, the single strongest is simply making progress in meaningful work, and that noticing progress is the cheapest lever a manager has ([HBR — The Power of Small Wins](https://hbr.org/2011/05/the-power-of-small-wins), 2011). "Good work" teaches nothing. "The second paragraph is the reason a dealer will read the rest — do that again" teaches the bar, and the bar is the thing that eventually lets you stop reading at all ([[13-product-and-technology-leadership-for-a-technical-ceo|lesson 13]] §6.4).

## 9. Speed versus correctness — pricing the decision you did not make

### 9.1 The asymmetry that makes every company too slow

A wrong decision produces an event. There is a moment, a consequence, a person who can be blamed, and usually a story people retell. **A slow decision produces nothing at all.** No log line, no incident, no postmortem. The cost is real and it is paid — in a district somebody else sold, in a dealer who bought something else, in three weeks of burn spent on a question instead of on a customer — but it is paid invisibly, in a currency nobody counts.

So every organisation, without any individual doing anything wrong, systematically over-weights being wrong and under-weights being slow. In a bootstrapped company the mis-pricing has a specific unit: **runway.** A decision that sits for three weeks costs three weeks of burn, spent without buying the information the decision would have bought. Do that arithmetic once with your own number from [[C13-runway-burn-and-scenario-planner|C13]] and the abstraction disappears.

The product-development literature has been measuring exactly this for fifteen years and calls it **cost of delay** — the economic value lost per unit of time when something is late, which combines urgency and value, two things people are reliably bad at separating. Its most cited finding is that most teams have never computed it, and that waiting time — work sitting in a queue between stages — accounts for the large majority of total delay rather than the work itself ([Black Swan Farming — Cost of Delay](https://blackswanfarming.com/cost-of-delay/); Reinertsen, _The Principles of Product Development Flow_, 2009). Read "queue between stages" as "sitting in the founder's head" and the whole of this lesson becomes one number.

### 9.2 The 70% rule, stated properly

Bezos's formulation, from the 2016 shareholder letter, is the one worth memorising: "Most decisions should probably be made with somewhere around 70% of the information you wish you had. If you wait for 90%, in most cases, you're probably being slow." He pairs it with the correction that makes it safe — "if you're good at course correcting, being wrong may be less costly than you think, whereas being slow is going to be expensive" ([Amazon, 2016 letter](https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders)).

Colin Powell's version puts a floor under it, which the Bezos version lacks: act somewhere between **40% and 70%** of the information you would like. Below 40 you are guessing; above 70 you have waited so long that the opportunity has moved ([Financial Advisor — Powell's 40/70 approach](https://www.fa-mag.com/news/colin-powell-s-40-70-approach-to-leadership-and-executive-decisions-34956.html); [42courses — Colin Powell's 40-70 rule](https://www.42courses.com/blog/home/2019/12/10/colin-powells-40-70-rule)). The floor matters at a company where the founder is fast and confident: 40% is not permission to decide from vibes, and "I decided quickly" is not a defence for a decision made with no information at all.

Both rules are descendants of Herbert Simon's **satisficing** — the finding that decision-makers with bounded information and bounded time do not optimise, they search until an option clears a threshold and then stop, and that this is rational rather than lazy ([Nobel Prize — Herbert A. Simon, 1978](https://www.nobelprize.org/prizes/economic-sciences/1978/simon/facts/)). The CEO's skill is not raising the threshold. It is setting the threshold correctly per category — which is the next table.

### 9.3 Where 70% does not apply

The rule is about **two-way doors**, and Bezos says so in the same breath. Applying it everywhere is how founders talk themselves into fast decisions in the four places speed is genuinely the wrong instinct.

| Category                                      | Default                                                                                       | Why                                                                                                                            | What to do instead of waiting                                                                                                                                                                                                                                                                                       |
| --------------------------------------------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Two-way door, low consequence**             | **70%, today.** No meeting, no note                                                           | The cost of being wrong is a reversal; the cost of waiting is the whole queue behind it                                        | Nothing. Decide. If it takes more than one sitting, it was in the wrong category                                                                                                                                                                                                                                    |
| **One-way door**                              | Not a speed question at all                                                                   | Reversal is impossible or ruinous: a published price, a migrated ledger, a signed exclusivity, a district committed to, a name | **Shrink the door before you slow the clock.** Most one-way doors can be made two-way: pilot in one district, a 3-month term instead of 12, the new price for new dealers only, a feature flag, a reversible migration. Shrinking is faster _and_ safer than deliberating, and founders reach for it far too rarely |
| **Money leaving the bank above the DoA line** | Get the arithmetic right, then decide fast                                                    | The failure mode here is not judgment, it is a spreadsheet error, and arithmetic has a cheap right answer                      | Do the sums twice, with the second pass by a different person. Then decide the same day. The number takes an hour; the judgment takes ten minutes                                                                                                                                                                   |
| **People's jobs**                             | The _judgment_ may be made at 70% — and usually is made far too late. The _execution_ is 100% | A mis-hire is nine months; a badly executed exit in India is a legal exposure and a permanent reputational one in a small city | Separate the two explicitly. Decide it is not working at 70%, then run the process at 100% — documentation, notice, dues, full and final — with the CA and, where relevant, a lawyer ([[10-building-the-team-hiring-equity-and-firing\|lesson 10]])                                                                 |
| **Statutory and filing matters**              | Never a judgment call                                                                         | The threshold is set by law, not by you, and "we moved fast" is not a submission to any registrar                              | Ask the CA/CS. **VERIFY LIVE**, always, and build the lead time into the calendar so the question arrives early ([[09-board-governance-and-the-directors-duties\|lesson 09]])                                                                                                                                       |

The line that ties the table together is the one from [[C03-decision-rights-matrix|C03]]'s purpose section: **the failure that kills speed is applying the Type 1 process to Type 2 decisions.** The failure that kills companies is the opposite. Both are failures of classification, not of nerve, which is why the first move in every case is to name the door out loud before arguing about the answer.

### 9.4 A personal default rule — copy this one and edit it

Written rules beat resolve, so write yours down where you will see it. Here is a default that fits a three-person, pre-revenue company; adjust the numbers, keep the shape.

```
MY DECISION DEFAULT                                    v1  ·  <date>

1. NAME THE DOOR FIRST.  Say out loud: one-way or two-way? Before any
   discussion of the answer. Most arguments are actually about this.

2. TWO-WAY  ->  decide today, with what I have. No overnight, no "let me
   think about it", no second meeting. If I am wrong I will course-correct
   and the correction is cheaper than the wait.

3. ONE-WAY  ->  first question is never "what should I decide", it is
   "can I shrink this into a two-way door?" Pilot it, term-limit it,
   flag it, scope it to new customers only. If yes, shrink and go to 2.

4. GENUINELY ONE-WAY AND UNSHRINKABLE  ->  one night's sleep, a written
   C29 entry with the reasoning BEFORE the outcome is known, and a
   decision date in the calendar. Not "when I'm ready."

5. EVERY DECISION I DO NOT MAKE TODAY GETS A DATE. A decision with no
   date is not pending. It is being made by default, in the direction
   of "no", by nobody.

6. NOTHING SITS MORE THAN 14 DAYS. On day 14 I decide with what I have,
   or I say out loud "I am choosing not to decide this, and here is why"
   and log THAT as the decision.

7. MONEY, PEOPLE, FILINGS ARE EXEMPT FROM RULE 2. Arithmetic twice,
   process at 100%, CA/CS asked. Speed applies to the judgment, never
   to the paperwork.
```

Rule 6 is the one that will feel uncomfortable and it is the one that does the work. **An undecided decision is a decision to keep the status quo, made by drift rather than by anyone.** Saying "I am choosing not to decide this yet, and I will revisit on the 15th" is a legitimate and often correct outcome — but it has to be _said_, and logged in [[C29-decision-journal-and-one-way-door-log|C29]], or it is indistinguishable from avoidance and everyone downstream treats it as one.

### 9.5 Three questions that separate slow from careful

Careful and slow look identical from the inside. These three tell them apart in about ninety seconds, and you can ask them of yourself or of anyone else holding a decision.

1. **What specific information am I waiting for?** Name it. If you cannot name a fact, a number or an event, you are not gathering information — you are postponing discomfort, and no amount of additional time will produce the thing you are waiting for.
2. **When will it arrive, and what would I do differently once it does?** If the honest answer is "nothing different", the information is not decision-relevant and waiting for it is theatre. This question kills more fake research than any other.
3. **What does each week of waiting cost?** Answer in rupees of burn, or in a named opportunity — the district not entered, the dealer who will sign with someone else, the release not shipped. If the cost is genuinely zero, the decision is not urgent and should leave your desk entirely under §2.2.

If any one of the three has no answer, decide now.

### 9.6 The correctness reflex, and why it is worse for a technical founder

There is a specific reason this section is harder for you than for a non-technical CEO, and it is worth naming plainly. **Engineering trains you on a domain where correctness is binary and cheaply checkable.** A program is right or wrong. The tests pass or they do not. The ledger balances or it does not. In that domain, "I am not sure yet, let me check" is always the correct instinct, and a decade of it builds a reflex.

Business decisions have no test suite. There is no assertion that tells you whether ₹4,000 per GSTIN per month was the right price, and there never will be — you will only ever have the counterfactual you did not run. Waiting for the certainty you are used to means waiting forever, and it does not feel like waiting; it feels like rigour.

The resolution is the same one [[02-how-a-ceo-thinks|lesson 02]] §7 gives for taste: **the standard is domain-specific and does not transfer.** Hold the engineering standard absolutely where it belongs — a stored money figure, a tenant boundary, a filed return, a schema migration; those are the places 100% is the only acceptable answer and this lesson never argues otherwise. Then, deliberately, run a different standard on the district, the price, the partner and the plan: 70%, today, logged, and revisited when it is wrong. A founder who runs the ledger at 70% will lose the company. A founder who runs the strategy at 100% will simply never finish, and will experience it as being thorough.

## 10. The technical-founder version — three bottlenecks in a technical costume

Every week, three requests arrive at a technical CEO's desk. _Can you look at the schema before I build this? Can you review my PR? Production is throwing 500s._ All three are legitimate-sounding. All three feel like the highest-value use of your time, because in each case you are demonstrably the best person in the company at the task. And all three are the queue from §1 wearing a costume that makes it very hard to see.

The tell is the same in each case and it is worth stating before the details: **the marginal value of your involvement declines with every repetition, while the cost of the queue behind you stays constant.** The fifth architecture question you answer is worth much less than the first, because by then the pattern was answerable from the first four — but the wait it imposes is identical. Nothing about this is a criticism of your engineering. It is arithmetic.

[[13-product-and-technology-leadership-for-a-technical-ceo|Lesson 13]] §3.2 already names the four things to stop owning and gives the rules. This section supplies what that lesson deliberately left out: **the exit condition for each — a written artefact, a tool that enforces it, and a number that tells you when you are actually out.** A rule with no tool decays inside a month. A tool with no number never gets checked.

### 10.1 Architecture approval

**What it looks like at VSYST.** _Should this be a new collection or a field on `so_msts`? Can I add an index here? Does rate confirmation belong in the API or a scheduled job? Do we denormalise the invoice lines? Mongo or Postgres for the new thing?_ Each takes you four minutes and blocks someone for four hours, because architecture questions arrive mid-task and nobody can continue while one is open.

**Why it is a bottleneck rather than leadership.** The question is being answered by the person who will not do the work, at a moment chosen by the queue rather than by you, using information that is mostly in the other person's head (§2.1's left-hand column). And the answer evaporates: it is given verbally, it convinces one person once, and the identical question returns in five weeks with a different noun.

**The exit: constraints written before the debate, and a decision log for the ones that matter.** You do not approve architecture. You publish the two or three properties every architecture at VSYST must satisfy, and you veto only on a violation of something written _before_ the debate started. For DZZLO the three write themselves, because each one already has an incident behind it:

| Constraint                                              | Stated as a law                                                                                                                                                                                                                       | The incident that justifies it                                                                                                                                                                                                                                           | How it gets enforced without you                                                                                                                              |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tenant isolation is structural, never per-handler**   | No route may take a tenant identifier from the client body or query; scoping happens at the middleware/data-access layer, and every collection route is covered by `protect` / `authorize` / `scope`                                  | The live gap: `so_msts` takes `dealer_id` from the request body and the collection routes are not uniformly protected. This is textbook OWASP API1:2023 broken object-level authorisation ([[13-product-and-technology-leadership-for-a-technical-ceo\|lesson 13]] §8.3) | An authorisation test in CI that fails the build when a route can be called with another tenant's identifier. A test, not a review                            |
| **Every stored money figure has a recoverable lineage** | Ledger state is derived from an append-only event sequence; nothing that represents money is mutated in place without a record of what produced the change; any month can be rebuilt from source and must reproduce the stored figure | The August double-post: a repeated status transition posted a month's total twice, and the drift was invisible until a periodic check that had never been run for that relation ([[13-product-and-technology-leadership-for-a-technical-ceo\|lesson 13]] §7.2)           | A rebuild-and-compare job, run on a schedule, that alerts on divergence. The alert replaces your suspicion                                                    |
| **Cost per tenant stays under a stated ceiling**        | Any design that raises AWS cost per tenant per month above ₹X at current volumes is a CEO decision, not an engineering one                                                                                                            | Cloud cost is a strategy constraint at a price point of a few thousand rupees per GSTIN ([[13-product-and-technology-leadership-for-a-technical-ceo\|lesson 13]] §8.4)                                                                                                   | The number on the monthly dashboard ([[17-the-numbers-a-ceo-watches\|lesson 17]]). **VERIFY LIVE** the ceiling against the actual bill before writing it down |

**The mechanism that makes an answer reusable.** Every architecture question you _do_ answer ends with the same sentence: _"…and write that up as an ADR."_ An architecture decision record is one page — context, the decision, the consequences, the date — kept in the repo next to the code, and its entire value is that the next person reads it instead of asking you ([ADR — architecture decision records](https://adr.github.io/); the format originates with Michael Nygard). The COO course already owns the general decision-log mechanics in [[T09-decision-log-and-adr|T09]]; what belongs to you is the discipline of never giving a verbal answer that does not become one.

**The anti-pattern to name and never do: the verbal architecture.** If a constraint exists only in your head, it is not a constraint — it is your mood, and you will eventually use it as a retroactive veto on work somebody already finished. That is the single most demoralising act available to a technical founder, and it is the reason rule 2 of §8.2's register table exists.

**Exit condition, written as a test.** _Four consecutive weeks in which no architecture question reaches you that is not already answered by the constraints document or an existing ADR._ Track it by tallying — a line in your weekly note each time one arrives, with a mark for whether the document should have answered it. The tally is the backlog: every "should have" is a missing ADR or a missing constraint, and writing it is a twenty-minute job that buys back the rest of the year.

### 10.2 Pull-request review

**What it looks like.** Your approval required to merge. PRs sitting two or three days. You reviewing at 11 PM because it was the only quiet hour. Thirty comments on a two-hundred-line change, most of them naming.

**The number that settles the argument.** Measure **change lead time** — hours from PR opened to merged — and split it in two: _time waiting for the first review_ and _everything else_. If the first is more than half the total, you are the constraint in the literal Goldratt sense (§1.1), and no amount of improving anything else in the pipeline will move throughput. Lead time is one of the four delivery metrics the DORA research programme has been measuring across the industry for a decade, which is a convenient way to say it is a real metric rather than a stick invented to beat yourself with ([DORA](https://dora.dev/)).

**Google's published practice supplies both halves of the exit.** On what a review is for: the purpose is to make sure the overall code health of the codebase improves over time, and a reviewer should **approve once the change definitely improves code health, even if it is not perfect** — if the author demonstrates several approaches are equally valid, the reviewer accepts the author's preference ([The Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html)). On speed: respond within **one business day**, optimise for the velocity of the team rather than of any individual, and give approval with unresolved comments when you are confident the author will address them ([Speed of Code Reviews](https://google.github.io/eng-practices/review/reviewer/speed.html)). Read those two documents once and most of your review habits will change on their own.

**The three-part exit, with dates.**

1. **Write the merge rule and stop being it.** Tests green, checklist passed, one reviewer — **except on the money paths**, where the rule is two reviewers, one of whom may be you. The money paths at VSYST are explicit and short: anything touching the ledger, vouchers, invoicing and TCS computation, tenancy and authorisation, rate confirmation, and payment-gateway callbacks. Everything else — screens, copy, tooling, reports — needs one reviewer who is not necessarily you.
2. **Encode it so nobody has to remember it.** A `CODEOWNERS` file that assigns you to the money paths and nothing else; branch protection that requires the checks rather than a person; a PR template carrying the checklist. Rule in a document, enforcement in the tool.
3. **The measurable exit.** _Median time-to-first-review under one business day for four consecutive weeks, with you removed as a required reviewer everywhere outside the money paths._ Both halves matter — removing yourself while the median stays at three days means you handed the bottleneck to someone else.

**What you keep doing, deliberately and visibly.** Reading merged code weekly, without blocking anything. Sampling is how a CEO keeps a bar without holding a gate ([[13-product-and-technology-leadership-for-a-technical-ceo|lesson 13]] §6.4), and it has the useful property of being invisible to the queue.

**The comment discipline that stops you re-authoring in the review.** Prefix every comment with its register — the same three registers as §8.2, in engineering clothes:

- `blocking:` — it is wrong, or it violates a written constraint. Must change.
- `question:` — I do not understand this. May end in nothing.
- `nit:` — taste. **Explicitly ignorable, and you must let some of them be ignored.**

Then count the ratio each month. **If `nit:` outnumbers `blocking:` by more than about three to one, you are editing prose, not reviewing code**, and the author is receiving it as a rewrite (§8.1). The count takes two minutes with `grep` and it is the most honest self-assessment in this lesson.

### 10.3 Fixing production

[[13-product-and-technology-leadership-for-a-technical-ceo|Lesson 13]] §11.4 gives the law — _you do not fix production at 2 AM once the rota exists_ — with one exception, the week you are on the rota. This section is the path to that law, because today there is no rota, and a law with no path is a slogan.

| Stage                   | What exists                                                                                                                      | What you do                                                                                                                   | Exit to the next stage                                                                                 |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **0 — today**           | No rota. No runbooks. Alerts are a dealer's WhatsApp message                                                                     | You fix it. But **you may not fix it silently: every fix produces a runbook entry the same week, or the fix did not happen**  | Five runbooks exist, covering the five failure classes that actually recurred                          |
| **1 — inventory**       | Runbooks for the top five recurring failures, each ending in a verification step                                                 | You fix it, then hand the runbook to someone else and watch them do it once                                                   | A second person has executed at least two runbooks unaided, on a real incident                         |
| **2 — rota of two**     | Alerts that name the failure class and page a person; a two-person rota, alternating weeks — yes, at three people                | You are on call half the weeks. On the other weeks **you go back to sleep**, and you say so out loud the first time you do it | Four consecutive weeks in which every incident during the other person's week was resolved without you |
| **3 — the law applies** | Rota, runbooks, severities, postmortems ([[12-product-and-engineering-operations\|COO 12]] §5, [[T17-incident-postmortem\|T17]]) | Nothing at 2 AM, except by choice or as the on-call person                                                                    | This is the destination. The measure is the count below, held at zero                                  |

**The measurable exit condition: the number of incidents in the last quarter you personally resolved outside your on-call week — target zero — alongside the number of distinct failure classes with a runbook, which should only go up.** Two numbers, on the quarterly review, no interpretation required.

**Two imports that make the stages survivable.** First, PagerDuty's uncertainty rule from §7.1 — if you are unsure of the severity, treat it as the higher one — combined with lesson 13's rule that a wrong stored figure in a live tenant is a SEV1 regardless of amount. Nobody should be deciding severity at midnight. Second, the SRE idea of an **error budget**: decide in advance what rate of failure is acceptable, so that no individual incident becomes a referendum on whether the whole company should slow down ([Google SRE — Embracing Risk](https://sre.google/sre-book/embracing-risk/)). At VSYST's size the practical form is a single sentence, decided once a quarter: _we accept N hours of degraded service this quarter; if we exceed it, the next bet becomes reliability instead of features._ That is one CEO decision replacing a hundred 11 PM ones.

### 10.4 The fourth bottleneck, which nobody names

The three above are visible. The fourth is not, and at VSYST it is the largest: **you are the only person who understands the money path.** The ledger, the voucher lifecycle, the month-close arithmetic, the reconciliation logic — the code where the August double-post happened. Every other bottleneck in this section costs you hours. This one is a **bus factor of one on the part of the product that holds customers' money**, which is not an engineering risk; it is a director-level risk that belongs on the register in [[18-risk-crisis-and-the-hard-things|lesson 18]] and in the board's minutes under [[09-board-governance-and-the-directors-duties|lesson 09]].

It also has a compounding effect that is easy to miss: because only you can safely change that code, all money-path work queues behind you, which means the fix for the last incident is still unmerged when the next one arrives. **A correctness fix that exists on a branch and is not deployed is the worst available state** — the corrupting path is still the code that runs ([[13-product-and-technology-leadership-for-a-technical-ceo|lesson 13]] §7.4).

**The exit condition, in three parts, and it is the most valuable hour in this lesson:**

1. **A second person independently traces one month's ledger for one relation, end to end, and arrives at the same number you do.** Not reads the code — traces the numbers, from source events to the stored figure, on paper. When their number matches, the knowledge has transferred. When it does not, you have found either a bug or the gap in the documentation, and both are wins.
2. **The regression tests written after the August incident are merged and running in CI** — the month-rebuild check and the bug-museum case that reproduces the double-post. A red test sitting on an unmerged branch protects nothing; it is a note to yourself with extra steps. Once they run on every push, the _class_ of bug is caught by the machine rather than by your suspicion, which is the actual transfer of the bus factor.
3. **The rebuild-and-compare job runs on a schedule for every relation, and alerts.** The August drift persisted because the periodic check had never run for that relation. A check that has to be remembered is not a check.

Note what all three have in common with §10.1–§10.3: **the exit is never "trust someone more." It is an artefact, a tool and a number.** Trust is what you feel after the number moves, not the thing you decide to do first.

### 10.5 The general form

| The request                                  | The costume it wears   | The artefact that replaces you                                    | The tool that enforces it                              | The number that says you are out                                                                             |
| -------------------------------------------- | ---------------------- | ----------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------ |
| "Approve this design"                        | Technical leadership   | Three written constraints + an ADR log                            | CI test for tenant scoping; the ADR folder in the repo | Four weeks with no question the documents did not answer                                                     |
| "Review my PR"                               | Quality ownership      | Written merge rule + PR checklist                                 | `CODEOWNERS`, branch protection, required checks       | Median time-to-first-review < 1 business day, four weeks, with you off the required list outside money paths |
| "Production is down"                         | Being a good teammate  | Runbooks + severities + a two-person rota                         | Alerting that pages by failure class                   | Zero incidents resolved by you outside your on-call week, one quarter                                        |
| _(unnamed)_ "Only you understand the ledger" | Care about correctness | A traced-by-a-second-person walkthrough + merged regression suite | Rebuild-and-compare on a schedule, tests in CI         | A second person's independent month-close figure matches yours                                               |

One last honesty note, because this section can be read as an instruction to stop doing engineering, and it is not. [[13-product-and-technology-leadership-for-a-technical-ceo|Lesson 13]] §2.4 says the honest allocation at three people is 40–60% of your week on engineering, and this lesson does not argue with it. **What §10 removes is not your hands from the keyboard. It is your name from the critical path.** You can write a great deal of code as a person whose absence does not stop anything — and that, not abstinence, is the goal.

## 11. Measuring whether you are still the bottleneck

Everything above can be done sincerely and change nothing, because delegation is the area of management where self-report is least reliable. Founders who have just written a decision-rights matrix feel like they have delegated. **The feeling arrives at the moment of writing; the change arrives, if at all, about two months later.** So measure it, with observable tests, on a fixed cadence, and let the numbers be the argument.

### 11.1 Six tests, all countable

| Test                                            | How to count it                                                                                                                                         | Where the data already is                                                                            | Target at VSYST this year                                                                          | What a bad reading actually means                                                                                                                                        |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Decisions made without you**                  | Count decisions taken by someone else and _reported_, not asked, in the last week                                                                       | The weekly notes — if the notes have no such section, add one, and the section itself is a mechanism | Rising month on month; never zero in a month                                                       | The limits are not real, or nobody has been told they exist (§4.3's routing failure)                                                                                     |
| **The unreachable test**                        | The longest stretch the company ran cleanly with you genuinely unavailable. "Cleanly" = it shipped, it sold, it supported, it filed, and nothing waited | Your own calendar, and an honest question to the other two                                           | Ladder: 4 hours → 1 working day → 3 days. **2–3 days is this year's honest target**, not two weeks | Whatever broke is the next mechanism, not a resolution to plan better ([[20-the-autopilot-test-and-scaling-the-machine\|COO 20]])                                        |
| **The only-me list**                            | Take this week's task list. Mark each item "only I can do this" — honestly. Compute the fraction                                                        | [[C27-ceo-weekly-template-and-calendar-audit\|C27]]'s calendar audit                                 | Under 30%, and **every item on it maps to one of §6's seven**                                      | Anything on the only-me list that is not in §6 is either not yours or has no owner yet. That list is your delegation backlog, already prioritised                        |
| **Overrule count**                              | Times you changed someone's already-made call in the last month                                                                                         | Your own honesty; ask the other two to check you                                                     | Falling toward one or two a quarter                                                                | Zero is _also_ a finding — it usually means you stopped routing decisions to people rather than stopped overruling them (§5.3's silent correction)                       |
| **Has anyone overruled you on their own turf?** | Count occasions in the last quarter when someone said, in effect, "that's my call and I'm doing it the other way" — and it stood                        | Nowhere. You have to remember it, which is the point                                                 | At least once a quarter                                                                            | If it has never happened, either your limits are not real or nobody believes they are. **This is the sharpest test on the page and it appears on no dashboard anywhere** |
| **Decision age**                                | Median days that open decisions have been sitting on your list; count anything over 14 days                                                             | Your list, [[C29-decision-journal-and-one-way-door-log\|C29]]                                        | Median under 5 days; zero items over 14 (§9.4 rule 6)                                              | Slow is the invisible failure. This row makes it visible                                                                                                                 |

Two of these deserve a sentence more.

**The unreachable test is designed before it is run, or it is a holiday.** The COO course's two-week version is the endgame and it is explicitly a _designed test_: a written list of what must keep working, a written rule about what may not be escalated, and a named decision-maker for the period ([[20-the-autopilot-test-and-scaling-the-machine|COO 20]]; the two-week holiday test as a system test is the course's definition of done). The CEO's version starts far smaller and far sooner: **one working day, next month, announced.** Phone off, one emergency number with a written definition of emergency, and a debrief the next morning that asks only what stopped and what was escalated that should not have been. A day is enough to find three broken things, and it costs a day.

**The reverse-overrule test is the one to watch.** A company where the founder has never been overruled inside someone else's written limit does not have decision rights; it has a suggestion box. The first time it happens, three things must be true or the test will never register again: it stands, you say publicly that it stands, and you name it as a good thing that happened rather than a thing you tolerated (§5.3).

### 11.2 The counter-metric, so this does not become a game

Every one of the six tests can be gamed by delegating badly, which is why they travel with a seventh number: **the quality of the decisions made without you.** Once a quarter, take a sample of six delegated decisions from the weekly notes, and score each the way [[02-how-a-ceo-thinks|lesson 02]] §1.1 says — **decision quality separately from outcome quality**, judged on what was knowable at the time.

Read the result carefully, because the naive reading is wrong. If delegated decisions are producing worse outcomes at a materially higher rate than yours, that is not a signal to take the decisions back. It is a signal that **the limit was drawn wrong or the context was thin** — parts two and three of §4.3's handover — and the fix lives in those two places. Pulling the decision back is the reflex, and it resets the clock on the whole exercise.

The number you will actually find, over a year, is the one that makes further delegation easy: a meaningful share of the calls you would have overruled turned out fine. Keep that count. It is the most persuasive argument available to you, and it is an argument with yourself.

### 11.3 The cadence

- **Weekly, five minutes, in your own note:** decisions made without you this week; anything that reached you and should not have; anything over 14 days old.
- **Monthly, fifteen minutes:** the six tests, written down as numbers, next to last month's. Not a narrative — a row.
- **Quarterly, forty-five minutes, with the other two directors:** the counter-metric sample, one rung moved on §5's ladder or an explicit statement that none was, and one decision formally handed over with its limit written into [[C03-decision-rights-matrix|C03]]. **A quarter in which nothing was handed over is the finding**, and it should be minuted as one.
- **Annually:** re-ratify C03 by board resolution, and re-run the unreachable test one level longer than last year's.

The rule underneath the cadence is the one from §2.3: **the rate of change here is the number of written limits, and nothing else.** Not the number of conversations about delegation, not the intent, not the framework. Count the limits. If the count did not go up this quarter, neither did anything else.

## 12. At VSYST — applying this now

Three people, no employees, no COO in the seat yet, and a CEO who writes most of the code. That combination makes almost everything in this lesson feel premature, and it is exactly the moment it is cheapest to install. **Every mechanism here costs an hour now and costs a quarter of renegotiation at fifteen people.**

- **Write [[C03-decision-rights-matrix|C03]] this week with twelve rows, not forty.** Twelve rows covering the decisions that actually recur: setup-fee waivers, credit notes and refunds, tooling spend, what ships in a release, which dealer gets visited, vendor renewals, support-tier promises, data-access requests, the money-path merge rule, board-resolution matters, borrowings, and anything involving a relative or a director's firm. A forty-row matrix written in one sitting is a document nobody reads; twelve rows argued over by all three directors is a working agreement. Ratify it by resolution and put the date on the `Board Calendar` tab of [vsyst-ceo-workbook.xlsx](toolkit/vsyst-ceo-workbook.xlsx).
- **Publish the same-day escalation page, and pin it.** §7.3's five triggers, written as tests, on one page in the vault, with the four-line message format from §7.4 and your two-hour acknowledgement promise. Then send it as a pinned WhatsApp message, because that is where the company actually reads things. It will take forty minutes and it is the highest-return forty minutes in this lesson.
- **Hand over exactly one decision this month, using §4.3's script.** One. The best candidate at VSYST today is **support credit notes and refunds up to ₹10,000 per tenant per month, live tenants only, never against an invoice already in a filed return** — it recurs, it has a natural limit, the information genuinely lives with whoever is answering the dealer, and the failure mode is bounded and visible. Write the limit into C03, tell both other directors the routing changed, and then do not touch it for two cycles.
- **Take your name off the required-reviewer list everywhere outside the money paths, this week.** Write the two-reviewer rule for ledger, vouchers, invoicing and TCS, tenancy and authorisation, rate confirmation and gateway callbacks; put a `CODEOWNERS` file in each of the three repos; turn on branch protection that requires the checks rather than a person. Then record today's median time-to-first-review as the baseline you are measuring against (§10.2).
- **Write the three architecture constraints and open the ADR folder.** The first three ADRs are retrospective and take an hour between them: tenant scoping is structural; every money figure has a recoverable lineage; billing is web-only and the app is gated server-side. Retrospective ADRs feel pointless and are not — they are how the folder gets its first readers.
- **Merge the ledger fix and its regression tests before anything else on this list.** A correctness fix that exists on a branch and is not deployed leaves the corrupting path running ([[13-product-and-technology-leadership-for-a-technical-ceo|lesson 13]] §7.4), and it is also the thing blocking §10.4's bus-factor exit. Then book ninety minutes with the domain-expert director to trace one month's ledger for one relation on paper, independently, and compare numbers.
- **Start the runbook inventory with a rule, not a project.** From today: every production fix produces a runbook entry the same week, or it did not happen. In a quarter you will have the five runbooks that stage 1 of §10.3 needs, without ever having scheduled a documentation sprint.
- **Book one unreachable day for next month and announce it.** One working day, phone off, one emergency number with a written definition of emergency, debrief the next morning. Whatever breaks is the next quarter's mechanism. Do not attempt the two-week version this year — you do not have the runbooks, the rota or the second pair of hands, and a failed test that was designed to fail teaches nothing.
- **Say the four-line escalation format out loud when you introduce it, including the uncomfortable clause** — that if the default in line 4 executes because you did not reply, you do not get to complain about it. Saying it is what makes the format usable.
- **What not to do:** do not roll out RAPID or delegation poker as a framework (§3.3 — three people need a page, not a vocabulary); do not write a second decision log alongside [[C29-decision-journal-and-one-way-door-log|C29]] and [[T09-decision-log-and-adr|T09]]; do not build a delegation-of-authority matrix that duplicates [[T22-delegation-of-authority-matrix|T22]]'s rows; do not delegate the kernel, the capital decision, an exec hire, the values when they cost money, the board signature, the story, or the IOCL relationship (§6); do not hand over two decisions at once; and do not agree a board matter over dinner because convening feels excessive at three people (§6.2).

## 13. Exercises

Each produces a dated artefact. Do them in order — 13.1 and 13.2 are prerequisites for 13.4, and 13.3 will tell you which decision to use in 13.4.

**13.1 — Fill [[C03-decision-rights-matrix|C03]] to twelve rows (45 min, all three directors, one sitting).** Use C03's template columns exactly: decision type, who decides, consulted, informed, the ₹ or scope limit, board resolution?, shareholder resolution?. Argue every row out loud; a row nobody argued about is a row nobody will follow. Mark each row Type 1 or Type 2 (§9.3) and add one column this lesson requires that the template does not force: **the escalation trigger** — the condition under which this decision comes to the CEO anyway. Flag every statutory cell **VERIFY LIVE** and send the sheet to the CS before ratification. **Artefact:** C03 v0.1 with twelve completed rows, a ratification date on the `Board Calendar` tab, and a list of the cells awaiting the CS's confirmation. **Success test:** for every row, all three directors give the same answer when asked separately who decides.

**13.2 — Write the escalation criteria (30 min, alone, then 10 min to circulate).** One page, three buckets (§7.2). Fill the same-day section with §7.3's five triggers rewritten in VSYST's own nouns — name the actual figures, the actual filings, the actual channels — so that no row requires judgment to apply. Add the four-line message format, your acknowledgement window, and the sentence that says a correct escalation which turned out to be nothing was still correct. Then do the installation test: ask each of the other two directors, separately, what would make them call you tonight, and compare their answers to the page. **Artefact:** `escalation-criteria.md` in the vault, linked from C03, pinned in WhatsApp, plus the gap list from the installation test. **Success test:** the two answers you got back match the page on at least four of the five triggers.

**13.3 — The one-week decision log, classified by who _should_ have decided (20 min to set up, 5 min a day, 25 min to analyse).** For five working days, log every decision you make — one line each, including the trivial ones, especially the trivial ones. At the end of the week add three columns: **reversibility** (one-way / two-way), **where the information actually lived** (§2.1), and **who should have made this** using §2.2's grid. Then count. Compute the fraction that should not have been yours, and the fraction of your total _time_ they consumed — the two numbers are usually very different and the second is the one that stings. Circle the three that recur most often; those are your delegation candidates, ranked by evidence rather than by comfort. **Artefact:** a dated table in the vault with a "should have been" column, a count, and three circled candidates. **Success test:** at least a third of the logged decisions are not yours, and you can name the missing limit for each of the three circled ones.

**13.4 — Hand one decision over, formally, with the limit written down (30 min conversation + 15 min writing).** Take the top candidate from 13.3 — or the credit-note row from §12 if you would rather start with the safe one — and run §4.3's four-part script out loud: the decision, the limit, the context (including the invisible fences from §4.4's middle column), and what comes back and when. Say the rung out loud (§5.1). Write the limit into C03 the same day. Send the routing message to both other directors in writing, that week, phrased as an instruction rather than an announcement: _X now decides this; stop sending it to me._ Put the 30-day review in the calendar before you leave the room, with §4.5's three questions already written into the invite. **Artefact:** a C03 row with a limit and a date, a [[C29-decision-journal-and-one-way-door-log|C29]] entry recording the handover as a decision, the routing message, and a booked review. **Success test:** at the 30-day review you have not touched the decision, and you can name one call inside the limit you would have made differently and let stand.

**13.5 — Write the three technical exit conditions, with today's baselines (45 min, at the keyboard).** This is the one a technical founder should not skip. Record the baselines first, because a target with no baseline is a wish: **(a)** median time-to-first-review on the last twenty merged PRs across the three repos, split into wait-for-first-review and everything else; **(b)** the number of distinct production failure classes that have a runbook, which today is probably zero; **(c)** a tally of architecture questions answered verbally in the last two weeks, marked for whether a document should have answered them. Then write the three exit conditions from §10.1–§10.3 with dates against them, the three architecture constraints from §10.1's table, and the first ADR. Finally write §10.4's bus-factor exit as a dated commitment with a named second person. **Artefact:** a dated note holding three baselines and three exit conditions, a `constraints.md` in the repo, one ADR, and a booked ledger-tracing session. **Success test:** each of the three exit conditions is a number a third party could check without asking you how you feel about it.

---

**Previous:** [[15-the-ceo-operating-cadence-and-calendar|15 — The CEO's Operating Cadence and Calendar]] — the week, the month, the quarter and the year; the calendar audit that shows where the CEO's time actually goes.

**Next:** [[17-the-numbers-a-ceo-watches|17 — The Numbers a CEO Watches]] — the five numbers from memory, the CEO dashboard, the metric tree, and the monthly business review where the decisions this lesson delegated come back as numbers instead of as questions.

**Related:** [[02-how-a-ceo-thinks|02 — How a CEO Thinks]] (one-way doors, the disagreement protocol, decision quality vs outcome quality) · [[03-the-ceo-core-value-and-the-founder-contracts|03 — The CEO's Core Value and the Founder Contracts]] (the CEO–COO contract, the no-surprises rule, the C03/T22 split) · [[05-strategy-i-diagnosis-and-the-strategy-kernel|05]] (the kernel you never delegate) · [[10-building-the-team-hiring-equity-and-firing|10]] · [[13-product-and-technology-leadership-for-a-technical-ceo|13 — Product and Technology Leadership for a Technical CEO]] (what to stop owning in product; the 2 AM rule; the ledger as a company-level risk) · [[18-risk-crisis-and-the-hard-things|18]] · [[20-the-ceo-own-operating-system-and-succession|20]] · [[C01-ceo-charter-and-90-day-plan|C01]] · [[C03-decision-rights-matrix|C03]] · [[C27-ceo-weekly-template-and-calendar-audit|C27]] · [[C29-decision-journal-and-one-way-door-log|C29]] · [[COO-Docs/index|COO Docs]] — [[17-delegation-decision-rights-and-org-design|17 — Delegation, Decision Rights and Org Design]], [[20-the-autopilot-test-and-scaling-the-machine|20 — The Autopilot Test]], [[12-product-and-engineering-operations|12 — Product and Engineering Operations]], [[T01-ceo-coo-operating-agreement|T01]], [[T07-raci-matrix|T07]], [[T09-decision-log-and-adr|T09]], [[T17-incident-postmortem|T17]], [[T22-delegation-of-authority-matrix|T22]].
