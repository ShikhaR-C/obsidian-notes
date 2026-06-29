# 03 — Launch Checklist

A concrete, date-anchored playbook for taking DZZLO OMS from validated idea to 100 paying fuel dealers. Structured across three phases: Pre-Launch (Days -90 to -1), Launch Week, and Post-Launch (Days +1 to +90). Each phase includes citations, specific targets, and copyable checklists.

Pair this document with `02_PRICING_STRATEGY.md` (pricing research sequence), `04_GTM_PLAYBOOK.md` (channels), and `RESEARCH_SOURCES.md` (full citations).

---

## PHASE 1: Pre-Launch (Days -90 to -1)

### Days -90 to -60 — Market validation & design partners

Lenny Rachitsky's research on [validating B2B startups](https://www.lennysnewsletter.com/p/how-to-validate-your-b2b-startup) finds that **only about one-third of successfully validated B2B startups formally worked with design partners**. For a high-touch, low-digital-maturity buyer like an Indian fuel dealer, design partners are not optional — they are the validation path.

**SaaStr's [design-partner structure](https://www.saastr.com/dear-saastr-what-incentives-are-given-to-design-partners-and-other-super-early-customers/)** (adapted for DZZLO):

- **Free / deeply discounted use for 6–12 months.**
- **Weekly feedback calls** — 30 minutes, founder-led, never delegated.
- **Logo and name rights** on landing page and pricing tiers.
- **Written case study** published at launch.
- **Post-launch loyalty discount of 20–30%** for life (or for 2 years).
- **Advisory credit** on the launch-week PR materials.

**Target: 3–5 flagship dealers across 2 states.** Mix one single-pump owner-operator and two multi-pump operators per state to cover the ICP breadth.

**Checklist — Days -90 to -60:**

- [ ] 30 customer discovery interviews (target 30, rejection rate ~60% — budget for 75 outreach)
- [ ] Written ICP document (pump count, state, OMC, monthly turnover band, pain-point ranking)
- [ ] Positioning statement finalised (one sentence, tested with 10 non-dealers for comprehension)
- [ ] Competitive teardown — SOFTGUN, PetroSoft, Vyapar, Zoho, Tally, manual/Excel
- [ ] 3–5 design partners signed on written MoU
- [ ] Weekly feedback call cadence booked in calendar
- [ ] Design-partner Slack/WhatsApp group created
- [ ] Success metrics for design-partner phase agreed (e.g., "DZZLO replaces 3 incumbent tools in 60 days")

### Days -60 to -30 — Waitlist + landing page

Waitlist-driven launches are dramatically more efficient than cold-paid launches. [Waitlister.me's guide](https://waitlister.me/growth-hub/guides/saas-product-launch-waitlist) reports **25–85% conversion from waitlist to paid signup**, vs **2–4% for paid acquisition** with a CAC around **$702**. For a market where trust is the primary barrier (Indian SMB fuel retail), a waitlist also compounds into social proof.

[DoWhatMatter's B2B Product Hunt guide](https://dowhatmatter.com/guides/product-hunt-launch-guide-b2b) finds **a 1,000+ email waitlist predicts 3–5x better PH rankings** vs an un-warmed launch.

A private Slack/WhatsApp community of pre-launch waitlist members compounds further: **BeyondLabs' community study** finds community-led SaaS grows revenue **25% faster** than non-community peers.

**Targets:**

- **1,000+ waitlist emails** pre-launch.
- **A private WhatsApp group** of 150+ engaged dealers (aim for 15% of waitlist).
- **Landing page conversion ≥ 25%** (industry median for waitlists).

**Checklist — Days -60 to -30:**

- [ ] Domain purchased (primary + typo variants + .in TLD)
- [ ] Hosting set up (Vercel/Cloudflare/AWS — whichever fits the stack)
- [ ] Tally Solutions sandbox account + Razorpay account (live + test) + GSTIN for DZZLO entity
- [ ] Brand identity finalised (logo + primary palette + typography + Hindi wordmark)
- [ ] Landing page live with waitlist form, positioning statement, one explainer video, pricing teaser, FAQ
- [ ] Analytics pixels installed (Google Analytics 4, Meta Pixel, LinkedIn Insight, PostHog)
- [ ] Privacy Policy, Terms & Conditions, Refund Policy (compliant with DPDP Act 2023)
- [ ] Waitlist form connected to CRM (HubSpot free tier / Airtable)
- [ ] Welcome email + drip sequence (4 emails over 21 days)
- [ ] Hindi and English versions of the landing page
- [ ] WhatsApp Business API sender verified
- [ ] Pre-launch WhatsApp community created with onboarding message
- [ ] AIPDA / state-association introductions warmed

### Days -30 to -7 — Pre-sales & beta

Figma's playbook, as documented in [Lenny's "First 10 B2B Customers"](https://www.lennysnewsletter.com/p/how-the-most-successful-b2b-startups-got-their-first-10-customers), is: **cold-email influential early users, filter ruthlessly for those who inspire you personally, and earn them with white-glove onboarding.**

For DZZLO, the cold-channel is not email — it is WhatsApp. Adapted playbook:

- **Scrape dealer association member directories** (AIPDA, state-level groups). Start with public PDFs and state-pump listings.
- **Join 10–15 dealer WhatsApp groups** (via a design-partner referral; never join unsolicited).
- **Run 30-minute Zoom + screen-share onboarding** with each of the 10 flagship dealers. Record with consent. Clip into vertical-format testimonial reels.
- **Daily WhatsApp feedback updates** from each flagship dealer for the full 30 days.
- **Track onboarding-to-first-value time.** Target < 72 hours.

**Checklist — Days -30 to -7:**

- [ ] 10 flagship dealers fully onboarded (live data, daily use)
- [ ] First-value event hit for 8/10 flagship dealers (first GST invoice issued via DZZLO)
- [ ] 3 video testimonials captured in vernacular (45–90s each)
- [ ] 3 written case-study drafts (one per tier segment)
- [ ] Founder Zoom availability calendar seeded for launch week
- [ ] Feedback-log spreadsheet active (every bug, feature request, friction point logged)
- [ ] First-pass pricing validated against 10 paid pilots (see `02_PRICING_STRATEGY.md`)

### Days -14 to -1 — Infrastructure readiness

**Analytics installed before launch — not after.** [Storylane's launch-readiness study](https://www.storylane.io/blog/saas-launch-analytics) finds the teams that instrument *before* launch ship 2.1x more useful iterations in the first 90 days than teams that instrument later.

**Load test at 3–5x expected traffic.** [HexagonIT's launch-day checklist](https://www.hexagonitsolutions.com/saas-launch-checklist) reports that **21% of SaaS launches have a material availability incident in the first 72 hours**, nearly all of them capacity-related.

**Legal layer** — [Secure Privacy's DPA guide](https://secureprivacy.ai/blog/data-processing-agreements-dpas-for-saas) and [toslawyer's SaaS legal checklist](https://toslawyer.com/legal-checklist-for-u-s-saas-startups-tos-privacy-dpa-sla-and-more/) together define the minimum: Terms of Service, Privacy Policy, Cookie Consent, Data Processing Agreement (GDPR Article 28 style), SLA, Refund Policy. For India, add **DPDP Act 2023 compliance** — consent ledger, data localisation preferences, grievance-officer contact.

**War-room.** [Storylane's data](https://www.storylane.io/blog/saas-launch-analytics) shows a dedicated Slack `#launch-day` war-room channel produces **60% faster incident response** vs ad-hoc coordination.

**Checklist — Days -14 to -1:**

- [ ] Analytics fully installed — PostHog or Mixpanel + GA4
- [ ] Activation events defined and firing (signup, first invoice, first payment received, WhatsApp send, first reconciliation)
- [ ] Funnel drop-off dashboards live
- [ ] Revenue tracking integrated from hour zero (Stripe MRR + Razorpay)
- [ ] Load test at 3–5x expected peak — documented result with bottleneck list
- [ ] Terms of Service published
- [ ] Privacy Policy published (English + Hindi)
- [ ] Cookie Consent banner (GDPR + DPDP Act 2023 compliant)
- [ ] Data Processing Agreement template ready (for Enterprise deals)
- [ ] SLA document (uptime commitment + credit schedule)
- [ ] Grievance Officer appointed and contact published (DPDP Act requirement)
- [ ] Data localisation stance documented
- [ ] Slack `#launch-day` war-room channel created, on-call rotation defined
- [ ] Razorpay end-to-end payment flow tested (INR + GST invoice generation)
- [ ] Stripe tested for international Enterprise (USD invoices)
- [ ] GST e-invoicing integration (if turnover eligibility applies to customers)
- [ ] Help center live with 20+ articles
- [ ] Hindi + English Loom-style onboarding videos (10–12 videos, 3–5 minutes each)
- [ ] Sentry / Rollbar error tracking live
- [ ] Uptime monitoring (BetterStack / Pingdom) — 5 endpoints min
- [ ] Backups running + last-72h restore tested
- [ ] On-call rotation published with PagerDuty / OpsGenie
- [ ] Incident runbook drafted
- [ ] Status page live (status.dzzlo.com or similar)
- [ ] Security review done (minimum: OWASP Top 10 audit, secrets rotated, 2FA on all founder accounts)
- [ ] DNS + SSL cert stability confirmed

---

## PHASE 2: Launch Week

### Product Hunt strategy

**Launch Tuesday at 12:01 AM Pacific.** This is the default for a reason — [Blazon Agency's 2026 Product Hunt guide](https://blazonagency.com/post/how-to-launch-on-product-hunt) confirms Tuesday–Thursday 12:01 AM PT gives the longest ranking window before daily reset.

**The first 4 hours are critical.** Rankings stabilise roughly by hour 5. Your goal: **land in the Top 4 within the first 4 hours.**

**Pre-build 200–400 hand-recruited upvoters** who will vote within the first 3 hours. Do not buy votes — Product Hunt will flag and suppress. [DoWhatMatter's B2B guide](https://dowhatmatter.com/guides/product-hunt-launch-guide-b2b) details the recruitment pattern: personal DMs across 6+ weeks before launch, day-before reminder, day-of morning reminder.

**Hunter.** [Postdigitalist's Product Hunt analysis](https://www.postdigitalist.xyz/blog/product-hunt-launch) shows **a celebrity hunter is not essential** if you have a solid pre-launch waitlist and community. A genuine hunter who actually uses the product beats a farmed-out hunter with follower count.

**For B2B specifically**, Peaka's PH analysis notes that **Product of the Day is less valuable than driving qualified traffic and closing deals.** Optimise for pipeline, not the badge.

**Comment cadence.** Answer every comment within 12 hours — ideally within 2. This alone can swing ranking in the 6–12 hour window.

**LinkedIn DMs = 2026's highest-ROI upvote channel.** [Postdigitalist](https://www.postdigitalist.xyz/blog/product-hunt-launch) finds 3 people DMing full-time on launch day drives **200–300 upvotes**. Divide and conquer — co-founders + advisors DM for the first 6 hours.

**Expected payoff.** A Top 5 finish typically drives **800–1,200 unique PH visitors** with a **15–25% signup rate** ([DoWhatMatter](https://dowhatmatter.com/guides/product-hunt-launch-guide-b2b)) — so a good launch adds 120–300 signups on day one.

### Other launch channels

| Channel | Effort | Expected impact for DZZLO |
|---|---|---|
| **BetaList** | Low | Modest. Developer audience, less fit for SMB fuel. |
| **Hacker News (Show HN)** | Medium | Low for SMB ops software. Skip unless there is a deep-tech angle. |
| **Indie Hackers** | Medium | Long-term community channel, not a single-day driver. |
| **[Firsto alternatives list](https://firsto.co/blog/product-hunt-alternatives)** | Low | Some will drive residual traffic — pick 3 from the list and submit. |

### India-specific launch channels

**LinkedIn India.** [Directive's 2026 B2B SaaS guide](https://directiveconsulting.com/insights/b2b-saas-2026-guide) finds **founder-led POV posts drive a 40% organic pipeline lift** in Indian B2B. Founder posts 3x/week for the 90 days around launch.

**Multi-thread every target account.** [PipelineRoad's multi-thread study](https://pipelineroad.com/blog/multi-thread-b2b-accounts) reports **3–5x conversion** when 3+ stakeholders are engaged per account. For a pump, thread: owner, manager, and accountant.

**WhatsApp communities.** WhatsApp Business has **487M Indian users** (WABiz India 2026). The [RentechDigital petrol-pump directory](https://www.rentechdigital.com/smartscrape/india/petrol-pumps) lists **2,082 Indian petrol pumps with public WhatsApp numbers** — a starting database for cold outreach (compliant, consent-respecting). Join state-level dealer WhatsApp groups through design-partner referrals.

**Trade bodies.**

- **AIPDA — All India Petroleum Dealers Association.** Single most important association.
- **[FIPI — Federation of Indian Petroleum Industry](https://www.fipi.org.in/)** — industry body; useful for enterprise credibility.
- **FAIPT** — All India Petroleum Traders federation.
- **CIPD** — Confederation of Indian Petroleum Dealers.
- **UPF** — United Petroleum Federation (**54,000 dealer members** — arguably the largest reachable network).

**Events.**

- **[India Energy Week 2026](https://www.businessstandard.com/industry/news/india-energy-week-2026-goa)** — Goa, 27–30 January 2026. Succeeded Petrotech as India's flagship energy event ([NewsDrum coverage](https://www.newsdrum.in/business/india-energy-week-2026)).
- **[World Petroleum Technology Congress 2026](https://www.worldpetroleumcongress.in/)** — Delhi.
- **OMC dealer conventions** — IOCL, BPCL, HPCL regional dealer meets. These are where Territory Managers congregate and where DZZLO's TM-endorsement strategy lands.

**Press.** Pitch YourStory, Inc42, and Entrackr during Week 1 after hitting a headline-worthy milestone (e.g. **"50 pumps signed in 30 days"**). Pre-write the headline; earn the number; land the pitch.

**Launch Week checklist:**

- [ ] Product Hunt page live (tagline, gallery images, video, first-comment drafted)
- [ ] 200–400 pre-recruited upvoters warmed via DM
- [ ] Hunter confirmed (if using one)
- [ ] 3 people on LinkedIn DM duty for first 6 hours
- [ ] Founder's LinkedIn post live at 12:05 AM PT (01:35 PM IST)
- [ ] BetaList + 3 alternative directories submitted
- [ ] AIPDA + UPF broadcast sent (via design-partner intro)
- [ ] 5 WhatsApp community posts across 5 state groups
- [ ] YourStory / Inc42 / Entrackr pitches sent at T+48h
- [ ] Live "office hours" Zoom slot advertised for launch day (45-min open call)
- [ ] OMC Territory Manager contact list warmed (3 TMs per state)

---

## PHASE 3: Post-Launch (Days +1 to +90)

### PMF signals & iteration

**Net Revenue Retention (NRR) targets.** [Directive's 2026 B2B SaaS report](https://directiveconsulting.com/insights/b2b-saas-2026-guide):

- **NRR > 100%** = existing customers net-expand revenue — organic growth.
- **NRR > 120%** = growth *without* new-customer acquisition — a hallmark of PMF.

**First-value in 14 days.** [Directive's onboarding study](https://directiveconsulting.com/insights/saas-onboarding-research) finds customers who do **not** hit first value in 14 days are **3x more likely to churn in the first 90 days**. For DZZLO, define first-value explicitly as **first GST invoice issued** OR **first WhatsApp reminder sent** OR **first credit note reconciled**.

**5-touch onboarding.** The cadence that reliably lifts 90-day activation from **45% → 68%** in SMB B2B ([Directive](https://directiveconsulting.com/insights/saas-onboarding-research)):

1. **Day 1** — Welcome email + WhatsApp + in-app primary CTA.
2. **Day 3** — Vernacular video walk-through (3 minutes).
3. **Day 7** — "Invite your accountant / manager" prompt.
4. **Day 10** — CS (Customer Success) check-in call or WhatsApp message.
5. **Day 14** — Milestone email: "You've issued N invoices and recovered ₹X — here's what next."

### Cadence targets

| Cadence | What to do |
|---|---|
| **Weekly** | 5 customer interviews · churn review · support ticket triage · NPS pulse |
| **Bi-weekly** | Feature ship with changelog · pricing A/B review |
| **Monthly** | NPS survey · cohort retention review · pricing test · dealer advisory call (design partners) · OMC TM outreach batch |

### Day 90 exit criteria

Treat these as gates, not aspirations. If any one fails at Day 90, pause expansion and return to the prior phase:

- [ ] **100+ paying customers** OR **500+ active free users**
- [ ] **NPS ≥ 30**
- [ ] **Activation rate ≥ 60%** (hit first-value in 14 days)
- [ ] **Monthly churn ≤ 3%** (logo churn; revenue churn lower)
- [ ] **At least 1 referenceable written case study** (with measurable ROI, dealer name and photo)
- [ ] **Tally + Razorpay integrations stable** (no P0 incidents last 30 days)
- [ ] **Support first-response ≤ 4 hours business-day median**
- [ ] **1 AIPDA / state-association partnership signed**
- [ ] **NRR trend positive** (even if absolute NRR < 100% in month 3)

---

## Concrete Pre-Launch Checklist (Copyable Master List)

A single-surface master checklist spanning product, legal, marketing, ops, GTM, and team. Print, tick, review weekly with cofounders.

### Product

- [ ] All P0 and P1 bugs closed
- [ ] Signup → first-value path tested end-to-end on 3 devices (low-end Android, mid-range Android, iOS)
- [ ] Payments end-to-end (Razorpay INR, GST invoice, refund path, subscription upgrade/downgrade, dunning)
- [ ] Onboarding flow tested with 5 non-technical users
- [ ] Empty states populated (no user should ever see a blank screen)
- [ ] Vernacular Hindi content for all user-facing screens
- [ ] WhatsApp sends, SMS sends, and in-app notifications all working
- [ ] Offline mode / poor-connectivity fallback tested
- [ ] Mobile-first pricing page loads < 2s on 3G
- [ ] Help center live with 20+ articles

### Legal

- [ ] Terms of Service published
- [ ] Privacy Policy (English + Hindi) published
- [ ] Data Processing Agreement template ready
- [ ] SLA document ready
- [ ] Refund Policy published
- [ ] DPDP Act 2023 consent mechanism active
- [ ] Grievance Officer appointed and contact published
- [ ] GSTIN registered for DZZLO entity
- [ ] SAC 998434 on all invoices
- [ ] Place-of-supply logic correct (intra-state vs inter-state GST)
- [ ] Cookie consent banner compliant
- [ ] Data localisation policy documented

### Marketing

- [ ] Landing page live (English + Hindi)
- [ ] Logo (SVG + PNG + favicon + social card)
- [ ] 60–90s demo video (English + Hindi)
- [ ] 3 written case studies (one per tier segment)
- [ ] Pricing page with ROI calculator live
- [ ] 3 tier-adjacent video testimonials
- [ ] Login-screen rotating quote carousel active
- [ ] WhatsApp message templates (welcome, reminder, broadcast, support)
- [ ] Email sequences (welcome, activation, trial-end, renewal)
- [ ] Launch blog post drafted
- [ ] Press kit ready (logos, founder bios, factsheet, high-res screenshots)

### Ops

- [ ] Slack `#launch-day` war-room channel
- [ ] On-call rotation published (24h coverage)
- [ ] Sentry / Rollbar error tracking live
- [ ] Uptime monitoring live (5+ endpoints)
- [ ] Status page public
- [ ] Incident runbook published
- [ ] Backups + restore tested in last 72h
- [ ] Load test at 3–5x expected peak documented
- [ ] Secrets rotated; 2FA on all founder accounts
- [ ] Support inbox + WhatsApp support number + ticketing tool (Intercom / Crisp / Freshdesk)

### Go-To-Market

- [ ] Product Hunt assets (tagline, images, video, first-comment)
- [ ] 200–400 PH upvoters pre-recruited
- [ ] Hunter confirmed (or deliberately skipped)
- [ ] LinkedIn founder posts drafted for launch week (7 posts, 1/day)
- [ ] WhatsApp broadcast lists segmented (design partners, waitlist, cold prospects)
- [ ] 20+ personal founder DMs pre-written and scheduled
- [ ] PR pitch drafts ready for YourStory, Inc42, Entrackr
- [ ] AIPDA / UPF / state-association intros warmed
- [ ] OMC Territory Manager contacts seeded (3 per state, min 3 states)
- [ ] Press release draft ready (timed to Day 1 milestone announcement)
- [ ] India Energy Week 2026 booth / attendance confirmed
- [ ] 3 alternative launch directories (from [Firsto list](https://firsto.co/blog/product-hunt-alternatives)) submitted

### Team

- [ ] Launch-day roles assigned (PH comments, LinkedIn DMs, support, on-call, press)
- [ ] On-call rotation through T+7 days
- [ ] Handoff document for each role (what to do if the primary is offline)
- [ ] Team availability calendar for first 14 days (no vacations)
- [ ] Post-launch retrospective scheduled for Day +10
- [ ] Founder time blocked for 25 dealer calls in first 14 days

---

## Sources → `RESEARCH_SOURCES.md`

Key sources cited in this document (full trail in `RESEARCH_SOURCES.md`):

- [Lenny Rachitsky: how to validate your B2B startup](https://www.lennysnewsletter.com/p/how-to-validate-your-b2b-startup)
- [Lenny Rachitsky: how successful B2B startups got first 10 customers](https://www.lennysnewsletter.com/p/how-the-most-successful-b2b-startups-got-their-first-10-customers)
- [SaaStr: incentives for design partners](https://www.saastr.com/dear-saastr-what-incentives-are-given-to-design-partners-and-other-super-early-customers/)
- [Waitlister.me: SaaS product launch with waitlist](https://waitlister.me/growth-hub/guides/saas-product-launch-waitlist)
- [DoWhatMatter: B2B Product Hunt launch guide](https://dowhatmatter.com/guides/product-hunt-launch-guide-b2b)
- [Blazon Agency 2026: how to launch on Product Hunt](https://blazonagency.com/post/how-to-launch-on-product-hunt)
- [Postdigitalist: Product Hunt launch analysis](https://www.postdigitalist.xyz/blog/product-hunt-launch)
- [Firsto: Product Hunt alternatives](https://firsto.co/blog/product-hunt-alternatives)
- [Directive: 2026 B2B SaaS guide](https://directiveconsulting.com/insights/b2b-saas-2026-guide)
- [PipelineRoad: multi-thread B2B accounts](https://pipelineroad.com/blog/multi-thread-b2b-accounts)
- [RentechDigital: petrol pump directory](https://www.rentechdigital.com/smartscrape/india/petrol-pumps)
- [FIPI](https://www.fipi.org.in/)
- [India Energy Week 2026 — Business Standard coverage](https://www.businessstandard.com/industry/news/india-energy-week-2026-goa)
- [India Energy Week 2026 — NewsDrum coverage](https://www.newsdrum.in/business/india-energy-week-2026)
- [World Petroleum Technology Congress 2026](https://www.worldpetroleumcongress.in/)
- [Secure Privacy: DPAs for SaaS](https://secureprivacy.ai/blog/data-processing-agreements-dpas-for-saas)
- [toslawyer: SaaS legal checklist](https://toslawyer.com/legal-checklist-for-u-s-saas-startups-tos-privacy-dpa-sla-and-more/)
- [Storylane: SaaS launch analytics](https://www.storylane.io/blog/saas-launch-analytics)
- [HexagonIT: SaaS launch checklist](https://www.hexagonitsolutions.com/saas-launch-checklist)
