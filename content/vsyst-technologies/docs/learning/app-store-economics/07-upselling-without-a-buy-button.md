# 7. How Do We Ask Users to Upgrade With No Purchase Button in the App?

The worry: _"If the app can't have a buy button, how do we ever sell upgrades?"_

The answer: **the ban covers in-app buttons, links, prices, and webviews — not selling.** Both stores explicitly leave every other channel open. And because DZZLO is B2B, the person who pays (the company owner) doesn't even need to be sold to inside the app.

## What the Rules Actually Permit

Apple, verbatim ([[04-apple-app-store-rules]]):

> "Developers can send communications **outside of the app** to their user base about purchasing methods other than in-app purchase."

Google, verbatim ([[05-google-play-store-rules]]):

> "you are free to communicate with your users about alternative purchase options. You can use **email marketing and other channels outside of the app** to provide subscription offers and **even special pricing**."

## Channel Matrix

| Channel                                                         | Allowed?                            | Notes                                                                                                             |
| --------------------------------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Website / web console (dip-web)**                             | ✅ Unrestricted                     | Store rules don't apply to the web. Pricing page, Upgrade buttons, billing portal, trial banners — all live here. |
| **Email**                                                       | ✅ Explicitly allowed               | Both stores say so in writing (quotes above).                                                                     |
| **WhatsApp / SMS / phone / field sales**                        | ✅ Outside the app                  | In India, WhatsApp Business is probably our #1 upsell channel.                                                    |
| **Push notifications**                                          | ⚠️ With opt-in                      | Apple 4.5.4 allows marketing pushes only with explicit user opt-in. Use sparingly; target company owners.         |
| **In-app: feature gating**                                      | ✅                                  | Features may be hidden or shown locked based on the company's plan (set server-side).                             |
| **In-app: "contact your admin/owner"**                          | ✅ (careful)                        | A neutral lock message pointing at a _person_ is fine. No price, no link, no "upgrade" button.                    |
| **In-app: prices, Upgrade buttons, links/webviews to checkout** | ❌ (India & all non-US storefronts) | This is the actual prohibition.                                                                                   |
| **App Store / Play listing text**                               | ❌                                  | Metadata is covered by the same anti-steering rules — no "cheaper on our website".                                |

## The B2B Trick: the App User Isn't the Buyer

In consumer apps (Netflix), the viewer and the payer are the same person — that's why the gag order hurts them. In DZZLO, **staff, drivers, and customers use the app, but the dealer/company owner pays** — and owners can be reached on owner surfaces: the web console, email, WhatsApp, and our sales team.

This is exactly how Slack does it: an end user hits a locked feature and sees _"Ask your workspace admin"_; the admin gets the pricing pitch by email and in the web dashboard. The app itself never sells.

## The Upgrade Funnel (recommended)

1. **User hits a gated feature in the app** → neutral lock screen: _"Reports are not part of your company's plan. Ask your company owner."_ Optionally a **"Notify owner"** action that sends an internal request to the owner (Slack's mechanic — it's a message to a person, not a purchase mechanism, so it's clean).
2. **Owner gets the pitch on unrestricted surfaces** — email + WhatsApp + a banner in the web console: features, price, one-click upgrade.
3. **Owner pays on the web** (payment gateway / UPI Autopay e-mandate — see [[08-dzzlo-subscription-strategy]]).
4. **Server flips the company's entitlements** → the app quietly gains the features for everyone in that company. No store involved at any step.

Supporting patterns:

- **Full-featured trial, server-side**: new companies start with everything on; at expiry the plan reverts and the _email/web_ carries the conversion push. The app just reflects state.
- **Plan visibility without selling**: the app may show "Current plan: Starter" as a fact. Keep it a statement, never a button.
- **Launch offers / discounts**: fine everywhere _except_ inside the app and the store listings.

## Renewal & Payment Reminders (when the next payment is near)

A renewal reminder is **account information, not selling** — but the same channel discipline applies: the price and the pay button live outside the app; the app may only state facts, and only to the **owner** (staff, drivers, and customer firms never see billing at all).

### The reminder ladder

| When                         | Channel                                                                                                                                      | Message                                                                                                                               | Store-safe because…                                                                                              |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **D-7**                      | Email (SES) + WhatsApp utility template                                                                                                      | "Your DZZLO Growth plan renews on 5 Aug — ₹1,799. Invoice attached. Pay/manage: dzzlo.in/billing" — full CTA, price, link             | Outside the app: explicitly allowed                                                                              |
| **D-3**                      | WhatsApp/SMS reminder + push to owner only                                                                                                   | Push: _"Your company's DZZLO plan renews in 3 days."_ No price, no link — tapping opens the app's neutral status screen               | Transactional account info, not a promo (Apple 4.5.4 gates _marketing_ pushes behind opt-in — keep it fact-only) |
| **D-0**                      | **Auto-debit** (UPI Autopay / eNACH mandate)                                                                                                 | NPCI/RBI rules force a **pre-debit notification** from the payment ecosystem 24–48h before the charge — the "reminder" is sent for us | Not our app at all                                                                                               |
| **Failed → grace (D+1…D+7)** | Email/WhatsApp retries + in-app banner to owner: _"Plan payment pending — service continues until 12 Aug. Manage on the DZZLO web console."_ | Neutral status, no tappable link/price/button                                                                                         |
| **D+8**                      | Server downgrades entitlements                                                                                                               | Keep the ledger/GST data **read-only, never bricked** — it's the dealer's books (Kano floor from `02_PRICING_STRATEGY.md`)            |

### In-app status rules (India storefront)

- **May show (owner only):** plan name, renewal/expiry date, "payment pending" state, and "managed on the DZZLO web console" as plain text.
- **Never show:** a Renew/Pay button, tappable checkout links or webviews, price next to any call-to-action. Conservative default: keep amounts out of the app entirely; they belong on the invoice email and the web billing page.

### The structural fix: don't remind — auto-collect

The e-mandate (Phase 4 of [[08-dzzlo-subscription-strategy]]) turns renewal into a background debit with a regulator-mandated advance notification, so the reminder problem only exists for **mandate failures** — which the grace ladder above handles. And for the first sales-led dealers (Phase 2), the honest renewal mechanism is a phone call from us or the CA — Indian B2B renewals are relationship-driven.

## Getting Owners Onto the Website

The app can't carry a tappable road to checkout, so the link must reach the owner through other doors — and the landing must be frictionless when they arrive.

### Routes that carry a real link

| Route                              | How                                                                                                                 | Notes                                                                                        |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **WhatsApp**                       | Utility template with a **URL button** ("View invoice" / "Manage plan")                                             | The primary artery in India — owner taps straight into the billing page                      |
| **Email (SES)**                    | Every onboarding/invoice/reminder mail carries a `dzzlo.in/billing` button                                          | ⚠️ Prereq: **capture the owner's email at onboarding** — today onboarding is phone-OTP-first |
| **SMS**                            | DLT-registered transactional template with a short tokenized link                                                   | Works on any phone, no smartphone assumptions                                                |
| **Printed QR**                     | The VSYST GST invoice PDF (Puppeteer already in the API) and dealer-meet pamphlets carry a QR to the billing portal | The fuel trade runs on paper — meet it there                                                 |
| **Sales / CA / Territory Manager** | Human sends the link on a call or visit                                                                             | For the first ~50 sales-led dealers this **is** the route (`13_REVENUE_GENERATION.md`)       |
| **dip-web itself**                 | Billing banners inside the console owners already use for DIP/wet-stock                                             | Unrestricted surface; billing lives one click away                                           |

### Routes inside the app (keep them purchase-blind)

- **Plain text, never tappable**: "Manage your plan on the DZZLO web console (dzzlo.in)" — stating the address as text is the conservative ceiling.
- In-app links to the website are fine for **non-purchase pages** (help, contact, privacy) — just ensure no in-app link can _reach_ the billing/checkout path.
- **Notify-owner** button → triggers an email/WhatsApp to the owner; the link travels **off-app**.
- **Push** → opens the in-app neutral status screen, never an external checkout.

### Kill the friction at the door (matters more than the link)

1. **One memorable address**: `dzzlo.in/billing`.
2. **Same phone-OTP login on web as in the app** — owners never see a password.
3. **Magic links**: the WhatsApp/email/SMS link carries a one-time token that lands the owner _already logged in_ on their invoice.
4. **WhatsApp-Web-style QR login** (optional): the web console shows a QR, the owner scans it from the app to authenticate the browser session. It's an auth feature, not purchase steering — the Zoho/WhatsApp pattern.
5. **Invert onboarding once subscriptions launch**: the owner's _first_ surface becomes the website (marketing site → trial signup → console tour → invite staff to the app). Then "go to the website" is just "go back to where you started" — the console is home, not a strange place.

## Rule of Thumb

> **Inside the app you may change what the software does; you may never open a road to money.**
> Everywhere else — web, email, WhatsApp, a phone call, a visit to the pump — sell as loudly as you like.
