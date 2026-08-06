# 15. TDD for a Node backend

Test-driving an Express API, outside-in, without a database in the fast tier.

**Stack:** Node 20+, Express, Vitest, supertest. Mongo is covered separately in [16](16-tdd-mongodb-mongoose.md) — deliberately, because most of your backend tests shouldn't touch it.

---

## Setup

```bash
npm i -D vitest supertest
```

```js
// vitest.config.js
export default {
  test: {
    projects: [
      { test: { name: "t0", include: ["packages/domain/**/*.test.js"] } },
      {
        test: {
          name: "t1",
          include: ["packages/api/**/*.int.test.js"],
          setupFiles: ["./test/setup-db.js"],
          fileParallelism: true,
        },
      },
      {
        test: {
          name: "t2",
          include: ["packages/api/**/*.api.test.js"],
          setupFiles: ["./test/setup-db.js"],
        },
      },
    ],
  },
}
```

```json
{
  "scripts": {
    "test:t0": "vitest --project t0",
    "test:t2": "vitest run --project t2"
  }
}
```

Three separate suites you can run independently is the point — `test:t0` is what you leave in watch mode all day.

---

## The app factory — the single most important line of setup

**Never call `app.listen()` in a module a test imports.** Split the app from the server:

```js
// src/app.js
import express from "express"

export function createApp(deps) {
  // deps injected, not imported
  const app = express()
  app.use(express.json())
  app.use("/orders", ordersRouter(deps))
  app.use(errorHandler)
  return app
}
```

```js
// src/server.js — the only file that binds a port. Never imported by a test.
import { createApp } from "./app.js"
import { buildProductionDeps } from "./composition-root.js"

createApp(await buildProductionDeps()).listen(process.env.PORT)
```

supertest starts an ephemeral server per test for you, so tests never fight over ports and run in parallel safely:

```js
const res = await request(createApp(deps)).get("/orders/42")
```

`deps` is the seam that makes every test in this doc possible. It's how a test swaps the real Mongo repository for an in-memory one, or the real Stripe client for a fake — without any module mocking.

---

## Outside-in: driving one endpoint

The ticket: _"POST /orders creates an order, reserving stock; if stock is short it fails and reserves nothing."_

### Step 1 — 🔴 The acceptance test, at the HTTP edge

Write the request and response you _wish_ existed. This designs the API before any code does.

```js
// orders.api.test.js
import request from "supertest"
import { createApp } from "../src/app.js"
import { buildTestDeps } from "../../test-support/deps.js"
import { aProduct } from "../../test-support/builders/product.js"

it("creates an order and reserves stock", async () => {
  const deps = buildTestDeps()
  await deps.products.save(aProduct({ sku: "PEN-1", stock: 10 }))

  const res = await request(createApp(deps))
    .post("/orders")
    .set("Authorization", `Bearer ${deps.tokenFor("ada")}`)
    .send({ items: [{ sku: "PEN-1", qty: 3 }] })

  expect(res.status).toBe(201)
  expect(res.body).toMatchObject({ status: "confirmed", totalCents: 897 })
  expect(res.headers.location).toMatch(/^\/orders\/[a-f0-9]{24}$/)
  expect((await deps.products.bySku("PEN-1")).stock).toBe(7)
})
```

Leave it red. It's the definition of done, not a lap ([11, Phase 5](11-tutorial-first-feature.md#phase-5--outside-in)).

### Step 2 — Drive inward at T0, in seconds

The interesting logic is pricing and the stock rule. Neither needs Express or Mongo:

```js
// packages/domain/order.test.js
import { placeOrder } from "./order.js"

it("rejects the whole order when any line is short", () => {
  const stock = { "PEN-1": 10, "PAD-2": 1 }
  const result = placeOrder(
    {
      items: [
        { sku: "PEN-1", qty: 3 },
        { sku: "PAD-2", qty: 5 },
      ],
    },
    { stock, prices: { "PEN-1": 299, "PAD-2": 500 } },
  )

  expect(result).toEqual({
    ok: false,
    error: { code: "INSUFFICIENT_STOCK", sku: "PAD-2", available: 1 },
  })
})
```

`placeOrder` is a pure function: state in, decision out. It reserves nothing and writes nothing. Every pricing rule, discount, tax band and partial-fulfilment case gets tested here at ~0.2 ms each.

### Step 3 — The use case wires ports together

```js
// packages/api/src/use-cases/place-order.js
export function placeOrderUseCase({ products, orders, clock, events }) {
  return async (command) => {
    const stock = await products.stockFor(command.items.map((i) => i.sku))
    const decision = placeOrder(command, stock) // ← the pure bit
    if (!decision.ok) return decision

    const order = await orders.create({ ...decision.order, createdAt: clock.now() })
    await products.reserve(decision.reservations)
    await events.publish("order.confirmed", { orderId: order.id })
    return { ok: true, order }
  }
}
```

Test it at T0 with in-memory ports — no DB, no HTTP:

```js
it("publishes order.confirmed exactly once", async () => {
  const deps = buildTestDeps() // in-memory everything
  await deps.products.save(aProduct({ sku: "PEN-1", stock: 10 }))

  await placeOrderUseCase(deps)({ items: [{ sku: "PEN-1", qty: 1 }] })

  expect(deps.events.published).toEqual([
    { topic: "order.confirmed", payload: { orderId: expect.any(String) } },
  ])
})
```

And assert the absence on the failure path — the test people forget:

```js
it("reserves nothing and publishes nothing when stock is short", async () => {
  const deps = buildTestDeps()
  await deps.products.save(aProduct({ sku: "PEN-1", stock: 1 }))

  const result = await placeOrderUseCase(deps)({ items: [{ sku: "PEN-1", qty: 5 }] })

  expect(result.ok).toBe(false)
  expect(deps.events.published).toEqual([])
  expect((await deps.products.bySku("PEN-1")).stock).toBe(1)
})
```

### Step 4 — The HTTP layer stays thin

```js
// routes/orders.js
router.post("/", async (req, res, next) => {
  const parsed = CreateOrderRequest.safeParse(req.body) // shared schema
  if (!parsed.success) return next(new BadRequest(parsed.error))

  const result = await deps.placeOrder({ ...parsed.data, userId: req.user.id })
  if (!result.ok) return next(toHttpError(result.error))

  res.status(201).location(`/orders/${result.order.id}`).json(present(result.order))
})
```

Parse, delegate, map, respond. If there's an `if` in here about business rules, it's in the wrong layer — and you'll notice because testing it required booting Express.

### Step 5 — Watch the acceptance test go green

It flips on its own. You never touched it to make it pass.

---

## What to test at T2 (and what not to)

T2 is expensive. It should cover things that **only exist at the HTTP boundary**:

```js
describe("POST /orders — contract", () => {
  it.each([
    ["missing items", {}, 400, "VALIDATION"],
    ["empty items", { items: [] }, 400, "VALIDATION"],
    ["unknown sku", { items: [{ sku: "X", qty: 1 }] }, 404, "SKU_NOT_FOUND"],
    ["short stock", { items: [{ sku: "PEN-1", qty: 99 }] }, 409, "INSUFFICIENT_STOCK"],
  ])("%s → %i", async (_, body, status, code) => {
    const res = await request(app).post("/orders").set(auth).send(body)
    expect(res.status).toBe(status)
    expect(res.body.error.code).toBe(code)
  })
})
```

One table covers your whole error contract. Note it asserts on the **error envelope**, which three clients depend on — that's a contract, not an implementation detail.

Also T2-only, and worth the cost:

- **Auth matrix** — anonymous, wrong user, right user, admin, expired token. One `it.each` per protected route.
- **Response shape parses against the shared schema** — see [18](18-tdd-api-network.md#contract-first).
- **Pagination** — `?limit`, `?cursor`, stable ordering across pages, the last page's cursor.
- **Content negotiation and large payloads** if you care about them.

**Don't** put pricing edge cases, tax rules or discount stacking here. Fifty T2 tests for rules that belong in T0 is how a suite gets to eight minutes.

---

## Auth in tests

Don't log in over HTTP in every test — it's slow and it couples every test to the login flow.

```js
// test-support/deps.js
export const tokenFor = (userId, claims = {}) =>
  jwt.sign({ sub: userId, ...claims }, TEST_SECRET, { expiresIn: "1h" })

export const asUser = (req, userId = "ada", claims) =>
  req.set("Authorization", `Bearer ${tokenFor(userId, claims)}`)
```

```js
await asUser(request(app).get("/orders"), "admin-1", { role: "admin" })
```

Then test the **login flow itself** properly, once, in its own file: wrong password, locked account, expired token, refresh rotation, and the token actually being rejected after logout.

---

## Async work: queues, jobs, webhooks

Background work is where "wait a bit and hope" tests breed. Two rules.

**1. The handler is a function. Test it directly.**

```js
it("marks the order shipped when the carrier webhook arrives", async () => {
  const deps = buildTestDeps()
  const order = await deps.orders.create(anOrder({ status: "confirmed" }))

  await handleCarrierWebhook(deps)({ type: "shipment.dispatched", orderId: order.id })

  expect((await deps.orders.byId(order.id)).status).toBe("shipped")
})
```

No queue, no broker, no polling. The queue's job is delivery; you don't need to test that.

**2. The queue adapter gets a fake with a `drain()`.**

```js
class FakeQueue {
  jobs = []
  enqueue(name, payload) {
    this.jobs.push({ name, payload })
  }
  async drain(handlers) {
    while (this.jobs.length) {
      const job = this.jobs.shift()
      await handlers[job.name](job.payload)
    }
  }
}
```

Now a test can assert _"placing an order enqueues exactly one `send-receipt` job"_, and separately _"draining it sends the email"_ — both instantly, both deterministic.

**Retries and idempotency deserve their own tests**, because they're where the real bugs are:

```js
it("is idempotent — the same webhook twice ships once", async () => {
  const evt = { id: "evt_1", type: "shipment.dispatched", orderId: order.id }
  await handleCarrierWebhook(deps)(evt)
  await handleCarrierWebhook(deps)(evt)

  expect(deps.events.published.filter((e) => e.topic === "order.shipped")).toHaveLength(1)
})
```

---

## Time, randomness, IDs

Three uncontrollable dependencies, one move — inject them.

```js
export const fixedClock = (iso = "2026-01-15T12:00:00Z") => ({
  now: () => new Date(iso),
})
```

For code you can't inject into (a library calling `Date.now()` internally), use fake timers, and prefer the async advance helpers so pending promises actually resolve:

```js
vi.useFakeTimers({ now: new Date("2026-01-15T12:00:00Z") })
await vi.advanceTimersByTimeAsync(30_000) // not advanceTimersByTime
vi.useRealTimers()
```

For IDs, inject a seeded generator so assertions can name the value: `ids: seq('order')` → `order-1`, `order-2`.

---

## Things people over-test at this layer

| Don't test                                          | Why                                                                  | Test instead                                                        |
| --------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------- |
| That Express routes to your handler                 | It's framework behaviour                                             | The endpoint's response, once, at T2                                |
| Every middleware in isolation with mock `req`/`res` | The mocks encode your assumptions, not Express's                     | One T2 test that hits a route through the real stack                |
| Getters, DTO mapping, `present()` field-by-field    | Nothing can break independently                                      | The response shape against the shared schema                        |
| Log lines                                           | They change constantly, break tests, and nobody reads the assertions | Structured events, _if_ something depends on them                   |
| Mongoose behaviour                                  | It's a tested library                                                | Your queries, against real Mongo — [16](16-tdd-mongodb-mongoose.md) |

---

## 🛠 Mini-project — one endpoint, all the way down

_Half a day._

1. Pick an endpoint with a real rule in it — not CRUD.
2. Write the supertest acceptance test first. Leave it red.
3. Extract the rule into `packages/domain` and test-drive it there, ≥ 6 cases, all T0.
4. Build the use case against in-memory ports; include one _absence_ test on the failure path.
5. Thin the route to parse → delegate → map → respond.
6. Add the T2 error-contract table and the auth matrix.
7. Time each tier. T0 should be under a second.

**Deliverable:** an endpoint whose business rules run without Express or Mongo, plus a T2 table covering its whole HTTP contract.

**Proves:** the shape from [14](14-large-project-strategy.md) works on real code — and that most of what you thought needed a running server didn't.

---

Next: [16. MongoDB & Mongoose →](16-tdd-mongodb-mongoose.md) · Related: [14. Large-project strategy](14-large-project-strategy.md) · [18. API & network tests](18-tdd-api-network.md)
