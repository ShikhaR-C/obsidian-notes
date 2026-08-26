# T20 — Budget vs Actual and Cash Forecast

_Toolkit · fills §8–§9 of [[06-money-rails-and-finance-operations|06 — Money Rails and Finance Operations]] and the monthly review of [[08-the-operating-cadence|08 — The Operating Cadence]] · Owner: COO owns the drivers; the founder-CFO seat owns the truth of the balances ([[finance/07-phase-7-bootstrapping-runway-burn|Finance Phase 7]]) · Cadence: the forecast every Monday; BvA monthly when the close pack lands · Workbook tabs: `Budget vs Actual` and `Runway & 13-Week Cash` in [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx)._

## Purpose

Two sheets, two different questions. **Budget vs actual (BvA)** compares each month's spend to the plan, category by category — the earliest honest signal that the plan and reality are diverging, read in the monthly business review ([[06-money-rails-and-finance-operations|lesson 06]] §9). **The 13-week cash forecast** answers the question that actually kills companies — _in which week do we go below zero?_ — because "fine on average, broke in week 6 when the annual bill and salaries collide" is precisely the failure a monthly average hides. The rolling 13-week grid of inflows, outflows and closing balances is the standard instrument for that question ([Graphite — why you need a 13-week cash flow forecast](https://www.graphitefinancial.com/blog/why-you-need-13-week-cash-flow-forecast); [Abacum — the 13-week cash flow](https://www.abacum.ai/blog/13-week-cash-flow)), and the number to read aloud is the **trough** — the lowest weekly closing balance. The habit and the red line come from [[finance/07-phase-7-bootstrapping-runway-burn|Finance Phase 7]]; this template gives both an owner and a slot.

## When to use

- **The forecast: every Monday**, before the ops meeting — week-1 actuals replace last week's guesses; the trough and the red line are read with the scorecard.
- **BvA: monthly**, when the CA's close pack lands (target: by the 10th), in the monthly business review with one decision attached — what gets more next month, what gets less.
- **Quarterly**: budgets re-based at [[T19-quarterly-plan-and-review|T19]]; the category set itself changes only there or at the annual plan.
- **The projected balance crossing the red line anywhere in the 13 weeks is an automatic agenda item** — not a feeling, a rule.

## How to fill (rules)

**BvA** (the `Budget vs Actual` tab computes variance, % and status):

1. **Seven categories, matching the tab**: People · Cloud/infra · SaaS/tools · Sales & marketing · Legal/compliance/CA · Office/admin · Other. Few enough to read in five seconds; change the set only at planning.
2. Budgets come from the annual plan ([[19-planning-okrs-and-the-quarterly-rhythm|lesson 19]]); actuals come from the close — ERPNext exports, never memory.
3. **Variance = actual − budget. Any line off by more than 10% _and_ more than a threshold ₹ amount (set yours; illustrative ₹10,000) gets exactly one written sentence: cause, and whether it repeats.** No sentence, no review — commentary is the discipline that separates a BvA from a spreadsheet.
4. "Other" growing for two months means a category is hiding in it — split it out at the next quarter.

**The 13-week forecast** (the `Runway & 13-Week Cash` tab):

5. **Inflows go in the week the cash will actually arrive**, not the invoice week — the AR ageing and dunning ladder tell you when that really is (lesson 06 §6). Pre-revenue, the collections row is honestly zero.
6. **Outflows come from the payments calendar**: salaries and contractors, the Thursday vendor run, TDS on the 7th, GST with the return, and the annual meteors (insurance, store memberships, audit fee) placed in their actual weeks from [[T14-vendor-and-tool-register|T14]]'s renewal dates.
7. **Week-1 actuals replace the guess every Monday**; any weekly line that missed by more than ~10% gets a one-line why — that is how the forecast learns.
8. **The red line is written at the top of the tab** (Finance Phase 7's rule — illustrative: act when runway drops below 6 months) and the **trough week is named** every Monday, even when it is comfortable.

## Template

**BvA** — one row per category per month (columns identical to the tab, which also rolls up by month and by category):

| Month | Category                                                                                           | Budget (₹) | Actual (₹) | Variance (₹) | Variance % | Status | Commentary (why, action)          |
| ----- | -------------------------------------------------------------------------------------------------- | ---------- | ---------- | ------------ | ---------- | ------ | --------------------------------- |
|       | People / Cloud–infra / SaaS–tools / Sales & marketing / Legal–compliance–CA / Office–admin / Other |            |            |              |            |        | one sentence where the rule fires |

**13-week cash forecast** — columns W1…W13 (week starting Monday), rows as in the tab:

```
Opening balance
Cash in:   customer collections (when they will actually arrive)
           other inflows (director loan, grant, interest, GST refund)
           total cash in
Cash out:  salaries & contractors · AWS/Atlas · SaaS/tools ·
           CA/legal/compliance · rent/office · marketing/travel · other
           total cash out
Net cash flow (in − out)
Closing balance            ← the row you read
Trough = lowest closing balance · Week of trough · Red line (months)
```

The tab's section A adds the monthly runway view (opening cash, gross burn, net burn, runway in months, cash-out date) — keep both: runway answers "how long on average", the grid answers "which week".

## VSYST example (illustrative)

Monthly review, month 3 (numbers illustrative, from the tab's example rows): People ₹2.50 lakh budget vs ₹2.50 lakh actual — no comment needed. Legal/compliance/CA budget ₹15,000, actual ₹42,000 — variance +180%, over both thresholds, so one sentence: _"Trademark filing and CS catch-up work — one-off, does not repeat; next spike expected at audit (Sep)."_ SaaS/tools +₹2,800: _"Helpdesk hosting added — recurring; budget raised at Q re-base."_ Then the Monday forecast: closing balances stay comfortable until W6, where the Apple Developer renewal, the insurance premium and the quarterly TDS payment stack into the same week — trough ₹2.1 lakh, still above the red line, but the vendor run for W6 is trimmed and one annual bill is moved a week earlier to flatten the dip. That is the entire method: **the average said "fine"; the grid found the week that wasn't.**

## Related

Lessons [[06-money-rails-and-finance-operations|06]], [[08-the-operating-cadence|08]], [[19-planning-okrs-and-the-quarterly-rhythm|19]] · Templates [[T05-kpi-scorecard|T05]], [[T19-quarterly-plan-and-review|T19]], [[T23-board-and-investor-update|T23]], [[T14-vendor-and-tool-register|T14]] · [[finance/07-phase-7-bootstrapping-runway-burn|Finance Phase 7]] · [[COO-Docs/toolkit/index|COO Toolkit]]
