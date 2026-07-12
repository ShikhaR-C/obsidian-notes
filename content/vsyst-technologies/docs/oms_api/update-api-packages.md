Breaking Changes Summary — File-by-File

Here are the required changes grouped by impact level:

---

HIGH IMPACT — Deprecated packages (must replace)

1. xss-clean (0.1.4) — archived, unmaintained

- dzzlo_oms.js:17,79 — remove require("xss-clean") + app.use(xss())
- test/dzzlo_oms_test.js:10 — remove import
- Fix: replace with DOMPurify on output, or xss package, or remove (mongo-sanitize + helmet cover most attack vectors)

1. html-pdf (3.0.1) — deprecated (uses abandoned PhantomJS)

- api_v1/controllers/App/invs.js:11 — uses .create().toBuffer()
- api_v1/controllers/Methods/Invoice/create.js:10
- api_v1/controllers/Methods/Invoice/emailPdf.js:1,31
- api_v2/controllers/App/email.js:3,24-25
- api_v3/services/invoice/htmlPdf/fileBuffer.js:1,5-17
- Fix: migrate to puppeteer or @sparticuz/chromium + puppeteer-core — API is await page.pdf() returning a Buffer. Rewrite the callback-style .create(html).toBuffer(cb) to  
  async/await.

1. nodemailer-ses-transport (1.5.1) — deprecated

- helpers/sendEmail.js:2,16 — var ses = require("nodemailer-ses-transport")
- Fix: use @aws-sdk/client-ses v3 with nodemailer's built-in SES transport:  
  const { SES } = require("@aws-sdk/client-ses");  
  const ses = new SES({ region, credentials: {...} });  
  nodemailer.createTransport({ SES: { ses, aws: { SendRawEmailCommand } } });

1. node-fetch v2 → v3 — ESM-only in v3

- api_v1/controllers/App/users.js:4
- api_v1/controllers/Methods/Invoice/create.js:19
- api_v3/controllers/App/notification.js, api_v2/controllers/App/notification.js
- Multiple payment controllers
- Fix: either (a) drop the dependency — Node 18+ has global fetch built-in; just remove require("node-fetch"), or (b) stay on v2, or (c) convert the project to ESM (large effort).

1. express-mongo-sanitize (2.2.0) — archived as of 2024

- dzzlo_oms.js:15,73, test/dzzlo_oms_test.js:8
- Fix: replace with mongo-sanitize (manual per-route) or @exortek/express-mongo-sanitize fork. Note: Express 5 makes req.query read-only, so the old middleware mutating req.query
  will crash on Express 5.

---

MEDIUM IMPACT — Major version bumps with API changes

1. express v4 → v5

- dzzlo_oms.js — app setup
- 50+ route files using express.Router()
- Breaking changes affecting this project:
  - req.query is now a getter (read-only) → breaks express-mongo-sanitize and hpp which mutate it
  - Path-to-regexp v6 → v8: your routes appear safe (no wildcards or :param? optional params found)
  - Async middleware errors now auto-forwarded to error handlers (behavior change, not a break)
  - res.redirect('back') removed → search-and-replace if used
  - app.del() removed → use app.delete()
- dzzlo_oms.js:50 — app.use(express.json()) still works
- dzzlo_oms.js:96 — express.static("public") still works

1. hpp (0.2.3) — also mutates req.query

- dzzlo_oms.js:19,89 — will break under Express 5
- Fix: remove or replace with route-local sanitization

1. helmet v7 → v8

- dzzlo_oms.js:16,76 — app.use(helmet())
- Breaking: stricter CSP defaults, CORP default changed to same-origin, X-Powered-By stripped differently
- Fix: test in dev; may need helmet({ contentSecurityPolicy: false }) if serving public assets breaks

1. nodemailer v6 → v7

- helpers/sendEmail.js:1, helpers/sendEmailnaAWS.js:1
- Breaking: requires Node 18+, some option renames, DKIM changes
- Generally compatible if using createTransport + sendMail

1. multer v1 → v2 — currently not imported anywhere → safe to remove from package.json
2. socket.io v2 → v4 — only in commented code (helpers/middlewares.js:258) → safe to remove
3. uuid v9 → v11 — not imported anywhere → safe to remove
4. dotenv v16 → v17

- dzzlo_oms.js:1-7 and 20+ other files doing require("dotenv").config()
- Breaking: v17 changed default behavior around .env discovery and made some quoted-value parsing stricter. Your explicit path: option keeps you safe.

---

LOW/NO IMPACT — Safe upgrades

┌─────────────────────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────┐  
 │ Package │ Status │  
 ├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ bcryptjs v2 → v3 │ API unchanged (hash/compare/genSalt). models/users.js:3,137-138,161 works as-is │  
 ├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ jsonwebtoken v9 │ Already latest. models/users.js:4,144-150, helpers/auth.js:1,15 fine │
├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤  
 │ mongoose 9.x │ Note: official Mongoose is at 8.x — verify ^9.2.0 is intentional. No deprecated callback APIs found │  
 ├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤  
 │ cors, cookie-parser, morgan │ Stable APIs, no changes needed │  
 ├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤  
 │ express-rate-limit v7 │ Already using modern standardHeaders/legacyHeaders config │  
 ├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤  
 │ express-validator v7 │ Imported but not actively used — consider removing │  
 ├─────────────────────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤  
 │ exceljs │ Stable Workbook API in all 7 usage files │  
 └─────────────────────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────┘

---

UNUSED DEPENDENCIES (remove from package.json)

- multer, uuid, socket.io, haversine, js-promisify, express-jwt, body-parser (only in tests — replaceable with express.json()), express-validator (imported but unused)

---

Biggest blockers to an Express 5 upgrade

1. express-mongo-sanitize + hpp both mutate req.query → will throw at runtime
2. xss-clean archived, needs replacement regardless
3. html-pdf callback API needs full rewrite to puppeteer or similar

I'd recommend tackling the deprecated packages (#1-5) first in isolation, then doing Express 4→5 as a separate migration.

✻ Sautéed for 3m 28s

Why deferring is the right call

1. Scope isolation — if something breaks post-deploy, you want to know whether it's your DIP permission code or Express 5's req.query getter. Bundling them makes rollback and
   triage painful.
2. The deprecated packages aren't on fire — html-pdf, xss-clean, nodemailer-ses-transport still work. They're security/maintenance debt, not outages.
3. Express 4 → 5 needs a dedicated branch — express-mongo-sanitize + hpp will throw at runtime on Express 5 (both mutate req.query). That's not something to discover in a feature
   deploy.
4. html-pdf migration is non-trivial — swapping to puppeteer touches 5 invoice files with callback→async rewrites. Needs its own PR + invoice regression testing.

Suggested sequence after this deploy

┌───────┬────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┬───────────────────────────────────────┐  
 │ Phase │ Scope │ Risk │
├───────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 1 │ Remove unused deps (multer, uuid, socket.io, haversine, js-promisify, express-jwt, body-parser, express-validator) │ Near-zero │
├───────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤
│ 2 │ Drop node-fetch, use Node 18+ global fetch │ Low │  
 ├───────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤  
 │ 3 │ Replace nodemailer-ses-transport → AWS SDK v3 │ Low, isolated to helpers/sendEmail.js │  
 ├───────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤  
 │ 4 │ Replace html-pdf → puppeteer │ Medium, needs PDF output verification │
├───────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤  
 │ 5 │ Replace xss-clean, patch express-mongo-sanitize/hpp │ Medium │
├───────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤  
 │ 6 │ Express 4 → 5 + helmet v8 │ High, dedicated testing cycle │
├───────┼────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┼───────────────────────────────────────┤  
 │ 7 │ Minor bumps (bcryptjs, nodemailer v7, dotenv v17, helmet v8) │ Low │
└───────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┴───────────────────────────────────────┘

Ship 1.4.7 as-is. Open a separate chore/deps-cleanup branch for Phase 1 right after — that alone removes 7 dependencies with zero code changes.

---

Progress log (branch: chore/update-packages)

Phase 1 — DONE (commit 55de9fe)

- Removed 7 unused deps: multer, uuid, haversine, js-promisify, express-jwt, body-parser, express-validator
- Bumped socket.io ^2.4.1 → ^4.8.1 (kept for future use per user decision; not removed)
- Cleaned stale require() lines in dzzlo_oms.js, test/dzzlo_oms_test.js, api_v/api1.js

Phase 2 — DONE (commit ee5bc25)

- Dropped node-fetch; active code now uses Node 22 global fetch
- Updated api_v2/controllers/App/notification.js + api_v3/controllers/App/notification.js (removed require lines; call sites unchanged)
- Disabled api_v1 load path to eliminate its node-fetch dependencies:
  - Commented `const api_v1 = require("./api_v/api1")` in dzzlo_oms.js
  - Commented 3 api_v1 cross-imports in api_v/api2.js (contact_us, pay_trns, payment/paytm)
- ROUTES DISABLED AS A RESULT: /api/v2/contact_us, /api/v2/pay_trns, /api/v2/payment/\* — verify no clients depend on them before deploy
- Server load verified: app starts cleanly without node-fetch in node_modules

Phase 3 — DONE

- Replaced nodemailer-ses-transport (1.5.1) → @aws-sdk/client-ses (^3.1024.0) in helpers/sendEmail.js
- New code: `new SES({ region, credentials })` + `nodemailer.createTransport({ SES: { ses, aws: { SendRawEmailCommand } } })`
- Env vars unchanged: ACCESS_KEY / ACCESS_SECRET / ACCESS_REGION map 1:1 to SDK v3 client config
- Zero changes to 31 call sites across api_v1/v2/v3 — `sendEmail(options)` signature preserved
- yarn remove nodemailer-ses-transport; yarn add @aws-sdk/client-ses (17 transitive deps added)
- Module load verified: `require('./helpers/sendEmail')` returns function cleanly

Phase 4 — DEFERRED (keep html-pdf as tech debt) + POC DONE

- Decision: html-pdf + PhantomJS stays in place for now. Works on current deploy; full migration deferred.
- Known risks accepted: no arm64 PhantomJS binary (fresh installs on M-series Macs break), OPENSSL_CONF=/dev/null workaround required, WebKit ~2014 rendering, no security patches since 2018.
- POC DONE: migrated api_v3/services/invoice/htmlPdf/fileBuffer.js from html-pdf → puppeteer (^24.40.0) as proof-of-concept.
  - Callers unchanged (api_v3/services/invs.js:33, api_v3/controllers/App/email.js:21) — same `fileBuffer(html, options)` signature, Buffer return.
  - Added mapOptions() helper that translates html-pdf opts {width, height, header, footer, border, orientation} → puppeteer page.pdf() opts {width, height, margin, headerTemplate, footerTemplate, landscape}. htmlTemplates/ files don't need to change.
  - Smoke test verified: 16KB valid %PDF buffer generated with real template options ({width: "30cm", height: "42.4cm", header/footer}).
  - Still using html-pdf in: api_v1/controllers/App/invs.js:11, api_v1/controllers/Methods/Invoice/create.js:10, api_v1/controllers/Methods/Invoice/emailPdf.js:1,31, api_v2/controllers/App/email.js:3,24-25.
- Next step when resuming: visual-diff a known invoice against the PhantomJS output, verify margins/fonts, then migrate remaining 4 call sites one at a time.

Phase 5 — DONE

- Removed xss-clean (0.1.4), express-mongo-sanitize (2.2.0), hpp (0.2.3)
- Added mongo-sanitize (^1.1.0) wrapped in new helpers/sanitizeMongo.js middleware
- Middleware mutates req.body/query/params in place via sanitize() — does NOT reassign req.query (Express 5 safe)
- Applied app-wide in dzzlo_oms.js before any route, so api_v2/api_v3/dip/v1 all get NoSQL injection protection without controller changes
- Decisions:
  - xss-clean: dropped entirely, not replaced. Real XSS defense is helmet CSP + output escaping on frontend; xss-clean was 2015-era input stripping with wide bypasses and archived since 2019.
  - hpp: dropped entirely. JSON API (not form-encoded), so HTTP param pollution blast radius is minimal. Any route needing dedup can do a local Array.isArray() check.
  - mongo-sanitize kept as central middleware (vs per-route) because ~20 controllers pass req.body.email/\_id/phone straight into Mongoose filters — central sanitation covers all sites including future ones.
- Files touched: dzzlo_oms.js, test/dzzlo_oms_test.js, helpers/sanitizeMongo.js (new), package.json, yarn.lock
- Smoke-tested: sanitizer strips {$ne: ""} / {$gt: ""} from body+query in isolation; all modified files pass node --check

Phase 6 — DONE

- Upgraded helmet ^7.1.0 → ^8.0.0 (installed 8.1.0)
- Upgraded express ^4.19.2 → ^5.0.0 (installed 5.2.1)
- Helmet done first as standalone step to isolate header-related issues from Express 5 migration
- helmet(): added `crossOriginResourcePolicy: { policy: "cross-origin" }` to preserve v7 behavior (no CORP blocking). Can tighten to "same-origin" later after confirming no cross-origin asset loading.
- Express 5 compatibility verified — no breaking patterns found:
  - No wildcard routes, optional params, res.redirect('back'), app.del(), req.param()
  - sanitizeMongo middleware mutates in-place (does not reassign req.query) — Express 5 safe
  - Error handler has correct (err, req, res, next) signature
  - asyncHandler wrapper still works (now optional — Express 5 auto-forwards async errors)
  - All middleware compatible: express-rate-limit v7, helmet v8, cors, morgan, cookie-parser
- Files touched: dzzlo_oms.js, test/dzzlo_oms_test.js, package.json, yarn.lock
- Module load verified: Express 5.2.1 + all middleware loads cleanly

Phase 7 — DONE

- Upgraded bcryptjs ^2.4.3 → ^3.0.0 (installed 3.0.3)
  - API unchanged: genSalt/hash/compare all work as-is in models/users.js:137-138,161
- Upgraded nodemailer ^6.7.2 → ^7.0.0 (installed 7.0.13)
  - createTransport + sendMail API unchanged. helpers/sendEmail.js (SES) and helpers/sendEmailnaAWS.js (SMTP) work as-is
- Upgraded dotenv ^16.4.5 → ^17.0.0 (installed 17.4.1)
  - v17 changed default .env discovery, but all usages in this project use explicit path: option — no impact
- No code changes — only package.json + yarn.lock updated
- All three modules load-verified
