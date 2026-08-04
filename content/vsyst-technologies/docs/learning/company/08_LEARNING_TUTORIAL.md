# 08 — Learning Tutorial: A 12-Week Founder Crash Course

## Framing

This is a zero-to-one founder's 90-day crash course, structured as a week-by-week plan. Assume ~30 hours per week on this path — roughly half a working week if you have a day job, or a full-time block if you have committed to the startup. The tutorial is designed specifically for a founder building B2B SaaS for Indian fuel distributors (DZZLO OMS), but the sequencing applies to any low-ARPU SME category.

The plan has three phases. **Weeks 1–4** are pure learning and discovery — no code. **Weeks 5–8** are build, price, and position. **Weeks 9–12** are distribute, sell, measure, and decide on capital. Every week has a goal, reading, watching, doing, and a single measurable success metric. The metric is non-negotiable — if you cannot hit it, you have either mis-scoped the week or mis-scoped the business, and both are useful to know.

Companion reference: [07_STARTUP_FOUNDATIONS.md](./07_STARTUP_FOUNDATIONS.md) for the underlying domains.

---

## Week 1 — Foundations & Mindset

- **Goal:** Internalise that the founder's job in month 1 is finding a real problem, not building software.
- **Read:** _Zero to One_ (Thiel), chapters 1–4; Paul Graham's [essays](https://www.paulgraham.com/articles.html) — "How to Get Startup Ideas," "Do Things That Don't Scale," "Startup = Growth." Estimated 6–7 hours of reading.
- **Watch:** Michael Seibel — ["Biggest Mistakes First-Time Founders Make"](https://www.ycombinator.com/library/66-biggest-mistakes-first-time-founders-make); Sam Altman's "How to Succeed with a Startup" lecture.
- **Do:** Write a 1-page founder memo answering: Why you? Why now? Why fuel distribution specifically? What's your unfair advantage — prior domain experience, network, insight, capital? Share the memo with 2 people — ideally one current petrol pump owner and one ex-OMC (BPCL/HPCL/IOCL) executive. Write down their unfiltered reactions, not your rebuttals.
- **Success metric:** Memo completed and feedback from at least 2 domain veterans captured in writing.

## Week 2 — Customer Discovery Theory

- **Goal:** Learn to interview customers without biasing their answers.
- **Read:** _The Mom Test_ by Rob Fitzpatrick — the entire book, ~3 hours. [momtestbook.com](https://www.momtestbook.com). Follow up with [Looppanel's customer interview playbook](https://www.looppanel.com/blog/customer-interviews).
- **Watch:** Steve Blank's Stanford ENG 212 — "Customer Development" lectures on YouTube. Focus on the "get out of the building" sessions.
- **Do:** Draft a 10-question discovery guide following Fitzpatrick's rules — ask about past behaviour, dig into specifics, never pitch. Book 20 interviews with fuel dealers via WhatsApp, cold calls, and the OMC dealer directory. Attend at least one BPCL, HPCL, or IOCL dealer association meet in your city. Use LinkedIn, local petroleum dealers' associations (FAIPT, FAIITDA), and referrals.
- **Success metric:** 20 interviews booked on the calendar with confirmed time slots.

## Week 3 — Discovery Execution

- **Goal:** Execute the 20 interviews and surface the burning problems — ranked by frequency and intensity.
- **Read:** Re-skim _The Mom Test_ specifically the "deflecting compliments" and "anchoring commitments" chapters before each day of interviews.
- **Do:** Complete 20 × 30-minute interviews, ideally two-person format — one leads, one notes, as Fitzpatrick recommends. Record with consent (WhatsApp voice call recordings work). Transcribe each (Rev, Otter, or a low-cost VA). Tag every pain point in a spreadsheet with columns: dealer profile (outlets, OMC, region), pain mentioned, frequency (daily/weekly/monthly), intensity (1–10), current workaround. At the end of the week, rank pains by frequency × intensity. Look for consensus — if 15 of 20 dealers independently mention the same problem, you have found signal.
- **Success metric:** 20 transcripts in the folder; top 5 pains ranked by frequency × intensity; at least one pain mentioned unprompted by ≥12 of 20 dealers.

## Week 4 — Problem Framing & Lean Canvas

- **Goal:** Convert your discovery data into a testable business hypothesis.
- **Read:** _Running Lean_ (Ash Maurya), Lean Canvas chapters — [Shortform summary](https://www.shortform.com/blog/ash-maurya-lean-canvas/). April Dunford's _Obviously Awesome_ — the 5 components of positioning.
- **Do:** Fill in the Lean Canvas on one page. Pick ONE Ideal Customer Profile — specific enough to be useful. For DZZLO OMS a good starter ICP might be "2–5 outlet petrol pump owner in Maharashtra or Gujarat, HPCL or BPCL-affiliated, owner personally involved in daily ops, existing Tally usage." Draft a one-paragraph positioning statement using Dunford's 5 components: competitive alternatives, unique attributes, value and proof, best-fit customers, category. Walk 3 prospects through the canvas and the positioning; capture where their eyes glaze over.
- **Success metric:** Lean Canvas and positioning statement reviewed and signed off (informally) by 3 prospects who said "yes, this is real."

## Week 5 — MVP Scoping

- **Goal:** Define the smallest possible thing that delivers the "magic moment" to the target user.
- **Read:** _The Lean Startup_ (Eric Ries), Part 2 on build-measure-learn.
- **Watch:** Marty Cagan on "Continuous Discovery"; Teresa Torres on opportunity-solution trees ([Product Talk](https://www.producttalk.org/)).
- **Do:** Write a 2-page MVP spec — one job, one outcome, one workflow. For DZZLO OMS, example: "Dealer receives a WhatsApp message at 10 PM with daily DSR reconciled against their HPCL portal and bank settlement. Discrepancy highlighted. One-tap approve." That is the entire v0. Show the spec to 5 of your interviewees and ask for a Letter of Intent (even an informal "yes, I'd pay ₹X/month for this"). Do not build yet.
- **Success metric:** 5 soft LOIs or explicit WTP signals ("I'd pay ₹X/month for exactly this").

## Week 6 — Build v0 (or Concierge)

- **Goal:** Ship. Michael Seibel's rule: "launch something bad quickly." Perfection in month 2 is procrastination.
- **Do:** For a low-tech ICP like fuel dealers, a WhatsApp-based concierge MVP often beats a proper app for the first 10 customers. Use WhatsApp Business API + Google Sheets + a daily manual back-office process. You pretend to be software; customers get the outcome; you get to learn what they actually use without shipping a line of production code. For more technical ICPs, ship a no-frills web app — Retool, Bubble, or a thin Next.js + Firebase stack. Either way, onboard 3 real users this week.
- **Success metric:** v0 live and actively being used by 3 paying (or firmly committed) customers.

## Week 7 — Pricing & Monetization

- **Goal:** Choose the right monetization model for a low-ARPU SME category.
- **Read:** First Round Review pricing essays; SaaStr on SMB pricing; a Stripe or Chargebee guide on usage-based models.
- **Do:** Decide your monetization axis — flat SaaS subscription, transaction-based (₹X per invoice/reconciliation), or embedded finance (free software, earn on fuel credit financing or payments). Benchmark against Khatabook, Vyapar, OkCredit, MyBillBook, Dukaan — study their pricing pages and reported ARPUs. [KrASIA — Khatabook raises $60M from B Capital](https://kr-asia.com/indian-digital-ledger-startup-khatabook-raises-usd-60-million-from-b-capital-group). Draft a 3-tier price sheet (Starter, Growth, Pro). Run it past 10 dealers — watch for the reaction that signals "this feels expensive but fair" (the right zone).
- **Success metric:** 3-tier pricing sheet finalized; WTP signals from at least 10 dealers across the three tiers.

## Week 8 — Positioning & Narrative

- **Goal:** Clarify the story so a 10-year-old (or a stressed dealer on a 4-inch Android at 3G) can understand it in 30 seconds.
- **Read:** _Obviously Awesome_ (April Dunford), _Play Bigger_ (Ramadan), _Building a StoryBrand_ (Donald Miller). Focus on the exercises, not the theory.
- **Do:** Write homepage copy — hero headline, sub-headline, 3 benefits, 3 testimonials, pricing CTA. Write it in English and at least one regional language (Hindi, Marathi, or Gujarati). Test on 10 prospects by showing them the page for 10 seconds, hiding it, and asking them to explain back what the product does.
- **Success metric:** ≥ 7 out of 10 prospects correctly paraphrase the value proposition after one read.

## Week 9 — Distribution & Traction

- **Goal:** Pick the one channel that can scale — before committing budget to it.
- **Read:** _Traction_ by Weinberg & Mares — the Bullseye framework across 19 channels ([99signals summary](https://www.99signals.com/marketing-lessons-traction-weinberg-mares/); [Brian Balfour — Bullseye](https://brianbalfour.com/essays/traction-the-bullseye-framework)).
- **Do:** Brainstorm all 19 channels with no filter. Rank into A (most plausible), B (promising), C (unlikely). Pick 3 from the A-ring and run cheap tests this week — typical candidates for Indian fuel SME: (1) field sales at a high-density petrol pump cluster, (2) OMC dealer event booth, (3) WhatsApp cold outreach via dealer associations, (4) partner channel through existing Tally/POS vendors, (5) referrals from the first 3 customers. Budget: ₹10,000–25,000 per test.
- **Success metric:** Test results captured across 3 channels with cost per qualified lead and cost per signup; one channel picked as the focus for the next 90 days.

## Week 10 — Sales Mechanics

- **Goal:** Close the first 10 paying customers through founder-led sales.
- **Read:** _SPIN Selling_ (Neil Rackham); a MEDDIC primer; a Challenger Sale summary ([Gong](https://www.gong.io/blog/sales-methodologies)).
- **Do:** Build a SPIN-based discovery script — 4 Situation questions, 4 Problem questions, 4 Implication questions, 4 Need-Payoff questions. Run 10 in-person demos this week (or Zoom + WhatsApp if geography prevents it). Record every demo; review with your co-founder (or alone) and tag where you lost control. For DZZLO OMS, expect objections like "I already have Tally," "my manager won't use it," "petrol margins are too thin to pay for software." Have scripted responses for the top 5.
- **Success metric:** 10 paying customers or 10 signed pilot agreements with a date-bound conversion milestone.

## Week 11 — Metrics, Retention, PMF Signal

- **Goal:** Instrument AARRR; run the Sean Ellis PMF survey; compute real unit economics.
- **Read:** [First Round Review — Superhuman PMF Engine](https://review.firstround.com/how-superhuman-built-an-engine-to-find-product-market-fit/); Amplitude's AARRR guide.
- **Do:** Instrument the funnel end-to-end — Acquisition (source per lead), Activation (first key action within 48 hours), Retention (weekly active), Referral, Revenue. Run the Sean Ellis survey to all live users — minimum n = 40 (if you have fewer, go back and sell more). Compute CAC (fully loaded), payback period in months, and Net Revenue Retention for your 60-day cohort.
- **Success metric:** Baseline PMF score recorded (target: ≥ 40% "very disappointed"); AARRR dashboard live and refreshing daily; CAC, payback, and NRR computed for each cohort.

## Week 12 — Fundraising Prep OR Bootstrap Path

- **Goal:** Make the definitive decision — raise a seed round or commit to bootstrapping.
- **Read:** _The Hard Thing About Hard Things_ (Ben Horowitz); _Crossing the Chasm_ (Geoffrey Moore).
- **Watch:** Naval Ravikant on the Tim Ferriss podcast; YC's "Seed Fundraising" lecture.
- **Do:** If raising — build a 10-slide deck (problem, market, product, traction, business model, GTM, team, ask, use of funds, vision). Build a target list of 30 investors — Peak XV, Accel, Blume, Together Fund, Neon Fund, Z47, and 6–8 seed-focused angels/micro-VCs active in Indian B2B SaaS. Line up warm intros through alumni networks, portfolio founders, SaaSBoomi, and operator angels. Aim for 10 first meetings. If bootstrapping — write a 12-month cash plan: MRR ramp assumption, hiring plan, runway at current burn, break-even month. Both paths are respectable; the wrong answer is not deciding.
- **Success metric:** 10 investor first meetings booked OR a signed 12-month bootstrap plan with monthly cash checkpoints.

---

## After Week 12: Ongoing Cadences

The 90-day sprint gets you to a defensible baseline. What follows is rhythm, not milestones.

**Weekly**

- 3 customer touchpoints minimum — no exceptions, no "we were busy shipping" excuses. Teresa Torres's rule.
- Team standup against AARRR dashboard; at least one experiment in flight.
- Founder health check: sleep, exercise, one non-work conversation with a peer.

**Monthly**

- Cohort unit economics refresh — CAC, LTV, payback, NRR.
- Pipeline review; update on the one chosen acquisition channel's CAC trend.
- 1:1 with one founder 1–2 stages ahead; 1:1 with one lead customer.

**Quarterly**

- Sean Ellis PMF survey (n ≥ 40 if you have the users).
- Positioning review — have you learned anything in the quarter that should change the one-liner?
- Strategy offsite (even if it is one afternoon, alone, with a notebook and no laptop).

## Books to Read in Parallel (Ordered)

1. _The Mom Test_ — Rob Fitzpatrick (already done in Week 2; re-read every 6 months)
2. _Obviously Awesome_ — April Dunford
3. _Inspired_ (2nd ed.) — Marty Cagan
4. _Continuous Discovery Habits_ — Teresa Torres
5. _The Hard Thing About Hard Things_ — Ben Horowitz
6. _Crossing the Chasm_ — Geoffrey Moore
7. _Traction_ — Weinberg & Mares
8. _Blitzscaling_ — Reid Hoffman (for the growth-stage mental model, even if you are nowhere near it yet)
9. _Zero to One_ — Peter Thiel (re-read annually)
10. _Lost and Founder_ — Rand Fishkin (the antidote to the above — honest about what went wrong)

## Communities to Join

- **SaaSBoomi** — the default network for Indian SaaS founders. Attend the annual Chennai event at least once.
- **Indie Hackers** — the global community for bootstrapped founders; filter for the SaaS Meetups board.
- **Lenny's Slack** — invite-only but worth the effort for PM/GTM peer discussion.
- **FirstPrinciples Founders**, **iSPIRT**, and your city's local founder WhatsApp groups — India-specific peer networks.
- Your YC Startup School batch cohort if you join one (free and the Slack is active).

The goal is not conference tourism; it is access to 2–3 peers at your stage you can text at 11 PM when something is on fire.

---

Sources → [RESEARCH_SOURCES.md](./RESEARCH_SOURCES.md)
