# 9. Encouraging Users to Use the Website for Specific Features

## First: This Is Unrestricted

Anti-steering ≠ anti-website. Apple's and Google's rules restrict directing users to **purchasing mechanisms** ([[04-apple-app-store-rules]], [[05-google-play-store-rules]]). Directing users to your website for **functionality** is legal on every storefront — tappable links, banners, deep links, QR codes, all fine. Apps say "available on desktop" all the time.

One discipline keeps it clean:

| Case                                                       | In-app treatment                                                                                                                 |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Feature the company **has**, but it lives on the web       | Link freely — button, deep link, banner: _"Full report on the web console →"_                                                    |
| Feature the company **doesn't have** (needs a higher plan) | **No link.** Neutral lock + notify-owner ([[07-upselling-without-a-buy-button]]). A lock screen + external link = steering combo |
| Any feature link's destination                             | Lands on the **tool**, never on pricing/checkout. Keep commerce and functionality on separate URL paths                          |

## When Users Actually Go to the Web

Three conditions, all needed: the **job is desk-shaped**, the **door is one tap**, and the **timing is a desk moment**. The playbook below engineers all three.

## The Playbook

1. **Honest surface split — the feature living there IS the encouragement.** Make web-only the things genuinely better on a big screen: bulk XLSX exports, TCS/TDS & GST reports, month-end reconciliation, credit-limit configuration, DIP dashboards, analytics, user administration. Never move field jobs (ordering, delivery OTP, vehicle ops) to web to force adoption — punishing phone users kills the network.
2. **Signpost at the moment of need.** On the app screen where the desire arises, a card: _"Monthly GST report is ready on the DZZLO web console →"_. Deep link to the exact page, not the console home.
3. **Tease, don't withhold.** App shows the summary tile (this month's sales, outstanding); the full breakdown lives on web. Enough visibility to create the pull.
4. **Zero-friction handoff.** A _"Send link to my WhatsApp/email"_ button in the app → magic link lands the user **already logged in on that exact report**. Plus QR web-login from the app, and the same phone-OTP auth on web. (Same mechanics as [[07-upselling-without-a-buy-button]] §Getting Owners Onto the Website.)
5. **Ride India's compliance calendar.** GSTR-1 by the 11th, GSTR-3B by the 20th — built-in monthly desk moments. Timely WhatsApp/email: _"GSTR-1 due in 3 days — download your sales register from the console."_ Recurring, useful, and it lands exactly when the owner is at a desk anyway.
6. **Email/WhatsApp digests.** Weekly business summary where every number is a link into the console — the Zoho/Search-Console habit loop: digest → click → web session.
7. **Target the desk personas.** Accountants (`DAccount`/`CAccount` scopes) and owners are the natural web users. Set the console up on their machine during onboarding; give the dealer's **CA** view access — the CA becomes your web evangelist (the pricing corpus already flags CAs as a hidden channel).
8. **Put administration web-only.** User management, roles, credit config, billing — owners _must_ visit periodically; the dashboard greets them every time they do.
9. **Desktop PWA** (`tasks_06_pwa`): an installable console icon on the owner's desktop turns "visit the website" into "open the app on my computer."
10. **Push as feature notification.** _"Your June TCS report is ready on the web console"_ — a functionality notice, not marketing; allowed, and it plants the web habit.

## What NOT To Do

- Never link out from a **premium** lock screen (that's purchase steering).
- Never land a feature link on a page carrying prices or upgrade CTAs.
- Don't degrade the app to push people web-ward — the app is the network's home; the web is the desk annex.

## Related

[[07-upselling-without-a-buy-button]] · [[08-dzzlo-subscription-strategy]] (feature split table) · `../../tasks/tasks_06_pwa/`
