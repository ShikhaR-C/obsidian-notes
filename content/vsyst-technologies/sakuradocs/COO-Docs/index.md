---
title: COO Docs
---

# COO Docs — Build and Run VSYST's Operating System

> Audience: whoever holds the **Chief Operating Officer seat at VSYST Technologies Pvt. Ltd.** (Raipur) — today a founder-director wearing the operations hat, tomorrow possibly a hired COO | Where we are: **newly formed, bootstrapped, pre-revenue; nothing operational established yet** — no cadence, no policies, no SOPs, no dashboards, no hiring process, no compliance calendar | Goal: understand the COO role, build the company's operating system from scratch, and run it well enough that the company **works without heroics — on autopilot** | Written & sanity-checked **2026-08-19** for an Indian Private Limited software company.

## Explain-it-like-I'm-5

A company is a **machine that turns effort into promises kept** — a dealer signs up and gets onboarded, an invoice goes out and money comes back, a bug is reported and fixed, a filing falls due and gets filed, a person is hired and becomes productive. When the company is three people, the machine is _you_: your memory, your WhatsApp, your Sunday nights. That works until the day it doesn't — a missed GST date, a customer nobody replied to, a founder falls sick and the deploys stop.

The **COO** — Chief Operating Officer — is the person who **builds the machine so it isn't you anymore**. The CEO decides _where_ the company goes and _why_; the COO makes sure it actually gets there, on time, at a cost the company can afford, without breaking anything or anyone. Every recurring thing gets an owner, a rhythm, a number that shows whether it's healthy, and a written way of doing it. Then the founders can steer instead of push.

That is the whole job. It looks like management; it is really **systems design applied to people, money, customers and time** — a discipline you already have as an engineer, pointed at a different machine.

## What This Folder Is

A **four-phase, hands-on course plus a toolkit** that takes someone with _no management background_ from "what does a COO even do?" to "here is VSYST's operating system, and here is the two-week holiday I took while it ran." It is written for **our actual company** (VSYST Pvt Ltd, maker of DZZLO OMS), **our actual stage** (just formed, nothing set up), and **our actual tools** (Obsidian + Quartz for docs, GitHub, AWS/Mongo, Expo, ERPNext, Figma, WhatsApp) — not a generic MBA syllabus.

Every lesson ends with exercises that produce something real: a signed operating agreement, a filled scorecard, a compliance calendar, an SOP, a decision log entry. The [[COO-Docs/toolkit/index|COO Toolkit]] holds the 30 templates those exercises fill, and [vsyst-coo-workbook.xlsx](toolkit/vsyst-coo-workbook.xlsx) holds the spreadsheets (runway & 13-week cash, KPI scorecard, OKRs, compliance calendar, vendor register, risk register, RACI, hiring pipeline, headcount plan and more — import it into Google Sheets).

Four neighbouring docs already exist, and this course **plugs into them instead of repeating them**:

- [[startup-operations-plan|Startup Operations Plan]] — the _business-level_ habits (advances, weekly cash check, the realities). This course is the _operating system underneath_ those habits.
- [[ERPNext-Implementation-Guide|ERPNext Implementation Guide]] — how to stand up ERPNext. Lessons 06, 09–11 assume it is our system of record for money, CRM, HR and support tickets.
- [[finance/00_README|Finance for Founders]] — the founder-CFO course. Where a lesson here touches money, it points there for the accounting depth.
- [[company/README|DZZLO Company Building Playbook]] — GTM, pricing, launch and acquisition research. Lessons 10–11 turn parts of it into operating routines.

## The One Idea That Governs Everything

> **Your product is the operating system, not the output.**

The engineer's product is code. The salesperson's product is a signed dealer. **The COO's product is the machine that produces those reliably** — the cadence, the owners, the numbers, the documents, the automations. If you find yourself doing the output every day (answering every ticket, filing every form, chasing every invoice), you are not yet doing the job; you are the machine's missing part. Amazon's phrase for the discipline is worth memorising: **good intentions don't work; mechanisms do.** Every recurring problem in this course gets a mechanism — an owner, a rhythm, a metric and a document — and never a resolution to "be more careful".

The corollary is the rule that runs the whole course:

```
If it happens twice        → write it down          (an SOP, lesson 15)
If it happens weekly       → put it on the scorecard (a number, lesson 16)
If it happens daily        → automate it            (a script or agent, lesson 18)
And in every case          → give it one owner       (a name, lesson 17)
```

## The COO's Toolkit (what you are actually learning to operate)

| The tool                       | ELI5                                                                | Its job for VSYST                                 | Taught in         |
| ------------------------------ | ------------------------------------------------------------------- | ------------------------------------------------- | ----------------- |
| **The CEO–COO contract**       | Who decides what, written down                                      | Stops two founders stepping on each other         | 03, T01, T22      |
| **The company binder**         | Every paper the company must have, in one place                     | Legal existence, filings, credentials, contracts  | 05, T02           |
| **The operating cadence**      | The company's heartbeat — daily, weekly, monthly, quarterly, annual | Problems surface on schedule, not by accident     | 08, T03, T04, T24 |
| **The scorecard**              | 5–15 numbers that say whether the machine is healthy                | Manage by exception instead of by inbox           | 16, T05, T28      |
| **SOPs & playbooks**           | "How we do X here", written so someone else can do it               | Delegation and autopilot become possible          | 15, T08, T25, T26 |
| **RACI / DoA**                 | One owner per outcome; who may spend or sign what                   | Decisions get made without you                    | 17, T07, T22      |
| **The compliance calendar**    | Homework-with-deadlines for an Indian Pvt Ltd                       | Zero missed filings, zero surprises               | 13, T16           |
| **The risk register**          | The list of things that could kill us, ranked                       | You fix the top three before they happen          | 13, T15           |
| **The vendor & tool register** | Every subscription, contract and renewal                            | Costs stay visible; nothing auto-renews unnoticed | 07, 14, T14       |
| **OKRs & the quarterly plan**  | This quarter's 3–5 promises, measured                               | The company moves in one direction                | 19, T06, T19      |
| **The people system**          | Hire → onboard → 1:1 → review → exit, each with a checklist         | Good people join, ramp and stay                   | 09, T10–T13, T27  |
| **Automation & AI agents**     | Scripts and agents that do the daily grind                          | The daily work stops needing a human              | 18                |
| **The workbook**               | The spreadsheets behind all of the above                            | Where the numbers live until we have dashboards   | Toolkit           |

Read that top to bottom and you have read the course: agree the seat (03), record the company (05–07), install the heartbeat (08), build each function one at a time (09–14), then systematise, measure, delegate, automate and plan (15–19) until the two-week test passes (20).

## Where VSYST Stands Today (and what that means for the COO)

| Fact about us                                                                               | What it means for this course                                                                                                                                                      |
| ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Private Limited company, three founder-directors, family-founded**                        | Governance is real from day one: board minutes, ROC filings, statutory audit. Decision rights between founders must be _written_ (lesson 03), not assumed.                         |
| **Newly formed; no operating system yet** (assumed stage)                                   | Everything here starts from a blank page. Order matters — the [[COO-Docs/00-course-map-and-timeline\|master timeline]] tells you what to set up in which week.                     |
| **Bootstrapped, pre-revenue**                                                               | Cheap-or-free tools, contractors before employees, every rupee of tooling on the register. The COO owns the _operational_ causes of cash: collections, cost control, vendor terms. |
| **One product (DZZLO OMS), live on both app stores, India-only, sales-assisted**            | Customer ops, revenue ops and product/engineering ops (lessons 10–12) are written for a fuel-distribution SaaS sold to dealers in one district at a time.                          |
| **A technical CEO who ships code; a domain-expert director; a small team**                  | The COO's first job is to take the _non-building_ work off the technical founder and turn it into mechanisms — without becoming the new bottleneck (lesson 17).                    |
| **Docs already live in this Obsidian/Quartz vault; ERPNext is the chosen system of record** | SOPs, policies and this course live here; transactions live in ERPNext; code lives in GitHub. Lesson 07 fixes the tool map so we stop debating it.                                 |

## The Phases

| Phase                       | Window      | Files                                                                                                                                                                                                                                                           | After it you can…                                                                        |
| --------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **0 — Orientation**         | Now         | this page, [[COO-Docs/00-course-map-and-timeline\|00-course-map-and-timeline]]                                                                                                                                                                                  | See the whole road, week by week                                                         |
| **1 — Understand the Seat** | Week 0      | [[01-what-is-a-coo]], [[02-how-a-coo-thinks]], [[03-the-coo-core-value-and-the-ceo-coo-contract]], [[04-how-to-become-a-coo-in-2026]]                                                                                                                           | Explain the role, think like an operator, sign the CEO–COO agreement, know your 30/60/90 |
| **2 — Foundation**          | Days 1–30   | [[05-legal-and-governance-foundation]], [[06-money-rails-and-finance-operations]], [[07-tools-and-it-foundation]], [[08-the-operating-cadence]]                                                                                                                 | Sign, pay, get paid, hire and meet — with a written record and a weekly heartbeat        |
| **3 — Build the Machine**   | Months 2–6  | [[09-people-operations]], [[10-customer-operations-support-and-success]], [[11-revenue-operations-and-partnerships]], [[12-product-and-engineering-operations]], [[13-compliance-calendar-risk-and-insurance]], [[14-vendors-procurement-and-cost-control]]     | Run each function on a checklist with an owner and a number                              |
| **4 — Autopilot**           | Months 6–18 | [[15-sops-and-playbooks]], [[16-metrics-dashboards-and-scorecards]], [[17-delegation-decision-rights-and-org-design]], [[18-automation-and-ai-in-operations]], [[19-planning-okrs-and-the-quarterly-rhythm]], [[20-the-autopilot-test-and-scaling-the-machine]] | Pass the two-week holiday test; plan quarters; let agents and SOPs do the daily grind    |
| **Toolkit**                 | Always      | [[COO-Docs/toolkit/index\|30 templates]] + [vsyst-coo-workbook.xlsx](toolkit/vsyst-coo-workbook.xlsx)                                                                                                                                                           | Copy, fill, run                                                                          |
| **Reference**               | Always      | [[COO-Docs/21-reference-glossary-reading-list-and-sources]]                                                                                                                                                                                                     | Look up any term, book or source                                                         |

Start with [[COO-Docs/00-course-map-and-timeline|00-course-map-and-timeline]] to see the road, then [[01-what-is-a-coo]].

## How to Use This Course

- **Do the exercises, in order.** Reading about operations is like reading about swimming. Each exercise is small (10–45 minutes) and leaves an artefact — a filled template in this vault or a tab in the workbook. Keep filled copies in a `coo-workbook/` folder next to this one (or wherever the vault's PARA structure puts live company records); the toolkit files stay blank masters.
- **Follow the timeline, not the table of contents.** Lessons are grouped by topic; the [[COO-Docs/00-course-map-and-timeline|timeline]] tells you what to actually do in week 1, week 2, month 3. In a newly formed company you will read lesson 13 (compliance) long before month 6, because the first GST/TDS date does not wait.
- **One owner per artefact.** Even with three directors, every register, calendar and scorecard has exactly one name on it. Shared ownership is no ownership.
- **You are the customer of the toolkit.** If a template doesn't fit VSYST, change the template — then note the change in its file so the next person inherits your version.
- **The CA, CS and lawyer stay.** This course makes you literate and dangerous on compliance, contracts and people law — enough to _run_ them well and catch mistakes, not to replace professionals. Every filing still goes through the CA/CS; every contract still gets a legal read.

---

> **A note on honesty (the vault rule).** Company-law deadlines, GST/TDS thresholds, labour-law rules, DPDP timelines, tool prices and scheme benefits **change every Budget and often mid-year.** Everything here was written to be right for an Indian Pvt Ltd as of **2026-08-19**, but wherever a _specific number, date, form, threshold or price_ matters to a real decision it is flagged **VERIFY LIVE** — confirm it with the CA/CS/lawyer or the vendor's page before you act. This course teaches the _system_ (owners, rhythms, numbers, documents), which barely changes; the _numbers_ you always verify.
