# DZZLO-OMS System Design

> Living document. Captures the current architecture, identifies structural weaknesses, and serves as the baseline for improvement discussions.

---

## 1. What the System Does

DZZLO-OMS is a **multi-tenant Order Management System for fuel distribution**. It manages the full lifecycle of fuel transactions between **Dealers** (fuel stations/distributors) and their **Customers** (fleet operators, businesses).

**Core business flow:**

```
Customer places Purchase Order (PO)
  → Dealer fulfils with Sales Order (SO)
    → System generates Invoice
      → Customer makes Payment (Voucher)
        → Balance updated in Dealer-Customer relationship
```

**Secondary systems:**

- **Fleet management** — vehicles, drivers, vehicle requests & transactions
- **DIP (Diesel Inventory/Pump management)** — tanks, nozzles, dispensing units, decantation, meter readings, inspections

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     CLIENTS                              │
│   Mobile App (React Native)  ·  Web (future)             │
└──────────────┬──────────────────────────────┬────────────┘
               │ HTTPS + JWT                  │
               ▼                              ▼
┌──────────────────────────┐   ┌──────────────────────────┐
│      Nginx (reverse      │   │     Nginx (reverse       │
│      proxy, TLS)         │   │     proxy, TLS)          │
│      test.doms.vsyst.in  │   │     prod domain          │
└──────────┬───────────────┘   └──────────┬───────────────┘
           │ :8030                         │ :PORT
           ▼                              ▼
┌─────────────────────────────────────────────────────────┐
│              Node.js / Express  (PM2 managed)            │
│                                                          │
│  ┌─────────────────────────────────────────────────┐     │
│  │              Middleware Pipeline                  │     │
│  │  healthcheck → api_key → logging → version_check │     │
│  │  → security (helmet,xss,hpp,sanitize) → CORS     │     │
│  │  → company_status_check                          │     │
│  └─────────────────────────────────────────────────┘     │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  /api/v2     │  │  /api/v3     │  │ /api/dip/v1   │  │
│  │  (OMS prod)  │  │  (experim.)  │  │ (Diesel mgmt) │  │
│  └──────┬───────┘  └──────────────┘  └──────┬────────┘  │
│         │                                    │           │
│  ┌──────▼───────────────────────────────────▼────────┐  │
│  │          Controllers → Services → Models           │  │
│  └──────┬───────────────────────────────────┬────────┘  │
└─────────┼───────────────────────────────────┼────────────┘
          │                                   │
          ▼                                   ▼
┌──────────────────┐              ┌──────────────────┐
│   MongoDB Atlas   │              │   MongoDB Atlas   │
│   (OMS Database)  │              │   (DIP Database)  │
│   mongoose.connect│              │ mongoose.create   │
│                   │              │   Connection      │
│   22 collections  │              │   4 collections   │
└──────────────────┘              └──────────────────┘
```

**Architecture style:** Monolithic REST API, single process, dual database connections.

---

## 3. Data Architecture

### 3.1 Entity Relationship Map

```
                    ┌──────────┐
                    │  users   │ ← multi-company, polymorphic co_id
                    │          │   (refPath → dealer_msts | cust_msts)
                    └────┬─────┘
                         │ companies[] (per-company scope, status, permissions)
              ┌──────────┼──────────┐
              ▼                     ▼
     ┌─────────────┐       ┌─────────────┐
     │ dealer_msts  │       │  cust_msts   │
     │ (Fuel Stn)   │       │ (Fleet Co.)  │
     └──────┬──────┘       └──────┬───────┘
            │                      │
            └──────────┬───────────┘
                       ▼
              ┌─────────────────┐
              │  dealer_custs   │  ← the RELATIONSHIP
              │  (composite _id │    credit terms, discount,
              │   dealer+cust)  │    balance history, tax config
              └────────┬────────┘
                       │
         ┌─────────────┼──────────────┐
         ▼             ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ order_msts│  │ prod_msts │  │ rate_msts │
   │ (PO)      │  │ (Products)│  │ (Pricing) │
   └─────┬─────┘  └──────────┘  └──────────┘
         │
         ▼
   ┌──────────┐      ┌──────────┐
   │  so_msts  │ ──▶  │   invs   │  (SO linked to Invoice)
   │ (SO)      │      │(Invoice) │
   └──────────┘      └─────┬────┘
                           │
                           ▼
                     ┌──────────┐
                     │ voc_msts  │  (Payment Vouchers)
                     │(Payments) │
                     └──────────┘

   FLEET MODULE:
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ veh_msts  │  │ veh_reqs  │  │ veh_trns  │  │ dvr_msts  │
   │(Vehicles) │  │(Requests) │  │(Trips)    │  │(Drivers)  │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘

   SUPPORT:
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │  psocs   │  │ invites   │  │  logs    │  │ counters  │
   │(Prod-SO- │  │(User      │  │(Request  │  │(Auto-incr │
   │ Cust link)│  │ Invites)  │  │ Logs)    │  │ sequences)│
   └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

### 3.2 Multi-Tenancy Model

Tenancy is **relationship-scoped**, not strict tenant isolation:

- A **Dealer** is a fuel station/distributor (company entity).
- A **Customer** is a fleet/business that buys fuel from one or more Dealers.
- The **dealer_custs** document IS the tenant boundary — it holds all commercial terms (credit, discount, tax, billing period) for a specific Dealer-Customer pair.
- A **User** can belong to multiple companies (via `companies[]` array). Each entry has its own scope, status, and permissions.
- **Data isolation is enforced at the query level** — controllers filter by `dealer_id` + `cust_id` from the JWT + `co_id` header. There is no row-level security or database-level tenant isolation.

### 3.3 Dual Database Strategy

| Database      | Connection                    | Purpose                    | Collections                              |
| ------------- | ----------------------------- | -------------------------- | ---------------------------------------- |
| OMS (default) | `mongoose.connect()`          | Core order management      | 22 (users, orders, invoices, etc.)       |
| DIP           | `mongoose.createConnection()` | Diesel inventory/pump mgmt | 4 (dealers, decants, meter_reads, insps) |

The DIP database was separated because:

- Different data lifecycle (operational vs. transactional)
- Different access patterns (DIP is equipment-level, OMS is business-level)
- Models registered on separate connections (`db_dip.model(...)` vs `mongoose.model(...)`)

---

## 4. Authentication & Authorization

### 4.1 Authentication Flow

```
Client                          Server
  │                               │
  │  POST /auth/login             │
  │  { email, password }          │
  │──────────────────────────────▶│
  │                               │  bcrypt.compare(password, hash)
  │                               │  jwt.sign({ id, email, co_id, role })
  │  { token, user }              │
  │◀──────────────────────────────│
  │                               │
  │  GET /api/v2/orders           │
  │  Authorization: Bearer <jwt>  │
  │  x-api-key: <key>             │
  │  co_id: <company_id>          │
  │──────────────────────────────▶│
  │                               │  1. Validate API key
  │                               │  2. Decode JWT → get user
  │                               │  3. Match co_id header to user.companies[]
  │                               │  4. Check company status (ACTIVE/INACTIVE/REMOVED)
  │                               │  5. Execute handler
```

### 4.2 Authorization Layers

| Layer              | Where                                     | What It Checks                                                                           |
| ------------------ | ----------------------------------------- | ---------------------------------------------------------------------------------------- |
| API Key            | `middlewares.api_key_v1()` / `api_key()`  | Valid `x-api-key` header (gate for all requests)                                         |
| JWT                | `helpers/auth.js`                         | Token signature + expiry                                                                 |
| Company Membership | `middlewares.check_user_company_status()` | User belongs to the company in `co_id` header, status is ACTIVE                          |
| Role               | Controller-level                          | `superadmin` bypasses most checks                                                        |
| Scope              | Controller-level                          | Per-company role (CPrimary, DAdmin, etc.) determines allowed operations                  |
| DIP Permissions    | `helpers/checkDipPerm.js`                 | Granular resource+action permissions (`dip.tanks.update`) stored in `amend_prem.allow[]` |

### 4.3 Role & Scope Hierarchy

```
superadmin (global)
│
├── Dealer Scopes
│   ├── DPrimary   — full dealer access, DIP bypass
│   ├── DAdmin     — admin-level dealer access, DIP bypass
│   ├── DOrder     — order operations only
│   ├── DAccount   — accounting operations only
│   ├── DOrderAccount — orders + accounting
│   └── DView      — read-only
│
└── Customer Scopes
    ├── CPrimary   — full customer access
    ├── CAdmin     — admin-level customer access
    ├── COrder     — order operations only
    ├── CAccount   — accounting operations only
    ├── COrderAccount — orders + accounting
    └── CView      — read-only
```

---

## 5. Core Business Flows

### 5.1 Order-to-Cash Flow

```
CUSTOMER SIDE                  SYSTEM                     DEALER SIDE
─────────────                  ──────                     ───────────
1. Create PO ──────────▶ order_msts created
   (products, qty,        (order_status tracking)
    vehicle, date)

2. OTP Verification        OTP sent via SMS ────────▶  Driver/Manager
   (2Factor.in)            (10 min expiry)              verifies delivery

3.                         PO acknowledged ◀────────── 3. Create SO
                                                        (slip_no, products,
                                                         actual qty/rate)

4.                         Invoice generated ◀───────── 4. Generate Invoice
                           (inv_no auto-increment        (from SO, with tax
                            from dealer_invdgt)           calc, discount)

5. View Invoice            Invoice linked to SO
   Payment due             (inv_status: UNPAID)

6. Create Voucher ────────▶ voc_msts created ─────────▶ 6. Approve Payment
   (amount, mode,          (pay_status: false)            (pay_status: true)
    bank, cheque)

7.                         Balance updated in
                           dealer_custs.cust_bal[]
                           inv_status → FULLPAID/PARTPAID
```

### 5.2 Invoice Numbering

Invoice numbers are auto-generated per dealer using stored counters:

- `dealer_invdgt` — Product invoices (prefix + "4xxxxxx")
- `dealer_cs_invdgt` — Cash reimbursement invoices (prefix + "7xxxxxx")
- `dealer_gst_invdgt` — GST invoices (prefix + "6xxxxxx")

The prefix is derived from the dealer name initials (e.g., "AB4000001").

### 5.3 Credit & Balance Management

The `dealer_custs` relationship document holds:

- `cust_type`: CASH or CREDIT
- `cust_bal[]`: Running balance history (array of {bal_value, bal_date})
- `max_cr_lmt`: Maximum credit limit
- `cr_lwr_lmt`: Warning threshold for low balance
- `max_cr_days`: Credit period in days
- `cr_bill_period`: Billing frequency (INSTANT, DAILY, WEEKLY, 10DAYS, FORTNIGHT, MONTHLY, MANUALLY)
- `adv_dep`: Advanced deposit amount
- Tax config (`taxRate`, `taxStatus`: TCS/TDS/NOT/NONE)
- Discount config (per-product or global)

---

## 6. Middleware Pipeline (Execution Order)

```
Request arrives
    │
    ▼
┌─ dzzlo_oms.js (app-level) ─────────────────────────────────────────┐
│  1. express.json()            — Parse JSON body                     │
│  2. morgan("dev")             — HTTP logging (dev only)             │
│  3. /healthcheck              — Short-circuit 200 (no auth needed)  │
│  4. api_key_v1()              — Lenient: block only INVALID keys    │
│  5. logging()                 — Async log to MongoDB (non-blocking) │
│  6. check_user_version()      — Min app version 1.68                │
│  7. cookieParser()            — Parse cookies                       │
│  8. mongoSanitize()           — NoSQL injection prevention          │
│  9. helmet()                  — Security headers                    │
│ 10. xss()                     — XSS prevention                     │
│ 11. hpp()                     — HTTP param pollution                │
│ 12. cors()                    — Cross-origin support                │
│ 13. express.static("public")  — Serve static files                 │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─ api_v/api2.js (router-level) ─────────────────────────────────────┐
│ 14. /contact, /updates, /auth — PUBLIC routes (no auth)            │
│ 15. api_key()                 — STRICT: require valid x-api-key    │
│ 16. /sadmin, /cust_msts,      — Routes that don't need co_id check │
│     /dealer_msts, /invites                                          │
│ 17. check_user_company_status — JWT user belongs to co_id company  │
│ 18. All remaining routes      — PROTECTED (auth + company check)   │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─ Route Handler ────────────────────────────────────────────────────┐
│  asyncHandler(controller) → service → model → MongoDB              │
│  Errors: next(new ErrorResponse(msg, code)) → global errorHandler  │
└────────────────────────────────────────────────────────────────────┘
```

---

## 7. API Design

### 7.1 Versioning Strategy

| Version | Status         | Mount Point               | Purpose                                      |
| ------- | -------------- | ------------------------- | -------------------------------------------- |
| v1      | Deprecated     | `/api/v1` (commented out) | Legacy, some routes still referenced from v2 |
| v2      | **Production** | `/api/v2`                 | Active OMS API                               |
| v3      | Experimental   | `/api/v3`                 | Refactor target (not fully routed)           |
| DIP v1  | **Production** | `/api/dip/v1`             | Diesel inventory management                  |

### 7.2 Request/Response Contract

**Headers required:**

```
x-api-key: <api_key>
Authorization: Bearer <jwt_token>
co_id: <company_object_id>
meta: {"version": "1.77", "deviceBrand": "Apple"}  (mobile clients)
```

**Standard response:**

```json
// Success
{ "success": true, "data": { ... } }

// Success (paginated — via advancedResults helper)
{ "success": true, "count": 25, "pagination": { "next": {...}, "prev": {...} }, "data": [...] }

// Error
{ "success": false, "error": "Human readable message" }
```

### 7.3 Route Naming Convention

Routes follow the MongoDB collection name: `/api/v2/<collection_name>`

```
GET    /api/v2/order_msts          — List (with pagination/filter)
GET    /api/v2/order_msts/:id      — Read one
POST   /api/v2/order_msts          — Create
PUT    /api/v2/order_msts/:id      — Update
DELETE /api/v2/order_msts/:id      — Delete
```

Custom actions use sub-paths:

```
POST   /api/v2/order_msts/:id/send_otp
GET    /api/v2/users/a/company          — Users for a company
PUT    /api/v2/users/a/amend            — Amend DIP permissions
```

---

## 8. Infrastructure & Deployment

### 8.1 Production Architecture

```
                         ┌──────────────────────┐
                         │     doms.vsyst.in     │
                         │       (DNS)           │
                         └──────────┬────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    AWS ALB            │
                         │  (Application Load    │
                         │   Balancer, TLS)      │
                         └────┬────────────┬─────┘
                              │            │
                         84% traffic   16% traffic
                              │            │
                              ▼            ▼
              ┌─────────────────┐   ┌─────────────────┐
              │  EC2 t3.small   │   │  EC2 t3.micro   │
              │  2 vCPU / 2 GB  │   │  2 vCPU / 1 GB  │
              │                 │   │                  │
              │  Nginx          │   │  Nginx           │
              │    ↓            │   │    ↓             │
              │  PM2            │   │  PM2             │
              │   └─ dzzlo-oms  │   │   └─ dzzlo-oms   │
              │                 │   │                  │
              │  (Auto Scaling  │   │  (Standalone)    │
              │   Group)        │   │                  │
              └────────┬────────┘   └────────┬─────────┘
                       │                     │
                       └──────────┬──────────┘
                                  │ same .env, same code
                                  ▼
                       ┌──────────────────────┐
                       │   MongoDB Atlas       │
                       │   (Dedicated Plan)    │
                       │                       │
                       │  ┌─────────┐ ┌──────┐ │
                       │  │ OMS DB  │ │DIP DB│ │
                       │  │22 colls │ │4 cols│ │
                       │  └─────────┘ └──────┘ │
                       │                       │
                       │  Auto backups enabled  │
                       └───────────────────────┘
```

**Testing environment** — separate EC2 server (not shown) with its own MongoDB instance.

### 8.2 Server Inventory

| Server       | Instance | vCPU | RAM  | Role                         | Scaling            |
| ------------ | -------- | ---- | ---- | ---------------------------- | ------------------ |
| Production A | t3.small | 2    | 2 GB | Primary prod (84% traffic)   | Auto Scaling Group |
| Production B | t3.micro | 2    | 1 GB | Secondary prod (16% traffic) | Standalone         |
| Testing      | t3.micro | 2    | 1 GB | Staging / QA                 | Standalone         |

### 8.3 Deployment Process

```
Developer                    Server (SSH)
   │                            │
   │  git push origin master    │
   │                            │
   │  ssh into server           │
   │───────────────────────────▶│
   │                            │  cd /path/to/dzzlo_oms_api
   │                            │  git pull origin master
   │                            │  yarn install (if deps changed)
   │                            │  pm2 restart dzzlo-oms
   │                            │
   │                            │  (repeat on second server)
   │                            │
   │  AMI snapshot taken        │
   │  (on significant updates)  │
   │                            │
```

**Deployment characteristics:**

- **Method:** Manual SSH → git pull → pm2 restart (per server)
- **Env management:** `.env` files copied manually to each server
- **CI/CD:** None — manual deployment
- **AMI snapshots:** Taken after significant updates for rollback/recovery
- **Launch template:** ASG uses AMI + launch template to spin up t3.small instances with pre-baked code

### 8.4 Load Balancing & Scaling

| Concern            | Configuration                                                        |
| ------------------ | -------------------------------------------------------------------- |
| Load balancer      | AWS ALB (Application Load Balancer)                                  |
| TLS termination    | At ALB level                                                         |
| Traffic split      | 84% → t3.small (ASG), 16% → t3.micro                                 |
| Auto Scaling Group | t3.small in ASG, target tracking policy: **maintain avg CPU at 45%** |
| ASG scaling        | Scales out/in as needed to hold 45% CPU target                       |
| Health checks      | ALB → `/healthcheck` on each instance                                |
| Sticky sessions    | Not needed — JWT is stateless                                        |

### 8.5 DNS & Networking

| Concern                 | Current State                                               |
| ----------------------- | ----------------------------------------------------------- |
| Production domain       | `doms.vsyst.in`                                             |
| Testing domain          | `test.doms.vsyst.in` (separate server)                      |
| Firewall (UFW/iptables) | **None configured**                                         |
| MongoDB IP whitelist    | **All IPs whitelisted** (0.0.0.0/0 in Atlas network access) |

**AWS Security Group (Inbound Rules):**

| IP Version | Type  | Protocol | Port | Source    | Note                        |
| ---------- | ----- | -------- | ---- | --------- | --------------------------- |
| IPv4       | HTTP  | TCP      | 80   | 0.0.0.0/0 | Open to all                 |
| IPv4       | SSH   | TCP      | 22   | 0.0.0.0/0 | Open to all                 |
| IPv4       | SMTPS | TCP      | 465  | 0.0.0.0/0 | Outbound email (Nodemailer) |
| IPv6       | HTTP  | TCP      | 80   | ::/0      | Open to all (IPv6)          |
| IPv4       | HTTPS | TCP      | 443  | 0.0.0.0/0 | Open to all                 |

### 8.6 Backup & Recovery

| Concern           | Strategy                                        |
| ----------------- | ----------------------------------------------- |
| Database backups  | MongoDB Atlas auto backups (dedicated plan)     |
| Server recovery   | AMI snapshots taken on significant updates      |
| Code rollback     | `git revert` or redeploy previous commit        |
| Disaster recovery | Launch new EC2 from latest AMI + point to Atlas |

### 8.7 External Services

| Service                   | Purpose              | Integration                   |
| ------------------------- | -------------------- | ----------------------------- |
| AWS EC2                   | Compute              | 2 prod + 1 test instances     |
| AWS ALB                   | Load balancing + TLS | Traffic distribution          |
| MongoDB Atlas (Dedicated) | Database hosting     | Mongoose ODM, auto backups    |
| 2Factor.in                | SMS OTP delivery     | REST API (`API_2F_KEY`)       |
| AWS SES / SMTP            | Email sending        | Nodemailer                    |
| OneSignal                 | Push notifications   | REST API (`ONESIGNAL_APP_ID`) |
| WhoisAPI                  | Email verification   | REST API (`EMAIL_VERIFY_KEY`) |

### 8.8 Monitoring & Observability

| Concern             | Current Solution                              |
| ------------------- | --------------------------------------------- |
| Request logging     | Custom middleware → MongoDB `logs` collection |
| Process management  | PM2 (auto-restart, logs)                      |
| Error tracking      | Global error handler → `errors` collection    |
| Health check        | `/healthcheck` endpoint (ALB + manual)        |
| APM / Metrics       | **None**                                      |
| CloudWatch alarms   | **None configured**                           |
| Alerting            | **None**                                      |
| Distributed tracing | **None** (not needed — stateless instances)   |

### 8.9 What's Missing (Infrastructure Gaps)

| Gap                                   | Current State                                                                                                          | Risk                                                                        |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| **Caching layer**                     | No Redis/Memcached/ElastiCache. Every request hits MongoDB directly.                                                   | Higher DB load, slower repeat queries, no session store for rate limiting   |
| **Server-side analytics / telemetry** | No log aggregation (CloudWatch Logs, Datadog, ELK, etc.). Logs exist only in PM2 stdout and MongoDB `logs` collection. | Hard to debug cross-server issues, no dashboards, no trend analysis         |
| **Active user count**                 | No mechanism to track concurrent/active users or sessions. JWT is stateless — no session store.                        | No visibility into usage patterns, capacity planning is guesswork           |
| **CloudWatch alarms**                 | None configured. No alerts on CPU, memory, disk, 5xx errors, or ALB unhealthy targets.                                 | Silent failures — issues discovered only when users complain                |
| **CI/CD pipeline**                    | None. Manual SSH deploy to each server.                                                                                | Human error risk, inconsistent deploys, no automated testing before deploy  |
| **Centralized logging**               | Each server has its own PM2 logs. No aggregation.                                                                      | Debugging requires SSH into each server individually                        |
| **SSH access control**                | Port 22 open to 0.0.0.0/0 (all IPs)                                                                                    | Security risk — should restrict to known IPs or use SSM                     |
| **MongoDB Atlas open access**         | All IPs whitelisted (0.0.0.0/0)                                                                                        | Database accessible from any IP if credentials leak                         |
| **Rate limiting**                     | Commented out in code, no WAF on ALB                                                                                   | Vulnerable to brute force, scraping, DDoS at app layer                      |
| **Secrets management**                | `.env` files copied manually, no AWS Secrets Manager / Parameter Store                                                 | Risk of stale/inconsistent env across servers, secrets in plaintext on disk |

---

## 9. Client Applications

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                  │
│                                                                  │
│   ┌──────────────────────┐         ┌──────────────────────┐     │
│   │  React Native App    │         │   Web Application     │     │
│   │  (iOS + Android)     │         │   (Browser)           │     │
│   │                      │         │                       │     │
│   │  Consumes: /api/v2   │         │  Consumes: /api/dip/v1│     │
│   │  (OMS — orders,      │         │  (DIP — tanks, meters,│     │
│   │   invoices, payments, │         │   decantation,        │     │
│   │   fleet, users)      │         │   inspections)        │     │
│   │                      │         │                       │     │
│   │  Users:              │         │  Users:               │     │
│   │  • Dealer staff      │         │  • Dealer staff       │     │
│   │  • Customer staff    │         │    (pump operators,    │     │
│   │  • Drivers           │         │     managers)          │     │
│   │  • Fleet managers    │         │                       │     │
│   └──────────────────────┘         └──────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**End users:** Businesses (fuel dealers + their customers) and their staff — ~120 businesses on the platform.

---

## 10. Business Scale & Data Growth

### 10.1 Current Scale

| Metric                 | Value   |
| ---------------------- | ------- |
| Businesses on platform | ~120    |
| Daily orders           | ~130    |
| Monthly orders (est.)  | ~3,900  |
| Yearly orders (est.)   | ~47,000 |

### 10.2 Data Growth Pattern

Every order generates a chain of documents across collections:

```
1 Purchase Order (order_msts)
  → 1 Sales Order (so_msts)
    → 1–3 Invoices (invs) — product, GST, cash reimburse
      → 1+ Vouchers (voc_msts) — payments against invoice
```

**Estimated daily document creation:**
| Collection | Docs/day (est.) | Growth driver |
|-----------|----------------|---------------|
| order_msts | ~130 | 1 per order |
| so_msts | ~130 | 1 per fulfilled order |
| invs | ~150–250 | 1–2 per SO (product + GST/reimburse) |
| voc_msts | ~100–200 | Payments, may lag behind invoices |
| logs | ~5,000+ | Every API request logged |
| dealer_custs.cust_bal[] | ~1/year per relationship | Balance pushed once annually |

**Logs collection (as of April 2026):** 1.4 million records, 114 MB, indexed.

### 10.3 Data Lifecycle

| Concern            | Current State                                                                                                       |
| ------------------ | ------------------------------------------------------------------------------------------------------------------- |
| Archival strategy  | **None** — all data kept forever in primary collections                                                             |
| TTL indexes        | **None**                                                                                                            |
| Collection cleanup | **None** — collections grow every day                                                                               |
| Logs retention     | **Unbounded** — 1.4M records / 114 MB and growing (~5K docs/day)                                                    |
| Balance history    | Low concern — `cust_bal[]` only pushed ~1x/year. Oldest relationship is 5 years (~5 entries). Not a growth problem. |
| Invoice numbering  | Changed to random ID in v2 — no more read-then-increment race condition                                             |

> At ~130 orders/day, transactional collections are manageable. The `logs` collection is the fastest-growing — at ~5K docs/day, it adds ~1.8M docs/year. At 114 MB currently it's not a problem yet, but without TTL or cleanup it will be.

---

## 11. Notification System

The app fires notification events through three channels:

| Channel           | Provider                    | Trigger Examples                                 |
| ----------------- | --------------------------- | ------------------------------------------------ |
| Push notification | OneSignal                   | New order, new invoice, payment approved         |
| SMS               | 2Factor.in                  | OTP for order verification, login OTP            |
| Email             | Nodemailer (SMTP / AWS SES) | Password reset, email verification, contact form |

**User notification preferences** are stored per-company in `users.companies[].notif[]`:

```
NotifTypes: NewOrder, NewSalesOrder, NewInvoice, NewPayment,
            NewVoucher, NewVehicleRequest, ApprovedPayment,
            NewCustomer, Verification, NewCompanyInvite
```

Each user opts into specific notification types per company. The app checks these preferences before sending.

---

## 12. Development & Team

### 12.1 Team

| Role               | Tool                                              |
| ------------------ | ------------------------------------------------- |
| Developer          | Solo developer                                    |
| AI pair programmer | Claude Code (CLI)                                 |
| Bus factor         | **1** — single person holds all production access |

### 12.2 Development Process

| Concern         | Current Practice                         |
| --------------- | ---------------------------------------- |
| Version control | Git (GitHub)                             |
| Branch strategy | Feature branches → `master` (production) |
| Code review     | Manual / Claude-assisted                 |
| Testing         | Jest + mongodb-memory-server (in-memory) |
| Release cadence | As needed — manual deploy                |
| Documentation   | `docs/` directory, AI-maintained         |

### 12.3 Deploy Rollback Procedure

```
1. Detect bad deploy (user reports / manual check)
2. Detach affected server from ALB (traffic stops going to it)
3. SSH into server → git revert to last good commit
4. pm2 restart dzzlo-oms
5. Re-attach server to ALB
6. Repeat for second server if needed
```

### 12.4 Bus Factor Risk

| Asset                 | Who Has Access | Shared With        |
| --------------------- | -------------- | ------------------ |
| Production `.env`     | 1 person       | No one             |
| SSH keys (EC2)        | 1 person       | No one             |
| AWS Console           | 1 person       | Unknown            |
| MongoDB Atlas console | 1 person       | Unknown            |
| GitHub repo           | 1 person       | Unknown            |
| Deploy knowledge      | 1 person       | **Not documented** |
| Domain / DNS          | 1 person       | Unknown            |

> **Critical risk:** If the sole developer is unavailable, no one can deploy, rollback, or access production infrastructure. This is the single biggest operational risk in the system.

---

## 13. Identified Structural Observations

> These are not bugs but architectural characteristics worth discussing when planning improvements.

### 13.1 Strengths

1. **Simple, understandable architecture** — monolith is the right choice at current scale. No premature microservice complexity.
2. **Clear controller → service → model separation** — business logic is organized by entity.
3. **Dual DB for domain separation** — OMS and DIP data are cleanly separated.
4. **Comprehensive middleware stack** — security headers, XSS, NoSQL injection, HPP all covered.
5. **Multi-company user model** — flexible; one user can work across companies with different permissions.
6. **DIP permission system** — granular, resource+action pattern is extensible.
7. **Request logging to DB** — gives audit trail and debugging visibility.

### 13.2 Areas to Evaluate

1. **No rate limiting in production** — rate limiter is commented out. API is open to abuse.
2. **API key comparison uses `==`** — not timing-safe, though practical risk is low with HTTPS.
3. **Logging middleware calls `getUserFromToken()` on every request** — JWT decode + DB lookup for every request just for logging.
4. **No request validation layer** — `express-validator` is imported but not used. Input validation is ad-hoc in controllers.
5. ~~**Balance stored as array in dealer_custs**~~ — `cust_bal[]` only pushed ~1x/year. Not a growth concern.
6. ~~**Invoice auto-increment race condition**~~ — Changed to random ID in v2. Resolved.
7. **Some v1 routes still mounted from v2 router** — `contact_us`, `pay_trns`, and payment routes point to `api_v1/` files.
8. **Server starts before DB connects** — `app.listen()` runs immediately; `mongoose.connect()` is fire-and-forget. Server can accept requests before DB is ready.
9. **Single PM2 process per server** — no clustering within instance (though ALB provides multi-instance).
10. **OTP stored in plaintext** — both user OTP and order OTP values stored as plain strings in the database.

### 13.3 Operational Resilience

| Scenario                    | Current Behavior                                                           | Impact                                                                                        |
| --------------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| MongoDB Atlas goes down     | App returns timeout errors to all clients                                  | **Full outage** — no graceful degradation, no retry, no queue                                 |
| Bad deploy                  | Manual: detach from ALB → git revert → reattach. Downtime during rollback. | Minutes of degraded service for affected server                                               |
| ASG scales out new instance | New instance launched from AMI with baked-in code                          | Works, but `.env` must be baked into AMI or launch template — any env change requires new AMI |
| SMS provider (2Factor) down | OTP delivery fails, orders can't be verified                               | Order flow blocked for OTP-required orders                                                    |
| OneSignal down              | Push notifications silently fail                                           | Users miss notifications, no alerting on failure                                              |
| Server disk full            | PM2 logs fill disk, app crashes                                            | No disk monitoring or alerts in place                                                         |
| Developer unavailable       | No one can deploy, rollback, or access infra                               | **Complete operational paralysis**                                                            |

### 13.4 Security Posture

| Concern                                    | Status                                                                                                                                           | Severity   |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- |
| SSH open to all IPs (0.0.0.0/0 on port 22) | Key-pair auth (no password) — mitigates brute force, but attack surface is unnecessarily wide                                                    | Medium     |
| MongoDB Atlas open to all IPs              | Can't restrict due to dynamic ASG IPs. Valid trade-off but increases risk if credentials leak. Could use VPC Peering or AWS PrivateLink instead. | Medium     |
| No WAF on ALB                              | No protection against OWASP attacks at edge, SQL injection, bot traffic                                                                          | Medium     |
| `.env` on disk in plaintext                | Single copy per server, never committed. But no encryption at rest, no secrets manager.                                                          | Low-Medium |
| Rate limiting disabled                     | No protection against brute-force login, API scraping, or DDoS at app layer                                                                      | Medium     |
| Production access = 1 person               | If compromised, attacker has full access. No audit trail of who did what on servers.                                                             | High       |

---

## 14. Technology Stack Summary

| Layer         | Technology                   | Version                   |
| ------------- | ---------------------------- | ------------------------- |
| Runtime       | Node.js                      | (see .nvmrc/package.json) |
| Framework     | Express.js                   | 4.19.2                    |
| ODM           | Mongoose                     | 9.2.0                     |
| Database      | MongoDB (Atlas)              | —                         |
| Auth          | jsonwebtoken + bcryptjs      | 9.0.2 / 2.4.3             |
| Process Mgr   | PM2                          | —                         |
| Reverse Proxy | Nginx                        | —                         |
| Testing       | Jest + mongodb-memory-server | 29.7.0                    |
| SMS           | 2Factor.in                   | REST API                  |
| Email         | Nodemailer (SMTP / AWS SES)  | 6.7.2                     |
| Push Notifs   | OneSignal                    | REST API                  |

---

## 15. Open Questions

Refined based on what we know now:

1. **Growth trajectory** — 120 businesses, 130 orders/day currently. What's the 6–12 month target? 500 businesses? 1000 orders/day? This determines whether current infra holds.
2. **Logs cleanup** — 1.4M records, 114 MB. Should we add a TTL index (e.g., drop logs older than 90 days)? Or archive to S3?
3. **Real-time features** — Socket.io is commented out. Are live order updates or real-time dashboards on the roadmap?
4. **Background jobs** — Invoice PDF generation, bulk reports, scheduled billing by `cr_bill_period` — are any of these needed? Would require a job queue (Bull/BullMQ + Redis).
5. **DB performance visibility** — How do we know if MongoDB is slow? No APM, no slow query logging, no Atlas Performance Advisor review.
6. **ASG verification** — Has it ever actually scaled? Check ASG activity history in AWS Console to confirm it works.
7. **Disaster recovery drill** — Has anyone ever launched from an AMI to verify recovery works? If not, it's an untested assumption.
8. **DIP as separate service** — DIP already has its own DB. As the web app grows, should DIP become an independent deployable?

---

_Last updated: 2026-04-04_
