# Phase 6 — Loans, Commission, Investments, Funds & Assets in Practice

> Level: Intermediate | Time: ~1.5 hr | Outcome: you can pass the correct journal entry for the transactions that trip up every founder — your own money going in, bank loans and their EMIs, commission paid or earned, parking surplus cash in investments — and you understand the capital-vs-expense judgement that decides whether something lands on your Balance Sheet or your P&L.

---

## 1. The Entries That Trip Founders

Phases 1–3 gave you the grammar. This phase is the *irregular verbs* — the specific, higher-stakes transactions from your list (loans, commission, investments, funds, assets, liabilities) where a wrong entry misstates your balance sheet or costs you tax. Each section below gives the plain entry and the one gotcha.

## 2. Your Own Money In: Capital vs Director's Loan (get this right *first*)

When you put personal money into VSYST, it can enter as **one of two completely different things** — and founders who blur them create a mess that surfaces painfully at fundraising:

| | **Share Capital (equity)** | **Director's Loan (liability)** |
| --- | --- | --- |
| What it is | You *buy shares* — permanent ownership | You *lend* the company money it will repay |
| On the Balance Sheet | Equity (Shareholders' Funds) | Liability (borrowings) |
| Can you take it back? | Only by selling shares / winding up | Yes — repay anytime, no tax event |
| Interest? | No (you get dividends *if* profits) | Optional — you *may* charge interest |
| Dilution/valuation | Sets your shareholding & price | None — it's just debt |

**Rule of thumb:** money you're **never** pulling back and that defines ownership → **capital**. Money you're floating the company that you'll **recover** → **director's loan**. Most bootstrappers use a *small* share capital (say ₹1–5 L to set clean ownership) plus **director's loans** for ongoing top-ups, because loans are flexible and repayable without touching the cap table.

```
Capital:   Dr Bank 5,00,000    /  Cr Share Capital 5,00,000
Loan:      Dr Bank 1,00,000    /  Cr Director's Loan (Shikhar) 1,00,000
Repay:     Dr Director's Loan 40,000  /  Cr Bank 40,000   ← no P&L impact, just settling a liability
```

**Companies Act gotchas (Pvt Ltd):**
- A private company **can** accept loans from its directors, but the director must give a **written declaration** that the money is *their own* and **not borrowed**. Keep it on file.
- These loans are reported yearly in **DPT-3** (Phase 5) as "amounts not treated as deposits."
- If you **charge interest** to the company: the interest is an *expense* for VSYST (Dr Interest / Cr Director's Loan or Bank), the company must **deduct TDS** on it, and it's *taxable income for you personally*. Many founders charge **0%** early to keep it simple — that's allowed for a director's own-funds loan. Decide deliberately with your CA.

## 3. Bank Loans: Term Loans, Working Capital & the EMI Split

When VSYST borrows from a bank, two axes describe the loan:

| Axis | Options | Meaning |
| --- | --- | --- |
| **Secured vs Unsecured** | Secured = backed by collateral (a **charge/hypothecation** on assets, or your personal guarantee); Unsecured = no collateral, higher rate | Secured loans require filing a **charge (CHG-1)** with ROC |
| **Term vs Working Capital** | **Term loan** = fixed sum, repaid over years in EMIs; **OD/CC** (overdraft / cash credit) = a revolving limit you dip into for day-to-day cash | Term loan funds an asset; OD/CC funds working capital |

**The one thing you must get right: an EMI is two things glued together.** Each monthly EMI = **principal** (repaying the debt) + **interest** (the cost of borrowing). They're accounted *completely differently*:

- **Principal portion** → reduces the **loan liability** on the Balance Sheet (not an expense!).
- **Interest portion** → an **expense** on the P&L.

```
₹10,000 EMI = ₹7,000 principal + ₹3,000 interest:
   Dr Bank Loan A/c ........ 7,000     (liability shrinks)
   Dr Interest Expense ..... 3,000     (hits P&L)
        Cr Bank ..................... 10,000
```

Booking the whole ₹10,000 as "loan repayment" (a beginner error) understates your expenses and overstates profit; booking it all as "interest" destroys your balance sheet. The **amortisation schedule** the bank gives you lists the principal/interest split for every month — use it. Early EMIs are mostly interest; later ones mostly principal (same total).

**Year-end split (Schedule III, Phase 4):** the part of the loan due **within 12 months** is a **Current Liability** (short-term borrowings / "current maturities of long-term debt"); the rest is a **Non-current Liability**. Your CA reclassifies this at year-end — now you know why.

## 4. Commission (both directions — DZZLO could do both)

**Commission** = a fee for facilitating a transaction. Two cases:

**(a) Commission you *pay*** (e.g. a channel partner who signs up petrol-pump dealers for DZZLO):
```
   Dr Commission Expense .... 10,000
        Cr Bank / Partner A/c ....... 9,500
        Cr TDS Payable (194H) .......... 500   ← withhold TDS (~2–5%, verify), deposit by the 7th
```
Commission is a **P&L expense**; you **deduct TDS under section 194H** (Phase 5) and pay the net. This is a real design question for DZZLO's go-to-market: partner commissions are a classic SaaS distribution cost.

**(b) Commission you *earn*** (if VSYST ever earns a facilitation fee):
```
   Dr Bank / Receivable ..... 10,000
        Cr Commission Income ....... 10,000   ← P&L income
```
> **Watch the "VSYST never holds funds" principle.** DZZLO's model is that VSYST is a *software provider*, not a money-holder or payment intermediary — so your income is most cleanly a **software/subscription fee**, not "commission on transactions" (which invites payment-aggregator regulation, RBI scope, and messy accounting). Keep revenue as *service fees* unless you deliberately choose a commission model with eyes open. This is as much a *regulatory* choice as an accounting one — flag it for Phase 9's business-model work.

## 5. Investments: Parking Surplus Cash

Once you raise or earn a cushion, idle cash in a current account earns ~0%. A CFO parks it in **investments** — and how you classify them follows the Phase-4 current/non-current split:

| Type | Examples | Balance Sheet line |
| --- | --- | --- |
| **Current investments** (to hold < 12 months) | Liquid/overnight mutual funds, short FDs | Current Assets → Current Investments |
| **Non-current investments** (to hold > 12 months) | Long FDs, equity of another company, a subsidiary | Non-current Assets → Non-current Investments |

```
Buy a ₹2,00,000 fixed deposit:   Dr Fixed Deposit (Investment) 2,00,000 / Cr Bank 2,00,000
Interest earned (accrued):        Dr Accrued Interest / FD 4,000 / Cr Interest Income 4,000
Redeem FD with interest:          Dr Bank 2,04,000 / Cr FD 2,00,000 / Cr Interest Income (bal.)
```

**Valuation (AS, roughly):** current investments are carried at **lower of cost or market value** (prudence — Phase 1); long-term investments at **cost**, written down only for a *permanent* fall. Interest is usually TDS-deducted by the bank (you claim it back — it shows as **TDS Receivable**, an asset). For a **pre-revenue** company, keep this simple: a sweep-FD or liquid fund for runway you won't touch for months. Don't chase yield with runway you might need next month — that violates the Survival Law.

## 6. "Funds" — Four Different Things That Word Means

"Funds" is dangerously overloaded. Disambiguate it every time someone uses it:

| "Funds" as… | Means | Where it lives / covered in |
| --- | --- | --- |
| **Sources of funds** | Where the company's money *came from* — capital + loans | The whole Equity + Liabilities side of the Balance Sheet |
| **Reserves / earmarked funds** | Profits set aside for a purpose (a "sinking fund" to repay a loan, etc.) | Reserves & Surplus (Note 4). Rare for startups |
| **Mutual funds** | An *investment* vehicle for surplus cash | §5, Investments |
| **Raising funds / "the fund"** | Getting investor money (VC); or a VC firm itself | **[[08-phase-8-fundraising-and-cap-table]]** |

When you "need funds," be precise: do you mean *put in more of your own* (capital/loan §2), *borrow* (bank loan §3), *deploy idle cash* (investments §5), or *raise from investors* (Phase 8)? Each has completely different mechanics, cost, and consequences. Founders who say "we need funds" without picking one make bad decisions fast.

## 7. Assets vs Expenses: the Capital-vs-Revenue Judgement

The single most common *judgement* error: is a payment an **asset** (goes on the Balance Sheet, used over years) or an **expense** (hits the P&L now)?

| | **Capital expenditure (asset)** | **Revenue expenditure (expense)** |
| --- | --- | --- |
| Benefit lasts | Multiple years | This period only |
| Examples | Server, laptop, furniture, a bought patent | AWS monthly bill, salary, rent, internet |
| Accounting | Capitalise → depreciate over life (Phase 4) | Expense fully now |

**Grey zones that need a call (ask your CA):** a ₹2,000 keyboard (asset or just expense? — most set a *capitalisation threshold*, e.g. expense anything under ₹5,000). A year of software paid upfront (→ *prepaid*, §8). **Your own DZZLO development effort** — can you capitalise it as an intangible asset, or must you expense it? This is genuinely judgemental and materially changes how your pre-revenue balance sheet looks; decide it *with* your CA, consistently.

## 8. The Four Accrual Adjustments (what makes "earned ≠ paid" work)

Accrual accounting (Phase 1) needs four period-end adjustments so income/expense land in the *right period*, not the *cash* period. These are the "accrued/prepaid/outstanding/unearned" entries you'll see at every year-end:

| Situation | Plain meaning | Entry | Balance Sheet effect |
| --- | --- | --- | --- |
| **Outstanding expense** | Incurred, not yet paid (Mar salary paid in Apr) | Dr Expense / Cr Outstanding Expenses | Current liability |
| **Prepaid expense** | Paid in advance (annual insurance) | Dr Prepaid Expense / Cr Bank | Current asset |
| **Accrued income** | Earned, not yet received (interest due) | Dr Accrued Income / Cr Income | Current asset |
| **Income received in advance** | Received, not yet earned (**annual DZZLO fee paid upfront!**) | Dr Bank / Cr Income Received in Advance | Current liability |

> **The one that matters most for DZZLO: unearned revenue.** If a dealer pays ₹12,000 for a *year* of DZZLO upfront, you have **not** earned ₹12,000 today — you've earned ₹1,000 and *owe* the customer 11 more months of service. So ₹11,000 sits as a **liability** ("Income Received in Advance" / deferred revenue) and moves to income ₹1,000/month. This is fundamental to SaaS accounting and to *not* overstating your revenue. Phase 9 builds pricing on top of this; Phase 11 shows ERPNext's deferred-revenue feature.

## 9. Provisions vs Liabilities vs Contingent (a precise trio)

Three words that sound alike and aren't:

- **Liability** — you owe a *known* amount to a *known* party (a ₹50,000 vendor bill). Recorded.
- **Provision** — you owe something *probable* but the *amount is estimated* (provision for a bonus, for doubtful debts, for tax). Recorded, as a best estimate (prudence).
- **Contingent liability** — a *possible* obligation depending on a future event (a lawsuit). **Not recorded — only disclosed** in the notes (Phase 4 §9).

The line between "provision" (book it) and "contingent" (just disclose) is a judgement about *probability* — another CA conversation, and another thing investors scrutinise.

## 10. Exercises

**10.1 — Split an EMI (10 min).** Your ₹2,00,000 bank loan has a ₹9,500 monthly EMI; month 1's interest is ₹1,800. Write the full journal entry splitting principal and interest, and state the new loan balance. Then say which part of the remaining loan is a *current* vs *non-current* liability if ₹80,000 is due within 12 months.

**10.2 — Capital or loan? (5 min).** You're about to move ₹3,00,000 of personal savings into VSYST to cover 4 months of burn, expecting to recover it once you raise. Capital or director's loan? Write the entry and one sentence on why — then note the Companies Act declaration and DPT-3 obligation that come with your choice.

**10.3 — The DZZLO unearned-revenue drill (15 min).** A dealer pays ₹18,000 for an annual DZZLO plan on 1 Jan. Write the entry on 1 Jan, and the entry at 31 Jan. How much is *income* in the year to 31 Mar, and how much is still a *liability*? This is the exact mechanic that stops SaaS founders from lying to themselves about revenue.

**10.4 — Asset or expense? (10 min).** Classify each and write the entry: (a) a ₹75,000 server, (b) a ₹1,499 Figma monthly sub, (c) ₹24,000 for a 1-year domain+hosting paid upfront, (d) ₹3,000 for a keyboard. For any grey one, write the question you'd ask your CA and the threshold rule you'd set.

---

**Next:** [[07-phase-7-bootstrapping-runway-burn]] — how a bootstrapped, pre-revenue company actually manages money: burn, runway, and the cash discipline that keeps VSYST alive long enough to find its model.
