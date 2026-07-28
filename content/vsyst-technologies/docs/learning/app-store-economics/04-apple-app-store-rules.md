# 4. Apple App Store Rules — Exact Text (Payments)

Source: [App Store Review Guidelines §3.1](https://developer.apple.com/app-store/review/guidelines/), fetched 2026-07-29. Quotes are verbatim; emphasis added.

## 3.1.1 In-App Purchase — the default rule

> "If you want to unlock features or functionality within your app, (by way of example: subscriptions, in-game currencies, game levels, access to premium content, or unlocking a full version), **you must use in-app purchase**. Apps may not use their own mechanisms to unlock content or functionality, such as license keys, augmented reality markers, QR codes, cryptocurrencies and cryptocurrency wallets, etc."

This is the rule that creates the 15–30% commission. Everything below is the map of exits.

## 3.1.1(a) Link to Other Purchase Methods

> "Developers may apply for entitlements to provide a link in their app to a website the developer owns or maintains responsibility for in order to purchase digital content or services. **These entitlements are not required for developers to include buttons, external links, or other calls to action in their United States storefront apps.**"

> "In all other storefronts, except for the United States storefront, where this prohibition does not apply, **apps and their metadata may not include buttons, external links, or other calls to action that direct customers to purchasing mechanisms other than in-app purchase.**"

⚠️ **India note:** the link-out freedom is **US storefront only** (result of Epic v. Apple — see [[06-epic-rulings-timeline]]). On the India storefront the old strict rule still applies: **no purchase links, no "buy on our website" buttons, not even in App Store metadata.**

## 3.1.3 Other Purchase Methods — the exits

> "The following apps may use purchase methods other than in-app purchase. **Apps in this section cannot, within the app, encourage users to use a purchasing method other than in-app purchase**, except for apps on the United States storefront and as set forth in 3.1.1(a) and 3.1.3(a). **Developers can send communications outside of the app to their user base** about purchasing methods other than in-app purchase."

Note the last sentence: **email/WhatsApp/web marketing about pricing is always allowed** — the gag order applies only inside the app and its store listing.

### 3.1.3(a) "Reader" Apps

> "Apps may allow a user to access previously purchased content or content subscriptions (**specifically: magazines, newspapers, books, audio, music, and video**). Reader apps may offer account creation for free tiers, and account management functionality for existing customers."

Netflix/Spotify/Kindle live here. Note the closed list — a business tool is _not_ a reader app.

### 3.1.3(b) Multiplatform Services

> "Apps that operate across multiple platforms may allow users to access content, subscriptions, or features they have acquired in your app on other platforms or your web site, including consumable items in multi-platform games, **provided those items are also available as in-app purchases within the app**."

⚠️ The catch: (b) only works if you _also_ sell via IAP. Pure web-billed products rely on (c) and (f) instead.

### 3.1.3(c) Enterprise Services ← **key for B2B (DZZLO)**

> "**If your app is only sold directly by you to organizations or groups for their employees or students** (for example professional databases and classroom management tools), **you may allow enterprise users to access previously-purchased content or subscriptions.** Consumer, single user, or family sales must use in-app purchase."

Company-pays subscriptions with employee logins are explicitly exempt from IAP.

### 3.1.3(d) Person-to-Person Services

> "If your app enables the purchase of real-time person-to-person services between two individuals (for example tutoring students, medical consultations, real estate tours, or fitness training), you may use purchase methods other than in-app purchase to collect those payments. One-to-few and one-to-many real-time services must use in-app purchase."

### 3.1.3(e) Goods and Services Outside of the App ← **physical goods (fuel!)**

> "If your app enables people to purchase physical goods or services that will be consumed outside of the app, **you must use purchase methods other than in-app purchase** to collect those payments, such as Apple Pay or traditional credit card entry."

Payments for **physical goods are not just exempt — IAP is forbidden for them.** Fuel orders, delivery charges, advance deposits against physical product all fall here (this is why Swiggy/Uber/Amazon retail pay no store tax).

### 3.1.3(f) Free Stand-alone Apps ← **the Figma rule**

> "**Free apps acting as a stand-alone companion to a paid web based tool** (i.e. VoIP, Cloud Storage, Email Services, Web Hosting) **do not need to use in-app purchase, provided there is no purchasing inside the app, or calls to action for purchase outside of the app.**"

### 3.1.3(g) Advertising Management Apps

> "Apps for the sole purpose of allowing advertisers … to purchase and manage advertising campaigns across media types … do not need to use in-app purchase."

---

## Commission Rates (for when IAP _does_ apply)

| Case                                                   | Apple's cut                                                                             |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| Standard                                               | 30%                                                                                     |
| Auto-renewing subscription after subscriber's 1st year | 15%                                                                                     |
| Small Business Program (dev earns < $1M/yr)            | 15%                                                                                     |
| US storefront web link-out purchases                   | **0% currently** — whether Apple may charge a "reasonable" fee is still in court (2026) |

## What This Means in Practice

1. Sell to companies on the web → **3.1.3(c) + (f)** shelter the free app completely.
2. Keep the app purchase-silent: no buy buttons, no prices, no external purchase links (non-US storefronts).
3. Collect payments for **physical goods** (fuel) with your own gateway — **required**, per (e).
4. Market pricing freely **outside** the app: email, web, WhatsApp.
