# 8. DZZLO Subscription Strategy — Applying the Figma Pattern

_Discussion of 2026-07-29. Product facts verified against the v1_79 repos and vault docs on that date._

## Where We Are Today

- **Product**: two-sided B2B credit-trade OMS for Indian fuel distribution — dealer firms (`dealer_msts`) ↔ transport/customer firms (`cust_msts`) sharing one non-deletable ledger, with GST/TCS/TDS rails. Multi-PSO (IOCL/BPCL/HPCL via `psocs`), India-only by design.
- **Surfaces**: free mobile app on both stores (`in.vsyst.dzzlooms`, v1.78 — [Play](https://play.google.com/store/apps/details?id=in.vsyst.dzzlooms) / [App Store id1553062924]); **dip-web** console (dealer DIP module + VSYST superadmin); `api_v3` backend.
- **Roles**: `dealer`/`customer` roles × six scopes each (Primary/Admin/Order/Account/OrderAccount/View), `SAdmin` = VSYST staff. Drivers are not logins — they only receive delivery OTPs.
- **Billing code today: none.** No gateway, no plan model, no entitlement checks anywhere in the three repos. Easebuzz/UBI is a live _negotiation_ (see `correspondence/IPG_Easebuzz/problem-statement.md`), not an integration. Company-level subscription is greenfield.
- **Prior thinking already in the vault**: `docs/learning/company/02_PRICING_STRATEGY.md` (per-tenant flat pricing, tier sheet, Kano gating), `10_AFFORDABILITY_PROBLEM.md` (ATP constraint, hybrid take-rate idea), `13_REVENUE_GENERATION.md` (MRR milestones). `00_OVERVIEW.md` names the **dealer as the paying tenant**.

## The Decision (2026-07-29)

> **Companies subscribe. Users are never charged, no matter how many the company adds.**

Concretely:

1. **Every company is its own billable tenant** (per GSTIN / `co_id`). **Dealers pay first** (consistent with `00_OVERVIEW.md`); **customer firms are planned to pay too in a future phase, for fleet-management features** (decided 2026-07-29). **Sister companies each carry their own subscription** — no shared or bundled free-riding. Individual users, staff, and drivers never pay: Figma's free-viewer logic applies to _people_, not companies (see [[01-figma-business-model]]). Recommendation to preserve the two-sided network: keep the customer firm's core trading with dealers (ordering, shared ledger) on a free tier and charge them for the fleet value-add (Vehicles/VehicleReports/`veh_trns` are the seed of that module).
2. **Unlimited users on every tier.** This _adjusts_ `02_PRICING_STRATEGY.md`, whose tier sheet capped staff users (2/10/∞): keep its per-tenant flat, GSTIN-bound model and price points, but gate on **transactions/month, branches, and features — never on headcount**. (The doc itself argues per-seat is wrong for Indian SMBs; we're taking that logic all the way.)
3. **All money to VSYST moves on the web** — the app stays a free, purchase-silent companion (Apple 3.1.3(c)+(f), Google consumption-only; see [[04-apple-app-store-rules]], [[05-google-play-store-rules]]).

## "Won't Apple/Google Know We Enable Features From Web Payments?"

They can see your app and your website; they cannot see your server or your payments — **and it doesn't matter, because there is nothing to hide.** Server-side entitlements for subscriptions bought elsewhere are the _explicitly documented, permitted pattern_: Google's FAQ literally blesses "log in … and access content paid for somewhere else," and Apple's 3.1.3(c)/(f) exist precisely for apps like ours. Netflix, Slack, Zoho, and Figma do this in the open.

What actually gets apps rejected:

| Risk                                                                             | Mitigation                                                                                                                                     |
| -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Purchase buttons/links/prices in the app or store listing (steering)             | Never ship them (India storefront = strict rules; see [[07-upselling-without-a-buy-button]])                                                   |
| App is a dead login wall at download (the HEY-vs-Apple problem)                  | App already works via phone-OTP onboarding + invites; give reviewers a **demo account** on a representative plan in App Review notes           |
| "Hidden features" deception (Apple 2.3.1 — app behaves differently after review) | Plan-gating of documented business features is normal SaaS entitlement, not concealment; keep gated features visible-but-locked where sensible |

## Feature Split by Accessibility

Principle: **field transactions belong in the app; administration, compliance, configuration, and anything involving money to VSYST belong on the web.** People at the pump or on the road are phone-first; owners and accountants sit at desks; VSYST staff are web-only.

| Surface                                        | Who                                               | Features                                                                                                                                                                                                                                                                                           |
| ---------------------------------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Mobile app** (free, field, on-the-go)        | Pump staff, transporter staff, owners on the move | Order placement & approval, sales orders, delivery OTP flow, invoices & payment _recording_ (vouchers, pay-ack), rate-confirmation in the 10 PM–6 AM window (push), vehicles & vehicle reports, requests/invites, daily summary, ledger lookup, advance-deposit view                               |
| **Web — dip-web grown into the owner console** | Owners (`DPrimary`), accountants, VSYST           | Existing: DIP wet-stock module (tanks/DUs/nozzles/decants/meter reads/inspections), masters, superadmin ops. Add: **subscription & billing portal**, user/role administration, credit-limit configuration, TCS/TDS + GST reports and bulk exports, analytics dashboards, partner-API keys (future) |
| **Public website** (build)                     | Prospects                                         | Marketing + **pricing page** + signup/trial start + payment checkout — the store-rule-free selling surface                                                                                                                                                                                         |
| **Both**                                       | All                                               | Orders/invoices/payments lists, shared ledger view                                                                                                                                                                                                                                                 |

So: _"should we build a website that has important features and make the app free?"_ — the app **is already free** and dip-web already exists; the move is to **extend dip-web into the paid-admin console and add a public pricing/checkout site**, not to move field features out of the app.

_"Can we show extra features for premium companies?"_ — **yes**: entitlements resolved server-side per company; the app renders or locks accordingly. Never gate compliance basics (GST invoice, core ledger — the Kano floor from `02_PRICING_STRATEGY.md`); usage-gate transactions/branches/WhatsApp sends; feature-gate analytics, WhatsApp automation, multi-branch, DIP module (already package-gated per resource — a natural paid add-on), partner API at the top.

## Implementation Plan

**Phase 0 — Decisions (product, ~1 week of thinking, no code)**
Sign off: tier sheet (₹599/₹1,799/₹4,999 + Enterprise ex-GST from `02_PRICING_STRATEGY.md`, users unlimited), trial policy (14-day no-card reverse trial per the doc), grandfathering existing paying tenants, and how far to wait on Easebuzz/UBI before pricing is final (`10_AFFORDABILITY_PROBLEM.md` couples the take-rate idea to the IPG). Billed entity is settled (2026-07-29): every company — dealer or customer, including each sister company — is its own subscription per GSTIN; commercial multi-company discounts, if any, live at invoice level, never as shared entitlements.

**Phase 1 — Entitlement backbone (dzzlo_oms_api)**
New `plans` (versioned, append-only price book — reuse the `partner_pricing` shape already designed in `tasks_11_partner_api` Phase 6) and `subscriptions` keyed by `co_id`, **polymorphic over `dealer_msts` | `cust_msts` from day one** (same `refPath`/`onModel` pattern as `users.co_id`) — dealers activate first; customer-side fleet plans arrive later with zero schema change. Fields: plan, status (`trial/active/past_due/cancelled`), period, entitlement snapshot. An entitlement resolver middleware in `api_v3` (next to `check_user_company_status()`) attaches `req.entitlements`; premium checks **fail closed** (note: `tasks_09_sadmin_settings`' "config is an override, never a dependency" rule is the _opposite_ of what entitlements need — its `feature_flags` object is global, not per-tenant, so extend, don't reuse as-is). Expose entitlements in the login/me payload so clients only _render_ state, never compute it.

**Phase 2 — Sales-led v0 billing (dip-web superadmin) — ship before any gateway**
SAdmin screen to assign/change a company's plan + record an offline NEFT payment; VSYST GST invoice PDF (Puppeteer + ExcelJS already in the API) emailed via existing AWS SES. This matches how the first ~50 dealers will actually buy (CA- and Territory-Manager-led sales per `13_REVENUE_GENERATION.md`) and proves the entitlement rails with zero payment-integration risk.

**Phase 3 — App gating & store compliance (dzzlo_oms_app v1.79+)**
Entitlement-aware gates: hidden or visible-but-locked features, neutral lock screen ("Not part of your company's plan — ask your company owner"), optional **Notify-owner** internal request (Slack mechanic). Zero prices/links/upgrade buttons; scrub store listings; App Review demo account + notes. Trial state just renders what the server says. Remember: no OTA — this rides a normal store release behind the existing server-side version gate.

**Phase 4 — Self-serve billing (web)**
When the Easebuzz/UBI deal lands: public pricing page + checkout, **UPI Autopay / eNACH e-mandate** for recurring collection, dunning (`past_due` → grace → downgrade), owner-facing billing portal in dip-web (plan, invoices, payment method). Note the IPG problem-statement's own constraints: net-banking-first, flat/waived fees, aggregator settles direct — VSYST subscription collection is a _separate, simpler_ flow from the dealer↔customer invoice-payment leg.

**Phase 5 — Growth loop**
Instrument quota usage via `tasks_10_analytics_events`; trigger owner-surface nudges (SES email, WhatsApp, dip-web banners) at 80%/100% of transaction/branch quotas; upgrade CTAs live only on those surfaces per [[07-upselling-without-a-buy-button]].

**Phase 6 — Expansion revenue**
Partner API tiers (`tasks_11`, the designed metering/invoice roll-up), DIP module as add-on, **customer-side fleet-management plans** (the decided second act: paid tier for `cust_msts` built on Vehicles/VehicleReports/`veh_trns`), and — if the IPG take-rate model wins — 0.3–0.5% of GMV processed with a lower flat base, per `10_AFFORDABILITY_PROBLEM.md`.

## Open Questions

### Answered 2026-07-29 (owner decisions)

1. **Customer-side firms will pay in the future — for fleet management.** Implications: the Phase 1 `subscriptions` schema is polymorphic (`dealer_msts` | `cust_msts`) from day one; fleet features become the customer-side premium module. Recommendation kept alongside the decision: leave the customer firm's core dealer-trading (ordering, shared ledger) free so the network keeps compounding — charge for the fleet value-add.
2. **No sister-company bundles: each sister company (each GSTIN / `co_id`) pays its own subscription.** Any multi-company discount is a commercial/invoice matter, never shared entitlements.

### Still open

3. `tasks_08` migration execution against production is still unverified — land that before entitlement middleware touches the same request path.
4. Final price points: hold until the UBI/Easebuzz outcome clarifies whether the hybrid (low base + take-rate) beats flat tiers. Customer-side fleet-plan pricing is a fresh Phase 0 question when that phase approaches.

## Related

[[01-figma-business-model]] · [[02-how-figma-avoids-store-tax]] · [[03-companies-that-do-this]] · [[04-apple-app-store-rules]] · [[05-google-play-store-rules]] · [[06-epic-rulings-timeline]] · [[07-upselling-without-a-buy-button]] · vault: `docs/learning/company/02_PRICING_STRATEGY.md`, `10_AFFORDABILITY_PROBLEM.md`, `13_REVENUE_GENERATION.md`, `docs/tasks/tasks_09_sadmin_settings`, `tasks_11_partner_api`, `tasks_10_analytics_events`
