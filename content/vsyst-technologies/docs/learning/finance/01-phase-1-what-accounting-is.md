# Phase 1 — What Accounting Even Is: The Equation, Debit/Credit, and Double-Entry

> Level: Easy | Time: ~45 min | Outcome: you can take *any* real event ("bought a laptop", "a dealer paid us") and write it as a balanced two-sided entry — the atom that every ledger, balance sheet, and CFO decision is built from.

---

## 1. The First Rule: The Company Is Not You

The day VSYST Technologies was registered, a **new legal person** was born. It is not Shikhar. It has its own PAN, its own bank account, and — this is the mental leap — **its own money that is not your money.**

When you put ₹5,00,000 of your savings into VSYST's account, you did not "spend" ₹5,00,000. You *lent/gave* it to a separate person (the company), and now **the company owes you** (or you own a stake in it). This is the **Business Entity Concept**, and it is the root of everything. Accounting always records the world **from the company's point of view**, never yours.

> **Why a developer should love this:** it's just scope. Your personal finances and the company's finances are two different objects with two different memory spaces. Mixing them (paying a personal Netflix bill from the company account) is a *scope violation* — it corrupts the company's books and, in a Pvt Ltd, can pierce the legal wall that protects your personal assets. Keep the boundary clean from rupee one.

Five more concepts sit under this, and then we never belabour theory again:

| Concept | ELI5 | Consequence |
| --- | --- | --- |
| **Going concern** | Assume the company will keep living | We value a laptop at cost & depreciate it, not at "fire-sale tomorrow" price |
| **Accrual** | Record when it's *earned/owed*, not when cash moves | A sale counts the day you deliver, even if paid 45 days later (Phase 3) |
| **Consistency** | Use the same method every year | So this year's numbers compare to last year's |
| **Prudence** | Count likely losses early, likely gains only when sure | Never flatter the books; investors & tax both punish surprises |
| **Money measurement** | Only record what has a ₹ value | "Our brand is loved" isn't an entry; a ₹ trademark purchase is |

## 2. Everything Is One of Five Buckets

Every account you will ever create — for VSYST or anyone — is one of exactly **five types**. Learn these five and you've learned the nouns of the entire language.

| # | Bucket | ELI5 | Examples at VSYST | Lives on |
| --- | --- | --- | --- | --- |
| 1 | **Assets** | What the company **owns** or is owed | Bank, cash, laptops, servers, money dealers owe us | Balance Sheet |
| 2 | **Liabilities** | What the company **owes** to others | Bank loan, unpaid vendor bills, GST payable, director's loan | Balance Sheet |
| 3 | **Equity / Capital** | The owners' true stake (what's left after debts) | Share capital you invested, retained profits | Balance Sheet |
| 4 | **Income / Revenue** | Money the company **earns** | DZZLO subscriptions, setup fees, interest earned | Profit & Loss |
| 5 | **Expenses** | Money the company **spends to operate** | Salaries, AWS bills, rent, internet, CA fees | Profit & Loss |

Notice the split: buckets **1–3 are the Balance Sheet** (the company's *net worth*, a snapshot), buckets **4–5 are the Profit & Loss** (the company's *performance*, over a period). And they're tied together by our one equation, now expanded:

```
   ASSETS  =  LIABILITIES  +  EQUITY
                              └── which grows with INCOME and shrinks with EXPENSES
```

That's why a profit (income > expenses) *increases* equity, and a loss *decreases* it. The two statements are the same equation looked at two ways. Hold that thought — Phase 3 makes it concrete.

## 3. Debit & Credit — The Thing Everyone Finds Confusing (You Won't)

Here is the one place beginners panic. Forget every everyday meaning of these words. In accounting:

> **Debit just means the *left* side of an entry. Credit just means the *right* side. That's it.** They are not "good" and "bad", not "in" and "out". Left and right.

(Your bank calls a deposit a "credit" because it's talking about *its* books, where **you are a liability to the bank** — the bank owes you your deposit. From *your* company's side, cash coming in is a debit. This is the #1 source of confusion; now it's dead.)

Every account increases on one side and decreases on the other. Which side? It follows straight from the equation — the two sides of `Assets = Liabilities + Equity` increase in opposite directions:

| Bucket | Increases with a… | Decreases with a… |
| --- | --- | --- |
| **Assets** | **Debit** (left) | Credit |
| **Expenses** | **Debit** (left) | Credit |
| **Liabilities** | **Credit** (right) | Debit |
| **Equity / Capital** | **Credit** (right) | Debit |
| **Income** | **Credit** (right) | Debit |

**The mnemonic that fits it in your head — "DEA / CLI":**

- **D**ebit increases **D**rawings\*, **E**xpenses, **A**ssets
- **C**redit increases **C**apital (equity), **L**iabilities, **I**ncome

\*(*Drawings* = an owner taking money out; you'll rarely use it in a Pvt Ltd — you take a salary instead.)

## 4. The Indian "Golden Rules" (because Tally and your CA speak this dialect)

Indian bookkeeping — and Tally, which you'll meet in Phase 11 — traditionally teaches the same truth through **three golden rules**, by first sorting each account into **personal / real / nominal**. You must recognise this dialect because every Indian accountant uses it:

| Account type | What it is | The Golden Rule |
| --- | --- | --- |
| **Personal** | A person or organisation — customers, vendors, banks, the director's loan a/c | **Debit the receiver, Credit the giver** |
| **Real** | A tangible/intangible *thing* the company owns — cash, laptop, building, goodwill | **Debit what comes in, Credit what goes out** |
| **Nominal** | Expenses, incomes, gains, losses — salary, rent, interest earned | **Debit all expenses & losses, Credit all incomes & gains** |

**Both systems give the identical answer** — they're two languages for one grammar. Example: *VSYST pays ₹40,000 salary from its bank.*

- *Modern:* Salary is an **expense** → increases → **Debit** Salary ₹40,000. Bank is an **asset** → decreases → **Credit** Bank ₹40,000.
- *Golden:* Salary is **nominal**, an expense → **Debit** it. Bank is **personal** (the giver here) → **Credit** the giver.
- **Same entry:** `Debit Salary 40,000 / Credit Bank 40,000`. ✅

Use whichever clicks — most developers prefer the modern bucket rules; just be able to *follow* the golden rules when a CA speaks them.

## 5. Double-Entry: Why Every Entry Has Two Sides

Here's the invention (Venice, ~1494, Luca Pacioli — it predates the printing press by a hair and hasn't needed a patch since):

> **Every transaction affects at least two accounts, and total Debits always equal total Credits.**

Why two sides? Because *money always comes from somewhere and goes somewhere*. There is no "money appears." If cash increases, either another asset shrank, a liability grew, equity grew, or income was earned — **something on the other side must move to match.** That matching is what keeps `Assets = Liabilities + Equity` permanently balanced, and it's a built-in error detector: if your debits and credits don't tie out, you *know* you slipped, before it ever reaches a statement.

**ELI5:** it's double-entry the way a bank transfer has two legs — one account down, one account up — never one. A single-sided note ("got ₹1,000") is a shopping list, not accounting. The second side ("...*from* whom, or *for* what") is what makes it provable.

Let's watch it hold across VSYST's first week. Each row is one transaction; every row's debits = credits; the running equation never breaks:

| # | Event | Debit (left) | Credit (right) |
| --- | --- | --- | --- |
| 1 | You invest ₹5,00,000 | Bank 5,00,000 | Share Capital 5,00,000 |
| 2 | Buy laptop, ₹80,000 cash | Laptop (asset) 80,000 | Bank 80,000 |
| 3 | Take ₹2,00,000 bank loan | Bank 2,00,000 | Bank Loan 2,00,000 |
| 4 | Pay ₹40,000 salary | Salary (expense) 40,000 | Bank 40,000 |
| 5 | Earn ₹60,000 DZZLO fee (on credit — not yet paid) | Accounts Receivable 60,000 | Subscription Income 60,000 |
| 6 | Dealer pays that ₹60,000 | Bank 60,000 | Accounts Receivable 60,000 |

Read row 5 twice — it's the accrual concept in action: you recorded **income** and an **asset (a receivable — the dealer owes us)** the moment you *earned* it, with **no cash involved**. The cash shows up in row 6, clearing the receivable. Two clocks, exactly as the Founder's Survival Law warned. This single pattern — earn now, collect later — is most of what makes "profit ≠ cash".

## 6. The Shape of One Entry (a "voucher")

In the books, one transaction is recorded as a **journal entry** (in Tally/ERPNext, a **voucher**). Its skeleton — debit line(s) first, credit line(s) indented under, and a one-line "narration" explaining it:

```
Date        Account                     Debit (₹)     Credit (₹)
2026-07-16  Salary A/c ................. 40,000
                To Bank A/c ...........................  40,000
            (Being July salary paid to the developer)
```

The word **"To"** before a credit line is old Indian convention — it just marks "this is the credit side". You'll see it everywhere in Tally and in your CA's entries. Debits on top, credits (with "To") below, and they must sum equal. That's a valid entry. **You now know how to write accounting's only sentence.**

## 7. Exercises

Open a fresh spreadsheet — call it `finance-workbook/phase1.xlsx`. Columns: `# | Event | Debit account | Credit account | Amount`.

**7.1 — Bucket-sort (5 min).** Label each with its bucket (Asset / Liability / Equity / Income / Expense): *AWS bill, share capital, a dealer who owes DZZLO ₹20k, your ₹3L director's loan to the company, monthly subscription revenue, office rent, the company laptop, GST payable to govt.* (Answers you can self-check: Expense, Equity, Asset, Liability, Income, Expense, Asset, Liability.)

**7.2 — Write six entries (15 min).** For each VSYST event, write the debit account, the credit account, and confirm they're equal:
1. Pay ₹1,180 for a domain (₹1,000 + ₹180 GST — for now lump it as ₹1,180 "Internet & Domain" expense; Phase 5 splits the GST).
2. Buy a ₹1,20,000 server, paying ₹50,000 now and owing the vendor ₹70,000.
3. A dealer subscribes and pays ₹15,000 upfront into the bank.
4. Pay yourself a ₹50,000 salary.
5. The company repays ₹25,000 of its bank loan.
6. You lend the company a further ₹1,00,000 from personal savings (director's loan — a *liability*, not capital).

**7.3 — Prove the equation (10 min).** After all six, total your Assets, Liabilities, and Equity columns and confirm `A = L + E` still holds. If it doesn't, you have a one-sided entry somewhere — find it. *This is exactly the error-hunt a CFO does when a balance sheet "doesn't tie".*

**7.4 — Spot the scope violation (2 min).** Which of these corrupts the company's books, and why: (a) paying the company's AWS bill from the company card, (b) paying your personal home rent from the company account, (c) the company reimbursing you for a laptop you bought for it? (Answer: b — it's your personal expense, not the company's; it must be a drawing/loan repayment or it's a scope violation. c is fine if documented.)

---

**Next:** [[02-phase-2-the-books]] — where these entries *live*: the journal, the ledgers, the chart of accounts, and the party accounts that track who owes VSYST money.
