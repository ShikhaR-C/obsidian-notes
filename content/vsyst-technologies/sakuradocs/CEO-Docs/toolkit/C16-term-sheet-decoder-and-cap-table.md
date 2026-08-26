# C16 — Term-Sheet Decoder, Cap Table and Dilution Model

_Toolkit · fills exercise 15.3 in [[08-capital-runway-and-fundraising|08 — Capital, Runway and Fundraising]] · Owner: CEO builds it; **every term goes past your own lawyer before signature — not the investor's lawyer, not a friend, not a template** · Cadence: built once in the calm, then re-run on every term sheet, every round and every ESOP top-up · Workbook tabs: `Cap Table & Dilution` and `ESOP Pool` in [vsyst-ceo-workbook.xlsx](vsyst-ceo-workbook.xlsx)._

## Purpose

Ask a founder what they got and they will tell you the valuation. Ask them in year four what actually happened and they will tell you about a term.

**Valuation is the headline. The terms are the deal.** ₹15 crore post-money with a 2x participating preference, a full ratchet, a 15% pre-money pool and a redemption right is arithmetically — not rhetorically — a worse outcome than ₹12 crore clean. This template exists so you can see that rather than take it on faith: a decoder that says, for each term, **what it says / what it means / the founder-friendly benchmark / what to do if it is worse**, plus the three pieces of arithmetic that decide most of the money (the option pool, the anti-dilution formula, and two rounds of dilution).

Two framing facts before the table. First, the standard reference for what these terms mean is [Brad Feld and Jason Mendelson's _Venture Deals_](https://www.venturedeals.com/) — read it before a term sheet arrives, not during, and use [Y Combinator's published documents](https://www.ycombinator.com/documents) to see what "standard" looks like even though the instruments differ in India. Second, and this is the finding that should change how you negotiate: **the liquidation preference matters most in modest outcomes and barely at all in enormous ones.** Because [[08-capital-runway-and-fundraising|lesson 08]] §8.4 argues VSYST's honest outcome is a good-but-modest one, the preference is for this specific company more consequential than the valuation — and a founder pattern-matching on Silicon Valley advice, where the assumed outcome is enormous, will under-weight exactly the term they should fight hardest on.

**Every statutory reference, threshold and rate below is VERIFY LIVE.** Indian company law, FEMA and tax move constantly, and the Income-tax Act, 2025 renumbered a great deal with effect from 1 April 2026.

## When to use

- **First fill: now, with no term sheet in hand.** Build your own two-round table with VSYST's real shareholding and your own assumed round sizes. The point is to know what a 15% pre-money pool costs the three of you, in rupees, _before_ anyone has been flattered by an investor.
- **On the day any term sheet, iSAFE, note or "simple" one-pager arrives** — including from a friendly angel, and including anything described as standard.
- **Before every ESOP top-up and every new grant** — the `ESOP Pool` tab is the pool's only honest record ([[C20-compensation-bands-and-esop-design|C20]]).
- **Every round, forever.** Model **control**, not just economics: an ordinary resolution needs a simple majority and a special resolution needs 75%, so a bloc above 25% blocks every special resolution — including further share issues and AoA amendments. **VERIFY LIVE with the CS** which matters fall into which class.
- **Reads from** [[C14-fundraise-readiness-and-data-room-index|C14]] folder 02 (the cap table must already be clean) and [[C13-runway-burn-and-scenario-planner|C13]] (what the money buys).

## How to fill (rules)

1. **Decide the instrument before the terms.** Section A. In India the instrument decides what is legal, not merely what is convenient.
2. **One cap table, fully diluted, one file.** Options — granted and ungranted — are a line, never netted off. Convertibles appear at their conversion shares, not at zero.
3. **Model the exit distribution, not just the ownership percentages.** Ownership tells you what you hold; the preference waterfall tells you what you receive. They are different numbers and the second is the one that arrives in your bank account.
4. **Size the ESOP pool bottom-up from a real eighteen-month hiring plan**, then argue pre versus post. Section C shows why that order is worth four and a half times the other.
5. **Run every anti-dilution clause through the formula before you agree it.** Section D. "Weighted average" and "ratchet" are not adjectives, they are arithmetic, and the gap between them in a small down round is an order of magnitude.
6. **Count existing grants separately from unallocated pool.** An investor sizing "the pool" may be sizing the unallocated portion. Get the definition written into the document.
7. **Track both thresholds every round: 50% and 25%.** Economics and control diverge, and founders notice the second one a round too late.
8. **Every term goes past your own lawyer.** An Indian seed round done properly costs real money in legal fees and it is among the best money the company will spend. This template is a decoder, not advice.
9. **Do nothing on the strength of a term sheet.** It is mostly non-binding — except the no-shop and confidentiality, which usually are. The money is not raised until the credit shows in the account.
10. **Date-stamp the model and keep every version.** The version you built before the negotiation is evidence of what you thought when nobody was watching. File it in [[C29-decision-journal-and-one-way-door-log|C29]].

## Template

**A. The instrument — decide this first**

| Instrument                                            | The Indian reality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Use when                                                                                                |
| ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| **CCPS — compulsorily convertible preference shares** | **What an Indian seed round almost always is.** Carries the preference and anti-dilution inside the share. "Compulsorily" is load-bearing: under the foreign-exchange framework a compulsorily convertible instrument is a capital instrument, while an optionally convertible or redeemable one is _debt_ and falls into the ECB regime ([EquityList — preferential allotment](https://www.equitylist.co/blog-post/preferential-allotment); [TaxGuru — CCPS through private placement](https://taxguru.in/company-law/ccps-issuance-private-placement-step-by-step-process.html))                                                                                                                        | Any real priced round                                                                                   |
| **Ordinary equity shares**                            | Simplest cap table; no institutional investor accepts it. Still needs a registered valuer's report and the full [§62(1)(c) / Rule 13](https://ca2013.com/rule-13-companies-share-capital-and-debentures-rules-2014/) machinery                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Founder subscriptions; small friends-and-family cheques where everyone genuinely accepts identical risk |
| **Convertible note**                                  | **Constrained at the issuer end, not the investor end.** Legal only for a **DPIIT-recognised** start-up, minimum **₹25 lakh in a single tranche per investor**, convert or repay within **10 years** — below the floor it becomes a _deposit_ with a regime a private company cannot comply with ([Invest India](https://www.investindia.gov.in/team-india-blogs/convertible-note-flexible-funding-options-startups); [IncorpX — FEMA rules](https://www.incorpx.io/blog/convertible-notes-startups-india-fema-rules)). **So the friendly ₹10 lakh angel cheque cannot be a note**                                                                                                                        | Bridging, at scale, with recognition in hand                                                            |
| **iSAFE**                                             | India's SAFE, created by 100X.VC — implemented as **CCPS allotted immediately**, conversion ratio fixed later ([100X.VC](https://www.100x.vc/blog/investing-through-i-safe-notes-yagnesh-sanghrajka-100x.vc-startups-2019); [Mondaq — decoding iSAFE](https://www.mondaq.com/india/securities/1330992/decoding-isafe--part-i); [Vinod Kothari — legality and taxation](https://vinodkothari.com/2024/03/the-isafe-option-to-start-up-funding-legality-and-taxation/)). It simplifies the **commercial** negotiation, not the compliance: shares are allotted, so PAS-4, valuer's report, separate account, PAS-3 and MGT-14 all apply. The **outside conversion date** (commonly ~3 years) is a real term | Pre-seed, accelerators, any round where an honest valuation is impossible                               |

Whatever the instrument, the machinery is the same and it belongs to the CS on a checklist **before** the money moves: board resolution, special resolution, registered-valuer report (the issue price cannot be below the valuer's price), PAS-4 to named persons, money through banking channels into a **separate account only**, allotment within 60 days, PAS-3 and MGT-14, share certificates, registers updated — plus **FC-GPR within 30 days of allotment** if any investor is non-resident ([CAclubindia — FC-GPR on the FIRMS portal](https://www.caclubindia.com/articles/fcgpr-filing-on-rbi-firms-portal-fema-compliance-for-fdi-in-india-process-documents-penalties-53783.asp)). Valuation methodology sits under Rule 11UA, which outlived the angel tax it was written for ([Dewan P N Chopra — Rule 11UA and CCPS valuation](https://www.dpncindia.com/rule-11ua-new-methods-for-valuing-ccps-and-unquoted-shares)); the angel-tax charge itself under §56(2)(viib) has been abolished ([ClearTax](https://cleartax.in/s/angel-tax); [Legal500 / Sarthak Advocates](https://www.legal500.com/developments/thought-leadership/abolition-of-angel-tax-in-india-a-boost-for-the-startup-ecosystem/)). **VERIFY LIVE, all of it.**

**B. The decoder**

| Term                                  | What it says                                                                                      | What it means                                                                                                   | Founder-friendly benchmark                                                                                                      | If it is worse                                                                                                                                                                                                                                                                      |
| ------------------------------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Liquidation preference**            | Investor is paid first on a sale or winding up                                                    | Decides who gets what in the _likely_ outcome, not the dream one                                                | **1x non-participating, pari passu**                                                                                            | Cap the participation (ceases at 2–3x, then converts). Refuse >1x. Refuse senior stacking. Show the investor the ₹15 cr row of the waterfall — the argument is arithmetic, not sentiment                                                                                            |
| **Anti-dilution**                     | Conversion price adjusts if you later issue cheaper shares                                        | How much of you a future down round costs                                                                       | **Broad-based weighted average**, with carve-outs for ESOP, strategic issues and existing convertibles                          | Refuse full ratchet — at seed it costs ~11x broad-based (§D) and tells you how the fund expects to behave later. Refuse narrow-based. Ask for pay-to-play                                                                                                                           |
| **Option pool**                       | "A 15% pool, in the pre-money"                                                                    | A silent discount on the price you agreed                                                                       | **Sized bottom-up from a written 18-month hiring plan**; pre-money is genuine market convention                                 | Fight the **size** first — it is worth 4.5x the pre/post argument and is a fact-based argument you can win (§C)                                                                                                                                                                     |
| **Board composition**                 | Investor gets a seat, or an observer                                                              | Where day-to-day control lives                                                                                  | **Observer only** at seed; failing that, one investor director on a board that keeps a founder majority                         | A four-person board is an **even** board. Decide the tie-break — chair's casting vote or a fifth independent — in the SHA, not in the first deadlock                                                                                                                                |
| **Protective provisions**             | A list of matters needing investor consent                                                        | Where control _actually_ lives, drafted as an annexure nobody reads                                             | Rupee **materiality thresholds**; **deemed consent** after N business days; consent by **investor majority**, not each investor | You will not delete the list. Do those three things instead. Watch two rows: related-party transactions (every family-pump arrangement becomes consented) and "change in the nature of the business" (do not let your own §8.5 expansion need permission)                           |
| **Founder vesting (including reset)** | Your existing shares now vest, typically 4 years / 1-year cliff                                   | The investor is buying a team; a founder who leaves in month eight holding a third makes the company unfundable | Substantial **credit for time served**; **double-trigger** acceleration; narrowly and objectively defined "cause"               | A vague "cause" plus a bad-leaver forfeiture is the most dangerous pair of clauses in a founder document. And **do the vesting yourselves first** — imposed vesting is a family negotiation with a stranger holding the pen ([[C02-founders-agreement-and-vesting-checklist\|C02]]) |
| **Drag-along**                        | A defined majority can force everyone to sell                                                     | Prevents a small holder blocking a good exit; can also force _you_ out at a price you hate                      | Drag requires a **founder majority too**; a **minimum price floor**; limited warranties you can be dragged into                 | Negotiate the threshold and the floor. Never accept an investor-only drag with no floor                                                                                                                                                                                             |
| **Tag-along / ROFR / ROFO**           | Small holders may join a large holder's sale; company or investors get first refusal on transfers | Broadly protective of you                                                                                       | Mutual tag; ROFR with a **hard time limit**                                                                                     | An open-ended ROFR process can freeze a transfer indefinitely. Put a clock on it                                                                                                                                                                                                    |
| **Founder lock-in / non-compete**     | Founders cannot sell or compete for a period                                                      | Standard — but for VSYST it has a specific trap                                                                 | Duration and geography reasonable, and an **express carve-out for the family's existing fuel business**                         | This is a real exposure at a family-founded company. Carve it out explicitly, in the document, not by understanding                                                                                                                                                                 |
| **Information rights**                | Monthly MIS, quarterly financials, audited annuals, budget, inspection                            | All reasonable                                                                                                  | **A cadence you can actually deliver**                                                                                          | A contractual monthly MIS by the 10th from a three-person company with no finance hire is a breach waiting to be signed. Negotiate the dates, then build the machinery ([[C23-stakeholder-and-investor-update\|C23]])                                                               |
| **No-shop / exclusivity**             | You may not talk to other investors for N days                                                    | **One of the few binding parts of a term sheet**                                                                | **30 days, 45 at most**, auto-lapsing if not closed by a stated date, and not catching conversations already live               | An open-ended no-shop is how a founder with six months of runway ends up with three                                                                                                                                                                                                 |
| **Redemption / put right**            | Investor can require a buyback after N years                                                      | Debt wearing an equity costume                                                                                  | **Absent**                                                                                                                      | Refuse. A company that could fund a redemption would not have needed the money — and for a non-resident holder an assured-return right raises serious FEMA questions. **VERIFY LIVE with a FEMA lawyer**                                                                            |

**C. The ESOP pool — pre- versus post-money, worked**

Running example, used throughout: **₹3 crore at ₹12 crore pre / ₹15 crore post; investor 20%; founders 100% before.**

| Pool | Created    | Founders  | Investor | Pool  | **Founders' value at ₹15 cr** |
| ---- | ---------- | --------- | -------- | ----- | ----------------------------- |
| None | —          | **80.0%** | 20.0%    | —     | **₹12.00 cr**                 |
| 6%   | Post-money | **75.2%** | 18.8%    | 6.0%  | **₹11.28 cr**                 |
| 6%   | Pre-money  | **74.0%** | 20.0%    | 6.0%  | **₹11.10 cr**                 |
| 10%  | Post-money | **72.0%** | 18.0%    | 10.0% | **₹10.80 cr**                 |
| 10%  | Pre-money  | **70.0%** | 20.0%    | 10.0% | **₹10.50 cr**                 |
| 15%  | Post-money | **68.0%** | 17.0%    | 15.0% | **₹10.20 cr**                 |
| 15%  | Pre-money  | **65.0%** | 20.0%    | 15.0% | **₹9.75 cr**                  |

A 15% pre-money pool leaves the founders with 65% of ₹15 crore = **₹9.75 crore**, against a headline pre-money of ₹12 crore. The investor effectively bought at a **₹9.75 crore pre-money — an 18.75% discount on the number in the term sheet** — and every document still says ₹12 crore. That is the **option pool shuffle**. Now the part nobody tells you:

```
  Winning the pre/post argument at a 10% pool:   70.0% -> 72.0%   = +2.0 points
  Cutting the pool from 15% pre to 6% pre:       65.0% -> 74.0%   = +9.0 points
```

**Four and a half times the value, and it is the easier argument** — because it is an argument about your hiring plan rather than about market convention. Bring the plan as a document: _"our 18-month plan needs 6.2%; here are the eleven roles and the grants"_ beats _"15% feels like a lot"_ in every room.

**D. Anti-dilution — the two formulas, worked**

Investor bought at ₹100/share: ₹3 crore for **3,00,000 CCPS** against **15,00,000** fully diluted shares. Eighteen months later, a down round of **₹1.5 crore at ₹50/share = 3,00,000 new shares.**

```
FULL RATCHET  -- conversion price resets all the way to the new price
    New conversion price            = Rs 50
    Investor shares on conversion   = 3,00,00,000 / 50 = 6,00,000
    Extra shares created, free      = 3,00,000

BROAD-BASED WEIGHTED AVERAGE
    NCP = OCP x (A + B) / (A + C)
      OCP = old conversion price                        = Rs 100
      A   = fully diluted shares before the down round
            (INCLUDING the option pool and all
             convertibles -- this is what "broad" means) = 15,00,000
      B   = money raised / OCP = 1,50,00,000 / 100       =  1,50,000
      C   = shares actually issued in the down round     =  3,00,000

    NCP = 100 x 16,50,000 / 18,00,000                    = Rs 91.67
    Investor shares = 3,00,00,000 / 91.67                = 3,27,273
    Extra shares created                                 =   27,273
```

|                                 | Full ratchet | Broad-based WA | Narrow-based WA |
| ------------------------------- | ------------ | -------------- | --------------- |
| New conversion price            | ₹50.00       | ₹91.67         | ₹90.91          |
| Investor's shares               | 6,00,000     | 3,27,273       | 3,30,000        |
| **Extra shares taken from you** | **3,00,000** | **27,273**     | **30,000**      |

**Full ratchet costs eleven times as much**, and the multiple gets worse the smaller the down round is. "Narrow-based" excludes the option pool from **A**, which mechanically favours the investor and grows with the size of your pool. **House call: broad-based weighted average, and nothing else.**

**E. The cap table and the two-round dilution model**

`Cap Table & Dilution` tab columns: `Holder · Class (Equity / CCPS / Option) · Shares · Fully diluted % · Amount invested · Preference multiple · Participating? · Seniority rank`. Below the table, three computed lines: **founder combined %**, **founder ability to pass an ordinary resolution (>50%)**, **and to block a special resolution (>25%)** — plus a **preference overhang** line: total preference stacked ahead of the ordinary shares.

Three founders start at 100%:

| Shareholder                                  | Today      | After seed (₹3 cr @ ₹15 cr post, 10% pool pre-money) | After Series A (₹15 cr @ ₹60 cr post, pool topped to 12%, pre-money) |
| -------------------------------------------- | ---------- | ---------------------------------------------------- | -------------------------------------------------------------------- |
| **Founders (three, combined)**               | **100.0%** | **70.0%**                                            | **49.0%**                                                            |
| Seed investor                                | —          | 20.0%                                                | 14.0%                                                                |
| Series A investor                            | —          | —                                                    | 25.0%                                                                |
| ESOP pool                                    | —          | 10.0%                                                | 12.0%                                                                |
| _Founders' value at that round's post-money_ | —          | _₹10.50 cr_                                          | _₹29.40 cr_                                                          |

If the seed investor takes ₹3 crore of pro-rata in the Series A: founders 49.0%, seed 19.0%, new investors 20.0%, pool 12.0%.

| Path                                                                                         | Founders' combined holding after Series A                   |
| -------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Seed, then Series A                                                                          | **49.0%**                                                   |
| **No seed** — bootstrap to the same metrics, then raise ₹15 cr @ ₹60 cr post with a 12% pool | **63.0%**                                                   |
| Difference                                                                                   | **14 points — ₹8.4 cr at ₹60 cr, ₹14 cr at a ₹100 cr exit** |

**The honest caveat, as plainly as the number:** that comparison is only real if you would actually reach Series A metrics without the seed money. If the seed round is what got you there, the 63% column does not exist — it is 100% of nothing.

## Worked example — VSYST (illustrative)

**A plausible first term sheet, scored on the ten lines.** ₹3 crore at ₹12 crore pre, CCPS. All figures illustrative.

| #   | Term                   | As offered                               | Score   | Counter                                                           |
| --- | ---------------------- | ---------------------------------------- | ------- | ----------------------------------------------------------------- |
| 1   | Liquidation preference | **1x participating**, pari passu         | **Red** | 1x non-participating. If refused, cap participation at 2x         |
| 2   | Anti-dilution          | Broad-based WA                           | Green   | Add ESOP carve-out                                                |
| 3   | Option pool            | **15%, pre-money**                       | **Red** | 6.5%, bottom-up from eleven roles — bring the plan                |
| 4   | Board                  | 3 founders + 1 investor director         | Amber   | Ask for observer; if refused, write the tie-break into the SHA    |
| 5   | Reserved matters       | Blanket list, each investor individually | **Red** | Thresholds, deemed consent in 10 business days, investor-majority |
| 6   | Founder vesting        | Full 4-year reset, no credit             | **Red** | 3 years' credit for time served; double-trigger; narrow "cause"   |
| 7   | Drag-along             | Investor majority, no floor              | Amber   | Add founder-majority requirement and a price floor                |
| 8   | Redemption             | Absent                                   | Green   | —                                                                 |
| 9   | Information rights     | Monthly MIS by the 7th                   | Amber   | By the 20th, and quarterly for the first year                     |
| 10  | No-shop                | **75 days, no lapse**                    | **Red** | 45 days, auto-lapse if not closed                                 |

**What the counter is worth, in rupees.** Two changes carry almost all of it. Moving the pool from 15% pre to 6.5% pre takes the founders from **65.0% to 73.5%** — at a ₹15 crore post-money, **₹9.75 crore → ₹11.03 crore**, a gain of **₹1.28 crore**. Moving the preference from 1x participating to 1x non-participating is worth nothing at a ₹75 crore exit and **₹2.4 crore at a ₹15 crore exit** — and ₹15 crore is the outcome band lesson 08 §8.4 says is honest for this company. **Together, roughly ₹3.7 crore, on a deal whose headline number does not change by a rupee.**

The two reds that are not about money are the ones a family company must not concede casually. The **vesting reset with no credit** turns three brothers-in-arms into three people with a cliff, and it is far better executed voluntarily between them beforehand ([[C02-founders-agreement-and-vesting-checklist|C02]]). The **blanket reserved-matters list** means every payment to the family pump becomes a consented, disclosed item — which [[09-board-governance-and-the-directors-duties|lesson 09]] §3.4 asks you to paper anyway, so paper it before the raise rather than letting diligence do it for you.

**And the counter the founders should also run: no round at all.** At 49% after two rounds versus 63% bootstrapped, the ₹3 crore has to buy something the company genuinely cannot earn its way to. That is the trade — priced, with arithmetic on the table, by three people who wrote their conditions down before anyone flattered them ([[C29-decision-journal-and-one-way-door-log|C29]]).

## Common mistakes

| Mistake                                           | Why it happens                                      | The fix                                                                                                 |
| ------------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Negotiating valuation, accepting terms            | Valuation is the number you can repeat at a wedding | Score the ten lines. ₹12 cr clean beats ₹15 cr dirty                                                    |
| Accepting a percentage pool without a hiring plan | It sounds like a convention, not a price            | Bottom-up from eleven named roles. Worth 4.5x the pre/post fight                                        |
| Reading "weighted average" as safe                | The words sound moderate                            | Run the formula. Narrow-based is not broad-based                                                        |
| Ignoring the preference stack across rounds       | Round one felt fine                                 | Model preference overhang every round. Three rounds of stacking can exceed the whole exit               |
| Modelling economics but not control               | Percentages are what people talk about              | 50% and 25% lines, computed, every round                                                                |
| Netting the option pool out of the cap table      | It is "not real yet"                                | It dilutes exactly like an investor. Own line, always                                                   |
| Believing an iSAFE is paperwork-free              | The name says simple                                | Shares are allotted; the full private-placement machinery applies                                       |
| Planning a ₹10 lakh convertible note              | It is the US default                                | Not legal below ₹25 lakh, and only for a DPIIT-recognised start-up                                      |
| Signing a long no-shop                            | It seems procedural                                 | It is binding. 30–45 days, auto-lapse                                                                   |
| Spending money at the term sheet                  | It feels done                                       | Not raised until the credit is in the account. Rounds die at every stage after this                     |
| Using the investor's lawyer, or no lawyer         | Fees on a pre-revenue company feel absurd           | Your own lawyer, every term. It is the cheapest insurance in this document                              |
| Building the model after the term sheet lands     | There was no reason to before                       | Build it now, in the calm. File the dated version in [[C29-decision-journal-and-one-way-door-log\|C29]] |

## Related

Lessons [[08-capital-runway-and-fundraising|08]] (§10 instruments, §12 terms, §13 what changes), [[09-board-governance-and-the-directors-duties|09]], [[10-building-the-team-hiring-equity-and-firing|10]] (the pool this argues about), [[20-the-ceo-own-operating-system-and-succession|20]] (§9.3 — what an option is actually worth) · Templates [[C02-founders-agreement-and-vesting-checklist|C02]], [[C13-runway-burn-and-scenario-planner|C13]], [[C14-fundraise-readiness-and-data-room-index|C14]], [[C15-investor-narrative-and-deck-outline|C15]], [[C17-board-pack-agenda-and-minutes|C17]], [[C18-director-duties-and-governance-checklist|C18]], [[C20-compensation-bands-and-esop-design|C20]], [[C23-stakeholder-and-investor-update|C23]], [[C29-decision-journal-and-one-way-door-log|C29]] · COO [[05-legal-and-governance-foundation|COO 05]], [[T16-compliance-calendar|T16]] · [[finance/06-phase-6-loans-commission-investments-funds|Finance Phase 6]] · ESOP tax: [Treelife — ESOP taxation in India](https://treelife.in/taxation/esop-taxation-in-india/) · [[CEO-Docs/toolkit/index|CEO Toolkit]]
