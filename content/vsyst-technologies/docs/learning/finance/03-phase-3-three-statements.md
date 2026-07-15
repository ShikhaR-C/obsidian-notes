# Phase 3 — The Three Statements and How They Interlock

> Level: Easy → Intermediate | Time: ~1 hr | Outcome: you can read a Profit & Loss, a Balance Sheet, and a Cash Flow statement, explain what each one answers, and — the part most founders miss — show how a change in one ripples through the other two.

---

## 1. Three Reports, Three Questions

Your trial balance (Phase 2) is correct but unreadable. The three **financial statements** are the human-readable reports built from it. Each answers exactly one question a founder, bank, or investor asks:

| Statement | The question it answers | Time nature | Built from (TB rows) |
| --- | --- | --- | --- |
| **Profit & Loss (P&L)** | *Are we making or losing money?* | A **period** (a movie: "the year") | Income & Expense |
| **Balance Sheet (BS)** | *What do we own and owe, right now?* | A **moment** (a photo: "31 March") | Asset, Liability, Equity |
| **Cash Flow (CF)** | *Where did the actual cash go?* | A **period** (a movie) | Movement in cash between two BS photos |

**The photo-vs-movie split is the key intuition.** The Balance Sheet is a *photo* taken on one day. The P&L and Cash Flow are *movies* of what happened *between* two photos. Two balance-sheet photos + the two movies that explain the change between them = the complete story of a year. Hold that; §5 makes it literal.

## 2. The Profit & Loss — the performance movie

The P&L (a.k.a. **Income Statement**, or "Statement of Profit and Loss" in Indian Schedule III) starts with revenue at the top and subtracts costs in layers until you reach the bottom-line profit. Each layer has a name investors will quiz you on — learn the ladder:

```
   Revenue (what DZZLO earned)                              12,00,000
 − Cost of Goods/Services Sold (COGS)                      − 2,00,000   ← cost to *deliver* (hosting, support)
 ─────────────────────────────────────────────
 = GROSS PROFIT                                             10,00,000   ← ₹ left to run the company
 − Operating Expenses (salaries, rent, tools, marketing)   − 9,00,000
 ─────────────────────────────────────────────
 = EBITDA                                                    1,00,000   ← profit before the "non-operating" stuff
 − Depreciation & Amortisation                              −  40,000   ← wearing-out of assets (Phase 4)
 ─────────────────────────────────────────────
 = EBIT / Operating Profit                                     60,000
 − Interest (on the bank loan)                              −  20,000
 ─────────────────────────────────────────────
 = Profit Before Tax (PBT)                                     40,000
 − Tax                                                      −  10,000
 ─────────────────────────────────────────────
 = PROFIT AFTER TAX (PAT) / Net Profit                         30,000   ← "the bottom line"
```

Vocabulary that pays your salary in investor meetings:

| Term | ELI5 | Why it matters |
| --- | --- | --- |
| **Gross Profit / Margin** | What's left after the cost to *deliver* the product | High-margin (SaaS ~80%+) is why investors love software vs. agencies |
| **EBITDA** | Profit ignoring accounting/finance noise (dep., interest, tax) | The rough "is the *operation* itself profitable?" number |
| **Operating vs Non-operating** | Core business vs. side effects (interest, one-offs) | Investors value the *core* engine, not lucky one-offs |
| **PAT / Net Profit** | The final money the company actually made | Flows into equity on the Balance Sheet (§5) |

**Pre-revenue reality for VSYST:** your revenue line is ~₹0, so your P&L is essentially *all expenses* → a **net loss**. That is completely normal and not a failure — it's the definition of pre-revenue. Your job right now isn't "profit"; it's "keep the loss small enough that runway lasts" (Phase 7). The P&L still matters because that accumulated loss shrinks your equity, and investors read the *shape* of your spending.

## 3. The Balance Sheet — the net-worth photo

The Balance Sheet is our Phase-1 equation, dressed up and dated. Left = what you own; right = who funded it (owed + owners'). It **must balance** — that's the name.

```
BALANCE SHEET as at 31 March 2027
─────────────────────────────────────────────────────────
ASSETS (what we own)              │  LIABILITIES + EQUITY (who funded it)
  Non-current:                    │   Equity:
    Computers & servers  1,20,000 │     Share capital        5,00,000
  Current:                        │     Reserves (retained  −1,50,000  ← accumulated losses
    Bank                 3,10,000 │       losses so far)
    Sundry debtors         80,000 │   Liabilities:
    GST input credit       15,000 │     Bank loan            1,75,000
                                  │     Director's loan        1,00,000
                                  │     Sundry creditors        50,000
─────────────────────────────────┼───────────────────────────────────
TOTAL ASSETS         5,25,000     │  TOTAL EQUITY + LIAB.    5,25,000  ✅
```

This is the *photo* on 31 March. It doesn't tell you *how* you got here (that's the two movies), only *where you stand*. Phase 4 dissects **every single line and its legally-required sub-schedule** — this is just the shape. Note the negative "Reserves": accumulated losses eat into equity, so a pre-revenue startup's equity *shrinks each year* until revenue turns it around. That erosion is your runway, drawn as a photo.

## 4. The Cash Flow Statement — the "where did the cash actually go" movie

Here's the statement founders skip and then die for skipping. The P&L can say "profit ₹30,000" while your bank *fell* by ₹2,00,000 — because the P&L runs on the **accrual clock** (records sales when earned, costs when incurred) and cash runs on the **cash clock** (records when money actually moves). The Cash Flow statement reconciles the two. It sorts every rupee of *real cash* into three bins:

| Section | ELI5 | Examples at VSYST | Healthy sign |
| --- | --- | --- | --- |
| **Operating (CFO)** | Cash from *running the business* | Subscriptions collected − salaries, AWS, rent paid | Eventually **positive** = the business self-funds |
| **Investing (CFI)** | Cash for *long-term assets* | Buying servers, laptops; (or selling them) | Negative early = you're building capacity |
| **Financing (CFF)** | Cash from *funders* | Your capital, director's loan, bank loan, later VC | Positive when raising, negative when repaying |

```
CASH FLOW — year to 31 March 2027
  Operating activities (CFO)                       − 2,60,000   ← burning cash to operate (normal pre-revenue)
  Investing activities (CFI)                       −   80,000   ← bought a server
  Financing activities (CFF)                       + 3,00,000   ← your capital + a loan
  ──────────────────────────────────────────────
  Net change in cash                               −   40,000
  Opening cash (1 Apr 2026)                          3,50,000
  Closing cash (31 Mar 2027)                         3,10,000   ← ties to the Bank line on the Balance Sheet
```

**The pre-revenue truth this exposes:** a bootstrapped startup lives on **negative CFO** (operations burn cash) funded by **positive CFF** (your money keeps the lights on). The day CFO turns positive is the day the business breathes on its own — the "transition to profitable" you asked about (Phase 10). Until then, `financing must cover the burn`, and **runway = cash ÷ monthly operating burn** (Phase 7). The Cash Flow statement is where that story is told in numbers.

> **Direct vs. indirect method** (so a term doesn't trip you): the *indirect* method starts from net profit and adds back non-cash items (like depreciation) and working-capital changes to arrive at CFO — it's what your accounting software and Indian standards produce by default. The *direct* method just lists actual cash receipts and payments. Same CFO number, two routes. You'll mostly see indirect; don't let the reconciliation table scare you — it's just "profit, un-accrual'd back into cash".

## 5. How the Three Interlock (the part that makes you dangerous)

The statements are not three separate reports — they are **three views of one system**, wired together. Three hard links, worth memorising because "do these tie?" is the first thing an investor's analyst checks:

```
   ┌─────────────────┐
   │   P&L (movie)   │   Net Profit / (Loss) ───────────┐
   └─────────────────┘                                   │ (1) flows into
                                                          ▼
   ┌─────────────────┐                          Reserves & Surplus (equity)
   │ BALANCE SHEET   │  ◄─── this year's photo         on the BALANCE SHEET
   │     (photo)     │  ◄─── last year's photo
   └─────────────────┘          │
        Cash line ◄─────────────┘ (3) equals CF's closing cash
             ▲
   ┌─────────────────┐          │ (2) explains the change between
   │  CASH FLOW      │  ◄───────┘     the two cash photos
   │    (movie)      │
   └─────────────────┘
```

1. **P&L → Balance Sheet:** net profit (or loss) for the year is added to (or subtracted from) **Reserves & Surplus** in equity. Make ₹30k profit → equity rises ₹30k. Lose ₹1.5L → equity falls ₹1.5L. This is *why* accumulated losses erode a startup's equity.
2. **Cash Flow → explains two Balance Sheets:** the CF movie explains exactly how cash went from last year's photo to this year's.
3. **Cash Flow closing cash = Balance Sheet cash:** the CF's ending cash number *is* the Bank/Cash line on the Balance Sheet. If they don't match, something's broken.

**Worked ripple — "we bought a ₹80,000 server for cash":** P&L barely moves (only ~₹40k/yr *depreciation* hits it — Phase 4); Balance Sheet: Bank −80k, Fixed Assets +80k (net asset change ₹0, still balances); Cash Flow: Investing −80k. *One event, correctly showing up differently in all three.* When you can trace an event through all three like this, you can read any company's financials — including the ones an investor hands you.

## 6. What Each Statement Is *For* (founder's cheat-sheet)

| When you want to… | Read the… |
| --- | --- |
| Pitch investors on the business engine | **P&L** (margins, growth) + unit economics (Phase 9) |
| Know if you can survive next quarter | **Cash Flow** + runway (Phase 7) |
| Apply for a bank loan / show net worth | **Balance Sheet** |
| Check if the books are even internally consistent | Do all three **tie** (§5)? |
| File with the government (MCA/tax) | All three, in **Schedule III** format (Phases 4–5) |

## 7. Exercises

**7.1 — Build a mini P&L (15 min).** In `finance-workbook/phase3.xlsx`, list VSYST's likely *monthly* expenses today (your salary, AWS, domains, tools, internet, CA retainer) and any revenue (probably ₹0–small). Compute the monthly net profit/(loss). That loss is your **monthly burn** — you'll reuse it constantly.

**7.2 — Draw the interlock (10 min).** Take one event — "you inject a ₹1,00,000 director's loan" — and write, in one line each, how it hits the **P&L** (it doesn't — it's financing, not income!), the **Balance Sheet** (Bank +1L, Director's Loan +1L), and the **Cash Flow** (Financing +1L). Prove the BS still balances. Internalise that *financing is not income* — a mistake that flatters pre-revenue founders' P&Ls.

**7.3 — Find your break-even (10 min).** Using 7.1's monthly burn, ask: *how much monthly revenue would make CFO = 0?* That number is your **operational break-even** — the headline target of Phase 10. Write it at the top of your workbook.

**7.4 — The two-clocks drill (10 min).** Invent a month where you *earn* ₹2,00,000 (all on 45-day credit) but *collect* only ₹20,000, while paying ₹1,00,000 of expenses in cash. What's the **P&L profit**? What's the **cash change**? Sit with why a "profitable" month just drained ₹80,000 from your bank. This single drill is why the Survival Law exists.

---

**Next:** [[04-phase-4-balance-sheet-in-full]] — the Balance Sheet dissected line by line in India's legally-required Schedule III format, with every schedule, note, and appendix explained.
