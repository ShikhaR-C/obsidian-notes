# Phase 5 — The Indian Accounting & Compliance System

> Level: Intermediate | Time: ~1.5 hr | Outcome: you understand the three "governments" a Pvt Ltd answers to, every recurring filing VSYST owes (GST, TDS, ROC, income tax), and the deadline calendar you cannot miss — so you can build the one-page compliance calendar the [[startup-operations-plan|ops plan]] tells you to get from your CA, and actually understand it.

---

> ⚠️ **Read this first — the honesty rule, loud.** *Every rate, threshold, form name, and deadline in this phase is exactly the kind of thing India revises in the annual Budget (Feb) or by notification mid-year.* This phase teaches the **system**, which is stable. The **numbers** you must confirm live with your CA or the official portal before acting. Treat every figure below as "roughly, as of 2026-07-16 — verify." Sources in [[12-reference]].

## 1. You Answer to Three Governments (plus your state)

A developer thinks of "the government" as one API. It's really three separate services with three separate portals, deadlines, and IDs:

| "Government" | Governs | Portal | VSYST's ID |
| --- | --- | --- | --- |
| **MCA** (Ministry of Corporate Affairs) | The *company* itself — existence, directors, annual filings | mca.gov.in | **CIN** + directors' **DIN** |
| **Income Tax** (CBDT) | Tax on *profits*, and **TDS** | incometax.gov.in | **PAN** + **TAN** (for TDS) |
| **GST** (indirect tax) | Tax on *sales of goods/services* | gst.gov.in | **GSTIN** (once registered) |
| *+ State* (Chhattisgarh) | Professional tax, Shops & Establishment, labour | state portals | as applicable |

You already have a **PAN** (the company's) and a **CIN** (from incorporation). The others switch on as you cross thresholds. Let's take them one at a time.

## 2. The Calendar Everyone Shares: the Financial Year

- **Financial Year (FY):** **1 April → 31 March.** "FY 2026–27" = 1 Apr 2026 to 31 Mar 2027. All statements, all filings, all taxes run on this.
- **Assessment Year (AY):** the year *after*, when you file tax on the FY. FY 2026–27 is assessed in **AY 2027–28**. (Just vocabulary — don't overthink it.)
- **AS vs Ind AS:** VSYST follows **Accounting Standards (AS)** (Phase 4, Division I). **Ind AS** (India's IFRS-converged standards) kicks in only for large/listed companies (net worth ≥ ₹250 cr, etc.). Not your problem for years, possibly ever.

## 3. GST — Tax on What You Sell

**What it is:** a value-added tax on the supply of goods/services. You *collect* it from customers and *pay* it to the government, minus the GST you *paid* on your own purchases (**Input Tax Credit, ITC**). You're an unpaid tax-collector; the ITC mechanism means you only remit the tax on the *value you added*.

| Thing to know | Roughly (verify) | VSYST relevance |
| --- | --- | --- |
| **Registration threshold** | **₹20 lakh** aggregate turnover for **services** (₹40 L for goods; ₹10 L/₹20 L in special-category states) | Software/SaaS = **services** → the ₹20 L line. **Below it you *need not* register** (even for inter-state services). |
| **Rate on software/SaaS** | **18%** | DZZLO subscriptions, if/when registered, carry 18% GST |
| **The three GSTs** | **CGST + SGST** (within your state) or **IGST** (across states) | Selling to a dealer in another state = **IGST**; same-state = CGST+SGST |
| **Export of software** | **Zero-rated**; supply under a **LUT** (Letter of Undertaking) without paying IGST | If DZZLO ever gets foreign customers |
| **e-invoicing** | Mandatory above **₹5 cr** turnover | Not you for a long time |
| **Reverse charge (RCM)** | *You* pay GST on certain purchases (e.g. some imports, lawyer fees) | Occasionally — your CA flags it |

**The returns** (once registered — a rhythm, not a one-off):

| Return | What | Frequency |
| --- | --- | --- |
| **GSTR-1** | Your outward sales, invoice-wise | Monthly, or quarterly under **QRMP** |
| **GSTR-3B** | Summary + actual tax payment | Monthly / quarterly |
| **GSTR-9** | Annual reconciliation | Yearly (if turnover > ₹2 cr) |

> **Founder's call — should VSYST register *before* ₹20 L?** Sometimes yes: business customers often *want* a GST invoice to claim their own ITC, and registration lets you reclaim GST on your AWS/tool bills. Sometimes no: it adds monthly-return overhead. **This is a real decision to make with your CA** given DZZLO's customers are GST-registered dealers who'll likely expect tax invoices.

## 4. TDS — Tax Deducted at Source (you withhold tax from people *you* pay)

**What it is:** when VSYST pays certain expenses, the government makes *you* withhold a slice of tax and deposit it on the payee's behalf. You need a **TAN** (separate from PAN) to do this. It feels like extra admin, but skipping it has teeth: **expenses on which you failed to deduct TDS can be disallowed** — you lose the tax deduction *and* pay a penalty.

Key sections you'll actually hit (rates *roughly*, verify — several changed recently):

| Section | You pay for… | TDS rate (verify) | VSYST example |
| --- | --- | --- | --- |
| **192** | Salaries | per employee's slab | Once you pay salaries above the exemption limit |
| **194J** | Professional / technical fees | **10%** | Your CA, a lawyer, a freelance designer |
| **194C** | Contractors | 1% (indiv) / 2% (company) | A contractor building something for you |
| **194H** | **Commission / brokerage** | **~2–5%** (recently reduced — verify) | If DZZLO pays channel-partner commission (Phase 6) |
| **194I** | Rent | 10% (2% for plant) | Office rent above the threshold |
| **194Q** | Purchase of goods > ₹50 L | 0.1% | Not you yet |

**The TDS rhythm:** deduct when you pay → **deposit by the 7th of next month** → file a **quarterly TDS return** (24Q for salaries, 26Q for others) → issue **Form 16** (salary) / **16A** (other) to the payee so *they* can claim credit. **TCS** (Tax *Collected* at Source) is the mirror — collecting extra tax on certain *sales* — mostly irrelevant to a SaaS company for now.

## 5. Income Tax — Tax on Profit

**Pre-revenue good news:** no profit → no income tax → no advance tax. But you still **file a return every year** (a company always files, even at a loss — and filing losses is *valuable*, §8). Know the shape for when you're profitable:

| Thing | Roughly (verify) |
| --- | --- |
| **Company tax rate** | **~22%** under the concessional **section 115BAA** regime (no exemptions), or **25%** (turnover ≤ ₹400 cr) / **30%** otherwise — plus surcharge + 4% cess. Your CA picks the regime. |
| **MAT** (Minimum Alternate Tax) | ~15% of book profit — a floor so profitable-on-paper companies can't pay ₹0. Doesn't apply under 115BAA. |
| **Advance tax** | If annual tax ≥ ₹10,000, pay in **4 instalments** (15 Jun / 15 Sep / 15 Dec / 15 Mar). Miss → interest. Pre-revenue = ₹0. |
| **Return form** | **ITR-6** for companies |
| **Two different depreciations** | Income-tax depreciation (block-of-assets, WDV) ≠ your books' Schedule II depreciation (Phase 4). The gap creates **deferred tax**. |

## 6. Two Different "Audits" — Don't Confuse Them (this one bites pre-revenue founders)

| Audit | Required when | Applies to VSYST now? |
| --- | --- | --- |
| **Statutory audit** (Companies Act) | **Every company, every year — regardless of turnover, even ₹0** | ✅ **YES. Mandatory even pre-revenue.** |
| **Tax audit** (u/s 44AB, Income Tax) | Turnover > **₹1 cr** (business; up to ₹10 cr if ≤5% cash) | ❌ Not until you're much bigger |

> **The trap:** many first-time founders assume "no revenue = no audit". **False for a Pvt Ltd.** Your company must appoint a Chartered Accountant as **statutory auditor** and get its accounts audited *every single year from incorporation*, even while dormant. This is the #1 reason you need a CA on retainer *now*, not "once we have sales". (A truly inactive company can file as a **Dormant Company** under Sec 455 to reduce some compliance — ask your CA if that fits a gap year.)

## 7. The MCA / ROC Filings — Keeping the Company Legally Alive

The Companies Act makes VSYST do "corporate housekeeping" every year via the **Registrar of Companies (ROC)**. Miss these and penalties accrue **per day**, directors can be disqualified, and the company can be **struck off**. The recurring ones:

| Filing | What it is | Rough deadline (verify) |
| --- | --- | --- |
| **INC-20A** | Declaration of *commencement of business* (capital received) | Within **180 days** of incorporation (one-time) |
| **ADT-1** | Appointment of the statutory auditor | Within 15 days of the AGM (auditor holds 5 yrs) |
| **AOC-4** | File the **financial statements** (BS, P&L, notes) | Within 30 days of AGM (~by end Oct) |
| **MGT-7 / MGT-7A** | **Annual return** (shareholders, directors). 7A = simplified, for small companies | Within 60 days of AGM (~by end Nov) |
| **DIR-3 KYC** | Each director re-verifies KYC | By **30 Sep** yearly |
| **DPT-3** | Return of deposits / **loans not treated as deposits** | By **30 Jun** yearly |
| **MSME-1** | Half-yearly, if you owe MSME vendors > 45 days | Half-yearly |
| **AGM** | Annual General Meeting | Within 6 months of FY-end (first AGM: 9 months) |
| **Board meetings** | Board meetings + minutes | Min 4/yr; **small companies: 2/yr** |

> **DPT-3 & your director's loan (Phase 6 tie-in):** the money *you* lend VSYST is a "loan not considered a deposit" and gets reported in **DPT-3** yearly. Getting the paperwork right (a board resolution, the loan in your name as director) keeps it clean and out of "deposit" rules. Your CA/CS handles the form; you must know it exists.

**Small Company relief:** VSYST is almost certainly a **"Small Company"** (paid-up capital and turnover under the prescribed limits — *verify current thresholds*), which grants real relaxations: 2 board meetings/year instead of 4, simplified MGT-7A, fewer disclosures, lower penalties. Confirm your status with your CS — it lightens the load meaningfully.

## 8. Startup-Specific Wins (don't leave these on the table)

Being a startup unlocks concessions worth real money — most founders miss them:

| Scheme | What you get | Worth doing? |
| --- | --- | --- |
| **DPIIT "Startup India" recognition** | Official startup status → unlocks the items below; self-certification on labour/env laws; easier IP & procurement; faster exit | **Yes — free, online, do it.** VSYST (Pvt Ltd, < 10 yrs, innovative, turnover < ₹100 cr) likely qualifies |
| **Section 80-IAC tax holiday** | **100% profit tax exemption for 3 consecutive years** (out of first 10), for eligible DPIIT startups | Huge *once profitable* — plan the 3 years for when profit peaks |
| **Angel tax abolished** | The dreaded "angel tax" on share premium above fair value (Sec 56(2)(viib)) was **abolished for all investors from AY 2025-26** | Removes a big historical fundraising headache (Phase 8) |
| **Carry-forward of losses** | Your pre-revenue losses can offset future profits — and eligible startups get **relaxed shareholding-continuity rules** (Sec 79) so raising funds doesn't kill the carry-forward | **File every loss year's return on time** to preserve this |
| **Udyam (MSME) registration** | MSME benefits: the 45-day payment protection, some scheme access | Quick, free — worth it |

**The loss point is subtle but valuable:** every rupee of pre-revenue loss you *file properly* becomes a future tax shield when you turn profitable. This is a concrete reason clean books matter *before* you make money — a Phase-10 payoff you set up now.

## 9. What Actually Applies to VSYST *Today* (priority order)

Cutting through the wall of acronyms — for a **pre-revenue Pvt Ltd**, here's what's live *now* vs. later:

**Do now (non-negotiable):**
1. **Appoint a CA as statutory auditor** and keep clean books — audit is mandatory even at ₹0.
2. **INC-20A** if not already filed (180-day clock from incorporation).
3. **Annual ROC filings** (AOC-4, MGT-7A) + **DIR-3 KYC** + **DPT-3** (your director's loan) — every year, on time.
4. **File the income-tax return** even at a loss (preserves loss carry-forward).
5. **DPIIT Startup India + Udyam** registration — free wins.
6. **TDS** the moment you pay a CA/contractor/salary above thresholds — get a **TAN**.

**Switches on later (by threshold):**
- **GST** at ~₹20 L services turnover (or voluntarily earlier if customers want tax invoices).
- **PF** (≥ 20 employees), **ESI** (≥ 10, state-dependent), **Professional Tax** (state) as you hire.
- **Tax audit** above ₹1 cr; **e-invoicing** above ₹5 cr; **GSTR-9** above ₹2 cr.

## 10. Exercises

**10.1 — Build your one-page compliance calendar (25 min).** In `finance-workbook/phase5-calendar.xlsx`, make a 12-month grid and drop every recurring deadline from §7 and the tax/GST rhythms onto its month (7th = TDS deposit, 30 Jun = DPT-3, 30 Sep = DIR-3 KYC + AGM, ~Oct/Nov = AOC-4/MGT-7A, quarterly = TDS returns). **Take this to your CA and have them correct it.** This is the single highest-value artifact in this phase.

**10.2 — The registration audit (15 min).** Write VSYST's status on each: statutory auditor appointed? INC-20A filed? DPIIT recognised? Udyam? TAN obtained? GST — registered / voluntary / below threshold? For each "no", note whether it's *needed now* (§9) and add it to a to-do.

**10.3 — The GST decision memo (10 min).** Write 5 lines: given DZZLO's customers are GST-registered dealers, should VSYST register for GST *before* hitting ₹20 L? List one reason for, one against, and the question to ask your CA. Deciding this deliberately (not by accident) is a CFO move.

**10.4 — Confirm your Small Company status (5 min).** Check VSYST's paid-up capital and turnover against the current Small Company thresholds (verify with CS). If you qualify, list the three reliefs you get. Knowing your own regulatory weight class saves real money.

---

**Next:** [[06-phase-6-loans-commission-investments-funds]] — the specific tricky entries you asked about: loans (yours and the bank's), commission, investments, funds, and how assets & liabilities behave in practice.
