# 12 — Product and Engineering Operations

_Phase 3 · Build the Machine · Months 2–6. After this lesson you can run the process around shipping without touching the code: a release cadence wrapped in a checklist, app-store listings and privacy forms that pass review, an incident process with severity levels and a blameless postmortem, monitoring that pages a named person, backups that provably restore, a product-side DPDP data map and breach one-pager, and four engineering numbers on the scorecard._

## 1. The COO and the CTO — who owns what in shipping

At VSYST the CEO is also the technical founder — the person who wrote the apps, the API and the web console. That makes this lesson's boundary the most delicate one in the course: **the COO owns the process around shipping, never the code.** You will not review pull requests, argue architecture, or have opinions about MongoDB schemas. You will own that releases happen on a rhythm, pass a checklist, don't surprise dealers, survive incidents with a process instead of adrenaline, and leave numbers behind.

The clean split:

| Question                             | CEO/CTO owns                                                             | COO owns                                                                           |
| ------------------------------------ | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| What gets built, and how             | Product direction, architecture, code, code review, technical debt calls | —                                                                                  |
| When and how it ships                | The deploy itself, the technical gate                                    | The cadence, the checklist, the go/no-go ritual, comms                             |
| When it breaks                       | The fix                                                                  | The incident process, severities, the rota, dealer comms, the postmortem happening |
| What it runs on                      | Technical choice of AWS/Atlas/OneSignal/2Factor                          | The vendor register rows, SLAs, credentials, spend alerts                          |
| What the law requires of the product | Implementing controls                                                    | The data map, breach process, store forms, DPDP artefacts, deadlines               |
| Whether it's healthy                 | Fixing what the numbers reveal                                           | The numbers existing, being read weekly, and triggering action                     |

Why the seat needs this at all: a solo-shipping founder is a single point of failure wrapped in a habit. Releases happen when energy allows, knowledge lives in one head, an outage at 2 AM is heroism instead of a page, and nobody outside the code knows whether this month was healthy. Every mechanism in this lesson is a way of converting that private reliability into company property — which is precisely the operating-system job. The test of whether you're doing it right: **releases get boring.** Boring is the goal.

## 2. Release cadence and the release checklist

Start from an honest inventory: the engineering half of release discipline already exists, and it is ahead of the company half. The three repos (`dzzlo_oms_api`, `dzzlo_oms_app`, `dip-web`) carry PR templates, GitHub Actions, and a cross-repo **release gate** — one script that runs all three test suites (hundreds of API integration tests as the backbone, plus web and app suites) and **blocks the release when red**, with a house rule that every bugfix starts life as a failing test. That whole system, including the per-repo PR checklists and runtime budgets, is the [[tasks_12_tdd_testing/00-overview|tasks_12 TDD plan]]. Do not rebuild any of it; wrap it.

The COO adds two things. First, **a cadence** — fixed release windows beat "whenever it's ready", because a rhythm makes everything downstream (store review buffers, dealer comms, support readiness) plannable. Decide it with the CTO and write it down (a sane starting shape: API/web deploys weekly or on demand, since they roll back in minutes; the mobile app on a monthly-ish train, since a store release is days to propagate and lives on phones for weeks). Record the decision in [[T09-decision-log-and-adr|T09]]; revisit quarterly.

Second, **the release checklist** ([[T26-release-checklist|T26]]) — everything the test gate cannot see:

- **Pre-release:** gate green (necessary, never sufficient) · plain-language changelog written · migration plan _and rollback plan_ for any data change · store listing, screenshots and privacy forms current (§4) · support briefed on what changes · a named **release owner** for this release.
- **Release:** staged rollout on Play (a small percentage first, widen as crash-free numbers hold — **VERIFY LIVE** the console's current staged-rollout mechanics) · monitoring window with someone actually watching §6's dashboards.
- **Post-release:** dealer announcement where the change is visible (§10) · 48-hour watch on errors, OTP/push delivery and support tickets · close the release with a one-line log entry — date, version, owner, anything learned.

The mobile reality that justifies all this ceremony: **a bad app release cannot be un-shipped.** There is no over-the-air escape hatch; a broken build rides store review and slow user updates for days. The staged rollout, the server-side version gate (§10) and the checklist are how a two-person engineering effort makes that risk survivable.

## 3. Environments and secrets hygiene

An **environment** is one complete copy of the system — code, configuration, data. Confusing two of them is how test data emails a real dealer, or a debugging session touches production ledgers. The COO doesn't administer environments; the COO makes sure the map is written and three rules are enforced:

| Environment              | What it is                                        | Data in it                                                                                                                                             |
| ------------------------ | ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Local                    | A developer's machine                             | Seeded, throwaway                                                                                                                                      |
| Test suites              | In-memory databases created and destroyed per run | Synthetic only — the [[tasks_12_tdd_testing/00-overview\|tasks_12]] constraint is explicit: **no test in any repo may reach cloud or production data** |
| Staging (when it exists) | A production-shaped copy for final checks         | Synthetic or anonymised                                                                                                                                |
| Production               | The real thing dealers run on                     | Real — treated as radioactive                                                                                                                          |

The rules, all inherited from lesson 07 and restated here because releases are where they get broken:

1. **Secrets never live in code or chat.** `.env` files are never committed; production values live as Bitwarden secure notes; signing keys, store certificates and provisioning profiles are in Bitwarden with sealed copies in the binder; rotation happens on every offboarding ([[T13-offboarding-checklist|T13]]).
2. **Production access follows the DoA.** Who may deploy, who may open a production database session, who may run a migration — named rows in [[T22-delegation-of-authority-matrix|T22]], reviewed at the quarterly access review. At today's size that list is one or two names; write it anyway, because the exception you'll regret is the contractor given "quick access" during a rush.
3. **Production data is not test data.** Debugging with a copy of real dealer ledgers on a laptop is a DPDP incident waiting for a lost bag (§9). Anonymise or synthesise.

## 4. App-store operations

DZZLO lives or dies on two storefronts, and the stores are a compliance surface the COO owns end-to-end — the CEO/CTO builds the binary; you own that everything wrapped around it is current, truthful and review-proof. The working set:

- **The listing pack.** Screenshots, descriptions, what's-new text, support URL and contact — versioned in Drive, updated as part of T26, owned by you. A stale listing quietly costs conversions; a wrong one costs review rejections.
- **Review timelines are a planning input.** Store review takes days, not hours, and can take longer when a form is questioned — **VERIFY LIVE** current typical times on each console before promising any dealer a date. Rule: nothing customer-promised may depend on same-day store approval.
- **Google Play Data Safety form.** Declares what data the app collects and why; accuracy is the developer's liability and Play's policy enforcement has tightened ([Respectlytics — Google Play Data Safety guide, 2026](https://respectlytics.com/blog/google-play-data-safety-guide/)). It must match reality — cross-check it against the §9 data map at every release that touches data collection.
- **Account deletion.** Apple requires an in-app account-deletion path (in force since 30 June 2022), and Play requires deletion in-app **and** via a web link ([Capgo — account-deletion compliance under Apple's guidelines](https://capgo.app/blog/account-deletion-compliance-apple-guidelines/)) — **VERIFY LIVE** both policies at each release; confirm DZZLO's deletion flow actually deletes what it claims (§9's retention note is the reference).
- **Apple privacy labels and SDK privacy manifests.** The privacy "nutrition labels" must stay truthful, and third-party SDKs need privacy manifests (enforced since 1 May 2024 — [Bitrise — Apple privacy-manifest enforcement](https://bitrise.io/blog/post/enforcement-of-apple-privacy-manifest-starting-from-may-1-2024)); the SDK list (push, analytics) is exactly the vendor list in §8.
- **The purchase-silent posture.** VSYST's monetisation runs entirely on the web; the app must contain **no prices, no purchase links, no upgrade buttons** — locked features render as "not part of your company's plan", and store listings stay scrubbed of buying language. The reasoning, the India-storefront steering rules, and the reviewer-notes tactics (a demo account on a representative plan) live in the [[app-store-economics/08-dzzlo-subscription-strategy|subscription strategy]] — treat that doc as binding for anything store-adjacent.

Put a quarterly "store audit" line on the cadence calendar: forms vs reality, listing freshness, developer-account contacts and payment method valid, both consoles owned by company accounts (lesson 07).

## 5. Incident management

An **incident** is any unplanned event that degrades the service dealers depend on. The difference between a company that handles incidents and one that survives them by luck is written down in advance: severity levels, a rota, a response sequence, comms templates, and a postmortem habit. All of it fits on two pages ([[T17-incident-postmortem|T17]]), and none of it requires more than two people.

**Severity levels** — decided in the calm, so nobody debates them at 2 AM:

| Sev      | Definition                                            | DZZLO examples                                                                                                      | Response                                                                              |
| -------- | ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **SEV1** | Core loop down or data at risk for many tenants       | API down; OTP delivery dead during dispatch hours (no deliveries can complete); data corruption or suspected breach | Page the on-call now, all hands, dealer comms within 60 min, fix before anything else |
| **SEV2** | A major function degraded, or one tenant hard-blocked | Rate-confirmation pushes failing in the 10 PM–6 AM window; invoice generation broken; a tenant locked out           | Work within hours; affected dealers informed; fix or workaround same day              |
| **SEV3** | Annoying, not blocking                                | Cosmetic bugs, a report mis-sorting, single-user how-to confusion                                                   | Ticket queue, normal prioritisation (lesson 10)                                       |

**The on-call rota — yes, for two people.** On-call means: this week, one named person's phone rings loudly for SEV1 alerts, nights included, and everyone knows who. With two eligible people it alternates weekly, published on the `Cadence Calendar` tab of [the workbook](toolkit/vsyst-coo-workbook.xlsx), with the other person as documented escalation. The point is not bureaucracy — it is that "who is watching?" always has exactly one answer, and that the technical founder can be unreachable for a week without the answer becoming "nobody" (the two-week test of lesson 20 starts here).

**The response sequence:** detect (an alert, §6, or a dealer report via lesson 10's escalation) → acknowledge (SEV1: within 15 minutes) → stabilise, which usually means **roll back first, diagnose later** → communicate → resolve → postmortem. During a SEV1/2 the roles split: the CEO/CTO fixes; the COO (or support owner) runs comms and keeps a timestamped log of events as they happen — that log becomes the postmortem's spine.

**Status comms to dealers happen on WhatsApp**, because that is where dealers live, from templates written in advance (T17 holds them): what's affected, what still works, when the next update comes — plain language, a Hindi line where natural, no jargon, no blame, never a promise of a fix time you don't have. Silence is what dealers punish; a 9 PM "we know, here's what works meanwhile, update by 10 PM" builds more trust than the outage cost.

**The blameless postmortem** follows every SEV1/2 within five working days. Google's SRE practice is the standard: a written record of impact, timeline, root causes and corrective actions with owners and dates — blameless because it "focuses on identifying the contributing causes of the incident without indicting any individual or team for bad or inappropriate behavior" ([Google SRE Book — Postmortem Culture](https://sre.google/sre-book/postmortem-culture/); [incident.io — postmortem best practices](https://incident.io/blog/sre-incident-postmortem-best-practices)). In a family founding team, blamelessness is not a nicety — it is the only way the incident record stays honest. Action items become tracked issues and get read out at the weekly ops meeting until closed; an incident whose actions never land will repeat on schedule.

## 6. Monitoring and alerting — manage by exception

You cannot manage by exception (lesson 02's discipline) if nothing raises exceptions. Monitoring is the machine that watches the machine, and the free tiers are enough for years: **UptimeRobot or Better Stack** pinging the public surfaces, **Sentry** catching errors inside the API and apps (recommended stack per lesson 07's tool table — free tiers, **VERIFY LIVE** current limits). The CEO/CTO wires them; the COO owns that the watchlist is complete and that alerts reach the rota.

DZZLO's watchlist — note how product-specific the middle rows are; generic uptime is the _least_ of it:

| Watch                                                 | Why it matters here                                                                                                      | How                                                                                                                                                |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| API + dip-web up                                      | Everything                                                                                                               | Uptime monitor, 1–5 min checks                                                                                                                     |
| Error rate / new exceptions                           | A bad deploy announces itself here first                                                                                 | Sentry alert on new issue / spike                                                                                                                  |
| **OTP delivery rate (2Factor)**                       | Login and delivery OTPs are the product's front door — a silent SMS failure stops dispatches while everything "looks up" | Panel checks + a delivery-rate scorecard row; **low-balance alert** on the SMS account (a prepaid balance hitting zero is a self-inflicted outage) |
| **Push delivery (OneSignal)**                         | The 10 PM–6 AM rate-confirmation window runs on push; failures here corrupt the next morning's trade                     | Delivery dashboards; a synthetic test notification before the window on release days                                                               |
| Scheduled jobs (month-end roll-ups, digests)          | Cron that fails silently is data quietly rotting                                                                         | Jobs report completion; a missed heartbeat alerts                                                                                                  |
| Disk, database storage, certificate and domain expiry | The boring outages                                                                                                       | Provider alerts + register renewal dates ([[T14-vendor-and-tool-register\|T14]])                                                                   |
| AWS / Atlas spend                                     | A runaway bill is an incident too                                                                                        | Billing alerts at agreed thresholds (§8)                                                                                                           |

Three rules keep the system alive: **every alert is actionable and owned** (an alert nobody acts on is deleted or tuned — alert fatigue kills the whole mechanism); **overnight paging is for SEV1-class checks only**, everything else waits for morning; and **the dashboards get a standing look every Monday** before the scorecard is filled, so trends are seen before they become incidents.

## 7. Backups and restore drills

Lesson 07 §5 already built the backup map — Atlas cloud backups plus a periodic `mongodump` for the production database, snapshots and written rebuild notes for the API server, git everywhere, ERPNext site backups, sealed key copies — and its law stands: **a backup you have never restored is a hope, not a backup.** What this lesson adds is the operating cadence that keeps it true:

- **Quarterly restore drill, on the calendar, rotating through systems.** One quarter the Atlas restore to a scratch cluster; the next, rebuilding the API server from the written notes; then an ERPNext restore into a test site. Run by **the person who did not build the system**, from the notes — if they fail, the notes failed; fix the notes the same day.
- **Every drill leaves a log entry**, in a `restore-drills` note in the vault: date · system · who ran it · time to restore (RTO achieved) · data window lost (RPO achieved) · targets met? · gaps found · fix owner and date. Four lines a quarter is the entire cost of knowing the company can survive a dead server.
- **The drill result feeds the risk register** ([[T15-risk-register|T15]], lesson 13): "server loss" and "data loss" carry mitigation entries that literally cite the last drill date. An 11-month-old drill date is a red flag a director should be able to spot in one glance.

## 8. Vendor dependencies — the five that can stop the product

DZZLO's production stack stands on a handful of vendors, and each is a company-stopping dependency with its own failure mode. The register ([[T14-vendor-and-tool-register|T14]]) already lists them as tools with costs and renewals (lesson 07); this section is the _dependency_ view — what you need to know about each before it fails:

| Vendor                          | If it fails…                                                              | The COO's homework                                                                                                                                                                                                                                               |
| ------------------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AWS** (EC2, SES)              | API and email down                                                        | Billing alerts set; root account sealed on an alias with hardware 2FA (lesson 07); rebuild notes drilled (§7); status page bookmarked                                                                                                                            |
| **MongoDB Atlas**               | The data                                                                  | Backup tier confirmed — **VERIFY LIVE** what the current plan includes; restore drilled quarterly; spend alert                                                                                                                                                   |
| **OneSignal** (push)            | Rate-confirmation window degrades                                         | Free-tier limits known — **VERIFY LIVE** the threshold where it turns paid; provider kept behind one code module so it can be swapped (lesson 07's rule)                                                                                                         |
| **2Factor.in** (SMS/OTP)        | Logins and deliveries stop — the sharpest single-vendor risk in the stack | **Prepaid balance floor alert**; delivery rate on the scorecard; same one-module swap rule; a second SMS provider's onboarding requirements researched _before_ the day you need them                                                                            |
| **Easebuzz / UBI IPG** (future) | Subscription collections stop                                             | Still in discussion — when live: settlement report checks, escrow terms read, and the dealer↔customer payment leg kept separate from VSYST's own subscription collection (per the [[app-store-economics/08-dzzlo-subscription-strategy\|subscription strategy]]) |

For each row, four facts belong in the register: **the SLA** (or the honest note "free tier — no SLA", which is itself a risk-register input — **VERIFY LIVE** each vendor's current terms), **where the credentials live** (Bitwarden, owner alias — never a personal login), **the spend alert** (threshold and who receives it), and **the swap path** (what it would take to leave — the export-path column lesson 07 insists on). Review the five rows at the quarterly vendor audit (lesson 14), and put the top one or two single-vendor risks into [[T15-risk-register|T15]] with a stated mitigation — for a fuel-distribution OMS whose deliveries hinge on OTPs, "OTP vendor outage" belongs near the top.

## 9. Security and DPDP for the product

Lesson 07 §6 set the company's twelve security controls and introduced the two laws; lesson 13 will put their deadlines on the compliance calendar. This section is the **product's** slice: DZZLO processes personal data — dealer and customer phone numbers, names, driver details, credit ledgers — and three artefacts make that defensible. All legal specifics below are **VERIFY LIVE with the lawyer**; the DPDP Rules commence in phases (the Data Protection Board stood up in November 2025; the substantive obligations bind from **13 May 2027**, with the older IT Act SPDI regime applying until then — [Scrut — DPDP Rules explained](https://www.scrut.io/post/dpdp-rules); [Seclore — DPDP Rules 2025 compliance guide](https://www.seclore.com/fundamentals/dpdp-rules-2025-compliance-guide/)).

**Artefact 1 — the data map.** One table: what personal data · whose it is · where it lives (Mongo collections, S3, logs, WhatsApp threads, analytics) · why we hold it · how long · who can access it. Two roles fall out of it, and they carry different duties: for its own users, employees and leads, VSYST is the **Data Fiduciary** (the party deciding purpose); for the dealer's end-customer data inside tenants, VSYST is a **Data Processor** working on the dealer's behalf — which is why the customer agreement needs data-processing clauses (lesson 05). The map is also what keeps the Play Data Safety form and Apple labels truthful (§4).

**Artefact 2 — the breach one-pager, with two clocks.** India runs two parallel reporting regimes and both apply to a company of three:

- **CERT-In: 6 hours.** Listed cyber incidents must be reported to CERT-In within six hours of noticing; ICT logs must be retained for **180 days in India**; clocks synced to NIC/NPL NTP; a point of contact designated — no size exemption ([SIRI Law — CERT-In's 6-hour mandate](https://sirilawllp.com/a-comprehensive-guide-to-indias-cert-in-6-hour-cyber-incident-reporting-mandate/); [IncorpX — CERT-In compliance 2026](https://www.incorpx.io/blog/cert-in-cybersecurity-compliance-2026)).
- **DPDP: without delay, then 72 hours.** On a personal-data breach, affected people are intimated without delay and a detailed report goes to the Data Protection Board within 72 hours; the penalty exposure for failures runs to hundreds of crores ([Scrut](https://www.scrut.io/post/dpdp-rules)).

The one-pager names who calls whom (the lawyer first), both deadlines, the CERT-In contact, and the dealer-comms template — and a suspected breach is automatically a SEV1 under §5, with the postmortem feeding the report.

**Artefact 3 — the retention note.** DPDP's direction of travel is erase-when-purpose-served, with security logs kept **at least a year** under the Rules — which, held against CERT-In's 180 days, means: keep security logs one year, and write down a purge rule for everything else (old OTP logs, stale invites, deleted-account data — the §4 deletion path must actually honour this). One paragraph per data class, agreed with the CEO/CTO and the lawyer.

## 10. Change management — flags, migrations, comms

**Change management** is the discipline of altering a live system that real pumps bill real diesel through, without breaking their trust. Three mechanisms:

**Server-side flags and entitlements.** The cleanest change tool DZZLO has is already designed into the [[app-store-economics/08-dzzlo-subscription-strategy|subscription strategy]]: the server resolves what each company can see, and clients only render that state. The same pattern decouples _deploying_ code from _releasing_ behaviour — ship dark, enable per tenant, watch, widen, and turn off in seconds if it misbehaves (a rollback with no store review attached). Alongside it sits the **server-side version gate**: the API can soft-nudge or hard-block outdated app versions, which is what lets the backend move without stranding old phones. Use the hard block sparingly and always with notice — a dealer force-updated mid-morning is an incident you caused.

**Migrations.** Any change to data shape ships with three written things: the migration script, the **rollback plan**, and a fresh backup taken immediately before it runs — plus a named runner and a time window outside dealer peak hours. The repos already practise script-based migrations for schema changes; the checklist (T26) makes plan-rollback-backup a gate, not a virtue.

**Comms.** Dealers forgive bugs and punish surprises. Anything a dealer can _see_ — a moved button, a changed invoice layout, new rate-screen behaviour — gets a plain-language WhatsApp note before or with the release (a Hindi line where natural), and **support is briefed before dealers are**, with the changelog in hand, so the first "what is this?" message gets a confident answer. Silent releases are reserved for changes nobody can perceive.

## 11. Roadmap hygiene

The COO does not decide what gets built. The COO keeps the deciding honest:

- **One backlog.** All of it — bugs, feature asks, partner requests, tech debt — lives in GitHub Issues/Projects (lesson 07's choice), not in WhatsApp, memory, or three notebooks. If it isn't in the backlog it doesn't exist.
- **Intake is plumbing, and it's yours.** The support complaint log (lesson 10's feedback loop), field-visit notes (lesson 11 §8) and partner asks flow into the backlog weekly, each tagged with its source and how many tenants it touches — so the CEO/CTO prioritises against evidence, not against whoever asked loudest or latest.
- **Quarterly themes, not a hundred-item list.** Each quarter names two or three themes in the quarterly plan (lesson 19); the backlog is groomed against them. At one-to-two engineers the honest WIP limit is **one theme at a time** — everything this course says about focus applies triple to engineering capacity.
- **Saying no is written down.** Declined-for-now requests get a one-line reason on the issue. It converts "they ignored me" into "they decided" — and gives sales an honest answer for the dealer who asked.
- **A roadmap is not a promise.** Nothing on it is committed to a dealer or partner with a date unless it has a [[T18-project-charter|T18]] charter behind it. Sales sells what exists; partnerships negotiate with charters, not vibes.

## 12. The engineering numbers the COO watches

Four numbers, on the scorecard ([[T05-kpi-scorecard|T05]]), filled from systems rather than memory:

| Metric                       | Definition                                                   | Source                  | What it tells you                                                                                         |
| ---------------------------- | ------------------------------------------------------------ | ----------------------- | --------------------------------------------------------------------------------------------------------- |
| **Release/deploy frequency** | Deploys per week (API/web); app releases per quarter         | GitHub / store consoles | The machine's shipping rhythm — a stall here predicts everything else stalling                            |
| **Incidents**                | Count by severity per week                                   | The incident log (§5)   | Stability trend; a rising SEV2 line is the early warning                                                  |
| **MTTR**                     | Mean time to restore — detection to service restored, SEV1/2 | Incident log timestamps | How good the §5–§7 machinery actually is; postmortems should push it down                                 |
| **Bug backlog age**          | Open bug count and the age of the oldest                     | GitHub Issues           | Whether quality debt is compounding; pair with a ratchet rule ("nothing over 90 days without a decision") |

Set the RAG thresholds _with_ the CEO/CTO, not for them, and add the two product-health rows from §6 (OTP delivery rate, push delivery rate) — lesson 16's KPI tree includes both. Then the rule that makes the whole section safe to run inside a founding team: **these numbers measure the machine, never the person.** Read weekly at the ops meeting, they trigger questions ("MTTR doubled — what does the postmortem say we need?"), never verdicts. The week a scorecard row becomes an accusation is the week the data starts lying to you — the same blameless logic as §5, because the alternative isn't accountability, it's fiction.

## 13. At VSYST — applying this now

- **Start from what exists, and say so out loud.** The [[tasks_12_tdd_testing/00-overview|tasks_12]] release gate, test suites and PR checklists mean the _engineering_ half of release discipline is already ahead of the _company_ half. Your first move is not to add process to the code — it is to wrap T26 around the gate, agree the cadence, and put names on rota and release-owner slots. Tell the CEO/CTO exactly that framing; this lesson lands better as "your gate, made company property" than as new rules.
- **This month, in order:** the severity table and rota agreed and published (exercise 14.1); uptime checks, Sentry, the 2Factor low-balance alert and AWS/Atlas billing alerts switched on — all free tiers; the quarter's restore drill run and logged (14.2); T26 filled for the next store release, including the Data Safety / account-deletion / privacy-label audit (14.3); the four metrics on the scorecard (14.4).
- **Write the two DPDP artefacts early, while they're small.** The data map and breach one-pager take an afternoon now, with one product and a handful of collections; they take a consultant later. May 2027 feels far away exactly until it isn't — and CERT-In's six-hour clock applies _today_ (**VERIFY LIVE** both with the lawyer).
- **Respect the delicacy.** The CEO/CTO has shipped a production system across three repos with a test discipline most funded startups lack. Every mechanism here should read as insurance for the days he is sick, travelling, or — the good ending — managing other engineers. The lesson 01 trap applies in mirror image: don't become the process police; own outcomes (boring releases, informed dealers, numbers that exist) and let the checklist be the servant.
- **What not to do:** no incident-management SaaS, no status-page product, no Kubernetes, no second APM tool, no 30-page security policy. A vault note, a WhatsApp template, two free monitors and a rota beat all of it at this size.

## 14. Exercises

**14.1 — Severity table and on-call rota (30 min, with the CEO/CTO).** Rewrite the §5 severity table with real DZZLO examples you both agree on — argue about the edge cases (is push failure during the rate window SEV1 or SEV2? decide now, not at midnight). Put the result at the top of [[T17-incident-postmortem|T17]], and publish the first four weeks of the rota on the `Cadence Calendar` tab of [the workbook](toolkit/vsyst-coo-workbook.xlsx). Artefact: a severity table nobody has to invent during an outage, and one name per week.

**14.2 — Run this quarter's restore drill (60–90 min, CEO/CTO drives, you time it).** Pick the system least recently proven — if lesson 07's Atlas restore is done, rebuild the API server from the written notes onto a fresh instance. The person who didn't build it runs it, from the notes. Log date, RTO/RPO achieved, gaps found and fix owners in a `restore-drills` vault note, and update the [[T15-risk-register|T15]] mitigation line with the drill date. If the notes failed, fixing them today is the deliverable.

**14.3 — Fill T26 for the next release (30 min, with the CEO/CTO).** Take the next planned store release and fill [[T26-release-checklist|T26]] end to end: gate, changelog, migration/rollback, staged-rollout plan, monitoring window, dealer note, 48-hour watch — plus the store-compliance audit from §4 (Data Safety form vs the data map, deletion path works, labels truthful, listing current, zero purchase language). Whatever the checklist reveals as missing becomes this week's issue list. Artefact: a filled checklist and a named release owner.

**14.4 — Four engineering metrics on the scorecard (15 min).** Add the §12 rows to [[T05-kpi-scorecard|T05]] with a source query, an owner and a RAG threshold each; add OTP and push delivery rates alongside. Enter this week's honest values — blanks and reds included. The first month of these numbers is a baseline, not a verdict; write that sentence on the tab so it stays true.

---

**Next:** [[13-compliance-calendar-risk-and-insurance|13 — Compliance Calendar, Risk and Insurance]] — the year's filing calendar built with the CA/CS, the risk register with the top twelve startup risks scored and owned, business continuity, and the insurance stack from group health to D&O.
