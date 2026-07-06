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

---

## Add-on apps: Frappe HR, Helpdesk & Wiki (Docker)

ERPNext covers CRM → accounting out of the box, but HR/payroll, a support desk, and a knowledge wiki are **separate Frappe apps**. All three install onto the *same site* as ERPNext — one URL, one login, shared users and data.

| App | What it gives you | Repo · branch (for v16) | Needs ERPNext? | Where it lives after install |
|---|---|---|---|---|
| **Frappe HR** (`hrms`) | Employees, leave, attendance, expense claims, payroll | `frappe/hrms` · `version-16` | **Yes** — major versions must match | Desk modules + employee self-service PWA at `/hr` |
| **Helpdesk** | Support tickets, agents, SLAs, customer portal | `frappe/helpdesk` · `main` | No | `/helpdesk` |
| **Wiki** | Public/internal documentation pages | `frappe/wiki` · `master` (v3 still RC as of Jul 2026) | No | Published pages at `/wiki`, managed from the desk |

### Why you can't just "install" them in Docker

Frappe apps live **inside the Docker image**, not in your site's data volumes. The stock `frappe/erpnext` image contains only Frappe + ERPNext, and anything added to a running container is lost when it's recreated. So extra apps = build a custom image once, then install the apps into your site.

All commands below run from inside the `frappe_docker` folder.

### Step 1 — Create `apps.json` (the app list baked into your image)

⚠️ ERPNext itself must be listed — the build starts from bare Frappe and includes exactly what's here.

```json
[
  { "url": "https://github.com/frappe/erpnext",  "branch": "version-16" },
  { "url": "https://github.com/frappe/hrms",     "branch": "version-16" },
  { "url": "https://github.com/frappe/helpdesk", "branch": "main" },
  { "url": "https://github.com/frappe/wiki",     "branch": "master" }
]
```

### Step 2 — Build the custom image (~15–30 min)

```bash
docker build \
  --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
  --build-arg=FRAPPE_BRANCH=version-16 \
  --secret=id=apps_json,src=apps.json \
  --tag=custom-erpnext:16 \
  --file=images/layered/Containerfile .
```

Give Docker Desktop ≥ 6 GB RAM (Settings → Resources); 8 GB is comfortable with four apps.

### Step 3 — Point `pwd.yml` at your image

```bash
sed -i '' 's|image: frappe/erpnext:.*|image: custom-erpnext:16|' pwd.yml
```

(Or manually replace every `image: frappe/erpnext:v16.x.x` line — several services use it.)

### Step 4 — Recreate containers and install into the site

Site data lives in Docker volumes, so this is non-destructive (the pwd.yml site is named `frontend`):

```bash
docker compose -f pwd.yml up -d
docker compose -f pwd.yml exec backend bench --site frontend install-app hrms
docker compose -f pwd.yml exec backend bench --site frontend install-app helpdesk
docker compose -f pwd.yml exec backend bench --site frontend install-app wiki
```

**Starting fresh instead?** Edit the `create-site` command in `pwd.yml` to read `--install-app erpnext --install-app hrms --install-app helpdesk --install-app wiki`, then `docker compose -f pwd.yml down -v && docker compose -f pwd.yml up -d` (⚠️ `down -v` wipes all data).

**Adding another app later:** append it to `apps.json`, re-run the Step 2 build (same tag), `docker compose -f pwd.yml up -d`, then `install-app` it as above.

### Adoption tip

Same rule as Phase 4: don't roll all three out at once. Helpdesk and Wiki are low-risk at any point; **hold payroll (Frappe HR) until accounting is stable** — payroll posts directly to your books.
