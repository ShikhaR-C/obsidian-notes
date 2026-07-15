# Phase 2 — The Books: Journal, Ledgers, Chart of Accounts & Parties

> Level: Easy | Time: ~1 hr | Outcome: you can take a pile of journal entries and turn them into ledgers, a chart of accounts, and a trial balance that proves the books balance — the exact pipeline ERPNext runs for you automatically (Phase 11), which you must understand before you trust it.

---

## 1. The Pipeline (this is the whole of bookkeeping)

Phase 1 taught you the atom — one balanced entry. Bookkeeping is just an assembly line that turns those atoms into statements:

```
  Event ──► JOURNAL ──► LEDGERS ──► TRIAL BALANCE ──► the 3 STATEMENTS
           (diary,     (sorted     (proof that       (Phase 3–4)
            in time    per-account  debits=credits
            order)     history)     everywhere)
```

Every accounting system on earth — a paper book, Tally, ERPNext, a Fortune-500's SAP — is this exact pipeline. **You record once (journal); the software sorts (ledger) and proves (trial balance) for free.** Understanding it means you can never be fooled by the software, and you can fix it when it's wrong.

## 2. The Journal — the diary, in time order

The **journal** (or "book of original entry", or **Day Book** in Tally) is every transaction written down **in the order it happened**, each as the two-sided entry from Phase 1. It answers *"what happened, chronologically?"*

```
Date        Particulars                    Debit (₹)     Credit (₹)
2026-07-16  Salary A/c ................... 40,000
                To Bank A/c .............................  40,000
            (Being July salary paid)
2026-07-17  Bank A/c .................... 15,000
                To Subscription Income .................  15,000
            (Being DZZLO annual plan — Ramesh Fuels)
```

That's it. The journal is complete and correct, but it's **useless for answering "how much cash do we have?"** — because cash entries are scattered across hundreds of days. For *that*, you need the ledger.

## 3. The Ledger — the same entries, re-sorted per account

A **ledger account** collects *every* entry that touched one account, in one place, so you can see its running balance. The journal is sorted by **time**; the ledger is sorted by **account**. Same data, different index — like a database table vs. an index on it.

The classic shape is the **"T-account"**: debits on the left, credits on the right. Here's VSYST's **Bank** ledger after Phase 1's six transactions:

```
                          BANK  A/C
        Debit (money in)          │        Credit (money out)
   ─────────────────────────────  │  ─────────────────────────────
   To Share Capital   5,00,000    │   By Laptop            80,000
   To Bank Loan       2,00,000    │   By Salary            40,000
   To A/c Receivable    60,000    │
   ─────────────────────────────  │  ─────────────────────────────
   Total in           7,60,000    │   Total out          1,20,000
                                   │   Balance c/d        6,40,000  ◄ what's in the bank
```

(*"By"* marks credit-side postings, the mirror of *"To"* on debits — more Indian-ledger convention.) Balance = ₹6,40,000. **This** is the number you couldn't get from the journal. Every account gets its own T: a Salary ledger, a Share Capital ledger, one ledger per dealer, etc. "Posting" = copying each journal line into the right ledger. Software does this instantly; on paper it's the tedious part (and why Tally won India).

## 4. The Chart of Accounts — the master list of drawers

Before you can post, you need the **list of accounts that exist** — the **Chart of Accounts (CoA)**. It's the labelled set of drawers everything sorts into, grouped under the five buckets from Phase 1. Get this skeleton right and your books are legible forever; get it messy and no report ever makes sense.

A sane **starter CoA for VSYST** (ERPNext & Tally both ship a default you'll adapt — don't hand-craft the whole thing, but understand it):

| Group (bucket) | Accounts under it |
| --- | --- |
| **Assets** → *Non-current* | Computers & Servers, Furniture, Intangibles (software/IP), Security Deposits |
| **Assets** → *Current* | Bank – Current A/c, Cash, **Sundry Debtors** (money owed to us), GST Input Credit, Prepaid Expenses, TDS Receivable |
| **Liabilities** → *Non-current* | Bank Term Loan, **Director's Loan** (unsecured loan from you) |
| **Liabilities** → *Current* | **Sundry Creditors** (vendors we owe), GST Payable, TDS Payable, Salaries Payable, Duties & Taxes |
| **Equity** | **Share Capital**, Securities Premium, Reserves & Surplus (retained profit/loss) |
| **Income** | Subscription Revenue, Setup/Onboarding Fees, Interest Income, Commission Income |
| **Expenses** | Salaries & Wages, Cloud/Hosting (AWS), Software Subscriptions, Rent, Internet, Legal & Professional (CA), Bank Charges, Depreciation |

> **Developer's mental model:** the CoA is your *schema*; each account is a *table*; a journal entry is a *transaction* that writes two+ rows; the ledger is a *materialised view* grouped by account; the trial balance is a *constraint check* (`SUM(debits) = SUM(credits)`). You've built this system before — it just had different names.

**Startup rule (from the [[ERPNext-Implementation-Guide|ERPNext guide]]):** accept the default India CoA, add only accounts you actually use, and let your CA refine it once. Don't gold-plate a 200-account chart for a company with 12 transactions a month.

## 5. Parties — Sundry Debtors & Sundry Creditors (the "who owes whom")

Two current-asset/liability accounts are so important they get their own sub-system, because they track **people**, not just totals:

| Term | AKA | Bucket | Means | At VSYST |
| --- | --- | --- | --- | --- |
| **Sundry Debtors** | Accounts Receivable (AR) | Asset | People who **owe us** money | Dealers billed for DZZLO but not yet paid |
| **Sundry Creditors** | Accounts Payable (AP) | Liability | People **we owe** money | AWS, your CA, a hardware vendor unpaid |

Under the single "Sundry Debtors" total sits a **subsidiary ledger** — one **party account per customer** (Ramesh Fuels, Sharma Petroleum…). So you can answer *"how much does Ramesh Fuels owe us, and since when?"* — the **ageing** question that decides who you chase. The sum of all party ledgers = the Sundry Debtors control account. Same for creditors.

> **You already built this.** DZZLO OMS *is* a party-ledger engine — "a single common ledger like a bank statement", per-customer credit limits, bill-to-bill matching. That's precisely a sundry-debtors subsidiary ledger with ageing and credit control. The accounting you're learning here is the same structure DZZLO implements for petrol-pump dealers; now you're implementing it for *VSYST itself*. Nice symmetry — and it means these concepts should feel like home.

**Bill-to-bill / bill-wise** tracking (a Tally term you'll reuse): matching each *payment* to the specific *invoice* it clears, so a party's account shows which bills are open. Essential once a customer has many invoices — and, again, exactly what DZZLO does.

## 6. Cash Book, Bank Book & the Reconciliation Habit

Two ledgers are used so constantly they're often kept as standalone "books":

- **Cash Book** — every physical-cash movement. Keep cash transactions *rare and small* (petty cash for tea, auto fare); cash is untraceable and a compliance/audit red flag if large. As a software company, VSYST should be ~99% bank, ~1% cash.
- **Bank Book** — every bank movement (your Bank ledger above).

**Bank reconciliation** (previewed here, done in Phase 11): monthly, you match your Bank *ledger* against the bank's *statement*. They differ for innocent reasons (a cheque you recorded hasn't cleared; a bank charge you didn't know about). Reconciling = finding and explaining every difference until they agree. **A CFO who doesn't reconcile monthly is flying blind** — it's how you catch fraud, double-payments, and forgotten charges. ERPNext has a **Bank Reconciliation Tool** for this.

## 7. The Trial Balance — the proof it all ties

Once everything's posted, list *every* ledger's closing balance in two columns — debit balances left, credit balances right — and total them. Because every entry had equal debits and credits (Phase 1), **the two totals must match.** That's the **Trial Balance (TB)**: the system's built-in checksum.

VSYST's TB after Phase 1's six transactions:

| Account | Debit (₹) | Credit (₹) |
| --- | --- | --- |
| Bank | 6,40,000 | |
| Laptop (asset) | 80,000 | |
| Salary (expense) | 40,000 | |
| Share Capital | | 5,00,000 |
| Bank Loan | | 2,00,000 |
| Subscription Income | | 60,000 |
| **Totals** | **7,60,000** | **7,60,000** ✅ |

Equal totals = your arithmetic is internally consistent. (It does **not** prove you booked things to the *right* accounts — you could debit Salary when it should be Rent and still balance. The TB catches *math* errors, not *judgement* errors. Judgement is what your CA and Phase 4 are for.) The TB is the launch-pad: the P&L is built from its income & expense rows, the Balance Sheet from its asset/liability/equity rows. Phase 3.

## 8. Voucher Types — the words Tally & ERPNext will ask you for

In software you rarely write a raw journal entry; you pick a **voucher type** and it writes the correct entry for you. Know the six so Phase 11 isn't alien:

| Voucher | Use it when… | Auto-entry it writes |
| --- | --- | --- |
| **Receipt** | Money comes **in** | Dr Bank / Cr (Debtor or Income) |
| **Payment** | Money goes **out** | Dr (Expense or Creditor) / Cr Bank |
| **Contra** | Moving between your *own* cash/bank | Dr Bank / Cr Cash (or vice-versa) |
| **Sales** | You invoice a customer | Dr Debtor / Cr Income (+ GST) |
| **Purchase** | A vendor invoices you | Dr Expense/Asset (+ GST) / Cr Creditor |
| **Journal** | Anything not cash/sales/purchase (depreciation, adjustments) | The manual two-sided entry |

## 9. Exercises

**9.1 — Post to ledgers (20 min).** In `finance-workbook/phase2.xlsx`, take your six entries from Phase 1's exercise 7.2 and create a T-account (or a two-column table) for **each account** they touch. Post every entry to both its accounts. Compute each ledger's closing balance.

**9.2 — Build the trial balance (10 min).** List every ledger's closing balance in a debit or credit column and total both. If they don't match, you mis-posted — hunt it down. Feel the checksum click.

**9.3 — Draft VSYST's chart of accounts (15 min).** Starting from §4's table, write the CoA *you'd actually use this quarter* — delete what you don't need, add anything real (e.g. "Figma subscription" under Software). Keep it under ~30 accounts. You'll load exactly this into ERPNext in Phase 11.

**9.4 — Party ageing (10 min).** Invent 3 dealers who owe DZZLO money, with invoice dates 20, 50, and 75 days ago. Make a tiny ageing table (`0–30 / 31–60 / 60+` days). Which one do you chase first, and what does the 60+ bucket tell you about your cash (recall the Survival Law)? This is the weekly **Accounts Receivable review** the ops plan mandates — now you know the machinery under it.

---

**Next:** [[03-phase-3-three-statements]] — turning that trial balance into the three reports every founder, bank, and investor reads: Profit & Loss, Balance Sheet, and Cash Flow.
