# Phase 8 — Fundraising & the Cap Table

> Level: Advanced | Time: ~1.5 hr | Outcome: you can read and build a cap table, do the dilution math in your head, tell CCPS from a SAFE from a convertible note, decode the dangerous lines in a term sheet, and — most importantly — decide *whether* raising is even right for VSYST. This is the phase that stops a founder from signing away control they didn't understand they were giving.

---

## 1. What "Raising" Actually Is

Fundraising = **selling a slice of ownership in VSYST for cash**. An investor wires money; in return they get **shares** (a permanent claim on the company's future) plus, usually, some **control rights**. Reframe it precisely, because the romance ("we raised ₹5 crore!") hides the trade:

> You are **selling part of the company forever** to buy **time and speed now**. It is the **most expensive money there is** — you repay it not in rupees but in ownership and control, potentially worth vastly more later. Sometimes that trade is brilliant. Often, for a company that hasn't found its model, it's a mistake. Phase 7 §8 is the "should you even?" gate; this phase is the "how, if you do."

## 2. The Cap Table — Who Owns the Company

A **capitalisation table ("cap table")** is simply the list of who owns what. At birth, VSYST's is trivial:

| Shareholder | Shares | % |
| --- | --- | --- |
| Shikhar | 40,000 | 40% |
| Paresh | 40,000 | 40% |
| Shikha | 20,000 | 20% |
| **Total** | **100,000** | **100%** |

That's it — a cap table is just this table, kept accurate through every share issuance forever. **"Fully diluted"** means counting *all* shares that *could* exist — including the ESOP pool and anything convertible — not just those issued today. Investors always negotiate on the fully-diluted number, so you must too. This table *is* Note 3 of your balance sheet (Phase 4 §5) in founder-facing form.

> **Do this before you ever raise:** get your cap table clean, put **founder vesting** on it (4-year vesting, 1-year cliff — the ops plan's #1-killer point), and record it properly. A messy pre-round cap table (unclear splits, no vesting, undocumented "advisor gave 5%") kills or re-prices deals in due diligence.

## 3. Dilution & Valuation — The One Piece of Math That Matters

When you raise, the company **issues new shares** to the investor. Everyone's *number* of shares stays the same, but everyone's *percentage* drops — that's **dilution**. The math hangs on two words:

- **Pre-money valuation** = what the company is agreed to be worth *before* the money goes in.
- **Post-money valuation** = pre-money **+** the new investment.
- **Investor's % = investment ÷ post-money.**

**Worked example — VSYST raises ₹1 crore at ₹4 crore pre-money:**

```
  Pre-money           ₹4,00,00,000
  + Investment        ₹1,00,00,000
  ─────────────────────────────────
  Post-money          ₹5,00,00,000
  Investor's stake  = 1cr / 5cr  =  20%
  Founders go from 100%  →  80%   (diluted by the new 20%)
```

New cap table:

| Shareholder | Before | After (diluted) |
| --- | --- | --- |
| Founders (all three) | 100% | **80%** |
| New Investor | — | **20%** |

**The ESOP-pool trick you must catch:** investors usually require an **employee option pool** (say 10%) be created *before* the round — meaning it comes out of the **pre-money**, diluting *founders*, not the investor. "₹4 cr pre-money with a 10% post-money option pool" quietly costs founders more than it looks. Always ask: *is the pool in the pre- or post-money?* This single question is worth lakhs.

**How is a pre-revenue company even valued?** Not by DCF or profit multiples (you have none). Early valuation is **negotiation dressed as analysis** — driven by team, traction, market size, comparable deals, and how badly the investor wants in. That's exactly why raising *before* you have traction gets you a low valuation and heavy dilution: you're negotiating from weakness. Traction (Phase 9) is what moves the number.

## 4. The Instruments — What You Actually Issue

You can take investment through several vehicles. The four that matter in India:

| Instrument | What it is | When used | Key feature |
| --- | --- | --- | --- |
| **Equity shares** | Straight ownership, priced now | Priced rounds (Series A+) | Simplest; requires agreeing a valuation *now* |
| **CCPS** | **Compulsorily Convertible Preference Shares** | **The Indian VC standard** | Converts to equity later; carries **liquidation preference** + rights. FEMA-friendly (compulsorily convertible) |
| **CCDs** | Compulsorily Convertible Debentures | Debt that must convert to equity | Debt-like until conversion |
| **SAFE / iSAFE** | **Simple Agreement for Future Equity** | Angel/pre-seed, *defer* valuation | Not priced now — converts at the *next* round, with a **cap** and/or **discount**. India's **iSAFE** (by 100X.VC) uses CCPS mechanics because Indian law has no native SAFE |

**Why CCPS dominates Indian venture deals:** it lets the investor be an *owner* (converts to equity on the upside) *and* a *creditor-ish preferred holder* (gets money back first on a downside exit, via liquidation preference). "Compulsorily convertible" is required so foreign investors comply with **FEMA** (RBI rules disallow assured-return/optionally-redeemable instruments for FDI). If you raise from a VC, you'll almost certainly issue **CCPS** — learn to read its terms.

**Why SAFE/iSAFE for the earliest cheques:** at pre-seed, nobody can agree a fair valuation, so you *defer* it. The angel gives ₹25 L now; it converts to shares at your *next priced round*, rewarded with a **discount** (e.g. 20% off that round's price) and/or a **valuation cap** (a ceiling price protecting them if you moon). Fast, cheap, few lawyers. India's iSAFE is the localised version.

## 5. Reading a Term Sheet — the Lines That Bite

A **term sheet** is the (mostly non-binding) summary of the deal, before the long legal docs. Most numbers are fine; a few clauses can quietly cost you the company. The ones to understand cold:

| Term | What it means | Founder-friendly | Dangerous version |
| --- | --- | --- | --- |
| **Liquidation preference** | Who gets paid first on exit, and how much | **1× non-participating** (they get their money back *or* convert, not both) | **Participating** ("double dip") or **>1×** — they take money back *and* their % |
| **Anti-dilution** | Protects investor if you later raise at a *lower* price (down round) | **Broad-based weighted average** | **Full ratchet** — brutally re-prices their shares, crushing founders |
| **Option pool** | ESOP set-aside | Post-money (shared dilution) | Pre-money (founders eat it all — §3) |
| **Board composition** | Who controls decisions | You keep control early | Investor majority board at seed = you lost the company |
| **Pro-rata rights** | Investor can maintain % in future rounds | Standard, fine | — |
| **Drag-along / tag-along** | Rules forcing/allowing sale participation | Standard | Overly broad drag |
| **Vesting** | Founders earn shares over time | 4 yr / 1 yr cliff — expected | — |
| **Liquidation pref. + control together** | — | — | The combo that lets investors make money even if *you* don't. Watch it |

> **The founder's rule:** **valuation is the number everyone brags about; the *terms* are what actually determine who gets rich.** A high valuation with participating 2× preference and a full ratchet can be worse than a lower valuation with clean 1× non-participating terms. Get a **startup-experienced lawyer** to read the term sheet — this is the one place penny-pinching on legal advice can cost you everything. Your job is to understand it well enough to *argue*.

## 6. ESOP — Paying People in Ownership

**ESOP** (Employee Stock Option Plan) = giving employees the *right to buy* shares later at a fixed (low) price, so they share in the upside. Startups use it to hire above-cash talent. Mechanics:

- You carve out a **pool** (e.g. 10% of the company) — this **dilutes founders** when created (§3).
- Options **vest** over time (typically 4 yrs, 1-yr cliff) — quit early, keep less. Same logic as founder vesting.
- Employees **exercise** (buy) on a liquidity event or per plan rules.

Even bootstrapped, set up a small ESOP pool early if you'll hire — it's a powerful, cash-free retention tool, and investors expect one. But every % you give is real dilution; budget it deliberately.

## 7. The Funding Ladder & India's Players

Money comes in stages, each with different sources and expectations:

| Stage | Typical source (India) | What they fund |
| --- | --- | --- |
| **Bootstrap / FFF** | You, friends, family | Getting to a prototype/first customers (VSYST is here) |
| **Pre-seed / Angel** | Angels, angel networks (IAN, Mumbai Angels), iSAFE cheques | First traction, small team |
| **Seed** | Seed funds, micro-VCs (100X, Blume, etc.) | Proven model → scale go-to-market |
| **Series A+** | VCs | Pouring fuel on a working engine |

Each round expects the *previous* stage's milestones to be *done*. Angels fund "there's a real early signal"; Series A funds "the model works, now scale it." **Raising out of order (Series-A ambitions with pre-seed traction) just means a bad valuation or a no.**

## 8. Due Diligence — Why Clean Books (Phases 1–6) Pay Off Here

Before wiring money, investors **audit you** — financial, legal, and technical. They'll want: clean **books & cap table**, your **compliance status** (all the Phase-5 filings done), **contingent liabilities** (Phase 4 §9), founder vesting, IP ownership (does the company own DZZLO's code?), and material contracts. **Everything you built in Phases 1–6 is what makes this survivable.** Founders who ignored bookkeeping "until we raise" discover in DD that messy books *lower their valuation or kill the deal*. Clean books are a fundraising *asset*, not just compliance.

## 9. India-Specific Fundraising Facts

| Fact | Why it matters |
| --- | --- |
| **Angel tax abolished** (Sec 56(2)(viib), from AY 2025-26, all investors) | The historic tax on share premium above "fair value" is **gone** — a major headache removed (Phase 5 §8) |
| **Valuation report required** | Issuing shares needs a **registered valuer** / merchant-banker valuation (Rule 11UA for tax; FEMA pricing for foreign investors) — your CA arranges it |
| **FEMA / FDI** for foreign investors | Software is under the **100% automatic route**, but foreign investment requires **FC-GPR** filing with RBI and pricing-guideline compliance |
| **DPIIT recognition** | Eases angel-tax scrutiny historically, and signals legitimacy | 
| **Instrument = usually CCPS** | See §4 — FEMA compliance drives this |

*(All of these are exactly the numbers/rules the honesty note warns move — confirm current position with your CA before a round.)*

## 10. So — Should VSYST Raise? (the honest gate)

Recall Phase 7 §8: raise only when you have a **proven model**, money is the **only** constraint, and **speed matters**. Right now VSYST is **pre-revenue with no set model** — which means:

- You'd raise at a **low valuation** (no traction to justify more) → **give away a big % for little money**.
- You'd be raising to *discover* a model — investors rightly hate funding that, and it's the worst reason to dilute.
- **Better sequence:** use Phase 9 to find and prove DZZLO's model on bootstrap/customer cash (Phase 7), get real traction, *then* raise — from strength, at a valuation that costs you far less ownership.

The most valuable fundraising skill is knowing **when not to**. For now, treat this phase as *literacy you'll need later*, and put your energy into Phase 9.

## 11. Exercises

**11.1 — Build VSYST's real cap table (15 min).** In `finance-workbook/phase8-captable.xlsx`, enter the actual founder split and share counts. Add a "fully diluted" column with a hypothetical 10% ESOP pool. Note whether founder vesting exists — if not, that's an action item.

**11.2 — Model a dilution round (20 min).** Add a row: raise ₹1 cr at ₹4 cr pre-money. Compute post-money, the investor's %, and every founder's *new* %. Then redo it forcing a 10% option pool into the *pre-money* and watch the founders' % drop further. Feel the "pool shuffle."

**11.3 — Term-sheet red-flag hunt (10 min).** Write, in your own words, what these do and whether you'd accept them: *2× participating liquidation preference; full-ratchet anti-dilution; investor-majority board at seed.* For each, note your counter-ask. This is the muscle that protects the company.

**11.4 — Write your "raise / don't raise" memo (10 min).** Five lines: given VSYST's stage, should you raise now? What would need to be true first (from §10 and Phase 7 §8)? What's your target milestone before even taking a meeting? Decide it on paper, calmly, now — not in a room with a persuasive investor later.

---

**Next:** [[09-phase-9-business-and-financial-model]] — the gap you named: how DZZLO actually makes money, what a customer is worth, and a 3-year financial model — the work that must come *before* any raise.
