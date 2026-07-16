# Reference — Links, Glossary, Templates & Sources

> The whole course's external links, a plain-English glossary of every term, the workbook artifact checklist, a compliance quick-reference, and sources. Bookmark this page. Verify every rate/threshold/deadline live before acting (the honesty rule — [[00_README]]).

---

## 1. Official Portals (your primary, always-current sources)

These are the authoritative government/vendor sites — when a number matters, it comes from here, not from this folder:

| Topic | Site | Use it for |
| --- | --- | --- |
| **Companies / ROC** | mca.gov.in | Filings (AOC-4, MGT-7, DIR-3 KYC, DPT-3), company master data, forms |
| **Income Tax** | incometax.gov.in | ITR filing, TDS, PAN/TAN, e-pay tax, Form 26AS/AIS |
| **GST** | gst.gov.in | Registration, returns (GSTR-1/3B/9), e-invoicing, rate finder |
| **TDS (TRACES)** | tdscpc.gov.in | TDS returns, Form 16/16A, challans |
| **Startup India** | startupindia.gov.in | DPIIT recognition, 80-IAC application, schemes |
| **Udyam (MSME)** | udyamregistration.gov.in | Free MSME registration |
| **ICAI** | icai.org | Accounting Standards (AS), find a Chartered Accountant |

## 2. Learning Resources (free & good)

| Resource | What | Where |
| --- | --- | --- |
| **Zerodha Varsity** | Free, excellent Indian modules on "Financial Modelling" & "Fundamentals" (accounting statements explained simply) | zerodha.com/varsity |
| **Frappe School** | Free "ERPNext for Beginners" and accounting courses | frappe.school |
| **ERPNext Docs** | Accounting module documentation | docs.frappe.io/erpnext |
| **Corporate Finance Institute (CFI)** | Free articles on statements, modelling, ratios | corporatefinanceinstitute.com |
| **Investopedia** | Look up any term (global, not India-specific) | investopedia.com |
| **ClearTax / Tax2win blogs** | India-specific GST/TDS/ROC how-tos (verify against the official portal) | cleartax.in |
| **Tally Learning Hub** | If you ever need Tally itself | tallysolutions.com |

## 3. Fundraising & Modelling References

| Resource | What |
| --- | --- |
| **Y Combinator SAFE / library** | The original SAFE docs & startup library (ycombinator.com/library) |
| **100X.VC** | **iSAFE** documents (India's SAFE) and early-stage guidance |
| **Indian angel networks** | IAN (Indian Angel Network), Mumbai Angels, LetsVenture — how angel rounds work |
| **VC term-sheet guides** | Search "Brad Feld Venture Deals" (the standard book) + Indian term-sheet explainers |
| **SaaS metrics** | Search "SaaS metrics ChartMogul / Baremetrics guide", "Rule of 40", "David Skok SaaS" |

## 4. Books (the ops-plan list + finance additions)

From the [[startup-operations-plan|ops plan]]'s reading list, the finance-relevant ones:
- **Profit First** (Mike Michalowicz) — the cash-management / multi-account system (Phase 7).
- **The Personal MBA** (Josh Kaufman) — the whole business vocabulary, including finance basics.
- **The Mom Test** (Rob Fitzpatrick) — customer conversations that validate the model (Phase 9).

Finance-specific additions:
- **Venture Deals** (Brad Feld & Jason Mendelson) — the term-sheet bible (Phase 8).
- **Financial Intelligence for Entrepreneurs** (Berman & Knight) — read statements like an owner (Phases 3–4).
- **Accounting Made Simple** (Mike Piper) — the whole of accounting in ~100 pages (Phases 1–3).

## 5. In-Vault Cross-References

- [[startup-operations-plan|Startup Operations Plan]] — business-level money habits, realities, phase roadmap.
- [[ERPNext-Implementation-Guide|ERPNext Implementation Guide]] — install, setup wizard, adoption sequence, add-on apps.
- The phases: [[01-phase-1-what-accounting-is]] · [[02-phase-2-the-books]] · [[03-phase-3-three-statements]] · [[04-phase-4-balance-sheet-in-full]] · [[05-phase-5-indian-accounting-system]] · [[06-phase-6-loans-commission-investments-funds]] · [[07-phase-7-bootstrapping-runway-burn]] · [[08-phase-8-fundraising-and-cap-table]] · [[09-phase-9-business-and-financial-model]] · [[10-phase-10-pre-revenue-to-profitable]] · [[11-phase-11-software-tally-erpnext]]

## 6. Glossary (every term, plain English)

**The basics (Phases 1–3)**
- **Debit / Credit** — the left / right side of an entry. Not good/bad, not in/out. [P1]
- **Double-entry** — every transaction hits ≥ 2 accounts; total debits = total credits. [P1]
- **Accounting equation** — Assets = Liabilities + Equity. Always balances. [P1]
- **Accrual** — record income/expense when *earned/incurred*, not when cash moves. [P1]
- **Going concern / Prudence / Consistency** — assume the company survives / count losses early & gains late / use the same methods yearly. [P1]
- **Journal** — the diary; all transactions in time order (Tally: Day Book). [P2]
- **Ledger** — the same entries re-sorted per account, with running balances. [P2]
- **Chart of Accounts (CoA)** — the master list of accounts (your schema). [P2]
- **Trial Balance** — list of all ledger balances; debits must equal credits (a checksum). [P2]
- **Sundry Debtors / Accounts Receivable (AR)** — people who owe you. **Sundry Creditors / Accounts Payable (AP)** — people you owe. [P2]
- **Voucher** — a software transaction type: Payment, Receipt, Contra, Sales, Purchase, Journal. [P2]
- **Bill-to-bill / bill-wise** — matching each payment to the specific invoice it clears. [P2]
- **P&L / Statement of Profit and Loss** (US name: Income Statement) — are we making or losing money, over a period. [P3]
- **Balance Sheet** — what we own & owe, at a moment. [P3]
- **Balance Sheet layout (Indian)** — Equity & Liabilities first, Assets second: left│right in the old horizontal form, top│bottom in today's Schedule III vertical form. American books mirror it (assets first) — same equation, same totals. [P3]
- **Cash Flow Statement** — where actual cash went (Operating / Investing / Financing). [P3]
- **Gross Profit / EBITDA / EBIT / PBT / PAT** — the P&L ladder from revenue down to net profit. [P3]

**Balance sheet & compliance (Phases 4–5)**
- **Schedule III** — the Companies Act's prescribed *format* for the balance sheet & P&L. Division I = AS; Division II = Ind AS. [P4]
- **Schedule II** — the Companies Act's prescribed *useful lives* for depreciation. [P4]
- **AS vs Ind AS** — Accounting Standards (smaller cos, you) vs Ind AS (large/listed). [P5]
- **Notes to Accounts** — the detailed "appendices" behind each balance-sheet line. [P4]
- **Depreciation / Amortisation** — spreading a tangible / intangible asset's cost over its life. [P4]
- **Gross block / Net block / Accumulated depreciation** — asset at cost / cost minus wear / total wear so far. [P4]
- **SLM / WDV** — Straight-Line (equal yearly) / Written-Down-Value (more early) depreciation. [P4]
- **Share capital: authorised / issued / paid-up** — max allowed / offered / actually paid. [P4]
- **Reserves & Surplus** — accumulated profits/losses + securities premium (equity). [P4]
- **Securities premium** — amount investors pay *above* a share's face value. [P4]
- **Provision** — a liability that's probable but estimated. **Contingent liability** — a *possible* obligation, only disclosed, not booked. [P4/P6]
- **PAN / TAN / CIN / DIN / GSTIN** — company tax ID / TDS ID / company reg. no. / director ID / GST ID. [P5]
- **GST / CGST / SGST / IGST / ITC** — the sales tax / its central, state, inter-state parts / input tax credit (offset). [P5]
- **TDS / TCS** — tax deducted (on what you pay) / collected (on what you sell) at source. [P5]
- **ROC / MCA** — Registrar of Companies / the Ministry it sits under. [P5]
- **AOC-4 / MGT-7(A) / DPT-3 / DIR-3 KYC / INC-20A / ADT-1** — file financials / annual return / loan return / director KYC / commencement declaration / auditor appointment. [P5]
- **Statutory audit** (mandatory for every company, even ₹0) vs **Tax audit** (only above turnover thresholds). [P5]
- **Advance tax / MAT** — pay tax in 4 instalments if liable / minimum tax on book profit. [P5]
- **80-IAC** — 3-year profit tax holiday for eligible DPIIT startups. **Angel tax** — tax on share premium above fair value, *abolished from AY 2025-26*. [P5/P8]
- **DPIIT / Udyam / MSME** — startup recognition / MSME registration / micro-small-medium enterprise. [P5]

**Loans, funds & practice (Phase 6)**
- **Director's loan** — money a director lends the company (a liability), distinct from share capital (equity). [P6]
- **Secured / Unsecured** — backed by collateral / not. **Charge / hypothecation** — the lender's claim on assets (filed as CHG-1). [P6]
- **Term loan vs OD/CC** — fixed sum over years vs a revolving working-capital limit. [P6]
- **EMI split** — each instalment = principal (cuts the liability) + interest (a P&L expense). [P6]
- **Capital vs revenue expenditure** — asset (used over years) vs expense (this period). [P6]
- **Deferred / unearned revenue** — cash received but not yet earned (a liability) — e.g. annual prepay. [P6]
- **Outstanding / Prepaid / Accrued income / Income-in-advance** — the four accrual adjustments. [P6]

**Startup finance (Phases 7–10)**
- **Gross burn / Net burn** — total monthly cash out / after revenue. **Runway** — cash ÷ net burn (months to zero). [P7]
- **Cap table** — who owns what. **Fully diluted** — counting all shares that could exist (incl. ESOP, convertibles). [P8]
- **Dilution** — your % falling when new shares are issued. **Pre-money / Post-money** — valuation before / after the investment. [P8]
- **CCPS / CCDs** — Compulsorily Convertible Preference Shares / Debentures (Indian VC standard). [P8]
- **SAFE / iSAFE** — Simple Agreement for Future Equity / its India version — defer valuation to the next round. [P8]
- **Liquidation preference** — who gets paid first on exit (1× non-participating = founder-friendly). [P8]
- **Anti-dilution** — investor protection in a down round (weighted-average = fair; full ratchet = harsh). [P8]
- **ESOP** — employee stock options. **Vesting** — earning shares/options over time (4 yr, 1-yr cliff). [P8]
- **FEMA / FDI / FC-GPR** — foreign-exchange law / foreign investment / the RBI filing for it. [P8]
- **MRR / ARR** — monthly / annual recurring revenue. **ARPA** — average revenue per account. [P9]
- **CAC / LTV / LTV:CAC / payback** — cost to acquire / lifetime value / ratio (≥3 healthy) / months to recoup CAC. [P9]
- **Churn / NRR** — % customers/revenue lost per period / net revenue retention (>100% = growth without new customers). [P9]
- **Unit economics** — the per-customer profitability math (CAC, LTV, margin). [P9]
- **Business Model Canvas** — 9 boxes describing how a business creates & captures value. [P9]
- **Value-based pricing** — price by what the outcome is worth to the customer, not by cost. [P9]
- **Default alive / dead** — will you reach profit before cash runs out, at current growth & burn? [P10]
- **Rule of 40** — growth % + profit margin % ≥ 40 (efficient SaaS). **Magic number** — sales efficiency. [P10]
- **Variance analysis** — comparing actual vs budget and asking *why* on every gap. [P10]

## 7. The Workbook Artifacts (what you should have built)

By the end of the course, `finance-workbook/` should contain:

- [ ] `phase1.xlsx` — journal entries + the equation proof
- [ ] `phase2.xlsx` — ledgers, trial balance, chart of accounts, party ageing
- [ ] `phase3.xlsx` — mini P&L, monthly burn, break-even
- [ ] `phase4.xlsx` — Schedule III mapping + depreciation schedule
- [ ] `phase5-calendar.xlsx` — **your one-page compliance calendar (CA-reviewed)**
- [ ] `phase7-runway.xlsx` — runway model + 3 scenarios + 13-week cash forecast
- [ ] `phase8-captable.xlsx` — cap table + dilution model
- [ ] `phase9-canvas.md` + `phase9-model.xlsx` — DZZLO's business model + **3-year financial model**
- [ ] `phase10-dashboard.xlsx` — the monthly CFO dashboard + default-alive calc
- [ ] Live books in **ERPNext** (Phase 11)

## 8. Compliance Quick-Reference (verify every date)

*Recurring obligations for a Pvt Ltd — rough timing, confirm with your CA (Phase 5):*

| When | What |
| --- | --- |
| **Monthly, by 7th** | Deposit TDS for prior month |
| **Monthly / Quarterly** | GST returns (GSTR-1, 3B) — if registered |
| **Quarterly** | TDS returns (24Q/26Q); advance tax instalments (15 Jun/Sep/Dec/Mar) if liable |
| **30 June** | DPT-3 (loan/deposit return) |
| **30 Sept** | AGM (by); DIR-3 KYC (by) |
| **~Oct–Nov** | AOC-4 (financials) + MGT-7/7A (annual return) after AGM |
| **31 Oct (approx)** | Income-tax return (ITR-6) — *file even at a loss* |
| **One-time** | INC-20A (180 days of incorporation); ADT-1 (auditor); DPIIT + Udyam registration |

---

> **Sources & honesty.** This curriculum was written and sanity-checked for an Indian Private Limited company as of **2026-07-16**, drawing on the official portals in §1, the Companies Act 2013 (Schedules II & III), the CGST/Income-Tax Acts, and standard startup-finance practice. **Tax rates, thresholds, form names, scheme rules, and deadlines change with each Union Budget and by notification — always confirm the live figure with your CA or the source portal before acting.** This folder teaches the *system* (stable); the *numbers* you verify (volatile). Nothing here is a substitute for a qualified Chartered Accountant and Company Secretary — it makes you the *informed client* who can direct, question, and decide.
