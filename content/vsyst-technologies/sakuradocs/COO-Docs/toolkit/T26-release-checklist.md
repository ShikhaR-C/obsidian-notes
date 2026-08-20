# T26 — Release Checklist

_Toolkit · fills exercise 14.3 in [[12-product-and-engineering-operations|12 — Product and Engineering Operations]] · Owner: the COO owns the checklist; each release has one named **release owner**; the CEO/CTO approves the build · Cadence: every production release of app, API or web · No workbook tab — the release log is a table in the vault, and release dates ride the `Cadence Calendar` tab of [vsyst-coo-workbook.xlsx](vsyst-coo-workbook.xlsx)._

## Purpose

The engineering half of release discipline at VSYST already exists and is ahead of the company half: three repositories with PR templates and GitHub Actions, and a **cross-repo release gate** that runs all three test suites and blocks the release when red, with the house rule that every bugfix starts life as a failing test — the whole system is the [[tasks_12_tdd_testing/00-overview|tasks_12 TDD plan]]. **Do not rebuild any of it; wrap it.**

This checklist is the wrapper: **everything the test gate cannot see.** The changelog a dealer can read, the migration's rollback, the store forms that must match reality, the person who is actually watching the dashboards for the next hour, and the message that goes out afterwards. Its justification is a fact of mobile life — **a bad app release cannot be un-shipped.** There is no over-the-air escape hatch; a broken build rides store review and slow user updates for days ([[12-product-and-engineering-operations|lesson 12]] §2).

## When to use

- **Every production release** of the API, the `dip-web` console or the mobile apps. API and web deploys roll back in minutes and use the short form; a store release uses the whole thing.
- **Emergency hotfixes** skip pre-release and run the short form afterwards — the fix is allowed under the DoA's emergency clause ([[T22-delegation-of-authority-matrix|T22]]), the paperwork is not optional ([[T17-incident-postmortem|T17]]).
- **Whenever the release cadence is set or changed** — the cadence itself is a decision for [[T09-decision-log-and-adr|T09]], revisited quarterly.

## How to fill (rules)

1. **One named release owner per release**, written at the top. Not "engineering" — a person, who is reachable during the monitoring window and who closes the log entry.
2. **Green gate is a precondition, not a permission.** The suites passing means the code is safe to consider shipping; every unticked line below is a reason not to.
3. **No data change without three written things** — the migration script, the **rollback plan**, and a fresh backup taken immediately before it runs — plus a named runner and a window outside dealer peak hours (lesson 12 §10).
4. **Store review is a planning input.** Review takes days, not hours, and longer when a form is questioned — **VERIFY LIVE** typical times on each console before promising anything. Rule: **nothing customer-promised may depend on same-day store approval.**
5. **The store forms must match reality at every release that touches data collection** — Play's Data Safety declaration (accuracy is the developer's liability), Apple's privacy labels and SDK privacy manifests, and the in-app account-deletion path both stores require — all cross-checked against the data map; **VERIFY LIVE** both policies at each release ([Respectlytics — Play Data Safety](https://respectlytics.com/blog/google-play-data-safety-guide/); [Capgo — account-deletion compliance](https://capgo.app/blog/account-deletion-compliance-apple-guidelines/); [Bitrise — Apple privacy manifests](https://bitrise.io/blog/post/enforcement-of-apple-privacy-manifest-starting-from-may-1-2024)).
6. **Support is briefed before dealers are**, with the changelog in hand — so the first "what is this?" message gets a confident answer ([[T25-customer-support-sop|T25]]).
7. **Anything a dealer can see gets a plain-language message**, with a Hindi line where natural. Dealers forgive bugs and punish surprises; silent releases are reserved for changes nobody can perceive.
8. **Ship dark, then release.** Server-side flags and entitlements let you deploy code and enable behaviour separately — enable per tenant, watch, widen, and switch off in seconds without a store round-trip ([[app-store-economics/08-dzzlo-subscription-strategy|subscription strategy]]).
9. **The checklist is amended by postmortems, not by opinion.** Every SEV1/2 whose cause was a missing pre-flight adds a line here the same week.

## Template

Copy one per release into `releases/YYYY-MM-DD-<component>-<version>.md`. Owners are roles; write the name next to them.

```
RELEASE <component> <version>      date: ______   release owner: ______
Approved by: CEO/CTO ______        rollback owner: ______
```

**Pre-release**

| #   | Item                                                                                               | Owner         | Done |
| --- | -------------------------------------------------------------------------------------------------- | ------------- | ---- |
| 1   | Cross-repo release gate green on all three suites ([[tasks_12_tdd_testing/00-overview\|tasks_12]]) | CEO/CTO       | ☐    |
| 2   | Changelog written in plain language — what a dealer would notice, not commit titles                | Release owner | ☐    |
| 3   | Migration plan written (script, runner, window) — or "no data change" stated                       | CEO/CTO       | ☐    |
| 4   | **Rollback plan** written and a fresh backup taken immediately before                              | CEO/CTO       | ☐    |
| 5   | Store listing, screenshots and what's-new text current                                             | COO           | ☐    |
| 6   | Play Data Safety form, Apple privacy labels, SDK privacy manifests re-checked against the data map | COO           | ☐    |
| 7   | Account-deletion path (in-app and web) still works as declared                                     | COO           | ☐    |
| 8   | Support briefed; macros/FAQ updated for anything visible ([[T25-customer-support-sop\|T25]])       | Support owner | ☐    |
| 9   | Feature flags set to the intended start state; version gate decided (soft nudge vs hard block)     | CEO/CTO       | ☐    |
| 10  | Release window chosen outside the 10 PM–6 AM rate window and dealer peak hours                     | Release owner | ☐    |

**Release**

| #   | Item                                                                                                                                                     | Owner          | Done |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------- | ---- |
| 11  | Deploy / submit; note the exact time in the log                                                                                                          | Release owner  | ☐    |
| 12  | Staged rollout started at a small percentage — widen only while crash-free numbers hold (**VERIFY LIVE** the console's current staged-rollout mechanics) | CEO/CTO        | ☐    |
| 13  | Monitoring window opened with a human watching: crash-free rate, API error rate, OTP delivery, push delivery, cron jobs                                  | Release owner  | ☐    |
| 14  | Smoke-check the core loop on a real device: rate set → order → dispatch OTP → invoice → voucher                                                          | COO or support | ☐    |
| 15  | Abort criteria agreed before starting — what number, at what level, triggers rollback                                                                    | Release owner  | ☐    |

**Post-release**

| #   | Item                                                                                 | Owner         | Done |
| --- | ------------------------------------------------------------------------------------ | ------------- | ---- |
| 16  | Dealer announcement sent where the change is visible (English + a Hindi line)        | Support owner | ☐    |
| 17  | 48-hour watch: errors, OTP/push delivery, crash-free rate, ticket volume by category | Release owner | ☐    |
| 18  | Rollout widened to 100%, or rolled back with the reason written                      | CEO/CTO       | ☐    |
| 19  | Release closed in the log: date, version, owner, what shipped, anything learned      | Release owner | ☐    |
| 20  | Any surprise added as a new line to this checklist                                   | COO           | ☐    |

**Short form** (API/web deploy, or a hotfix after the fact): gate green · rollback plan · deploy time logged · 60-minute watch · support told · log entry closed.

## VSYST example — a monthly app train

A sane starting cadence, agreed with the CTO and logged in T09: **API and `dip-web` deploy weekly or on demand** (they roll back in minutes), **the mobile apps ride a monthly train** (a store release takes days to propagate and lives on phones for weeks). The train's shape: the build cuts on a fixed day; items 1–10 are ticked over the following two days; submission goes in with a review buffer that assumes days, not hours; staged rollout opens small the morning after approval; the dealer message goes out only once the rollout has held for a day; the release closes at the end of the 48-hour watch with one line in the log.

Two habits make this cheap rather than ceremonial. **The log is one table, not a document per release** — date, component, version, owner, one line of "what shipped", one line of "what we learned". And **deploy frequency, incidents, MTTR and bug-backlog age are scorecard rows** ([[T05-kpi-scorecard|T05]]), so a stalling train shows up on a Monday rather than at a quarterly review.

## Related

Lessons [[12-product-and-engineering-operations|12]] (releases, environments, app-store operations, change management), [[10-customer-operations-support-and-success|10]] (who tells the dealers), [[15-sops-and-playbooks|15]] (checklists vs SOPs) · Templates [[T17-incident-postmortem|T17]], [[T25-customer-support-sop|T25]], [[T09-decision-log-and-adr|T09]], [[T22-delegation-of-authority-matrix|T22]], [[T14-vendor-and-tool-register|T14]] · [[tasks_12_tdd_testing/00-overview|tasks_12 TDD plan]] · [[toolkit/index|COO Toolkit]]
