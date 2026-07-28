# 2. How Figma Avoids the App Store / Play Store Tax

## The One-Sentence Answer

**Apple and Google can only take a cut of purchases made _inside_ the app — and Figma never sells anything inside the app.** Subscriptions are bought on figma.com (web checkout or a sales contract). The mobile app is a free companion you log into. No in-app transaction → nothing to tax. Figma pays ~2–3% card-processing fees instead of 15–30% store commission.

---

## The Four Mechanics

### 1. All money changes hands on the web

Self-serve plans → figma.com checkout (credit card, ~2–3% processing).
Organization/Enterprise → sales team, annual invoices. The stores never touch either flow.

### 2. The mobile app sells nothing

The Figma iOS/Android app has **no purchase button, no IAP catalog, no price list**. You download free, sign in, and view/comment/present files. Even the login isn't a paywall — a free Starter account works too.

### 3. The product shape makes this painless

Design work happens on desktop browsers; mobile is inherently a **viewer/companion** (view, comment, present, mirror prototypes). Figma gives up nothing by not monetizing mobile — unlike a game, where the phone _is_ the product (see Fortnite in [[03-companies-that-do-this]]).

### 4. No steering inside the app

Historically the app also never _told_ you where to buy (anti-steering rules). Since the 2025 US court rulings, US-storefront apps may link out to web checkout — but Figma never even needed that; its buyers arrive via the web anyway.

---

## Which Exact Rules Make This Legal

| Rule                                      | What it permits                                                                                               | Fit for Figma                                                                                            |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Apple **3.1.3(f)** Free Stand-alone Apps  | Free app as companion to a **paid web-based tool**, if no purchasing or purchase CTAs in-app                  | **The cleanest fit**                                                                                     |
| Apple **3.1.3(c)** Enterprise Services    | Apps sold directly to organizations may let enterprise users access previously-purchased subscriptions        | Covers Org/Enterprise plans                                                                              |
| Apple **3.1.3(b)** Multiplatform Services | Access content bought on other platforms — **but only if also offered as IAP in-app**                         | ⚠️ Trap: the "also available as IAP" catch means (b) alone would NOT cover Figma. (f) has no such catch. |
| Google Play **consumption-only app** rule | "A user could log in when the app opens and access content paid for somewhere else" — allowed for **any app** | Exactly Figma's Android app                                                                              |

Verbatim rule text: [[04-apple-app-store-rules]] and [[05-google-play-store-rules]].

---

## The Honest Framing

Figma doesn't exploit a loophole — it was **never in the taxed category**. The store tax effectively falls on **consumer apps whose discovery, purchase, and consumption all happen on the phone** (games above all). B2B SaaS that lives on desktop/web — Slack, Notion, Zoom, GitHub, Zoho, Salesforce — has always sold subscriptions on the web, tax-free, with free mobile companion apps. Figma is simply the best-known member of that family (full gallery: [[03-companies-that-do-this]]).

**Rule of thumb: the store taxes transactions, not apps.** Keep the transaction off the device and keep the app quiet about it, and the commission never applies.
