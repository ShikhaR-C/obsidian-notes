# 11 — Metrics, Budget, CAC and the Marketing Scorecard

_Phase 4 · Scale · Months 3–12. After this lesson you can pull DZZLO's funnel as nine real numbers from Mongo and the pipeline sheet, define every term you use in one line, compute fully-loaded CAC and payback separately for each channel you have used, fill the eight-row weekly marketing scorecard, set the month's ₹30–50k budget with a cut-first order, and say which numbers belong to this course, which to the COO's sheet and which to the CEO's._

## Explain-it-like-I'm-5

Watch a sabzi stall in Raipur's mandi for a morning. Two hundred people walk past. Forty slow down. Fifteen ask the rate. Six buy. Two come back on Thursday, and one brings her neighbour. The stall owner has never heard the word "funnel," but she can tell you all six numbers, because she watched them from behind her own crates.

Now the harder question: which is cheaper — paying a boy ₹200 to hand out slips at the bus stop, or ₹20 off for every regular who brings a neighbour? She answers instantly, because she knows what each cost and how many buyers each produced. That is CAC by channel, and it is the only marketing arithmetic that has ever changed anyone's mind. This lesson builds VSYST's version of that morning, out of Mongo, a Google Sheet and the WhatsApp Business app.

## 1. The funnel, as numbers you can actually pull

A **funnel** is a list of stages with a count at each. It works only when each stage is defined tightly enough that two people counting on the same day agree. DZZLO's funnel has an unusual bottom, because of HC2 and HC10: **the sale is not finished when the dealer pays; it is finished when both sides are live.**

| # | Stage | Definition at DZZLO | Source | Qtr |
| --- | --- | --- | --- | --- |
| 1 | **Named target** | On the Raipur 100 list, owner name + phone | `Target List` tab, [[M03-target-list-builder\|M03]] | 100 |
| 2 | **Contacted** | First WhatsApp, call or walk-in, dated | `Pipeline` tab, [[M07-sales-pipeline-tracker\|M07]] | 60 |
| 3 | **Pump visit** | You stood there, spoke to owner or son | M07 Visit Log | 40 |
| 4 | **Demo done** | The 10-minute demo, on the owner's phone | M07, stage `Demo done` | 15 |
| 5 | **Trial started** | Tenant created, 14-day no-card trial live | Mongo `dealer_msts` | 9 |
| 6 | **Dealer activated** | ≥1 `dealer_custs` **and** ≥1 non-test `invs` within 14 days | Mongo `dealer_msts` × `dealer_custs` × `invs` | 6 |
| 7 | **Both sides live** | ≥3 customers confirmed a rate in the 10 PM–6 AM window, 7 days | Mongo `rate_msts`, confirmed | 4 |
| 8 | **Paying GSTIN** | Invoice raised **and** money received | Billing / Easebuzz | 4 |
| 9 | **Referring dealer** | ≥1 named introduction, closed or not | `Referral Tracker`, [[M09-referral-program-one-pager\|M09]] | 2 |

Stage 6's definition is not ours — it is [[T05-kpi-scorecard|T05]] row 3, ratified in [[17-the-numbers-a-ceo-watches|CEO lesson 17]] §6.6. **Never invent a second activation definition.** Stage 7 exists only because DZZLO is two-sided: a dealer whose customers never confirm rates churns by month three.

Targets are illustrative until quarterly planning — **VERIFY LIVE** against the real Raipur pump count. Indian B2B cold conversion runs near 2.23% on 30–90 day SMB cycles ([Zeliq](https://www.zeliq.com/blog/b2b-conversion-rates-by-industry)).

## 2. The words, defined once, with formulas

| Term | Definition at DZZLO | Formula |
| --- | --- | --- |
| **Lead** | Named pump, named owner, a phone we have used | count at stage 2 |
| **MQL / SQL** | A scoring handshake between two teams | **not used** |
| **Conversion rate** | Movement between two stages, fixed window | stage N+1 ÷ stage N |
| **Activation rate** | Trials reaching stage 6 in 14 days | activated ÷ trials |
| **CAC** | Fully-loaded cost of one paying dealer, **by channel** | (cash + hours × imputed rate) ÷ dealers from that channel |
| **ARPA** | Monthly revenue per account, ex-GST | MRR ÷ paying GSTINs |
| **Gross margin** | Revenue less cost to serve (OTP, hosting, support) | (revenue − cost to serve) ÷ revenue |
| **CAC payback** | Months of gross profit to earn CAC back | CAC ÷ (ARPA × gross margin) |
| **LTV** | Lifetime value of a dealer | **not reported yet** |
| **Logo churn** | Dealer firms lost in a month | lost ÷ firms at start |
| **Revenue churn** | MRR lost in a month | MRR lost ÷ MRR at start |
| **NPS** | "Recommend DZZLO to another owner, 0–10?" | %(9–10) − %(0–6) |
| **WhatsApp reply rate** | Of dealers messaged, how many wrote back | repliers ÷ recipients |
| **Referral rate** | Of activated dealers, how many introduced someone | referrers ÷ activated |
| **Customers per dealer** | Depth of the two-sided loop | active `dealer_custs` ÷ activated `dealer_msts` |

**Why we skip MQL/SQL.** They arbitrate a handoff between a marketing team and a sales team; VSYST has neither. Count **pumps at a stage**, never scored contacts.

**Why LTV stays blank.** Churn sits in LTV's denominator, so a small error becomes an enormous one. Gurley's warning is canonical — the formula is "deceptively simple" and makes speculation look like accounting ([Above the Crowd](https://abovethecrowd.com/2012/09/04/the-dangerous-seduction-of-the-lifetime-value-ltv-formula/)). **No LTV or LTV:CAC until 30 paying GSTINs and 12 months of churn history** ([[17-the-numbers-a-ceo-watches|CEO lesson 17]] §6.5). Report **payback in months**; it degrades gracefully at N=4.

**Calibration.** Median SaaS activation is 30% ([Lenny's Newsletter](https://www.lennysnewsletter.com/p/what-is-a-good-activation-rate)) — but on self-serve products where activating is one click; ours needs a second company, so read it as a ceiling.

## 3. CAC by channel — and why blended CAC lies

CAC at VSYST is almost entirely founder time. Ignore it and you get a CAC of ₹2,000 and a business nobody but you can run. The fix is an **imputed rate**: value a founder hour at what replacing it would cost.

> **House rule:** ₹30,000 salary + ~₹8,000 travel/phone for the field associate we would hire instead (**VERIFY LIVE**, HC1) ÷ 22 days ÷ 8 hours ≈ ₹216/hour, **doubled to ₹400/hour** because the founder also demos, prices and closes. Set it once a year in [[M13-marketing-scorecard-and-cac-calculator|M13]] with the derivation beside it; never change it mid-quarter, or CAC moves for reasons unrelated to marketing ([Tango — CAC at early-stage startups](https://www.tango.vc/p/early-cac)).

Numbers illustrative; the method is not.

| | **Referral (Dealer Dost)** | **OMC intro (IOCL TM)** | **Field visit (cold)** |
| --- | --- | --- | --- |
| Cash spend | ₹6,000 (3 × ₹2,000 bounty) | ₹18,000 (6 intros × ₹3,000) | ₹1,500 leaflets |
| Founder hours | 24 h (8 asks, 5 warm visits, closes) | 32 h (TM time, 6 visits, follow-up) | 68 h (30 visits, 6 demos, follow-up) |
| Hours × ₹400 | ₹9,600 | ₹12,800 | ₹27,200 |
| Fuel / travel | ₹1,250 | ₹2,100 | ₹2,700 |
| **Total cost** | **₹16,850** | **₹32,900** | **₹31,400** |
| Paying dealers | 3 | 2 | 2 |
| **CAC** | **₹5,617** | **₹16,450** | **₹15,700** |
| **Payback** at ₹1,200/mo gross profit | 4.7 mo (+2 free months = **6.7**) | **13.7 mo** | **13.1 mo** |

Gross profit assumes ARPA ≈ ₹1,500/month ex-GST on a mid-skewed mix at 80% margin. Tiers are **₹599 / ₹1,799 / ₹4,999 + Enterprise, ex-GST, 14-day no-card trial** — **VERIFY LIVE, owner sign-off pending** ([[08-dzzlo-subscription-strategy|subscription strategy]]).

Referral is **three times cheaper** and pays back inside seven months even after two free months are given away — under Skok's bar of recovering CAC in under 12 months ([David Skok — SaaS Metrics 2.0](https://www.forentrepreneurs.com/saas-metrics-2/)). OMC and field sit at that bar's edge: ordinary, not broken, against the early-stage Indian vertical-SaaS band of 12–18 months ([[13_Metrics_and_KPIs|transporters 13]] §6). That is HC4's channel order arriving as arithmetic rather than assertion.

**Blended CAC is ₹81,150 ÷ 7 = ₹11,593, and it lies in two directions at once.** It sits above referral and below OMC, flattering the expensive channel and punishing the cheap one; and it moves when the *mix* moves with no change in any channel's efficiency. It says nothing about **where the next rupee goes** — the only decision the number exists for. Report it once as a sanity check; decide on channel CAC, and treat one as real only after **three paying dealers from it**.

## 4. The weekly marketing scorecard

Eight numbers, one owner each, filled Monday, 13-week trailing — the same shape as [[T05-kpi-scorecard|T05]]. The form is EOS's weekly Scorecard ([EOS](https://www.eosworldwide.com/level-10-meeting)); the discipline is Amazon's preference for **controllable input metrics** over outcomes you can only watch ([Commoncog](https://commoncog.com/the-amazon-weekly-business-review/)). Rows 1–7 are inputs you control this week; row 8 is the lagging row the other seven exist for.

| # | Metric (HC8) | Owner | Source | Goal | Red |
| --- | --- | --- | --- | --- | --- |
| 1 | Pump visits | Domain dir. | M07 Visit Log | 8 | 4 |
| 2 | Demos done | Domain dir. | M07, stage `Demo done` | 5 | 2 |
| 3 | Trials started | Third dir. | Mongo `dealer_msts` | 3 | 1 |
| 4 | Dealers activated (≥1 customer linked + ≥1 invoice, 14 days) | Third dir. | Saved Mongo aggregation | 2 | 0 |
| 5 | Customers activated per activated dealer | Third dir. | Mongo `dealer_custs` × `rate_msts` | ≥3 | 1 |
| 6 | Referrals asked / received | Domain dir. | `Referral Tracker` tab | 5 / 2 | 2 / 0 |
| 7 | WhatsApp reply rate | Third dir. | WhatsApp Business → Stats | ≥40% | 20% |
| 8 | CAC by channel (rolling 90 days) | CEO | `CAC & Payback` tab | best ≤ ₹8,000 | ₹20,000 |

Goals and red lines are illustrative until quarterly planning ([[T19-quarterly-plan-and-review|T19]]) — **VERIFY LIVE**. One debt, named honestly: rows 4 and 5 need a Mongo aggregation only the technical CEO can write, which breaks T05's rule that owners enter their own numbers.

**Which course owns which artefact:**

| Artefact | Owned by | Lives in |
| --- | --- | --- |
| Weekly **marketing** scorecard, CAC by channel, marketing budget lines | **CMO-Docs (this course)** | [[M13-marketing-scorecard-and-cac-calculator\|M13]] |
| Company **KPI scorecard**, ops meeting, scorecard mechanics | COO-Docs | [[T05-kpi-scorecard\|T05]], [[T03-weekly-ops-meeting-agenda\|T03]], [[16-metrics-dashboards-and-scorecards\|COO 16]] |
| Five numbers from memory, **binding definitions**, the LTV ruling | CEO-Docs | [[17-the-numbers-a-ceo-watches\|CEO lesson 17]] |
| Unit economics, gross margin, runway | CEO-Docs | [[C12-unit-economics-and-business-model-calculator\|C12]], [[C13-runway-burn-and-scenario-planner\|C13]] |

The feed is mechanical and one-directional. **Row 2 *is* T05 row 2. Row 4 *is* T05 row 3. Row 5 feeds T05 rows 4 and 5** — same numbers, not similar ones, entered once in M13 and read by T05 at 10:00. **If a marketing and a COO number disagree, [[17-the-numbers-a-ceo-watches|CEO lesson 17]] §6.6 wins and M13 is wrong.**

## 5. The budget: ₹40k of cash, ₹78k of founder time

HC7 sets the envelope at ₹30–50k/month. Here it is at the midpoint, with a **cut-first order** decided now rather than during the panic.

| Line | ₹/mo | What it buys | Cut order |
| --- | --- | --- | --- |
| Contingency / channel experiment | 3,000 | one `Channel Experiments` test | **1st — cut first** |
| Tools (Canva, landing page, hosting) | 3,000 | minimum digital presence, [[M11-content-and-whatsapp-calendar\|M11]] | 2nd |
| Dealer Day / association | 8,000 | a ₹24k event per quarter ÷ 3 | 3rd |
| WhatsApp API + BSP fee | 3,000 | ~1,500 utility + ~500 marketing messages | 4th |
| Printing (leaflets, booklet, standee) | 4,000 | ~150 leaflets + 30 booklets | 5th |
| Video / creative (Hindi demo) | 5,000 | one shoot, phone + freelance edit | 6th |
| Fuel & travel (2 field days/week) | 8,000 | ~60 pump visits within 60 km | 7th |
| Referral payouts (Dealer Dost) | 6,000 | 3 × ₹2,000 | **8th — never cut** |
| **Total** | **₹40,000** | | |

One rule underneath the order: **cut whatever is furthest from a live conversation with an owner, first.** The WhatsApp line is real money now — roughly ₹0.86 per marketing message and ₹0.115 per utility message, plus a BSP markup of ₹0.10–0.30 and 18% GST on both ([MyOperator, 2026](https://myoperator.com/blog/whatsapp-business-api-pricing-india-2026)) — **VERIFY LIVE** with the chosen BSP; rates changed in January 2026.

**The cash budget is the small half.** Three founders selling ~15 h/week each is 45 h × ₹400 ≈ **₹78,000/month** of imputed cost, roughly twice the cash. So saving ₹5,000 of cash by spending ten extra founder hours is a **losing** trade, and the real monthly question is never "what do we spend money on" but "where do the 45 hours go." A pre-revenue budget is an **absolute** number set against runway: a CEO call ([[C13-runway-burn-and-scenario-planner|C13]]).

> **The rule for adding money to a channel:** raise a line only when that channel's **measured CAC has beaten blended CAC for two consecutive monthly reviews** *and* it has produced **≥3 paying dealers**. Cap the raise at **+50% of the line**, one channel at a time. HC4's order still binds: no paid ads before ~50 dealers and a landing page with real proof.

## 6. Vanity metrics, and the honest ones

A **vanity metric** goes up reliably, feels like progress, and cannot be traced to a paying dealer. The full ignore-list is [[13_Metrics_and_KPIs|transporters 13]] §7; four will tempt VSYST.

| Vanity number | Why it tempts | Replace it with |
| --- | --- | --- |
| **App installs** | Store dashboard, daily, only goes up | Dealers activated (row 4) — an install with no invoice is a cost |
| **Followers / group size** | 200 in a group feels like reach | WhatsApp reply rate (row 7); referrals received (row 6) |
| **Impressions / views** | Video analytics are free and generous | Demos booked from that content, in M07 |
| **Website visits** | Looks like demand | Landing page → trial started (stage 5) |

The warning is standard ([MarTech](https://martech.org/7-vanity-metrics-marketers-should-avoid-and-7-to-replace-them/); [Improvado](https://improvado.io/blog/what-is-a-vanity-metric)); our exposure is specific. **A two-sided product generates more flattering counts than a normal one.** Customer-side users are free, so "total users on DZZLO" grows beautifully while paying GSTINs stays flat. That belongs in a product report — never a marketing scorecard ([[17-the-numbers-a-ceo-watches|CEO lesson 17]] §2).

## 7. The cadence

| When | What | Output |
| --- | --- | --- |
| **Mon 09:30** | Each owner enters their own row in M13 | The week's scorecard column |
| **Mon 09:40, 15 min** | Marketing numbers huddle, on-track / off-track only; **red twice running escalates automatically** | Off-track rows into the ops issues list |
| **Mon 10:00** | COO ops meeting reads T05, which already holds rows 2, 4, 5 | Company decisions |
| **1st Monday monthly, 45 min** | **Channel review** — spend, dealers, CAC and a verdict per channel: **kill / keep / scale** | Channel table in M13; next month's budget |
| **Quarterly** | **Positioning refresh** into [[M04-positioning-and-message-house\|M04]]; goals reset with [[T19-quarterly-plan-and-review\|T19]] | Updated M04; new goals in M13 |

Two workbook tabs carry it — **`Marketing Scorecard`** (eight rows × 13 weeks) and **`CAC & Payback`** in `vsyst-cmo-workbook.xlsx`. Campaign budgets and post-mortems stay in [[M12-campaign-brief-budget-and-post-mortem|M12]]: M13 is the standing sheet, M12 is per campaign.

The verdict needs a rule or it becomes a mood. **Kill** after two months at >2× blended CAC with no improving trend; **keep** at parity; **scale** only on the two-cycle rule in §5.

## 8. At VSYST — applying this now

- **CEO (technical, ships code)** — owns row 8 and the `CAC & Payback` tab. **This week:** save the aggregations behind rows 4 and 5 as named scripts the others can run; set the ₹400/hour rate in M13 with its derivation.
- **Domain director (fuel distribution)** — owns rows 1, 2, 6. **This week:** back-fill last week's visits, demos and referral asks into [[M07-sales-pipeline-tracker|M07]] and M13 from memory and WhatsApp history.
- **Third director** — owns rows 3, 4, 5, 7. **This week:** pull the WhatsApp reply rate from the Business app stats, and reconcile trials in `dealer_msts` against the pipeline sheet; that gap is the most informative number you will see this month.
- **All three, Monday 09:40** — run the huddle, then walk into the ops meeting with rows 2, 4 and 5 filled.

**Fill the sheet anyway, with blanks where the data is not there** — a blank cell with a reason beats a filled cell with a guess.

## 9. Exercises

**9.1 — Fill the v0 scorecard for last week (30 min).** Copy the eight-row table from [[M13-marketing-scorecard-and-cac-calculator|M13]] into the `Marketing Scorecard` tab and fill **week 1** from [[M07-sales-pipeline-tracker|M07]], the WhatsApp Business stats screen and the domain director's memory. Leave rows 4, 5, 8 blank if the query does not exist, reason in the cell note. **Artefact:** one filled column, owners named on every row.

**9.2 — Compute CAC for the two channels you have used (45 min).** For the last complete quarter, list cash spend, founder hours and travel per channel separately, apply the ₹400/hour rate, divide by paying dealers from that channel. Compute blended too, then write one sentence saying what blended hides. **Artefact:** a filled `CAC & Payback` tab, CAC and payback per channel, that sentence beneath it.

**9.3 — Set next month's budget lines and get them signed (30 min).** Fill the eight budget lines in M13 inside the ₹30–50k envelope, cut-first order beside each, plus founder time (hours × ₹400) as a ninth non-cash line. Send it to the CEO for sign-off and paste the dated reply into the sheet. **Artefact:** a dated, signed-off budget block in M13, plus — if any line moved over ₹5,000 — one line in the decision log ([[T09-decision-log-and-adr|T09]]).

---

**Related:** [[05-channels-where-to-find-them-and-in-what-order|lesson 05]] · [[07-onboarding-and-activation-getting-both-sides-live|lesson 07]] · [[10-campaigns-planning-running-and-measuring-one|lesson 10]] · [[12-scaling-hiring-and-launching-the-big-campaign|lesson 12]] · [[13-reference-glossary-reading-list-and-sources|lesson 13]] · [[M13-marketing-scorecard-and-cac-calculator|M13]] · [[T05-kpi-scorecard|T05]] · [[17-the-numbers-a-ceo-watches|CEO lesson 17]] · [[12_OWNER_ACQUISITION|Owner Acquisition]]
