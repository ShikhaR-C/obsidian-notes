# App Store Economics — Free Apps, Web Subscriptions, and DZZLO's Plan

_Learning folder from a discussion on 2026-07-29: how Figma (and Netflix, Slack, Zoho…) offer free store apps yet charge subscriptions without paying the 15–30% App Store / Play Store commission — and how DZZLO OMS applies the same pattern to a company-pays subscription._

## TL;DR

1. **The stores tax in-app transactions, not apps.** Sell the subscription on the web, keep the app a free login-only companion, and the commission never applies (~2–3% card fees instead of 15–30%).
2. This is **explicitly permitted**, not a loophole: Apple 3.1.3(c) Enterprise Services + 3.1.3(f) Free Stand-alone Apps; Google's "consumption-only app" rule.
3. The one real constraint is **anti-steering**: no purchase buttons, prices, links, or webviews inside the app or its store listing (US storefront is now exempt after Epic v. Apple; **India is not**).
4. Selling still works because every **outside-the-app channel is fair game** — web console, email, WhatsApp, sales — and in B2B the app user isn't even the buyer; the company owner is.
5. **DZZLO decision (2026-07-29): dealer companies subscribe (per GSTIN), users are unlimited and never charged, all billing on web, app features gated server-side by the company's plan.**

## Notes

| #   | Note                                  | What's in it                                                                                                  |
| --- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| 1   | [[01-figma-business-model]]           | Freemium per-editor seats, free viewers as the growth engine, NDR 136%, FY2025 ~$1B revenue, 2026 seat prices |
| 2   | [[02-how-figma-avoids-store-tax]]     | The four mechanics + exactly which rules make it legal                                                        |
| 3   | [[03-companies-that-do-this]]         | Netflix, Spotify, Kindle, Slack, Notion, Zoom, Zoho, Canva; HEY-vs-Apple and Fortnite cautionary tales        |
| 4   | [[04-apple-app-store-rules]]          | **Verbatim** App Store Review Guidelines §3.1.1–3.1.3(g) + commission table + India note                      |
| 5   | [[05-google-play-store-rules]]        | **Verbatim** Play Payments policy: requirement, consumption-only FAQ, anti-steering list, fees, India UCB     |
| 6   | [[06-epic-rulings-timeline]]          | Epic v. Apple & Epic v. Google 2020→2026: how the US carve-outs and fee caps happened                         |
| 7   | [[07-upselling-without-a-buy-button]] | How upgrades get sold with zero in-app purchase UI: channel matrix + the Slack "ask your admin" funnel        |
| 8   | [[08-dzzlo-subscription-strategy]]    | Applying it all to DZZLO: decision, compliance FAQ, app-vs-web feature split, 6-phase implementation plan     |
| 9   | [[09-driving-web-adoption-for-features]] | Feature steering is unrestricted — signposts, teasers, magic-link handoffs, GST-calendar moments, PWA         |
| 10  | [[10-pricing-metric-decision]]        | What the subscription is ON: metric scoring, 3-layer model (flat tiers → payments take-rate → fleet slabs)    |

## Related elsewhere in the vault

- Pricing research: `../company/02_PRICING_STRATEGY.md`, `../company/10_AFFORDABILITY_PROBLEM.md`, `../company/13_REVENUE_GENERATION.md`
- Payment-gateway thread: `../../../correspondence/IPG_Easebuzz/problem-statement.md`
- Build hooks: `../../tasks/tasks_09_sadmin_settings/`, `../../tasks/tasks_11_partner_api/`, `../../tasks/tasks_10_analytics_events/`
