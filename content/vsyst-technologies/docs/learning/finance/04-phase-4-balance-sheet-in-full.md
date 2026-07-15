# Phase 4 — The Balance Sheet in Full: Schedule III, Every Note & Appendix

> Level: Intermediate | Time: ~1.5 hr | Outcome: you can read any Indian company's Balance Sheet line by line, understand *why* the format is fixed by law, and know what every "Note to Accounts" (the schedules/appendices) contains — including the depreciation schedule, ageing tables, contingent liabilities, and the newer regulatory disclosures. This is the phase that lets you review your CA's work instead of rubber-stamping it.

---

## 1. The Format Isn't Your Choice — It's the Law

In Phase 3 you saw a Balance Sheet in a friendly shape. The *real* one VSYST files is not freestyle: its exact format is dictated by **Schedule III of the Companies Act, 2013**. Every Indian company's balance sheet looks the same because they're all obeying the same schedule — which is *good* for you: learn it once, read every company's forever.

Schedule III has two "Divisions":

| Division | For companies following… | Applies to VSYST? |
| --- | --- | --- |
| **Division I** | **Accounting Standards (AS)** — smaller/unlisted companies | **Yes** — this is you (Phase 5 explains AS vs Ind AS) |
| Division II | **Ind AS** — listed & large companies (net worth ≥ ₹250 cr, etc.) | Not yet; maybe never |

Everything below is **Division I**, the format VSYST actually files. Two structural rules first:

- The Balance Sheet is **"vertical"**: Equity & Liabilities on top, Assets below (not the side-by-side T of Phase 3 — that was for teaching).
- Everything splits into **Non-current** (life > 12 months) vs **Current** (within 12 months). This split is the spine of the whole statement — a lender's first question is "how much do you owe *this year* vs *later*?"

## 2. The Balance Sheet Skeleton (memorise this table of contents)

```
BALANCE SHEET as at 31 March ____                          Note   ₹ this yr   ₹ last yr
══════════════════════════════════════════════════════════════════════════════════════
I. EQUITY AND LIABILITIES
  1. Shareholders' Funds
       (a) Share Capital ....................................  3
       (b) Reserves & Surplus ...............................  4
       (c) Money received against share warrants
  2. Share Application Money Pending Allotment
  3. Non-Current Liabilities
       (a) Long-Term Borrowings .............................  5
       (b) Deferred Tax Liabilities (net)
       (c) Other Long-Term Liabilities
       (d) Long-Term Provisions .............................  6
  4. Current Liabilities
       (a) Short-Term Borrowings
       (b) Trade Payables ...................................  7
       (c) Other Current Liabilities ........................  8
       (d) Short-Term Provisions ............................  9
                                                             ─────────────────────────
                                                    TOTAL   (must equal Assets total)
II. ASSETS
  1. Non-Current Assets
       (a) Property, Plant & Equipment (PPE) ................ 10
             (i) Tangible assets / (ii) Intangible assets
             (iii) Capital Work-in-Progress (CWIP)
             (iv) Intangible assets under development
       (b) Non-Current Investments .......................... 11
       (c) Deferred Tax Assets (net)
       (d) Long-Term Loans & Advances ....................... 12
       (e) Other Non-Current Assets
  2. Current Assets
       (a) Current Investments
       (b) Inventories ...................................... 13
       (c) Trade Receivables ................................ 14
       (d) Cash & Cash Equivalents .......................... 15
       (e) Short-Term Loans & Advances ...................... 16
       (f) Other Current Assets
                                                             ─────────────────────────
                                                    TOTAL   (must equal Equity+Liab.)
```

Every dotted line ends in a **Note number**. That's the crucial idea of §3.

## 3. The Balance Sheet Is a Table of Contents; the Notes Are the Book

The face of the Balance Sheet shows only **one summary number per line**. All the *detail* — the "appendixes" you asked about — lives in the **Notes to Accounts** (also called **Schedules** or **Notes forming part of the financial statements**). Line "(a) Share Capital … Note 3 … ₹5,00,000" means *"the number is 5 lakh; the full story is in Note 3."*

> **Developer's model:** the Balance Sheet is an API response with summary fields; each Note is the *expanded object* you get by following the `note_id`. The financial statements you file = Balance Sheet + P&L + Cash Flow + **Notes**, and the Notes are usually 80% of the page count. "Reading a balance sheet properly" *means reading the notes*. Amateurs read the face; a CFO reads the notes.

The rest of this phase walks the notes that matter, in filing order.

## 4. Notes 1–2 — Corporate Info & Significant Accounting Policies

- **Note 1 — Corporate Information:** one paragraph: who VSYST is, where incorporated (Raipur), what it does (DZZLO OMS software). Boilerplate, but investors read it first.
- **Note 2 — Significant Accounting Policies:** the *rules VSYST chose* where standards allow a choice — basis of accounting (accrual), depreciation method (SLM or WDV — §7), revenue recognition (when a subscription is "earned"), how you value investments, etc. **This note is where a company can flatter itself**, so a sharp reader checks it first. Consistency (Phase 1) means you can't change these year to year without disclosing it.

## 5. Note 3 — Share Capital (the ownership note — critical before you raise)

The single most important note for a founder, because it's *who owns the company*. It has a strict internal ladder:

| Layer | Means | VSYST example |
| --- | --- | --- |
| **Authorised capital** | The ceiling you're *allowed* to issue (set in your MoA; raising it costs an ROC fee) | ₹10,00,000 (1,00,000 shares × ₹10) |
| **Issued capital** | What you've actually *offered* | ₹5,00,000 |
| **Subscribed & Paid-up capital** | What shareholders took and *paid for* | ₹5,00,000 (50,000 shares × ₹10) |

**Face value / par value** = the ₹10 (or ₹1) printed value per share — *not* the price an investor pays (Phase 8: investors pay a **premium** over face value, and that premium goes to a separate "Securities Premium" reserve, not here). The note must also disclose, by law:

- A **reconciliation** of shares outstanding at the start vs end of year (issued any new ones?).
- **Rights, preferences & restrictions** attached to each class (equity vs preference shares).
- Every shareholder holding **> 5%**, with their %.
- **Shareholding of promoters** and any change during the year (a 2021 addition).

This note *is* your cap table in legal form — Phase 8 builds the founder-facing version.

## 6. Note 4 — Reserves & Surplus (where profit/loss accumulates)

The other half of "Shareholders' Funds". Main components for a startup:

- **Securities Premium** — the amount investors paid *above* face value (huge after a funding round; ₹0 while bootstrapped).
- **Surplus / (Deficit) in Statement of P&L** — the running total of every year's net profit or loss. This is the link from Phase 3: each year's PAT lands here. **For pre-revenue VSYST this is negative and growing** (accumulated losses), which is why total equity shrinks until revenue turns it. A large negative balance here is normal for a young startup and *expected* by investors — but a lender hates it.

## 7. Note 10 — PPE & the Depreciation Schedule (the classic "appendix")

**Property, Plant & Equipment** (old name: Fixed Assets) gets the most detailed note of all — the famous **depreciation schedule**, a grid of *gross block → depreciation → net block*:

```
                    │  GROSS BLOCK (cost)          │ DEPRECIATION              │ NET BLOCK
Asset               │ Open   +Add  −Sold  Close    │ Open  +Yr  Close          │ Close  (last yr)
────────────────────┼──────────────────────────────┼───────────────────────────┼─────────────────
Computers & servers │ 0     1,20k    0   1,20,000   │  0    40k   40,000        │ 80,000    —
Furniture           │ 0      30k     0     30,000   │  0     3k    3,000        │ 27,000    —
────────────────────┼──────────────────────────────┼───────────────────────────┼─────────────────
TOTAL               │              1,50,000         │             43,000        │ 1,07,000
```

Read left to right: what it *cost* (gross block), how much has *worn out* so far (accumulated depreciation), what it's *worth on the books now* (net block = gross − accumulated). The net block figure is what appears on the face of the Balance Sheet.

**Depreciation** = spreading an asset's cost over its useful life instead of expensing it all in year one (Phase 1's *matching* — the server helps earn revenue for years, so its cost is charged over those years). Two things govern it in India:

| Question | Answer |
| --- | --- |
| *How long does each asset "live"?* | **Schedule II of the Companies Act** prescribes useful lives — e.g. **computers ~3 yrs, servers ~6 yrs, furniture ~10 yrs, office equipment ~5 yrs.** (*Verify current Schedule II lives — they're occasionally revised.*) |
| *Straight-line or reducing-balance?* | **SLM** (Straight-Line — equal each year) or **WDV** (Written-Down Value — more early, less later). You pick in Note 2 and stay consistent. Tax uses WDV by block; your books can use either. |

> **Two depreciations, don't confuse them:** your *books* depreciate per Companies Act Schedule II; the *Income Tax Act* has its *own* depreciation rates and the **block-of-assets** WDV method. They differ on purpose, which creates **deferred tax** (that mysterious Balance Sheet line) — a Phase-5/CA topic; just know the two systems exist and don't reconcile by design.

**Intangibles** (DZZLO's own software/IP, patents, trademarks) sit here too but get **amortised** (same idea, different word for non-physical). Whether you can even *capitalise* your own software development (vs expensing it) is a genuine judgement call — **ask your CA**, because it materially changes how your pre-revenue balance sheet looks to investors.

## 8. Notes 7 & 14 — Trade Payables & Receivables (now with mandatory ageing)

- **Note 7 — Trade Payables** (your Sundry Creditors from Phase 2): who VSYST owes. Since 2021, must include an **ageing schedule** (outstanding for < 1 yr / 1–2 / 2–3 / > 3 yrs) **and** split **MSME vs non-MSME** dues — because India legally protects micro & small suppliers (you must pay them within 45 days or disclose it, under the MSMED Act).
- **Note 14 — Trade Receivables** (Sundry Debtors): who owes VSYST, with the same **ageing schedule** and a split of "considered good / doubtful". This is your Phase-2 ageing table, now a legal disclosure. The 60+ column you learned to chase is the one auditors and investors zoom into — it signals collection risk.

## 9. The Off-Balance-Sheet Note — Contingent Liabilities & Commitments

A note with **no number on the face of the balance sheet**, because these aren't liabilities *yet* — they're *maybe* liabilities:

- **Contingent liability** = a possible obligation depending on a future event — a lawsuit you might lose, a guarantee you gave, a disputed tax demand. Not recorded as a liability (prudence says disclose, not book, until likely), but **must be disclosed** so readers see the risk lurking.
- **Commitments** = things you've *committed* to spend but haven't yet — e.g. a signed contract to buy ₹5L of servers next quarter.

**Why a founder must know this:** in due diligence (Phase 8), investors hunt this note hardest — an undisclosed lawsuit or guarantee here can kill a deal. Never hide one; disclose cleanly.

## 10. The Newer Regulatory "Appendices" (2021 Schedule III amendments)

The MCA bolted on a batch of extra disclosures (effective FY 2021–22) — the "additional regulatory information". Most are one-line "No" statements for a clean small startup, but you must *know they exist* because your CA will ask you to confirm each:

| Disclosure | What it asks | Typical VSYST answer |
| --- | --- | --- |
| **Promoter shareholding** | % held by promoters + year change | Founders' % (real content for you) |
| **Ageing schedules** | Receivables, payables, CWIP, loans (§8) | Real content once you have parties |
| **Title deeds of immovable property** | Any property not in company's name? | N/A (you rent) |
| **Loans to promoters/directors/related parties** | Any, and are they repayable on demand? | Your director's loan direction matters (Phase 6) |
| **Wilful defaulter / struck-off companies / Benami** | Declarations | "No" |
| **Registration of charges with ROC** | Any pending? | "No" unless you took a secured loan |
| **Utilisation of borrowed funds / share premium** | Did money go where you said? | Real once you raise |
| **Undisclosed income, crypto/virtual currency, CSR** | Declarations | "Nil" / "Not applicable" (CSR applies only to large cos) |
| **Financial ratios** | 11 prescribed ratios + explain >25% swings | §11 |

Don't be intimidated — for a tiny pre-revenue company, 80% of these are "No / Nil / Not applicable". But an investor's lawyer reads every one, so answer honestly.

## 11. The Ratios Appendix (the 11 that must be disclosed)

Schedule III now requires these ratios in the notes, with an explanation for any that moved > 25% year-on-year. They double as the health metrics you'll track anyway (Phase 10):

| Ratio | Rough meaning | Founder's read |
| --- | --- | --- |
| **Current ratio** | Current assets ÷ current liabilities | > 1 = can cover this year's dues; liquidity |
| **Debt-Equity** | Borrowings ÷ equity | How leveraged; high = risky |
| **Debt Service Coverage** | Can profits cover loan repayments? | Lenders live here |
| **Return on Equity (ROE)** | Profit ÷ equity | Owner's return |
| **Inventory / Debtors / Creditors turnover** | How fast stock/receivables/payables cycle | Working-capital efficiency |
| **Net profit ratio** | Net profit ÷ revenue | Margin |
| **Return on Capital Employed (ROCE)** | Operating profit ÷ capital employed | Core efficiency |
| **Return on Investment** | Return on invested funds | For your investments |

## 12. What VSYST's Balance Sheet Actually Looks Like Today

Reassuring reality-check for a **pre-revenue, bootstrapped** company:

- **Equity:** Share Capital (your investment) minus a *growing accumulated loss* in Reserves. Total equity is small and shrinking. Normal.
- **Liabilities:** maybe a **director's loan** (you), maybe a small bank loan, a few unpaid vendor bills. Little else.
- **Assets:** mostly **Bank/Cash** (your runway), a couple of laptops/servers under PPE, perhaps GST input credit and a security deposit. Trade receivables ≈ ₹0 until you bill customers.
- **Half the notes read "Nil / Not applicable."** That's fine — the *structure* is what you're learning; the content fills in as VSYST grows.

The one line to watch obsessively: **Cash & Cash Equivalents (Note 15)** ÷ monthly burn = your runway. Everything else is bookkeeping; that ratio is survival (Phase 7).

## 13. Exercises

**13.1 — Map your trial balance to Schedule III (20 min).** Take Phase 2's trial balance and slot every account into the correct Schedule III line from §2. Notice which lines are empty. You've just drafted VSYST's first real-format balance sheet.

**13.2 — Build a depreciation schedule (15 min).** In `finance-workbook/phase4.xlsx`, list VSYST's actual assets (laptops, any server, furniture). Assign each a Schedule II useful life, pick SLM, and compute year-1 depreciation and net block. This is Note 10, and it's the entry you'll pass every year-end (Phase 6).

**13.3 — Write your contingent-liabilities note (5 min).** List any guarantees, disputes, or signed-but-unpaid commitments VSYST has (probably none — write "Nil"). Get in the habit; this is the note that ambushes founders in due diligence.

**13.4 — Self-audit the appendices (10 min).** Go down §10's table and write VSYST's honest one-line answer to each. Flag any that aren't a clean "No" for a conversation with your CA. You're now doing exactly what a CFO does at year-end close.

---

**Next:** [[05-phase-5-indian-accounting-system]] — the compliance machine around these statements: GST, TDS, the Companies Act filings, income tax, and the deadline calendar you cannot miss.
