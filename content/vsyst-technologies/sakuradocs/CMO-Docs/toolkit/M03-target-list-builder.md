# M03 — The Named Target List (Raipur 100) — sources and columns

_Toolkit · fills exercise 8.3 in [[03-who-exactly-icp-personas-and-the-target-list|03 — Who Exactly]] · Owner: the domain director owns the list; the third director owns source hygiene · Cadence: 30 rows in Week 1, 100 by Week 4, groomed every Monday · Workbook tab: `Target List` in [vsyst-cmo-workbook.xlsx](vsyst-cmo-workbook.xlsx)._

## Purpose

One sheet, a hundred **named** pumps, ranked, each with a route to an introduction. It is the difference between "we're targeting Raipur dealers" and "Tuesday morning I am visiting these four, and Verma-ji is calling ahead for two." Everything downstream — the pipeline in [[M07-sales-pipeline-tracker|M07]], the visit plan in [[06-founder-led-sales-the-pump-visit-demo-and-close|lesson 06]], CAC by channel in [[M13-marketing-scorecard-and-cac-calculator|M13]] — is computed off it. Build it badly and every later number is fiction. It is also the **denominator for HC3**: saturating Raipur means ~60% of ICP pumps within 60 km, and you cannot claim a percentage without a count.

## When to use

- **Week 1**: first 30 rows (exercise 8.3). **Week 4**: 100 rows.
- **Every Monday, 20 minutes**: statuses, next actions, names heard last week.
- **Whenever a dealer signs**: add his five biggest credit customers as customer-side rows (HC2, [[07-onboarding-and-activation-getting-both-sides-live|lesson 07]]).

## How to fill (rules)

1. **A row is a pump, not a company.** One dealer with two outlets is two rows, cross-referenced.
2. **No row without an owner's name.** "IOCL pump, Tatibandh" is not a lead — get the name from the locator, Maps or the domain director before scoring.
3. **Estimated fields are marked `est.`** and replaced after the first visit. An estimate that silently becomes fact is how a pipeline lies.
4. **One internal owner, one next action, one date, per row.** No date, no action, row is dead.
5. **Disqualified rows stay**, status `DQ` with a re-look date ([[M02-icp-and-persona-field-cards|M02]]) — or you research them again in three months.
6. **Re-score after every visit.** Pump #3 changes pump #11.

## Template — the `Target List` tab

| Column | Type | Notes |
| --- | --- | --- |
| Pump name | text | As on the board, not the locator |
| OMC | IOCL / BPCL / HPCL / other | Decides which territory manager can help |
| Location · km from Raipur | text · number | Straight-line km; drives clustering |
| Owner name | text | Mandatory before scoring |
| Second-gen? | Y / N / unknown | The strongest nice-to-have |
| Est. B2B credit customers | number | `est.` until the first visit |
| Credit volume band | A ₹50L+/mo · B ₹15–50L · C <₹15L | Rough is fine; wrong-by-a-band is not |
| Intro path | text | Who introduces us, by name — or `none yet` |
| Priority score | 0–50 | Computed, see rubric |
| Status | New · Researching · Intro requested · Visited · Demo · Trial · Won · Lost · DQ | Mirrors [[M07-sales-pipeline-tracker|M07]] |
| Next action + date | text · date | Mandatory |
| Owner (ours) | CEO / domain / third director | One name |

**Scoring rubric.** Four factors, each 1–5, weighted; maximum 50.

| Factor | Weight | 5 | 3 | 1 |
| --- | --- | --- | --- | --- |
| B2B credit volume | ×3 | 20+ credit customers, band A | 8–15 customers, band B | Cash/UPI only |
| Second-generation presence | ×2 | Son/daughter running operations | Involved but not deciding | Owner 65+, nobody younger |
| Distance from Raipur | ×2 | ≤20 km | 21–40 km | 60 km+ |
| Intro path strength | ×3 | The domain director knows him | A CA or association contact | None yet |

**Bands: A ≥ 38 · B 26–37 · C ≤ 25.** Work A first, in geographic clusters so one morning covers four pumps.

**Weekly maintenance rule.** Every Monday before the ops meeting: no row older than 14 days without a status change; every A row carries a dated next action; last week's new names added; last week's visits re-scored. Ungroomed for three weeks, it is a list nobody trusts.

## Sources

| Source | Gives you | URL |
| --- | --- | --- |
| IndianOil locator | Names, addresses, phones, timings | [locator.iocl.com/location/chhattisgarh/raipur](https://locator.iocl.com/location/chhattisgarh/raipur) |
| BPCL fuel-station locator | Stations by state / district | [bharatpetroleum.in/fuel-station-locator](https://www.bharatpetroleum.in/fuel-station-locator) |
| HPCL retail-outlet list | Dealer details by state/UT, plus a map locator | [rooutletlist](https://www.hindustanpetroleum.com/rooutletlist) · [petrolpump.hpretail.in](https://petrolpump.hpretail.in/) |
| PPAC statewise retail outlets | The denominator: Chhattisgarh had **2,587 outlets on 1 April 2026**, 2,363 a year earlier | [PPAC](https://ppac.gov.in/infrastructure/retail-outlets) · [XLS](https://ppac.gov.in/uploads/page-images/1787131130_Statewise_Retail_Outlets.xls) |
| Consumer directories | Gap-fill and phones — ~275 pumps listed around Raipur city; **VERIFY LIVE**, a scrape | [CarDekho](https://www.cardekho.com/fuel-stations/raipur) |
| Association rolls | Office-bearers and member lists | [AIPDA (national)](https://www.pib.gov.in/PressReleseDetailm.aspx?PRID=2145847) · [VPDA (model)](https://www.vpda.co.in/) |
| Hardware service engineers | Who is automated — quarterly visitors to every pump | [Gilbarco India](https://www.gilbarco.in/) |
| Domain director's phone; the OMC territory manager | The intro path — the one column nobody can scrape | [[discussion-document\|IOCL discussion document]] |

## Worked example — VSYST (illustrative)

**All five rows below are fictional** — invented names and numbers, showing the shape of a filled sheet. None is a real pump.

| Pump name | OMC | Location · km | Owner | 2nd gen? | Est. credit custs | Band | Intro path | Score | Status | Next action + date | Ours |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Maa Danteshwari Fuels *(fictional)* | IOCL | Tatibandh · 8 | R. Verma | Y | 24 est. | A | Domain director — school friend | **50** | Intro requested | Call Verma-ji, ask for Tues slot — 02 Sep | Domain dir. |
| Highway Auto Centre *(fictional)* | BPCL | NH-53, Kharora · 34 | S. Sahu | Y | 30 est. | A | Transporter who fuels there | **40** | New | Visit on the Kharora cluster run — 05 Sep | Domain dir. |
| Shree Balaji Filling *(fictional)* | HPCL | Bhanpuri · 11 | M. Agrawal | N | 12 est. | B | Our CA handles his books | **30** | Researching | CA to introduce over WhatsApp — 03 Sep | CEO |
| Ring Road Fuels *(fictional)* | IOCL | Ring Rd 2 · 6 | K. Dewangan | unknown | 4 est. | C | none yet | **20** | New | Walk-in during Tatibandh cluster — 09 Sep | Third dir. |
| City Point Petroleum *(fictional)* | BPCL | Pandri · 4 | (manager-run, owner in Dubai) | N | 0 | C | — | **18** | DQ | Re-look Mar 2027 | — |

Read the last two rows as the point of the sheet: **20 and 18 are not visits, they are a reason to spend Tuesday on 50 and 40 instead.**

## Common mistakes

1. **Rows without owner names.** An address is not a lead.
2. **Scoring on enthusiasm.** The score is four numbers. To visit a C-row, change a number and say which.
3. **Deleting disqualified pumps** instead of `DQ` with a date — you will research them again.
4. **Never re-scoring.** Pre-visit estimates are the most dangerous numbers on the sheet.
5. **Building the customer side from directories.** They come from the dealer, once he is live (HC2).
6. **Letting it rot.** Twenty minutes every Monday, or it is a museum.

## Related

Lesson [[03-who-exactly-icp-personas-and-the-target-list|03]] · [[M02-icp-and-persona-field-cards|M02]] · [[M07-sales-pipeline-tracker|M07]] · [[M10-partner-and-channel-playbook|M10]] · [[M13-marketing-scorecard-and-cac-calculator|M13]] · [[C09-icp-and-customer-discovery-guide|C09]] · [[12_OWNER_ACQUISITION|Owner Acquisition]] · [[CMO-Docs/toolkit/index|CMO Toolkit]]
