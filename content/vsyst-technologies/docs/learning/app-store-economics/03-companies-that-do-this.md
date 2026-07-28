# 3. Companies That Keep the App Free and Sell the Subscription Elsewhere

The Figma pattern — **free store app + subscription bought outside the store** — is everywhere once you look for it.

## Consumer "Reader" Apps (Apple 3.1.3(a))

| Company                     | Where you subscribe | What the free app does                     | Notes                                                                                                                                                                                                 |
| --------------------------- | ------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Netflix**                 | netflix.com         | Watch video after login                    | Removed iOS in-app signup in **Dec 2018**, saving an estimated $100M+/yr in commissions. Since May 2025 the US app can link straight to web checkout.                                                 |
| **Spotify**                 | spotify.com         | Play music after login                     | Dropped IAP in **2016** — before that it charged **$12.99 in-app vs $9.99 web** to pass Apple's 30% to the user. Its EU complaint led to Apple's **€1.84B fine (Mar 2024)** over music anti-steering. |
| **Amazon Kindle / Audible** | amazon.com          | Read/listen to books bought on the website | For years you literally could not buy a book in the iOS app. After the 2025 US ruling, Amazon added a real "Get book" link-out button.                                                                |
| **YouTube Premium**         | Both (deliberately) | Full app either way                        | The **counter-strategy**: keep IAP but historically price it higher in-app — pass the tax to the user instead of dodging it.                                                                          |

## B2B / SaaS Companion Apps (Apple 3.1.3(f) & (c)) — the family DZZLO belongs to

| Company                           | Billing model                               | Mobile app role                                                                                               |
| --------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Slack**                         | Company pays per active user, billed on web | Free app, log in to your workspace                                                                            |
| **Notion**                        | Workspace subscription on web               | Free app, member login                                                                                        |
| **Zoom**                          | Licenses bought by company on web           | Free app for meetings                                                                                         |
| **GitHub**                        | Org billing on web                          | Free companion app                                                                                            |
| **Salesforce / Atlassian (Jira)** | Enterprise contracts                        | Free login-only apps                                                                                          |
| **Zoho** (India 🇮🇳)               | Org subscriptions billed on web             | Whole suite of free apps — India's best-known example of the pattern                                          |
| **Canva**                         | **Hybrid**: web billing AND optional IAP    | Chose to _accept_ the store tax on mobile conversions for convenience — a deliberate trade-off, not a mistake |

## Two Cautionary Tales

### HEY email vs Apple (June 2020)

Basecamp launched HEY as a free iOS app whose accounts could only be bought on hey.com. Apple **rejected it**: for a _consumer_ app, downloading something that does nothing without an external purchase violated 3.1.1. Resolution: HEY added a free in-app mode (temporary randomized address) so the app "works" at download.
**Lesson:** the free app must be functional when downloaded. (Business apps sold to organizations get explicit shelter under 3.1.3(c)/(f) — reviewers typically just require a demo account.)

### Fortnite (2020–2026)

The opposite case: the phone **is** the consumption device, so Epic couldn't move the transaction off it without losing sales. It smuggled its own payment option into the app → both stores pulled it → five years of litigation that eventually rewrote US store rules (see [[06-epic-rulings-timeline]]).

---

## Can DZZLO Implement This? — Yes

DZZLO OMS fits the **Slack/Zoho column**, the safest one: a business tool where the **company subscribes on the web** and staff/customers use a **free login-only app**. Even better, the sale is company-to-company, which Apple's 3.1.3(c) exempts explicitly. Full application to our product: [[08-dzzlo-subscription-strategy]]. How upgrades get sold with no in-app buy button: [[07-upselling-without-a-buy-button]].
