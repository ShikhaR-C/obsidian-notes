# 5. Google Play Store Rules — Exact Text (Payments)

Sources: [Play Payments policy](https://support.google.com/googleplay/android-developer/answer/9858738) and [Understanding Google Play's Payments policy](https://support.google.com/googleplay/android-developer/answer/10281818), fetched 2026-07-29. Quotes verbatim; emphasis added.

## The Requirement

> "Play-distributed apps requiring or accepting payment for access to in-app features or services … **must use Google Play's billing system** for those transactions unless Section 3, 8, or 9 applies."

What counts as in-app digital goods (examples given by the policy):

> "Items (such as virtual currencies, extra lives, additional playtime, add-on items, characters, and avatars); **subscription services** (such as fitness, game, dating, education, music, video, **service upgrades**, and other content subscription services); app functionality or content (such as an ad-free version of an app or new features not available in the free version); and **cloud software and services (such as data storage services, business productivity software, and financial management software)**."

⚠️ Note: business SaaS **is** on the list — the exemption is not "we're B2B", it's "**we don't transact inside the app**" (next section).

## The Consumption-Only Exemption ← **the Figma/DZZLO rule**

From Google's own FAQ, verbatim:

> **Q: "Can I offer a consumption-only (reader) app on Google Play?"**
> **A: "Yes. Google Play allows any app to be consumption-only, even if it is part of a paid service. For example, a user could log in when the app opens and access content paid for somewhere else. Remember, consumption-only means that any product(s) or service(s), whether digital or physical, cannot be purchased from within the app."**

Unlike Apple's closed "reader" category, Google allows **any app** to be consumption-only — no category test at all.

## When Play Billing is FORBIDDEN (physical goods)

Play billing **must not** be used when:

> "payment is primarily: **for the purchase or rental of physical goods** (such as groceries, clothing, housewares, electronics); for the purchase of physical services (such as transportation services, cleaning services, airfare, gym memberships, food delivery, tickets for live events); or a remittance in respect of a credit card bill or utility bill"

Fuel orders and their payments are physical-goods payments → own gateway (Easebuzz etc.) is the _required_ path, commission-free.

## Anti-Steering — what the app may NOT do

> "apps may not lead users to a payment method other than Google Play's billing system. This prohibition includes, but is not limited to, leading users to other payment methods via:
>
> - An app's listing in Google Play;
> - In-app promotions related to purchasable content;
> - **In-app webviews, buttons, links, messaging, advertisements, or other calls to action**; and
> - In-app user interface flows, including account creation or sign-up flows, that lead users from an app to a payment method other than Google Play's billing system"

But **outside the app** is free territory:

> "you are free to communicate with your users about alternative purchase options. You can use email marketing and other channels outside of the app to provide subscription offers and even special pricing."

## Service Fees (when Play billing _does_ apply)

| Case                                                   | Google's cut                                                                                   |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| First $1M/yr (enrolled)                                | 15%                                                                                            |
| Above $1M/yr                                           | 30%                                                                                            |
| Auto-renewing subscriptions                            | 15% from day one                                                                               |
| Media-experience programs                              | as low as 10%                                                                                  |
| **User Choice Billing** (own gateway alongside Play's) | fee reduced by ~4 points (so ~11%/26%) — **available in India since 2023 after the CCI order** |

## United States — post-Epic changes (context)

The Epic v. Google injunction (affirmed July 2025, effective after SCOTUS declined a stay in Oct 2025) forced Google to allow **external payment links and alternative billing in US apps from Dec 9, 2025**. The March 4, 2026 Epic–Google settlement converts this into a **global framework through June 2032** with capped service fees (9% or 20% tiers, plus ~5% if Play billing itself is used). Rollout is ongoing — see [[06-epic-rulings-timeline]]. India additionally has the **CCI ruling (Oct 2022)** that produced User Choice Billing for all India developers.

## What This Means in Practice

1. A **consumption-only app is explicitly blessed** — company subscribes on the web, users log in on Android free.
2. Keep every purchase flow, link, webview, and CTA out of the app **and out of the Play listing**.
3. Fuel/physical payments must use your own gateway anyway.
4. Email/WhatsApp/website pricing promotion is explicitly allowed.
