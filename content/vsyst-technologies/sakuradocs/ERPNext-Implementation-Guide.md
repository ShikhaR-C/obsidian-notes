# ERPNext Implementation Guide for an Early-Stage Startup

> ERPNext — open-source ERP with built-in CRM, by Frappe Technologies (Mumbai, India).
> Repo: https://github.com/frappe/erpnext · Latest version: v16 (as of July 2026)
> 100% free and open source (GPLv3). Native Indian compliance: GST, e-invoicing, e-way bills, TDS.

---

## Phase 0 — Decide *where* to run it (Day 1)

| Option | Best for | Cost | Effort |
|---|---|---|---|
| **Frappe Cloud** (managed hosting) | Startups without a DevOps person | ~₹800–2,500/mo (small plans) | Almost zero — they handle setup, backups, upgrades |
| **Docker self-host** | Trying it out, or hosting on your own cheap VPS | Server cost only (~₹500–1,500/mo VPS) | Moderate — you manage updates and backups |
| **Manual (bench) install** | Developers who'll customize deeply | Server cost only | High — full control, full responsibility |

**Recommendation for a new startup:** Start with a **free trial on [Frappe Cloud](https://frappecloud.com)**, or run **Docker locally** to explore first. Your time is your scarcest resource — don't spend it maintaining servers. You can always migrate to self-hosting later; ERPNext exports everything.

---

## Phase 1 — Install / spin it up (Day 1–2)

### Option A: Frappe Cloud (recommended)
1. Sign up at [frappecloud.com](https://frappecloud.com)
2. Create a new site → choose **ERPNext** → pick a plan
3. Done. You get a URL like `yourstartup.frappe.cloud` in minutes.

### Option B: Docker (local trial or your own VPS)
```bash
# Prerequisites: Docker Desktop (docker.com), git
git clone https://github.com/frappe/frappe_docker
cd frappe_docker
docker compose -f pwd.yml up -d
```
Wait ~5 minutes for the site to initialize, then open `http://localhost:8080`.
Login: username `Administrator`, password `admin` (change it immediately).

### Option C: Manual bench install (only for heavy customization)
On an Ubuntu server:
```bash
# Install bench via the official easy-install script, then:
bench new-site yourstartup.localhost
bench get-app https://github.com/frappe/erpnext
bench --site yourstartup.localhost install-app erpnext
bench start   # → http://yourstartup.localhost:8000/app
```

---

## Phase 2 — Initial setup wizard (Day 2–3)

Decide these **before** starting the wizard:

1. **Country & currency** — selecting India auto-enables GST features (add the **India Compliance** app for e-invoicing / e-way bills).
2. **Company name, abbreviation, and logo.**
3. **Fiscal year** — April–March for India.
4. **Chart of Accounts** — accept the default standard template for your country. Don't hand-craft this early; your CA can adjust later.
5. **What you sell** — goods, services, or both.

Then immediately:
- [ ] Change the Administrator password
- [ ] Set up **email** (Settings → Email Account) so quotations/invoices can be sent from the system
- [ ] Enable **daily backups** (automatic on Frappe Cloud; on Docker set up a cron for `bench backup`)

---

## Phase 3 — Load your master data (Week 1)

Masters are the "nouns" of your business. Enter in this order (each supports bulk **Data Import** from spreadsheets):

1. **Items** — everything you sell or buy, with prices and units
2. **Customers** — even if it's just 5 right now
3. **Suppliers** — vendors you buy from
4. **Users** — invite the team, assign minimum-needed roles (Sales User, Accounts User, …)
5. **Bank accounts & opening balances** — involve your accountant if migrating from spreadsheets/Tally

**Startup tip:** Don't aim for completeness. Load your top 20 items and current customers; add the rest as they come up.

---

## Phase 4 — Turn on ONE workflow at a time (Weeks 2–6)

The #1 reason ERP adoption fails is trying to use everything at once. Adopt in this sequence, moving on only when the current one is a habit:

### Week 2–3: Sales cycle (CRM → cash)
> Lead → Opportunity → Quotation → Sales Order → Delivery Note → Sales Invoice → Payment Entry

This is the built-in CRM plus billing. Replaces spreadsheets + Word invoices; every rupee of revenue is tracked and GST-compliant.

### Week 3–4: Purchase cycle
> Material Request → Purchase Order → Purchase Receipt → Purchase Invoice → Payment

### Week 4–5: Inventory *(skip if services-only)*
Stock updates automatically from sales/purchase documents. Do one physical stock reconciliation to set opening quantities.

### Week 5–6: Accounting review
Books build themselves from the documents above. Review **General Ledger**, **Profit & Loss**, and **Balance Sheet** with your CA. Fix account mappings once.

### Later (only when needed)
HR & Payroll, Projects, Manufacturing, Website/e-commerce — don't touch until the core runs smoothly.

---

## Phase 5 — Go-live discipline (from Week 2 onward)

- **Pick a cutover date** (e.g., start of a month): from that date, *every* invoice and purchase goes through ERPNext. No parallel spreadsheets — dual systems kill adoption.
- **Train by doing:** each team member enters their own real transactions for a week, reviewed daily.
- **One owner:** designate one ERPNext admin who answers questions and controls settings changes.
- **Weekly review:** every Friday, check **Accounts Receivable** (who owes you money) and stock levels. This is where the ERP starts paying for itself.

---

## Phase 6 — Grow with it (Month 2+)

- **Customize carefully:** use **Custom Fields** and **Client Scripts** (no-code, upgrade-safe) before writing custom apps. Never modify core code — it makes upgrades painful.
- **Automate:** email alerts for overdue invoices, auto-reorder levels, approval workflows for purchases above a threshold.
- **Integrate:** payment gateways (Razorpay), Google Workspace, WhatsApp/Telegram notifications.
- **Update regularly:** one click on Frappe Cloud; on Docker, pull new images monthly. Stay on the stable track (v16).
- **Get help:** community forum at [discuss.frappe.io](https://discuss.frappe.io); free courses at [Frappe School](https://frappe.school) — start with "ERPNext for Beginners".

---

## The short version

1. **Today:** Sign up on Frappe Cloud (or `docker compose -f pwd.yml up -d` locally to explore).
2. **This week:** Run the setup wizard; add items + customers + users.
3. **Next 4 weeks:** Adopt sales cycle → purchase cycle → inventory → accounting review, one at a time.
4. **Rule of thumb:** enter real transactions from day one, never run a parallel spreadsheet, and don't touch HR/Manufacturing until the money-flow modules are habits.
