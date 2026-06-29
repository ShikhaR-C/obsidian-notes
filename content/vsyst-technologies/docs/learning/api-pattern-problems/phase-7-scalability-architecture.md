# Phase 7: Scalability Architecture

**Priority:** P2 (7A, 7D) + P3 (7B, 7C, 7E) | **Timeline:** Week 9-12

---

## Research: Scaling Node.js + MongoDB

### Horizontal Scaling Strategies

1. **PM2 Cluster Mode** -- multiple Node.js processes on one server (leverages all CPU cores)
2. **Load Balancer** -- distribute across multiple servers (Nginx already configured)
3. **Read Replicas** -- route read queries to secondary MongoDB nodes
4. **Microservices** -- split monolith into domain-specific services (long-term)

### Connection Pool Mathematics

```
Total connections = PM2_instances × maxPoolSize
MongoDB Atlas M10 limit = 1,500 connections
Safe target = 70% of limit = 1,050

If PM2 instances = 4 (quad-core server):
  maxPoolSize per instance = 1,050 / 4 = ~260

But typically lower is better:
  maxPoolSize = 50-100 per instance (200-400 total)
  Enough for 200+ concurrent requests
```

### Queue-Based Architecture

```
Client → API → Queue (Redis/BullMQ) → Workers
                                          ├── Email Worker
                                          ├── SMS Worker
                                          ├── Notification Worker
                                          └── Report Worker
```

Benefits:

- API responds immediately (no waiting for SMS/email)
- Workers can retry independently
- Workers scale independently
- System remains responsive under load

---

## Sub-Phase 7A: PM2 Cluster Mode

### Problem

**File:** `ecosystem.config.js`

```js
module.exports = {
  apps: [
    {
      name: "dzzlo-oms",
      script: "dzzlo_oms.js",
      instances: 1, // Single instance -- doesn't use multiple CPU cores
      // ...
    },
  ],
};
```

Single process = single CPU core utilized. On a 4-core server, 75% of CPU capacity is wasted.

### Prerequisites Check

Before enabling cluster mode, ensure no shared in-process state:

| Concern                | Status                        | Fix Required                                             |
| ---------------------- | ----------------------------- | -------------------------------------------------------- |
| Module-level variables | `logBuffer` in middlewares.js | Each instance gets its own buffer (OK with batch writes) |
| Socket.io              | Currently commented out       | If re-enabled, needs Redis adapter                       |
| Redis cache            | Shared by design              | No fix needed                                            |
| File uploads (multer)  | Disk storage                  | Switch to memory/S3 for multi-instance                   |
| Rate limiting          | In-memory by default          | Use Redis store (Phase 4A)                               |

### Proposed Solution

```js
// ecosystem.config.js
const os = require("os");

module.exports = {
  apps: [
    {
      name: "dzzlo-oms",
      script: "dzzlo_oms.js",
      instances: process.env.PM2_INSTANCES || "max", // Use all CPU cores
      exec_mode: "cluster", // Enable cluster mode

      // Graceful shutdown
      kill_timeout: 5000,
      listen_timeout: 10000,

      // Auto-restart on memory leak
      max_memory_restart: "500M",

      // Logging
      log_date_format: "YYYY-MM-DD HH:mm:ss Z",
      error_file: "./logs/pm2-error.log",
      out_file: "./logs/pm2-out.log",
      merge_logs: true,

      // Environment
      env_testing: {
        NODE_ENV: "testing",
        PM2_INSTANCES: 2,
      },
      env_production: {
        NODE_ENV: "production",
        PM2_INSTANCES: "max",
      },
    },
  ],
};
```

### Graceful Shutdown Handler

```js
// Add to dzzlo_oms.js
process.on("SIGINT", gracefulShutdown);
process.on("SIGTERM", gracefulShutdown);

async function gracefulShutdown() {
  console.log("Graceful shutdown initiated...");

  // 1. Stop accepting new connections
  server.close(async () => {
    // 2. Flush log buffer
    if (logBuffer.length > 0) {
      await Logs.insertMany(logBuffer.splice(0), { ordered: false }).catch(
        () => {},
      );
    }

    // 3. Close Redis
    await redis.quit().catch(() => {});

    // 4. Close MongoDB
    await mongoose.connection.close();

    console.log("Shutdown complete");
    process.exit(0);
  });

  // Force shutdown after 5 seconds
  setTimeout(() => {
    console.error("Forced shutdown");
    process.exit(1);
  }, 5000);
}
```

### Zero-Downtime Deployment

```bash
# Reload without downtime (cluster mode required)
pm2 reload dzzlo-oms

# Or with ecosystem file
pm2 reload ecosystem.config.js --env production
```

**Impact:** 2-4x throughput increase depending on server CPU cores.

---

## Sub-Phase 7B: Queue-Based Email/SMS Processing

### Problem

**File:** `api_v3/services/order_msts.js`, lines 566-652

Order processing sends SMS and email **synchronously** during the request:

```js
// Line 610-635: SMS sending blocks the response
await sendSMSToDriverPhone(
  async (onResult) => {
    await OTP_BY(onResult.body);
  },
  { driver_phone, var1, var2, notify },
);

// Then email:
await sendEmail({ email: driver.email, subject, html });
```

If 2Factor.in SMS API takes 500ms and email takes 200ms, that's 700ms added to every order process request.

### Proposed Solution: BullMQ

**Install:**

```bash
yarn add bullmq
```

**New file:** `workers/queues.js`

```js
const { Queue } = require("bullmq");
const { redis } = require("../helpers/cache");

const connection = { connection: redis };

exports.smsQueue = new Queue("sms", connection);
exports.emailQueue = new Queue("email", connection);
exports.notificationQueue = new Queue("push-notification", connection);
```

**New file:** `workers/smsWorker.js`

```js
const { Worker } = require("bullmq");
const { redis } = require("../helpers/cache");
const { sendSMSToDriverPhone } = require("../helpers/sms");

const worker = new Worker(
  "sms",
  async (job) => {
    const { phone, var1, var2, template } = job.data;

    await sendSMSToDriverPhone(
      async (onResult) => {
        console.log(`SMS sent to ${phone}: ${onResult.body}`);
      },
      { driver_phone: phone, var1, var2, notify: true },
    );
  },
  {
    connection: redis,
    concurrency: 5, // Process 5 SMS jobs concurrently
    limiter: { max: 10, duration: 1000 }, // Rate limit: 10/second
  },
);

worker.on("completed", (job) => {
  console.log(`SMS job ${job.id} completed`);
});

worker.on("failed", (job, err) => {
  console.error(`SMS job ${job.id} failed: ${err.message}`);
});
```

**New file:** `workers/emailWorker.js`

```js
const { Worker } = require("bullmq");
const { redis } = require("../helpers/cache");
const { sendEmail } = require("../helpers/sendEmail");

const worker = new Worker(
  "email",
  async (job) => {
    const { email, subject, html } = job.data;
    await sendEmail({ email, subject, html });
  },
  {
    connection: redis,
    concurrency: 3,
  },
);
```

**New file:** `workers/notificationWorker.js`

```js
const { Worker } = require("bullmq");
const { redis } = require("../helpers/cache");
const { sendNotifyToExternalIDs } = require("../helpers/sendNotify");

const worker = new Worker(
  "push-notification",
  async (job) => {
    await sendNotifyToExternalIDs(job.data);
  },
  {
    connection: redis,
    concurrency: 10,
  },
);
```

**Update order service** (`api_v3/services/order_msts.js`):

```js
const { smsQueue, emailQueue, notificationQueue } = require("../../workers/queues");

// BEFORE (blocking):
await sendSMSToDriverPhone(...);
await sendEmail({ email: driver.email, ... });
await sendNotifyToExternalIDs({ userIds, ... });

// AFTER (non-blocking):
await smsQueue.add("otp-sms", {
  phone: driver.phone,
  var1: otpValue,
  var2: `${vehicle.veh_reg_no} Order ${orderNumber}`,
});

await emailQueue.add("otp-email", {
  email: driver.email,
  subject: `OTP for Order ${orderNumber}`,
  html: otpEmailHtml,
});

await notificationQueue.add("new-order", {
  userIds: notifUserIds,
  jsonData: { superadmin: "", customer: "", dealer: "NewOrder" },
  headingData: `New Order: ${orderNumber}`,
  contentData: `${vehicle.veh_reg_no} - ${amt}`,
});
```

**Start workers (PM2):**

```js
// ecosystem.config.js - add worker processes
module.exports = {
  apps: [
    {
      name: "dzzlo-oms-api",
      script: "dzzlo_oms.js",
      instances: "max",
      exec_mode: "cluster",
    },
    {
      name: "dzzlo-oms-sms-worker",
      script: "workers/smsWorker.js",
      instances: 1,
    },
    {
      name: "dzzlo-oms-email-worker",
      script: "workers/emailWorker.js",
      instances: 1,
    },
    {
      name: "dzzlo-oms-notif-worker",
      script: "workers/notificationWorker.js",
      instances: 1,
    },
  ],
};
```

**Impact:**

- Order process response: removes ~700ms (SMS + email wait)
- SMS/email failures don't affect API response
- Workers auto-retry failed jobs (3 attempts by default)
- Queue metrics visible via BullMQ dashboard

---

## Sub-Phase 7C: WebSocket for Real-Time Updates

### Problem

The codebase has Socket.io installed (`socket.io@2.4.1` in package.json) and commented-out code (`middlewares.js` lines 249-293). Currently, the app must poll or manually refresh to see order status changes.

### Proposed Solution

**Upgrade Socket.io** to v4.x (v2.4.1 is outdated):

```bash
yarn remove socket.io
yarn add socket.io@4
```

**New file:** `helpers/socket.js`

```js
const { Server } = require("socket.io");
const { createAdapter } = require("@socket.io/redis-adapter");
const { redis } = require("./cache");
const Redis = require("ioredis");

let io;

exports.initSocket = (httpServer) => {
  io = new Server(httpServer, {
    cors: {
      origin: process.env.CORS_ORIGIN_1 || "*",
      methods: ["GET", "POST"],
    },
    // Redis adapter for multi-instance support (PM2 cluster)
    adapter: createAdapter(redis, redis.duplicate()),
  });

  io.on("connection", (socket) => {
    // Join user-specific room on auth
    socket.on("auth", (userId) => {
      socket.join(`user:${userId}`);
    });

    // Join company room
    socket.on("joinCompany", (companyId) => {
      socket.join(`company:${companyId}`);
    });
  });

  return io;
};

exports.getIO = () => {
  if (!io) throw new Error("Socket.io not initialized");
  return io;
};

// Emit helpers
exports.emitOrderUpdate = (dealerId, custId, orderData) => {
  if (!io) return;
  io.to(`company:${dealerId}`).emit("order:updated", orderData);
  io.to(`company:${custId}`).emit("order:updated", orderData);
};

exports.emitNewOrder = (dealerId, orderData) => {
  if (!io) return;
  io.to(`company:${dealerId}`).emit("order:new", orderData);
};
```

**Integrate in `dzzlo_oms.js`:**

```js
const http = require("http");
const { initSocket } = require("./helpers/socket");

const server = http.createServer(app);
initSocket(server);

server.listen(PORT, () => { ... });
```

**Emit on order lifecycle:**

```js
// In order_msts service, after status update
const { emitOrderUpdate, emitNewOrder } = require("../../helpers/socket");

// After order creation
emitNewOrder(order.dealer_id, { orderId: order._id, status: "PENDING" });

// After order process (OTP sent)
emitOrderUpdate(order.dealer_id, order.cust_id, {
  orderId: order._id,
  status: "PROCESSING",
});

// After order delivery
emitOrderUpdate(order.dealer_id, order.cust_id, {
  orderId: order._id,
  status: "DELIVERED",
});
```

**App-side (React Native):**

```js
// src/utils/socket.js
import io from "socket.io-client";
import { api } from "../store/apis/createApi";

const socket = io(BASE_URL, { autoConnect: false });

export const connectSocket = (userId, companyId) => {
  socket.connect();
  socket.emit("auth", userId);
  socket.emit("joinCompany", companyId);

  socket.on("order:new", (data) => {
    store.dispatch(api.util.invalidateTags([{ type: "orders", id: "LIST" }]));
  });

  socket.on("order:updated", (data) => {
    store.dispatch(
      api.util.invalidateTags([{ type: "orders", id: data.orderId }]),
    );
  });
};
```

---

## Sub-Phase 7D: Connection Pool Tuning

### Problem

**File:** `helpers/db_conn.js` -- uses Mongoose default connection pool (100 connections).

With PM2 cluster mode (4 instances), that's 400 connections. MongoDB Atlas M10 supports 1,500 max.

### Proposed Solution

```js
// helpers/db_conn.js
const numCpus = require("os").cpus().length;
const instances = parseInt(process.env.PM2_INSTANCES, 10) || numCpus;

const connectDB = async () => {
  const conn = await mongoose.connect(process.env.DATABASE_URI, {
    maxPoolSize: Math.ceil(200 / instances), // 200 total across all instances
    minPoolSize: 5,
    maxIdleTimeMS: 30000, // Close idle connections after 30s
    serverSelectionTimeoutMS: 5000,
    socketTimeoutMS: 45000,
    connectTimeoutMS: 10000,
  });

  console.log(
    `MongoDB Connected: ${conn.connection.host} (pool: ${Math.ceil(200 / instances)})`,
  );
};
```

**For DIP database (secondary connection):**

```js
const dipConn = mongoose.createConnection(process.env.DIPDB, {
  maxPoolSize: Math.ceil(50 / instances), // Lower pool for secondary DB
  minPoolSize: 2,
  maxIdleTimeMS: 60000,
});
```

---

## Sub-Phase 7E: Event-Driven Order Lifecycle

### Problem

Order lifecycle operations (create, process, deliver, cancel) are monolithic -- each controller function handles:

1. Core business logic
2. Notifications (push, SMS, email)
3. Cache invalidation
4. Logging/auditing
5. Balance updates

This couples unrelated concerns and makes the code brittle.

### Proposed Solution: Event Emitter Pattern

**New file:** `helpers/events.js`

```js
const EventEmitter = require("events");

class OrderEvents extends EventEmitter {
  constructor() {
    super();
    this.setMaxListeners(20); // Allow multiple listeners
  }
}

const orderEvents = new OrderEvents();

module.exports = { orderEvents };
```

**New file:** `helpers/eventListeners.js`

```js
const { orderEvents } = require("./events");
const {
  smsQueue,
  emailQueue,
  notificationQueue,
} = require("../workers/queues");
const { emitOrderUpdate, emitNewOrder } = require("./socket");
const { invalidate } = require("./cache");

// Notification listener
orderEvents.on(
  "order:created",
  async ({ order, dealer, customer, vehicle, notifUserIds, amount }) => {
    const orderNumber = pad(order.order_no);
    const amt = formatCurrency(amount);

    await notificationQueue.add("new-order", {
      userIds: notifUserIds,
      headingData: `New Order: ${orderNumber}`,
      contentData: `${vehicle.veh_reg_no} - ${amt} of ${customer.cust_name} to ${dealer.dealer_name}`,
    });

    emitNewOrder(order.dealer_id, { orderId: order._id, status: "PENDING" });
  },
);

orderEvents.on(
  "order:processing",
  async ({ order, driver, vehicle, otpValue }) => {
    await smsQueue.add("otp-sms", {
      phone: driver.phone,
      var1: otpValue,
      var2: `${vehicle.veh_reg_no} Order ${pad(order.order_no)}`,
    });

    if (driver.email) {
      await emailQueue.add("otp-email", {
        email: driver.email,
        subject: `OTP for Order ${pad(order.order_no)}`,
      });
    }

    emitOrderUpdate(order.dealer_id, order.cust_id, {
      orderId: order._id,
      status: "PROCESSING",
    });
  },
);

orderEvents.on("order:delivered", async ({ order }) => {
  // Invalidate balance caches
  await invalidate(`dc:${order.dealer_id}:${order.cust_id}`);
  emitOrderUpdate(order.dealer_id, order.cust_id, {
    orderId: order._id,
    status: "DELIVERED",
  });
});

orderEvents.on("order:cancelled", async ({ order }) => {
  await invalidate(`dc:${order.dealer_id}:${order.cust_id}`);
  emitOrderUpdate(order.dealer_id, order.cust_id, {
    orderId: order._id,
    status: "CANCELLED",
  });
});
```

**Register listeners in `dzzlo_oms.js`:**

```js
require("./helpers/eventListeners");
```

**Usage in order service:**

```js
const { orderEvents } = require("../../helpers/events");

exports.createMstTrn = async ({ body, meta }) => {
  // ... create order ...

  // Emit event (non-blocking)
  orderEvents.emit("order:created", {
    order: order_mst,
    dealer,
    customer,
    vehicle,
    notifUserIds,
    amount: finalAmount,
  });

  return order_mst;
};

exports.processOrder = async ({ body }) => {
  // ... process order, generate OTP ...

  orderEvents.emit("order:processing", {
    order,
    driver,
    vehicle,
    otpValue,
  });

  return order;
};
```

**Impact:**

- API response no longer blocked by notifications
- Easy to add new side effects (analytics, webhooks) without modifying core logic
- Each listener can fail independently without affecting the main flow

---

## Architecture After All Phases

```
                    ┌─────────────────────────┐
                    │    React Native App      │
                    │    RTK Query + Cache      │
                    │    Secure Storage         │
                    │    Offline Queue          │
                    └───────────┬──────────────┘
                                │
                    ┌───────────▼──────────────┐
                    │       Nginx (LB)         │
                    │   Rate Limit + SSL       │
                    └───────────┬──────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                   │
    ┌─────────▼───┐   ┌────────▼───┐    ┌─────────▼───┐
    │  API (PM2)  │   │  API (PM2) │    │  API (PM2)  │
    │  Instance 1 │   │  Instance 2│    │  Instance 3 │
    └──────┬──────┘   └─────┬──────┘    └──────┬──────┘
           │                │                   │
    ┌──────▼────────────────▼───────────────────▼──────┐
    │                    Redis                          │
    │  User Cache │ Product Cache │ Rate Limits │ Queue │
    └──────────────────────┬───────────────────────────┘
           │               │                    │
    ┌──────▼──────┐ ┌──────▼──────┐   ┌────────▼───────┐
    │   MongoDB   │ │   Workers   │   │   WebSocket    │
    │   Atlas     │ │  SMS/Email  │   │  (Socket.io)   │
    │  (Primary)  │ │  Push Notif │   │  Redis Adapter │
    └─────────────┘ └─────────────┘   └────────────────┘
```

---

## Verification

1. **PM2 cluster:** `pm2 list` shows N instances; `pm2 reload` completes with zero downtime
2. **Connection pool:** `db.serverStatus().connections` stays under 70% of Atlas limit
3. **Queue processing:** BullMQ dashboard shows jobs processed, retry counts, failure rates
4. **WebSocket:** Connect from app; verify real-time updates on order status change
5. **Events:** Create order; verify notification sent asynchronously via event listener
6. **Load test:** k6 at 200 RPS with PM2 cluster; verify p95 < 50ms
