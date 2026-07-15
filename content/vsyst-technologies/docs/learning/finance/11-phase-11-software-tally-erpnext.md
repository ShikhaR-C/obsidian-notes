# Phase 11 — The Software: Tally vs ERPNext vs Others, and Hands-On ERPNext

> Level: Hands-on | Time: ~2 hr | Outcome: you understand the Indian accounting-software landscape, why VSYST is standardising on **ERPNext**, and how to record every transaction type from Phases 1–6 in it — then generate the three statements automatically. This turns the whole course from theory into a working set of books. Pairs with the setup-focused [[ERPNext-Implementation-Guide|ERPNext Implementation Guide]].

---

## 1. When to Graduate From Spreadsheets

Your `finance-workbook/` sheets were perfect for *learning*. But books kept in a spreadsheet don't enforce double-entry, don't compute GST, don't age receivables, and won't survive an audit. **Move to real software the moment you have real transactions** — for a Pvt Ltd needing a statutory audit from day one (Phase 5), that's basically *now*. Software gives you the Phase-2 pipeline (journal → ledger → trial balance → statements) for free, and it can't silently break the accounting equation.

## 2. The Indian Accounting-Software Landscape

| Software | What it is | Cost | Best for | Watch-out |
| --- | --- | --- | --- | --- |
| **Tally Prime** | The incumbent; on ~every Indian CA's desk | Paid licence (perpetual + renewal) | **Universality** — every accountant knows it; rock-solid statutory reports | Desktop-first, closed, dated UX, weak as a full ERP |
| **ERPNext** | Open-source **full ERP** (accounting + CRM + inventory + HR) by Frappe (Mumbai) | **Free/OSS**; hosting ~₹800–2,500/mo | **VSYST** — one system for books *and* operations, GST-native, customisable | You/your CA must learn it; fewer Tally-native accountants |
| **Zoho Books** | Polished cloud accounting, Indian company | ~₹0–2,500+/mo (free tier under a turnover limit) | Clean UX, great if you live in the Zoho suite | Per-org pricing; not a full ERP |
| **Vyapar / myBillBook** | Simple mobile billing + GST for small shops | Low | Micro-businesses, quick invoicing | Too light for a Pvt Ltd's needs |
| **Busy / Marg** | Traditional SMB accounting (North India popular) | Paid | Distribution/inventory-heavy SMBs | Similar era to Tally |
| **QuickBooks** | (Exited India in 2023) | — | — | **No longer serviced in India — don't start here** |

**The honest trade-off:** **Tally is the safe, universal choice** — hand your data to any CA and they're instantly productive. **ERPNext is the strategically better choice for VSYST** — it's free, open-source (a developer-founder's natural home), and it's *one system* for accounting **and** the operational side (CRM, invoicing, later HR), so DZZLO's business and books don't live in two disconnected tools. The [[ERPNext-Implementation-Guide|implementation guide]] already made this call; this phase is how you *use* it for the books.

## 3. Learn a Little Tally Anyway (your CA speaks it)

Even on ERPNext, spend an hour understanding Tally, because **your CA and most Indian accountants think in Tally's vocabulary** — and you already learned that vocabulary in Phases 1–2:

| Tally concept | You already know it as | Phase |
| --- | --- | --- |
| **Ledger** | An account | 2 |
| **Group** | An account group / bucket | 1–2 |
| **Voucher** (Payment/Receipt/Contra/Sales/Purchase/Journal) | The voucher types | 2 §8 |
| **Day Book** | The journal | 2 |
| **Bill-wise details** | Bill-to-bill / party ageing | 2 §5 |
| **Golden rules** (personal/real/nominal) | The golden rules | 1 §4 |

So if a CA says "pass a journal voucher and set the bill-wise reference," you know exactly what they mean. You don't need to *run* Tally; you need to *converse* in it. Everything transfers.

## 4. ERPNext ↔ The Concepts You Learned (the map)

Before the click-by-click, see how ERPNext *is* this course:

| ERPNext feature | Course concept | Phase |
| --- | --- | --- |
| **Chart of Accounts** | Chart of accounts | 2 |
| **Customer / Supplier** | Sundry debtors / creditors (parties) | 2 |
| **Sales Invoice** | Sales voucher (Dr Debtor / Cr Income + GST) | 2, 5 |
| **Purchase Invoice** | Purchase voucher | 2, 5 |
| **Payment Entry** | Receipt / Payment voucher | 2 |
| **Journal Entry** | Journal voucher (depreciation, director's loan, accruals) | 1, 6 |
| **Bank Reconciliation Tool** | Bank reconciliation | 2 §6 |
| **Asset + depreciation schedule** | PPE & depreciation (Schedule II) | 4, 6 |
| **Deferred Revenue** | Unearned/annual-prepay revenue | 6 §8, 7 |
| **Financial Statements reports** | Trial Balance, P&L, Balance Sheet, Cash Flow | 3, 4 |
| **Accounts Receivable (ageing)** | Debtor ageing | 2, 4 |

Every button maps to something you now understand. That's the point of learning the theory *first* — you're not clicking blind.

## 5. Hands-On: Recording VSYST's Transactions in ERPNext

Assuming ERPNext is set up (setup wizard, India Compliance app, company, fiscal year — all in the [[ERPNext-Implementation-Guide|implementation guide]]). Here's how each transaction type from Phases 1–6 is actually entered. *(Menu paths are approximate for v16 — the labels shift slightly by version; find via the search bar.)*

**5.1 — Chart of Accounts.** *Accounting → Chart of Accounts.* ERPNext ships an India CoA; adapt it to your Phase-2 draft (§9.3 there). Add accounts like "AWS Hosting", "Director's Loan – Shikhar", "Subscription Revenue" under the right groups. Don't over-build.

**5.2 — Create parties.** *Add a Customer* (a dealer) and *Supplier* (AWS, your CA). These become the subsidiary ledgers under Sundry Debtors/Creditors automatically.

**5.3 — Sales Invoice (billing a dealer for DZZLO).** *Accounting → Sales Invoice → New.* Pick the customer, add the DZZLO subscription item, set the GST tax template (18%). On submit, ERPNext posts `Dr Debtor / Cr Subscription Income / Cr GST Payable` — the exact entry from Phase 5, automatically. The invoice ages in Accounts Receivable.

**5.4 — Receive payment.** *Payment Entry* against that invoice (or from the invoice's "Create → Payment"). Posts `Dr Bank / Cr Debtor` and clears the invoice **bill-to-bill**. The receivable drops.

**5.5 — Purchase Invoice + payment.** *Purchase Invoice* for a vendor bill (records `Dr Expense/Asset + GST Input / Cr Creditor`); then a *Payment Entry* to pay it. Your GST input credit accumulates automatically for offset.

**5.6 — Journal Entry (the manual ones).** *Journal Entry → New* for anything that isn't sales/purchase/cash:
- **Director's loan in:** Dr Bank / Cr "Director's Loan – Shikhar" (Phase 6 §2).
- **Depreciation:** Dr Depreciation / Cr Accumulated Depreciation — though better, use ERPNext's **Asset** module which auto-computes the Schedule-II schedule (Phase 4).
- **Accruals** (outstanding/prepaid): the four adjustments from Phase 6 §8.

**5.7 — Fixed assets & depreciation.** *Assets → Asset.* Create the laptop/server as an Asset, set its category with the useful life (Schedule II), and ERPNext generates the **depreciation schedule** and posts monthly/annual depreciation entries for you — no manual math (Phase 4 §7).

**5.8 — Deferred revenue (DZZLO's annual prepay!).** On the subscription **Item**, enable **Deferred Revenue** with a deferred-revenue liability account. Now when a dealer pays ₹18,000 for a year upfront, ERPNext parks it as a **liability** and releases ₹1,500/month to income automatically — the Phase 6 §8 mechanic, done by the software. **This is the single most valuable feature for a SaaS company** — it stops you overstating revenue and keeps the two clocks honest.

**5.9 — Bank reconciliation.** *Bank Reconciliation Tool.* Import your bank statement, match transactions to entries, resolve differences (Phase 2 §6). Do this monthly — it's the keystone of your Phase-10 monthly close.

## 6. Generating the Three Statements (the payoff)

Once transactions are in, the reports you spent Phases 3–4 learning are one click each — *Accounting → Financial Statements*:

| ERPNext report | What you get | Phase |
| --- | --- | --- |
| **Trial Balance** | Every account's debit/credit balance — the checksum | 2 |
| **Profit and Loss Statement** | The P&L, any period | 3 |
| **Balance Sheet** | The Schedule III balance sheet | 3–4 |
| **Cash Flow** | Operating/investing/financing | 3 |
| **General Ledger** | Any account's full transaction history | 2 |
| **Accounts Receivable / Payable** | Party balances **with ageing** | 2, 4 |
| **GST reports** (India Compliance) | GSTR-1 / 3B data for filing | 5 |

The machine runs the entire Phase-2 pipeline instantly. **But you'll trust it, spot its errors, and configure it correctly *only because you learned the theory first.*** A founder who jumps straight to ERPNext without Phases 1–10 gets clean-looking reports they can't interpret or verify — which is worse than useless in a DD or an audit.

## 7. Setup & Migration Notes (cross-ref, not repeat)

The [[ERPNext-Implementation-Guide|ERPNext Implementation Guide]] covers install (Frappe Cloud vs Docker), the setup wizard, master data, and the *one-workflow-at-a-time* adoption sequence — follow it. Two additions from a *bookkeeping* angle:

- **Opening balances.** If VSYST already has some history (a laptop, a bank balance, your existing director's loan), enter **opening balances** as of your ERPNext go-live date via a **Journal Entry** (or the Opening Invoice tools), with your CA's help, so the balance sheet starts correct.
- **Cutover discipline.** Per the guide: pick a date, and from it **every** transaction goes through ERPNext — no parallel spreadsheet. Dual systems are where books go to die.

## 8. Exercises

**8.1 — Stand up ERPNext (60 min).** If not already running, follow the [[ERPNext-Implementation-Guide|guide]] to get a Frappe Cloud trial or local Docker instance live, with India Compliance installed and the setup wizard done for VSYST (India, April–March FY).

**8.2 — Load your chart of accounts (15 min).** Adapt the default India CoA to the Phase-2 draft you built. Add "Director's Loan", your real expense accounts, and "Subscription Revenue".

**8.3 — Record a real week (45 min).** Enter a week of actual VSYST transactions: a director's-loan top-up (Journal Entry), an AWS bill (Purchase Invoice + Payment), your salary (Journal/Payment), and — if you have one — a DZZLO Sales Invoice with GST and its Payment. Set up your laptop as an Asset and let ERPNext schedule depreciation.

**8.4 — Generate & read the statements (20 min).** Pull the **Trial Balance, P&L, Balance Sheet, and Cash Flow**. Confirm the balance sheet balances (it must — the software enforces it) and trace *one* number (e.g. your bank balance) from a transaction → General Ledger → Balance Sheet. You've now closed the loop from Phase 1's single entry to a live, audit-grade set of books.

**8.5 — Turn on deferred revenue (15 min).** Configure the DZZLO subscription item for deferred revenue, book a hypothetical ₹18,000 annual prepay, and watch ERPNext hold it as a liability and release it monthly. Reconcile this with your Phase 6 §8 exercise — same answer, now automated.

---

**Next:** [[12-reference]] — every link, term, template, and source from the whole course, in one place. And that's the CFO curriculum. From "what is a debit?" to a live set of books, a financial model, and a cap table — you can now run VSYST's finances.
