# Plan: Build OneSignal's Value-Add Features In-House (on FCM + FIAM + BullMQ)

> Companion to `FIREBASE_NOTIFICATIONS_MIGRATION_PLAN.md`. That plan gets us off OneSignal for **transactional** push. This plan builds the **marketing / growth** layer OneSignal would have given us — segmentation, campaigns, delivery reporting, journeys, templates, in-app + multi-channel — on top of our own stack: MongoDB + BullMQ + Firebase Admin SDK + FIAM.
>
> Two rules of the road:
>
> 1. **Dogfood existing infra.** We already have RTK Query, BullMQ queues, Mongo, Firebase Analytics, Remote Config, FIAM. Don't introduce Kafka/Redshift/Hasura to rebuild a dashboard.
> 2. **Ship the MVP of each phase before moving on.** Each phase is independently useful — if business priorities change, we can stop after any phase and still have shipped value.

Scope recap — features to rebuild:

| Feature                     | Source                                                     |
| --------------------------- | ---------------------------------------------------------- |
| A. Segment builder          | OneSignal → tags + filters                                 |
| B. Campaign composer        | OneSignal → dashboard compose UI                           |
| C. Delivery reporting       | OneSignal → sent/delivered/clicked/converted funnel        |
| D. Templates + localization | OneSignal → WYSIWYG + variables                            |
| E. Journeys / drip          | OneSignal → automation workflows                           |
| F. Multi-channel            | OneSignal → push + email + SMS + in-app under one audience |
| G. iOS rich media           | OneSignal NSE out-of-the-box                               |

---

## Phase 0 — Prerequisites (foundation already in place)

**Only proceed if these are true** (they are, per the other plans in this folder):

- Firebase Analytics is live (`FIREBASE_ANALYTICS_PLAN.md`) with `role`, `company_id`, `app_version` default params + user properties.
- FCM is the delivery mechanism (`FIREBASE_NOTIFICATIONS_MIGRATION_PLAN.md`).
- BullMQ `notifications` queue + `pushWorker` are deployed.
- `fcm_tokens` + `notif_logs` collections exist.
- Remote Config is initialized (we'll use it for kill-switches).

No new dependencies in Phase 0. Move on.

---

## Phase 1 — Segment Builder (MVP)

**Goal:** Let a non-engineer (ops/support) target a group of users without writing code.

### Step 1.1 — Data model: `segments` collection

```js
{
  _id,
  name: "Delhi dealers who logged in last 7 days",
  created_by: ObjectId,
  created_at: Date,
  rules: {
    op: "AND",
    clauses: [
      { field: "role", op: "eq", value: "dealer" },
      { field: "company.state", op: "eq", value: "DL" },
      { field: "last_login_at", op: "gt_days_ago", value: 7 },
    ],
  },
  materialized_count: 1240,   // cached, refreshed on open
  materialized_at: Date,
}
```

### Step 1.2 — Whitelist the fields available

Hard-code in `config/segmentFields.js`:

```js
module.exports = [
  { key: "role", label: "Role", type: "enum", options: ["customer", "dealer"] },
  {
    key: "company.state",
    label: "State",
    type: "enum_dynamic",
    source: "states",
  },
  {
    key: "company.district",
    label: "District",
    type: "enum_dynamic",
    source: "districts",
  },
  { key: "last_login_at", label: "Last login", type: "date_ago" },
  { key: "created_at", label: "User created", type: "date_ago" },
  { key: "app_version", label: "App version", type: "semver" },
  {
    key: "platform",
    label: "Platform",
    type: "enum",
    options: ["ios", "android"],
  },
  { key: "has_active_orders", label: "Has open orders", type: "boolean" },
];
```

Never allow arbitrary Mongo queries from the UI — the UI builds these typed clauses, the server translates to Mongo.

### Step 1.3 — Translator `lib/segments/toMongo.js`

```js
const OPS = {
  eq: (field, v) => ({ [field]: v }),
  neq: (field, v) => ({ [field]: { $ne: v } }),
  in: (field, v) => ({ [field]: { $in: v } }),
  gt_days_ago: (field, v) => ({ [field]: { $gt: daysAgo(v) } }),
  lt_days_ago: (field, v) => ({ [field]: { $lt: daysAgo(v) } }),
  exists: (field) => ({ [field]: { $exists: true, $ne: null } }),
};
```

### Step 1.4 — Endpoints

| Method | Path                           | Purpose                                                      |
| ------ | ------------------------------ | ------------------------------------------------------------ |
| GET    | `/sadmin/segments/fields`      | Return whitelist for UI builder                              |
| POST   | `/sadmin/segments`             | Create — validates vs whitelist                              |
| GET    | `/sadmin/segments/:id/preview` | Returns count + 10 sample user IDs                           |
| POST   | `/sadmin/segments/:id/resolve` | Returns the full user-id array (internal, used by send step) |

### Step 1.5 — UI (admin web, not the RN app)

Three dropdowns per clause (field, op, value) + AND/OR toggle + "Preview → N users" button. Keep it ugly; nobody outside the team uses it.

**Exit gate for Phase 1:** ops can define a segment via UI, preview returns expected count, `resolve` returns the right user ids.

---

## Phase 2 — Campaign Composer + Delivery Reporting (MVP)

**Goal:** Ops can compose a one-shot push to a segment, hit Send, and see how many arrived / were tapped.

### Step 2.1 — Data model: `campaigns` + enrich `notif_logs`

```js
// campaigns
{
  _id,
  name: "Q1 promo — dealer",
  segment_id: ObjectId,
  channels: ["push"],   // room for ["push","email","sms","inapp"] later
  template_id: ObjectId | null,
  message: {
    push: { title, body, data: {} },
  },
  schedule: { type: "now" | "at", at: Date | null },
  status: "draft" | "queued" | "sending" | "sent" | "cancelled",
  metrics: { resolved: 0, sent: 0, failed: 0, delivered: 0, clicked: 0, converted: 0 },
  created_by, created_at, sent_at,
}
```

Extend `notif_logs` (from migration plan §S5) with: `campaign_id`, `user_id` (per-row, not array), `fcm_message_id`, `delivered_at`, `clicked_at`, `converted_at`.

### Step 2.2 — Flow

```
[Admin clicks Send]
      │
      ▼
POST /sadmin/campaigns/:id/send
      │  (validates segment, status=queued, push job onto campaignQueue)
      ▼
campaignQueue: "send-campaign" { campaign_id }
      │
      ▼
Worker:
   resolve segment → user ids
   chunk user ids → fan-out send-push-one jobs onto `notifications` queue
   update metrics.resolved
      │
      ▼
notifications queue worker (already exists):
   for each job: sendEachForMulticast to that user's tokens
   record notif_logs row per (user, token) with fcm_message_id
   update campaigns.metrics.sent / .failed atomically ($inc)
```

Why fan-out: one campaign to 50k users → 50k `send-push-one` jobs → BullMQ gives us rate-limiting, retry, concurrency out of the box (per `system-design/09-async-queues.md`).

### Step 2.3 — Delivery tracking

**Sent** = FCM accepted the message → record from `sendEachForMulticast` response.

**Delivered** (harder — FCM doesn't tell us reliably):

- **Android**: enable FCM delivery-reports via BigQuery export → daily ingest into `notif_logs` keyed by `fcm_message_id`. _Or_ use a data-only payload + client acknowledgment.
- **iOS**: no APNs delivery receipt. Use data-only pushes + client ack (next bullet) if you really need this.
- **Client-ack option (most reliable, works on both platforms):** send `notification: null, data: { campaign_id, log_id }` + let the worker draw the notification via notifee on receipt → before rendering, fire `POST /notif-logs/:log_id/delivered` (fire-and-forget). Trade-off: system-tray notifications only appear after the app receives the data payload (so the app must be allowed to wake; Android ≥ 8 with Doze will delay this for inactive users). **Recommendation:** use client-ack only for campaigns where delivery metrics matter more than immediacy. Transactional pushes keep the dual `notification` + `data` shape from the migration plan.

**Clicked**:

- Client tap handler (already added in migration plan Step C4): `onNotificationOpenedApp` + `getInitialNotification` → on data payload with `log_id`, call `POST /notif-logs/:log_id/clicked`.
- This is accurate on both platforms.

**Converted**:

- Each campaign optionally has a `conversion_event` (Firebase Analytics event name) + `conversion_window_minutes` (default 60).
- After click, watch for that Analytics event in the app → when the event fires within the window, call `POST /notif-logs/:log_id/converted` with the event params.
- Simpler: just count "campaign tap → did the user reach screen X within Y min" via a thin middleware on the RN side that reads the most recent click from Redux.

### Step 2.4 — Dashboard

Per campaign, four numbers + trend:

```
Resolved 10,000  Sent 9,840  Delivered 7,412  Clicked 612  Converted 74
                 (CTR 8.2% of delivered)  (CVR 12.1% of clicked)
```

Plus a per-hour bar chart from `notif_logs.{sent_at,clicked_at}`.

Power it with a single aggregate endpoint `GET /sadmin/campaigns/:id/metrics` — don't pre-aggregate yet, Mongo handles this at scale below 100k/day.

**Exit gate for Phase 2:** ops can pick a segment, compose a push, hit send, and see "X sent, Y clicked" in the dashboard within 10 minutes.

---

## Phase 3 — Templates + Localization

**Goal:** Ops reuses messaging copy without copy-pasting; different strings per `user.lang`.

### Step 3.1 — `templates` collection

```js
{
  _id, name, channel: "push",
  variants: {
    en: { title: "Hi {{first_name}}, new orders!", body: "You have {{count}} pending." },
    hi: { title: "नमस्ते {{first_name}}", body: "{{count}} ऑर्डर बाकी हैं।" },
  },
  variables: ["first_name", "count"],
  created_by, created_at,
}
```

### Step 3.2 — Renderer `lib/templates/render.js`

- Lock variables to a small whitelist (`{{first_name}}`, `{{company_name}}`, `{{order_count}}`, `{{amount}}`, `{{due_date}}`).
- Use `mustache.js` (no eval, no code execution). Never `eval`, never `new Function`.
- Fall back to `en` if the user's `lang` is missing.

### Step 3.3 — Wire into campaigns + transactional sends

`campaigns` gets `template_id` (already scaffolded in Phase 2). The worker's first action becomes: `const rendered = render(template, { ...userVars, ...campaignVars });`.

Also expose the renderer to **transactional** senders — e.g. `services/invs.js` switches from inline strings to `template.invoice_created` with `{ amount, dealer_name }`. This kills hard-coded notification strings scattered across 26 files.

**Exit gate for Phase 3:** creating a template, editing its Hindi variant, and sending a campaign using it works; non-engineers can tweak copy without a deploy.

---

## Phase 4 — Scheduled Sends + Journeys (Drip Automation)

**Goal:** "Send a reminder 48h after order placed if still pending" without hand-rolling cron per campaign.

### Step 4.1 — Scheduled one-shots (simple)

Already free via BullMQ `delay` / `repeat` (per `system-design/09-async-queues.md`):

```js
campaignQueue.add("send-campaign", { campaign_id }, { delay: msUntil(at) });
// or repeatable:
campaignQueue.add(
  "send-campaign",
  { campaign_id },
  { repeat: { cron: "0 9 * * 1" } },
);
```

Expose in the composer as "Send now / Send at / Repeat weekly at …".

### Step 4.2 — Journeys (state machine)

Data model `journeys`:

```js
{
  _id, name,
  trigger: { type: "analytics_event", event: "order_create" },
  audience_segment_id: ObjectId | null,
  steps: [
    { id: "s1", type: "wait", duration: "24h" },
    { id: "s2", type: "check", segment_id: ObjectId /* still has pending orders */ },
    { id: "s3", type: "send", template_id: ObjectId, channel: "push" },
    { id: "s4", type: "wait", duration: "24h" },
    { id: "s5", type: "check", segment_id: ObjectId },
    { id: "s6", type: "send", template_id: ObjectId, channel: "email" },
  ],
  status: "draft" | "active" | "paused",
}
```

Runtime `journey_runs` collection tracks `(journey_id, user_id, current_step, resume_at, context)`.

### Step 4.3 — Entering a journey

Two paths:

1. **Server event** (preferred) — when `order_create` happens in `services/order_msts.js`, producer-emit `journeyEngine.enqueue('order_create', { user_id, order_id })`. Engine matches active journeys whose trigger matches, creates a `journey_run`.

2. **Analytics event (via BigQuery export or webhook)** — avoid unless we absolutely must trigger off events we can't see server-side. Adds latency (BigQuery is ~min-to-hours).

### Step 4.4 — Engine worker

BullMQ `journeyQueue` with one job type `advance-run { run_id }`:

- Load run, look up `steps[current_step]`.
- `wait` → re-enqueue with `delay` = duration. Update `resume_at`.
- `check` → evaluate segment; if user no longer matches, set `status=exited` and stop.
- `send` → enqueue `send-push-one` (or email/sms when Phase 6 lands) with rendered template.
- Advance `current_step`. If end of list → `status=complete`.

### Step 4.5 — Kill switches

Every journey gets a global Remote Config flag: `journey_<id>_enabled` default `true`. Engine checks before each advance. Flip `false` to pause without a deploy.

**Exit gate for Phase 4:** "send 24h follow-up to dealers with unpaid invoices" journey works on a synthetic test user, exits correctly if the user pays in between, and can be paused via Remote Config.

---

## Phase 5 — Richer In-App Messaging (beyond FIAM limits)

**Goal:** FIAM covers modal / banner / card triggered by Analytics events. When we need **user-targeted** in-app messages (not audience-targeted) or **custom layouts**, build on top.

### Step 5.1 — Native fallback first — use FIAM

For 80% of cases (update-app, feature announcement, promo), a FIAM campaign triggered on `app_open` with an audience filter is enough. **Don't build custom UI until FIAM is insufficient.**

### Step 5.2 — `inapp_messages` collection (for user-targeted messages)

When ops wants "show this banner to user_123 next time they open the app":

```js
{
  _id, user_id, template_id,
  variant: "banner" | "modal" | "card",
  priority: 0..10,
  expires_at: Date,
  shown_at: Date | null,
  dismissed_at: Date | null,
  clicked_at: Date | null,
}
```

### Step 5.3 — Client polling endpoint

On app foreground, RN calls `GET /inapp/messages/pending`. Returns top-priority un-shown non-expired message. RN's shell layout reads one slot from Redux and renders the right component per `variant`. POST dismiss/click back.

Keep the polling trivial — don't build realtime push for in-app messages yet; on-open poll is enough at our scale (per `system-design` cost-benefit framing).

**Exit gate for Phase 5:** ops can queue a per-user banner from the dashboard; the next app-open renders and acks it.

---

## Phase 6 — Multi-Channel (Email + SMS under the same campaign)

**Goal:** one campaign, multiple channels, one delivery report.

### Step 6.1 — Channel-agnostic campaign

`campaigns.channels` already is an array (Phase 2). Extend:

```js
{
  channels: ["push", "email", "sms"],
  message: {
    push: { template_id },
    email: { template_id, subject_template_id, from },
    sms: { template_id },
  },
  fallback: { if: "push_not_delivered_in", duration: "2h", then: "sms" },
}
```

### Step 6.2 — Reuse existing senders

We already have:

- **Email** via Nodemailer + AWS SES (`helpers/sendEmail.js` — already called through a queue per the async-queues plan).
- **SMS** via 2Factor.in (`SMSOTP/template/index.js`).

Add `send-email` and `send-sms` job types to the `notifications` queue (they're already proposed in `system-design/09-async-queues.md` §Step 6).

Worker extends to dispatch by channel. Rendered template per channel, per locale.

### Step 6.3 — Fallback logic

A "fallback" step pattern: campaign fan-out schedules **two** jobs per user — the primary channel immediately, the fallback with `delay: 2h` and `jobId: user_id:campaign_id:fallback`. When the primary's `delivered_at` lands in `notif_logs`, worker calls `job.remove()` on the fallback. Otherwise the fallback fires.

**Exit gate for Phase 6:** a campaign defined as "push with SMS fallback after 2h" delivers correctly in both the happy path (push delivered, SMS cancelled) and fallback path (push fails, SMS fires).

---

## Phase 7 — iOS Rich Media (NSE rebuild)

**Goal:** large image in push notification, like OneSignal's NSE gave us for free.

### Step 7.1 — Add Notification Service Extension

In Xcode: File → New → Target → Notification Service Extension. Name it `OmsNotifServiceExtension`.

### Step 7.2 — Handle mutable-content

```swift
override func didReceive(_ request: UNNotificationRequest,
                         withContentHandler handler: @escaping (UNNotificationContent) -> Void) {
  guard let content = (request.content.mutableCopy() as? UNMutableNotificationContent),
        let imageUrlString = content.userInfo["image_url"] as? String,
        let imageUrl = URL(string: imageUrlString) else {
    handler(request.content); return
  }
  URLSession.shared.downloadTask(with: imageUrl) { tempUrl, _, _ in
    if let tempUrl = tempUrl,
       let attachment = try? UNNotificationAttachment(identifier: "image",
                                                      url: tempUrl,
                                                      options: nil) {
      content.attachments = [attachment]
    }
    handler(content)
  }.resume()
}
```

### Step 7.3 — Server sets `mutable-content` + `image_url`

```js
apns: { payload: { aps: { "mutable-content": 1 } } },
data: { image_url: "https://cdn.../promo.png" },
```

Android: FCM supports `android.notification.imageUrl` natively — no extension needed.

**Exit gate for Phase 7:** a test campaign with `image_url` renders with image expanded on iOS and Android.

---

## Phase 8 — Polish (only if we grew past OneSignal parity)

Each of these is an **independent** improvement — cherry-pick based on pain.

1. **Frequency capping** — `user_id + day` doc in a `send_caps` collection with TTL. Worker refuses to send if cap exceeded. Config per-channel.
2. **Quiet hours** — per-user `quiet_hours` object; worker reschedules to `duration_until_end_of_quiet_hours`.
3. **A/B testing** — `campaigns.variants: [{ template_id, weight }]`; worker picks by deterministic hash of `user_id % 100`. Metrics tagged with variant.
4. **Send-time optimization** — aggregate `clicked_at` by user+hour over trailing 30 days → pick the user's best hour as default send time. Cheap Mongo aggregation, nightly job.
5. **Webhook integrations** — outbound webhook on `delivered` / `clicked` / `converted` so other internal systems can react.
6. **BigQuery export of `notif_logs`** — when volume exceeds ~100k events/day, Mongo aggregation chokes on dashboards. BigQuery export + Metabase over it.

---

## Cross-cutting concerns

### Observability

- Every job in `notifications` / `campaigns` / `journeys` queues logs to **Bull Board** (already recommended in `system-design/09-async-queues.md`).
- `notif_logs` is the source of truth for delivery metrics.
- CloudWatch alarm on queue depth + failed-job rate.

### Safety rails

- Every outbound step honors a Remote Config kill-switch: `push_send_enabled`, `email_send_enabled`, `sms_send_enabled`. Flip off instantly if something goes wrong.
- Every campaign has `dry_run: true` by default — running a campaign in dry-run materializes the would-be `notif_logs` rows but skips actual send. Ops previews the fan-out before flipping `dry_run: false`.
- Hard cap per-campaign: reject send if `resolved_count > 100_000` without an explicit `confirm_large_send: true` flag.

### Compliance

- User's `notification_preferences` per channel (push / email / SMS) — honor on every send. Transactional events (OTP, order-status) bypass marketing opt-outs; marketing campaigns respect them.
- `unsubscribe_token` in email footer.

### Testing

- Seed a `staging` segment (`role=dealer`, `phone: /^9999/`) that's safe to blast.
- Integration test per phase: synthetic user → synthetic send → assert `notif_logs` row shape → assert dashboard math.

---

## Sequencing recap

| Phase | What lands                                         | Effort               | Depends on                       |
| ----- | -------------------------------------------------- | -------------------- | -------------------------------- |
| 0     | Prereqs already satisfied                          | —                    | Migration plan                   |
| 1     | Segment builder + preview                          | ~3 days              | —                                |
| 2     | Campaign composer + delivery report                | ~5 days              | 1                                |
| 3     | Templates + localization                           | ~3 days              | 2                                |
| 4     | Scheduled + journeys                               | ~5 days              | 2, 3                             |
| 5     | Rich in-app messaging                              | ~3 days              | 2 (FIAM must cover basics first) |
| 6     | Multi-channel (email/SMS under campaigns)          | ~4 days              | 2, 3                             |
| 7     | iOS rich media                                     | ~1 day               | Migration plan NSE deleted       |
| 8     | Frequency cap / quiet hours / A-B / STO / webhooks | Pick n days per pick | 2                                |

**The honest take** (mirrors the cost/benefit framing in `system-design/09-async-queues.md`): Phases 1–3 alone already replicate 80% of OneSignal's day-to-day value at DZZLO OMS scale. Phase 4+ is only worth it if the business genuinely wants drip marketing. **Stop when it stops paying off** — we are not building a notification platform, we are building an OMS.
