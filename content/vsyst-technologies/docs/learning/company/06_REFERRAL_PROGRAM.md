# 06 — Referral Program

A founder's reference for designing, costing, and operating a referral program for DZZLO OMS, targeting Indian SME fuel dealers.

---

## 1. Why referrals matter for DZZLO

Referrals are the single highest-ROI acquisition channel for Indian SME fuel dealers (see `12_OWNER_ACQUISITION.md`). The dealer community is tight, geographically clustered, and defined by trust: a dealer in Ahmedabad calling his college friend in Vadodara to recommend a piece of software converts at 10-20x the rate of the same dealer seeing a LinkedIn ad.

The canonical reminder of what a well-built referral program can do: **Dropbox scaled 3,900% in 15 months via referrals — from 100,000 to 4,000,000 users** ([ReferralRock — Dropbox referral program](https://referralrock.com/blog/dropbox-referral-program/), [Viral Loops — how Dropbox grew 3,900%](https://viral-loops.com/blog/dropbox-grew-3900-simple-referral-program/)). While DZZLO will not replicate Dropbox's consumer virality (B2B SaaS has structurally lower K-factors), the core dynamic is the same: SME India is a trust-first market, and dealer trusts dealer far more than dealer trusts brand.

Two practical consequences for DZZLO:

1. **Referral channel contribution should be a planned metric, not an incidental surprise.** Target 25% of new customers referral-attributed by month 12.
2. **The referral program has to be easy enough that a 50-year-old dealer can share on WhatsApp in 10 seconds.** Anything more complex than one-tap share and it dies.

---

## 2. Types of referral programs

| Type                | Mechanics                                                                 | Best-fit                                            | Example                                     |
| ------------------- | ------------------------------------------------------------------------- | --------------------------------------------------- | ------------------------------------------- |
| Double-sided        | Both referrer and referee get rewarded                                    | Default B2B SaaS — both sides have skin in the game | Dropbox (extra space to both)               |
| Milestone           | Rewards unlock at 1, 3, 5, 10 referrals                                   | Building streaks, cumulative engagement             | Tesla (wheels → trips → Roadster)           |
| Tiered              | Commission % rises with referral volume                                   | Power users and super-referrers                     | HubSpot affiliates                          |
| Gamified            | Leaderboards, badges, public rankings                                     | WhatsApp-native markets, community-driven           | PayPal early program; Airbnb travel credits |
| Partner / affiliate | Professional referrers (CAs, consultants, OMC reps) with formal contracts | Channel-partner territory                           | PartnerStack-powered SaaS programs          |

### Guidance per type

**Double-sided** is the default for B2B SaaS. It removes the awkwardness of the referrer earning while the referee gets nothing — which, in relationship-driven SME India, kills the motivation to share.

**Milestone** stacks psychological reward: hitting "Gold Dealer Dost" at 3 referrals feels more meaningful than getting ₹2,000 three times. Use as a layer on top of double-sided cash.

**Tiered** is powerful for later-stage when you have a handful of super-referrers. Early on, keep it simple.

**Gamified** is highly effective in WhatsApp-native India where public "Top 10 dealer" lists get screenshotted and re-shared. Layer carefully — gamification without a strong base reward feels hollow.

**Partner / affiliate** is the B2B scale lever. CAs, OMC territory managers, and pump-hardware engineers are all natural advocates. Requires a formal agreement layer separate from the dealer-to-dealer program.

---

## 3. B2B SaaS referral economics

### Commission ranges

Enterprise B2B SaaS norms ([SaaStr — typical commission ranges for referral partners](https://www.saastr.com/what-are-typical-commission-ranges-for-referral-partners-for-enterprise-b2b-saas/)):

- **5-10%** of first-year ACV for a warm lead (no qualification).
- **10-20%** for a qualified opportunity.
- **25-40%** for a closed-won deal.

### Example: DZZLO unit economics

At DZZLO's target ARPA of ₹2,500/month (₹30,000/year per dealer-outlet), a 10%-of-first-year-ACV referrer payout is **₹3,000** per closed-won referral — a useful, round, WhatsApp-shareable number.

### Recurring vs one-time

Recurring commissions (e.g., **15%/month capped at $500/deal**) align referrer incentives with retention — the referrer only keeps earning if the referred dealer keeps paying. This also naturally prevents signup-fraud because low-quality referrals churn and stop paying out ([Expando — referral commission structure guide](https://www.expando.ai/blogs/guide-to-referral-commission-structure)).

### Cash vs credit

B2B strongly favors **cash or gift cards** over in-product credit because the referrer is typically an individual (the owner, the accountant) not the company — and individuals prefer cash ([Viral Loops — SaaS referral program](https://viral-loops.com/blog/saas-referral-program-2/)). For dealers specifically, **UPI transfer** is the cleanest.

### Fixed ₹ vs percentage

For SMB audiences, **fixed rupee amounts outperform percentages** because the math is legible. "₹2,000 when your friend signs up" beats "10% of first-year ACV" every time with dealers. Percentages are for partner-tier affiliates who understand MRR and LTV.

### Gross-margin floor

SaaS gross margin sits around 80%. To protect LTV:CAC, cap total referral commission at **≤30% of first-year ACV** — any higher and the cohort becomes unprofitable in year one. DZZLO's program below sits at 16.7% for the core dealer loop, well within the ceiling.

---

## 4. Dropbox lessons (canonical case study)

The Dropbox referral program is the single most-studied B2B/prosumer referral program because of its clarity of lessons:

- **Framing matters.** "Get more space" outperformed "Invite your friends" because it led with the referrer's benefit, not the behaviour being asked. Frame DZZLO's CTA as "Earn ₹2,000 for each dealer friend" not "Refer a friend".
- **Place the prompt at moments of value realization.** Dropbox surfaced the referral prompt when the user hit storage limits — the exact moment of felt value. For DZZLO, the equivalent triggers are: after the first successful Form R filing, after the first month with visible shortage reduction on the dashboard, after onboarding a second outlet.
- **Genuinely two-sided.** Both sides got space. When referrer gets ₹2,000 but referee gets nothing, the social ask becomes awkward and the program dies.
- **Built into onboarding, not a side panel.** The referral CTA was inside the core product flow, not buried in a "Rewards" menu. DZZLO should surface it on the main dashboard.
- **Outcome: 3,900% growth in 15 months, from 100k to 4M users.**

---

## 5. Tooling options 2026

- **[Rewardful](https://www.rewardful.com)** — 2 lines of JavaScript, Stripe/Paddle integration, 15-minute setup. Churn-aware recurring commission, auto self-referral fraud detection ([self-referral fraud detection](https://www.rewardful.com/self-referral-fraud-detection), [affiliate fraud prevention guide](https://www.rewardful.com/guides/how-to-detect-and-prevent-affiliate-fraud)). Ideal early-stage.
- **[PartnerStack](https://partnerstack.com/resources/guides/anatomy-of-a-referral-program)** — full Partner Relationship Management (PRM); handles affiliate + referral + reseller tiers in one system. Expensive; turn on at ₹1 Cr ARR or later.
- **[Tolt](https://tolt.com/)** — purpose-built for SaaS startups; branded referral portals, auto UPI/Stripe payouts, Indian-rupee-friendly. Strong default for DZZLO at launch.
- **FirstPromoter + Stripe Instant Flow** — coupon codes via Stripe instant flow; <5 minute setup for the minimum viable program.
- **[Friendbuy](https://www.friendbuy.com/blog/saas-referral-program)** / **Viral Loops** — viral-loop mechanics, built-in A/B testing; more consumer-leaning.

**DZZLO recommendation:**

- **Launch phase (0–₹50 L ARR):** Tolt or Rewardful + Razorpay for INR payouts.
- **Scale phase (₹50L–₹5 Cr ARR):** Stay on Tolt/Rewardful; add a Google Sheet-based partner layer for CAs and OMC reps.
- **Enterprise phase (₹5 Cr+ ARR):** Migrate to PartnerStack for multi-tier partner management.

---

## 6. India fuel-dealer reward motivators

What actually moves the needle with a 40–55 year-old dealer in Tier-2/3 India:

- **Cash / UPI transfer** — the universal currency. Zero friction. Works every time. Lead with this.
- **Fuel or petrol vouchers** — on-brand but OMC-specific logistics (HPCL voucher for HPCL dealer, etc.), making them hard to operationalize across the dealer base.
- **Tech upgrades** — free POS hardware (tablet, receipt printer, dashboard TV for the office). Perceived value higher than cash for the same ₹ amount because the dealer wouldn't have bought it himself.
- **Visibility and awards** — "Top DZZLO Dealer — Gujarat Q2 FY27", LinkedIn feature, physical certificate delivered to the pump, jacket/cap. Status matters more than first-time founders assume — dealers will compete hard for a free framed certificate.
- **Free months of DZZLO software** — good for retention / lock-in, weak as a cold motivator. Use as a stacking bonus, not the headline.
- **Trade-show perks** — free passes to India Energy Week, OMC national dealer conventions, reserved sponsor seating. Makes the dealer feel included in the industry elite tier.

---

## 7. Recommended DZZLO referral program — "Dealer Dost" (Dealer Friend)

### Reward structure

| Action                                     | Referrer gets                                                                      | New customer gets   |
| ------------------------------------------ | ---------------------------------------------------------------------------------- | ------------------- |
| Friend signs up + onboards (1 outlet live) | ₹2,000 UPI                                                                         | First 2 months free |
| Friend starts paying (month 3)             | Additional ₹3,000 UPI                                                              | —                   |
| Referrer reaches 3 paid referrals          | ₹5,000 bonus + "Dealer Dost Gold" badge                                            | —                   |
| Referrer reaches 5 paid referrals          | Free Samsung tablet (~₹15,000) + profile feature on DZZLO site + FIPI event invite | —                   |
| Referrer reaches 10 paid referrals         | ₹50,000 bonus + "State Ambassador" title + annual trip invite                      | —                   |

### Economic sanity check

At DZZLO ARPA of ₹2,500/month (₹30,000/year):

- 3 paid referrals = ₹90,000 new annual ARR.
- Referrer payout at that tier = ₹2,000 + ₹3,000 per paid referral = ₹15,000 across 3 (plus ₹5,000 milestone bonus = ₹20,000 all-in).
- **₹20,000 / ₹90,000 = 22.2%** of year-1 ACV — within the 25% ceiling for SaaS unit economics and well-covered by DZZLO's 80% gross margin.

The 5-referral tier (free tablet, ₹15k value) and 10-referral tier (₹50k cash) are intentionally generous because those tiers are the true channel — a dealer referring 10 peers is effectively running a part-time DZZLO sales desk, and a ₹50k annual incentive is far cheaper than the equivalent SDR headcount.

### Mechanics

- **Unique referral link** auto-generated on Day 1 of paid subscription and surfaced on the main dashboard.
- **One-tap WhatsApp share** with pre-populated Hindi copy:
  > _"Namaste bhai, main DZZLO use kar raha hoon apne pump pe. Shortage aur GST ka tension khatam. 2 mahine free milega aapko is link se — [link]. Try karo."_
- **Unique coupon codes per referrer** (e.g., `RAJESH25`) — so offline referrals at dealer meets and association events still attribute correctly.
- **Tracking:** Rewardful (or Tolt) + Razorpay for INR payouts. Every payout logged with a GSTIN-compliant receipt.

---

## 8. Fraud prevention (2026 standard)

Fraud in referral programs is well-understood. The following patterns are mandatory, not optional:

- **Self-referral block** — same GSTIN or PAN on both sides = reject automatically. Rewardful and Tolt both support this out of the box ([Rewardful self-referral detection](https://www.rewardful.com/self-referral-fraud-detection)).
- **Pay only after month 3 active + paid** — defeats signup-and-churn fraud where the referrer onboards fake accounts to collect the signup bonus. The delayed payout is the single most important anti-fraud lever.
- **Device fingerprint + IP match blocks** — catches the "same owner, multiple shell accounts" fraud pattern.
- **Manual review threshold** — any referrer with >5 referrals in a single month is flagged for manual review before payout clears.
- **Churn-aware reward reversal** — if a referred account churns within 6 months, the paid-out bonus is clawed back (either from future payouts or as a debit). Discloses upfront in program terms.
- **Quarterly expiry on unused referral codes** — keeps the program fresh and prevents stale code stockpiling ([Rewardful affiliate fraud prevention guide](https://www.rewardful.com/guides/how-to-detect-and-prevent-affiliate-fraud)).

---

## 9. Activation triggers (Dropbox lesson applied)

The referral CTA has to show up at moments of felt value. For DZZLO:

- **Day 7 post-activation** — dashboard card: _"₹2,000 for each dealer friend. Share now →"_.
- **Day 30 (after the first successful GST filing)** — popup: _"You just saved 2 hours on GST. Tell a friend — earn ₹2,000."_
- **Day 60 (after the first month with a visible shortage-reduction win on the dashboard)** — dashboard card with the dealer's own shortage % reduction as a shareable stat card.
- **Monthly WhatsApp nudge on the 1st** — _"Rajesh ji, 3 dealer friends ko DZZLO share karo, ₹15,000 tak earn karo. Aapka link: [link]"_.
- **Event triggers** — after onboarding a second outlet, after touching a new feature milestone, after a dealer support win (high-NPS survey response).

---

## 10. Target metrics (launch benchmarks)

| Milestone | Metric                                                                              |
| --------- | ----------------------------------------------------------------------------------- |
| Month 3   | ≥15% of active customers submit at least 1 referral                                 |
| Month 6   | ≥25% of new customers are referral-attributed; K-factor ≥0.3                        |
| Month 12  | K-factor ≥0.6 (Dropbox peak was ~0.9 — that is the outlier ceiling, not the target) |

K-factor = (invitations sent per user) × (conversion rate per invitation). A K-factor of 1.0 is pure organic doubling; anything above 0.5 is exceptional for B2B SaaS.

---

## 11. Partner / affiliate layer (once the dealer loop works)

Once the dealer-to-dealer loop is proven, add a professional partner layer. This is where CAs, OMC territory managers, and hardware engineers become the third-party sales arm.

### Channel partner archetypes

- **Chartered Accountants (CAs)** — 10-30 fuel-dealer clients each, already trusted for GST and compliance. Commission structure: **10-15% revenue share** on referred accounts (recurring, capped at 12 months). CAs are highest-intent referrers because the dealer already defers to them on anything software/compliance.
- **OMC Territory Managers (HPCL, BPCL, IOCL)** — visit every dealer in their territory monthly; a casual recommendation from a TM carries enormous weight. Commission: **₹3,000–₹5,000 per qualified intro** (not % revenue — keeps it legally clean and avoids perception of OMC-employee conflict of interest). Must be structured via a formal written agreement with OMC permission.
- **Gilbarco / pump-hardware engineers** — on-site when new dispensers are installed; perfectly placed to recommend OMS software. Commission: **₹1,000–₹2,500 per booked demo**.

### Dealer associations

- **AIPDA** (All India Petroleum Dealers Association), **FAIPT** (Federation of All India Petroleum Traders), and state-level bodies.
- Structure: annual sponsorship + endorsement revenue-share (e.g., 5% of members-only signups) in exchange for newsletter features, conference slots, and member-benefit listing.

### Formalization

Every partner layer needs:

- A written Referral Partner Agreement signed before any payout.
- GSTIN collection and TDS compliance.
- A dedicated partner portal (Tolt → PartnerStack path) with login, dashboard, payout history.
- Monthly reconciliation on the 10th of the following month.

---

Sources → [RESEARCH_SOURCES.md](./RESEARCH_SOURCES.md)
