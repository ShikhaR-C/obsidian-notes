# Finance for Founders — Become the CFO of Your Own Company

> Audience: me (Shikhar) — developer-founder of **VSYST Technologies Pvt. Ltd.** (Raipur), maker of **DZZLO OMS** | Where we are: **pre-revenue, bootstrapped, no business/financial model set yet** | Goal: understand my company's money end-to-end, keep the books, stay legal, build a financial model, and know when to raise vs. when to turn profitable — well enough to **act as my own CFO**. | Written & sanity-checked **2026-07-16** for an Indian Private Limited company.

## Explain-it-like-I'm-5

Your company is a **separate little person** who happens to have your face. It has its own pocket, its own money, and — by law — its own diary. **Accounting is that diary.** Every time the company-person gets money, spends money, owes money, or is owed money, one line goes in the diary. Do it honestly and neatly, and at any moment you can answer the only three questions that decide whether the company lives:

1. **What do I own, and what do I owe?** (the Balance Sheet)
2. **Am I making or losing money?** (the Profit & Loss)
3. **Do I have actual cash to survive next month?** (the Cash Flow)

A **CFO** — Chief Financial Officer — is just the person who keeps that diary honest and then *reads it to steer the company*. That's the whole job. You already think in systems and data structures; a company's finances are just another system with very strict, very old, very well-documented rules. This folder teaches you those rules from zero.

You will not become a chartered accountant, and you don't need to — **you'll still hire a CA** to file and audit (Phase 5 explains why that's legally required for you). But you'll stop being blind. You'll read your own balance sheet, catch your CA's mistakes, model your runway, price DZZLO, and talk to an investor without nodding along to words you don't understand.

## What This Folder Is

An **eleven-phase, hands-on course** that takes a developer with *no finance background* to *founder-CFO* of an Indian Private Limited startup — from "what is a debit?" to "here's my 3-year financial model and my cap table." It is written for **our actual company** (VSYST Pvt Ltd, a software product company behind DZZLO), **our actual stage** (pre-revenue, bootstrapped), and **our actual tools** (we're standardising on **ERPNext**), not a generic textbook.

Read the phases in order — each one assumes the last. Every phase ends with an exercise that produces something real: a journal entry, a chart of accounts, a balance sheet you can read, a runway number, a financial model, your books set up in ERPNext.

Two neighbouring docs already exist and this course **plugs into them instead of repeating them**:

- [[startup-operations-plan|Startup Operations Plan]] — the *business-level* money habits (pricing, advances, the weekly cash check, the realities). This finance course is the *accounting depth underneath it*.
- [[ERPNext-Implementation-Guide|ERPNext Implementation Guide]] — how to stand up ERPNext. Phase 11 here is how to *keep your books* in it.

## The One Equation That Governs Everything

On the Google Flow course it was *credits*. In accounting, it's this — memorise it, because **every entry, every ledger, every balance sheet, and every mistake is this one equation staying balanced:**

```
                 ASSETS   =   LIABILITIES   +   EQUITY
             (what you own)  (what you owe    (what's truly
                              to others)       yours / owners')
```

**ELI5:** everything the company *has* (cash, laptops, money customers owe it) had to come from somewhere — either you *borrowed* it (a liability) or the *owners put it in / the company earned it* (equity). So the two sides can never disagree. If they disagree, you made an error. That self-checking property is the whole magic of double-entry bookkeeping (Phase 1).

A 30-second worked example — you start VSYST by putting ₹5,00,000 of your own money into the company bank account:

| Event | Assets | = | Liabilities | + | Equity |
| --- | --- | --- | --- | --- | --- |
| You invest ₹5,00,000 | Bank **+5,00,000** | = | 0 | + | Share capital **+5,00,000** |
| Buy a ₹80,000 laptop (cash) | Bank −80,000, Laptop **+80,000** | = | 0 | + | (unchanged) |
| Take a ₹2,00,000 bank loan | Bank **+2,00,000** | = | Loan **+2,00,000** | + | (unchanged) |

After all three: Assets ₹7,20,000 = Liabilities ₹2,00,000 + Equity ₹5,00,000. **Balanced.** Always. That's the game.

## The Founder's Survival Law (different from the equation — this one keeps you alive)

> **Profit is an opinion; cash is a fact.**

The equation keeps your books *correct*. This law keeps your company *breathing*. You can show a "profit" on paper and still die next month because a customer hasn't paid and payroll is due. Accounting has two clocks — when a sale is *earned* (accrual, what the P&L shows) and when the cash *arrives* (what your bank shows) — and they are rarely the same day. Phase 3 explains the two clocks; Phase 7 turns this law into your weekly **runway** habit. This is already drilled in the [[startup-operations-plan|operations plan]] — here you'll learn the accounting mechanics that make it precise.

## The CFO's Toolkit (what you're actually learning to operate)

A camera doesn't make a film department, and a Tally login doesn't make a finance function. Here's the whole toolkit in 5-year-old terms and in job terms:

| The tool | ELI5 | Its job for VSYST | Taught in |
| --- | --- | --- | --- |
| **The books** (journal + ledgers) | The company's daily diary, sorted into folders | Every rupee in/out, recorded once, provably | Phases 1–2 |
| **Chart of accounts** | The labelled drawers the diary sorts into | The skeleton every number hangs on | Phase 2 |
| **Parties** (debtors/creditors) | The "who owes whom" list | Which dealer owes us, which vendor we owe | Phase 2 |
| **The 3 statements** | The company's report card | Owned/owed, profit/loss, cash — for you & investors | Phases 3–4 |
| **Schedule III + notes** | The legally-required *format* of that report card | What the govt & auditors demand you file | Phase 4 |
| **Compliance calendar** | The homework-with-deadlines list | GST, TDS, ROC, tax — miss these = fines | Phase 5 |
| **The financial model** | A spreadsheet crystal ball | Runway, pricing, "what if", the fundraise deck | Phase 9 |
| **The cap table** | Who owns how many slices of the company | Founders/investors/ESOP — before you raise | Phase 8 |
| **ERPNext** | The robot bookkeeper that does all the above | Where VSYST's real books actually live | Phase 11 |

Read that top to bottom and you've read the whole course: learn to keep the diary (1–2), turn it into a report card (3–4), stay legal (5), handle the tricky entries (6), survive on cash (7), understand ownership & raising (8), model the future & price the product (9), run the monthly CFO rhythm (10), and make ERPNext do the grunt work (11).

## Where VSYST Stands Today (and what that means for you)

Naming reality so the course stays concrete:

| Fact about us | Why it matters to the finance you need |
| --- | --- |
| **Private Limited company** (not LLP/proprietorship) | The strictest, most investor-ready form. **Statutory audit is mandatory from day one even at ₹0 revenue.** Schedule III balance sheet, ROC filings, a board — all apply. Phase 5 is non-optional homework. |
| **Pre-revenue** | Your P&L is basically all expenses; your survival metric is **runway**, not profit (Phase 7). Most "revenue" accounting waits, but you must still keep clean books *now* — investors and the taxman look back. |
| **Bootstrapped** | Money in is **founder capital** and possibly **director's loans** — and those two are *not the same thing* on the balance sheet (Phase 6 & 7). Getting this right early avoids a mess when you raise. |
| **No business/financial model yet** | This is the gap Phase 9 exists to close: how DZZLO actually makes money, what a customer is worth, and a spreadsheet that projects it. |
| **Product company** (DZZLO), possible services alongside | Changes revenue recognition, pricing, and unit economics vs. a pure agency. The [[startup-operations-plan|ops plan]] covers both models; Phase 9 does the product math. |
| **We'll use ERPNext** | Phase 11 is a hands-on ERPNext bookkeeping guide, built on the existing [[ERPNext-Implementation-Guide|implementation guide]]. |

## The Phases

| Phase | File | Level | What you'll be able to do after it |
| --- | --- | --- | --- |
| 1 | [[01-phase-1-what-accounting-is]] | Easy | Read any transaction as a balanced debit/credit entry |
| 2 | [[02-phase-2-the-books]] | Easy | Keep a journal, ledgers, a chart of accounts, and party accounts |
| 3 | [[03-phase-3-three-statements]] | Easy → Mid | Read a P&L, Balance Sheet, and Cash Flow, and see how they connect |
| 4 | [[04-phase-4-balance-sheet-in-full]] | Intermediate | Understand every line & schedule of a Schedule III balance sheet |
| 5 | [[05-phase-5-indian-accounting-system]] | Intermediate | Know every filing you owe (GST/TDS/ROC/tax) and its deadline |
| 6 | [[06-phase-6-loans-commission-investments-funds]] | Intermediate | Record loans, commission, investments, funds & assets correctly |
| 7 | [[07-phase-7-bootstrapping-runway-burn]] | Intermediate | Compute burn & runway; manage a bootstrapped company's cash |
| 8 | [[08-phase-8-fundraising-and-cap-table]] | Advanced | Read a cap table & term sheet; know equity/CCPS/SAFE; decide whether to raise |
| 9 | [[09-phase-9-business-and-financial-model]] | Advanced | Build DZZLO's business model, unit economics & a 3-year financial model |
| 10 | [[10-phase-10-pre-revenue-to-profitable]] | Advanced | Run the founder-CFO monthly rhythm; know when to flip to profit |
| 11 | [[11-phase-11-software-tally-erpnext]] | Hands-on | Keep VSYST's real books in ERPNext (and know how Tally compares) |
| — | [[12-reference]] | Reference | Every link, term, template, and source in one place |

Start with [[01-phase-1-what-accounting-is]].

## How to Use This Course

- **Do the exercises.** Reading accounting is like reading swimming. Each phase's exercise is small and produces a real artifact — a spreadsheet, an entry, a number. Keep them in a `finance-workbook/` folder.
- **One CA, from early.** This course makes you *literate and dangerous*, not a substitute for a chartered accountant. A Pvt Ltd legally needs one (Phase 5). The goal is to be the *smartest person in the room when you talk to them* — to review, question, and decide, not to file returns yourself.
- **Numbers here are illustrative.** Every ₹ figure is a teaching example, not VSYST's real books.

---

> **A note on honesty (the vault rule).** Tax rates, GST/TDS thresholds, MCA forms, and startup-scheme rules **change every Union Budget (February) and often mid-year.** Everything here was written to be correct for an Indian Pvt Ltd as of **2026-07-16**, but where a *specific number, rate, threshold, form name, or deadline* matters to a real decision, **confirm it live with your CA or the source** before you act — those are exactly the things that move. Volatile figures are flagged inline, and sources are listed in [[12-reference]]. This folder teaches you the *system*, which barely changes; the *numbers* you always verify.
