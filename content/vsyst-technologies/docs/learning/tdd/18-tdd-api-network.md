# 18. API and network tests

Two distinct jobs that get muddled together:

- **API contract tests** — _is the shape right, and do the server and its three clients agree on it?_
- **Network tests** — _what happens when the network misbehaves?_ Timeouts, 500s, retries, offline, cancellation.

The first stops your clients breaking when the API changes. The second stops your app hanging, double-charging or crashing on a train. Almost nobody writes the second kind until an incident forces them to, and they're the easiest tests in this whole document to write.

---

## Contract-first

The rename problem from [14](14-large-project-strategy.md#cross-boundary-drift-the-failure-mode-unique-to-this-size): the API renames a field, every suite stays green, the React Native app breaks in production. It happens because the server's tests and each client's mocks are **independent statements of the same belief**.

Fix: one schema, imported by both sides.

```js
// packages/contracts/order.js
import { z } from "zod"

export const OrderDto = z.object({
  id: z.string().regex(/^[a-f0-9]{24}$/),
  ref: z.string(),
  status: z.enum(["pending", "confirmed", "shipped", "cancelled"]),
  totalCents: z.number().int().nonnegative(),
  createdAt: z.string().datetime(),
})

export const OrderListResponse = z.object({
  items: z.array(OrderDto),
  nextCursor: z.string().nullable(),
})

export const CreateOrderRequest = z.object({
  items: z.array(z.object({ sku: z.string(), qty: z.number().int().positive() })).min(1),
})

export const ErrorResponse = z.object({
  error: z.object({
    code: z.string(),
    message: z.string(),
    fields: z.record(z.string()).optional(),
  }),
})
```

### The server proves it produces the shape

```js
// orders.api.test.js  (T2)
it("GET /orders returns the documented shape", async () => {
  await seedOrders(3)
  const res = await asUser(request(app).get("/orders?limit=2"))

  expect(res.status).toBe(200)
  expect(() => OrderListResponse.parse(res.body)).not.toThrow()
})
```

Do this on **every** endpoint. It's one line, and it's the line that fails the moment someone changes a field name, loosens a type, or forgets to serialise a date.

Assert the errors too — the error envelope is as much a contract as the success body, and it's the one clients handle worst:

```js
it.each([
  ["bad body", {}, 400, "VALIDATION"],
  ["unknown sku", { items: [{ sku: "NOPE", qty: 1 }] }, 404, "SKU_NOT_FOUND"],
])("%s → %i %s", async (_, body, status, code) => {
  const res = await asUser(request(app).post("/orders").send(body))
  expect(res.status).toBe(status)
  expect(ErrorResponse.parse(res.body).error.code).toBe(code)
})
```

### The clients build their mocks from the same schema

```js
// test-support/msw/handlers.js
import { http, HttpResponse } from "msw"
import { OrderListResponse, OrderDto } from "@app/contracts"

export const anOrderDto = (o = {}) =>
  OrderDto.parse({
    id: "64b7f00000000000000000a1",
    ref: "A-100",
    status: "confirmed",
    totalCents: 897,
    createdAt: "2026-01-15T12:00:00.000Z",
    ...o,
  }) // ← parse, so an invalid fixture fails loudly at build time

export const handlers = [
  http.get("*/api/orders", () =>
    HttpResponse.json(OrderListResponse.parse({ items: [anOrderDto()], nextCursor: null })),
  ),
]
```

```js
// test-support/msw/server.js  (node + jsdom)   |   server.native.js uses setupServer too
import { setupServer } from "msw/node"
export const server = setupServer(...handlers)
```

Now the fixture cannot drift: `OrderDto.parse` throws in every client's test run the moment the schema changes. Rename `totalCents` and you get a red API test _and_ red web tests _and_ red React Native tests, at commit time, from one change.

> **Also worth doing:** have the API validate its own outgoing responses against the schema in non-production builds. A contract you only check in tests is a contract you'll eventually violate at runtime.

**Existing OpenAPI spec?** Same discipline: generate client types and MSW handlers from the spec, and assert responses against it in T2. The mechanism differs, the rule doesn't — _one artefact, both sides_.

---

## Test-driving an endpoint from its contract

The workflow, with the schema as the starting point:

1. **Write the schema** for the new endpoint. This is the design conversation, and it takes ten minutes.
2. **Write the T2 test** with a concrete request and expected response. Red — the route doesn't exist.
3. **Add the handler to `handlers.js`** so clients can start building against it immediately, in parallel.
4. **Drive the implementation** inward at T0 ([15](15-tdd-node-backend.md)).
5. **The T2 test goes green**, and the client work built against the mock now works against the real thing.

Step 3 is where the payoff is at team scale: the frontend isn't blocked on the backend, and when they meet, they meet on a schema both sides have been tested against.

---

## Network tests

Everything above assumes the request completes. These are the tests for when it doesn't.

Put every request through **one client wrapper** and test that wrapper hard. Then no feature code has to think about any of this.

```js
// packages/api-client/http.js
export function createHttpClient({ baseUrl, fetch = globalThis.fetch, timeoutMs = 5000,
                                   retries = 2, backoff = (n) => 2 ** n * 100, sleep, clock }) {
  return async function req(path, { method = 'GET', body, signal, idempotencyKey } = {}) {
    for (let attempt = 0; ; attempt++) {
      const controller = new AbortController()
      const onAbort = () => controller.abort(signal.reason)
      signal?.addEventListener('abort', onAbort, { once: true })
      const timer = setTimeout(() => controller.abort(new TimeoutError(path)), timeoutMs)
      try {
        const res = await fetch(`${baseUrl}${path}`, { method, body, signal: controller.signal, headers: {...} })
        if (res.status >= 500 && attempt < retries) { await sleep(backoff(attempt)); continue }
        return await toResult(res)
      } catch (err) {
        if (isRetryable(err) && attempt < retries) { await sleep(backoff(attempt)); continue }
        throw err
      } finally {
        clearTimeout(timer)
        signal?.removeEventListener('abort', onAbort)
      }
    }
  }
}
```

`fetch`, `sleep` and `clock` are injected — which is what makes all of the following tests instant and deterministic.

### Timeout

```js
it("aborts a request that exceeds the timeout", async () => {
  server.use(
    http.get("*/slow", async () => {
      await delay("infinite")
    }),
  )
  const client = createHttpClient({ baseUrl, timeoutMs: 50, retries: 0, sleep: noSleep })

  await expect(client("/slow")).rejects.toThrow(TimeoutError)
})
```

Then assert the thing that actually matters for correctness: **the socket was released**. A "timeout" that leaves the request running will still fire your `.then()` handler later and update state on a screen the user left.

### Retry, and — more importantly — not retrying

```js
it("retries a 503 and succeeds", async () => {
  let calls = 0
  server.use(
    http.get("*/orders", () => {
      calls++
      return calls === 1
        ? new HttpResponse(null, { status: 503 })
        : HttpResponse.json({ items: [], nextCursor: null })
    }),
  )

  await expect(client("/orders")).resolves.toMatchObject({ items: [] })
  expect(calls).toBe(2)
})

it("does NOT retry a 400", async () => {
  let calls = 0
  server.use(
    http.get("*/orders", () => {
      calls++
      return new HttpResponse(null, { status: 400 })
    }),
  )

  await expect(client("/orders")).rejects.toThrow(BadRequest)
  expect(calls).toBe(1) // retrying a client error is a bug
})

it("does NOT retry a non-idempotent POST without an idempotency key", async () => {
  let calls = 0
  server.use(
    http.post("*/orders", () => {
      calls++
      return new HttpResponse(null, { status: 500 })
    }),
  )

  await expect(client("/orders", { method: "POST", body })).rejects.toThrow()
  expect(calls).toBe(1) // ← the test that prevents double-charging
})
```

That last one is the highest-value network test in this document. Blanket retry-on-5xx plus a POST is how a payment gets taken twice, and the failure only shows up under load.

### Backoff without waiting

```js
it("backs off exponentially", async () => {
  const waits = []
  const client = createHttpClient({
    baseUrl,
    retries: 3,
    sleep: async (ms) => {
      waits.push(ms)
    },
  })
  server.use(http.get("*/orders", () => new HttpResponse(null, { status: 500 })))

  await expect(client("/orders")).rejects.toThrow()
  expect(waits).toEqual([100, 200, 400])
})
```

Injecting `sleep` means the test is instant. If you must use real timers, `vi.advanceTimersByTimeAsync` — the sync `advanceTimersByTime` won't let pending promises settle.

### Cancellation

```js
it("rejects with the caller's abort reason", async () => {
  server.use(
    http.get("*/orders", async () => {
      await delay(1000)
    }),
  )
  const ac = new AbortController()
  const promise = client("/orders", { signal: ac.signal })

  ac.abort(new Error("user navigated away"))
  await expect(promise).rejects.toThrow("user navigated away")
})
```

And at the component level, the test that catches the "setState after unmount" class of bug: start a request, unmount, resolve the request, assert nothing threw and nothing rendered.

### Race conditions — the one that ships

```js
it("ignores a stale response that arrives after a newer one", async () => {
  server.use(
    http.get("*/search", async ({ request }) => {
      const q = new URL(request.url).searchParams.get("q")
      await delay(q === "ab" ? 200 : 10) // the older request is slower
      return HttpResponse.json({ items: [q] })
    }),
  )
  render(<Search />)

  await userEvent.type(screen.getByRole("searchbox"), "ab")
  await userEvent.type(screen.getByRole("searchbox"), "c")

  await waitFor(() => expect(screen.getByRole("list")).toHaveTextContent("abc"))
  await delay(300)
  expect(screen.getByRole("list")).toHaveTextContent("abc") // not 'ab'
})
```

Type-ahead showing results for a query the user already changed. Nearly every search box has this bug, and it's essentially invisible on a fast connection — which is why you assert it with a controlled delay rather than hoping.

### Offline and error surfaces

```js
it("shows an offline message rather than a generic error", async () => {
  server.use(http.get("*/orders", () => HttpResponse.error())) // network-level failure
  render(<OrderPage />)

  expect(await screen.findByRole("alert")).toHaveTextContent(/check your connection/i)
})
```

`HttpResponse.error()` is a transport failure, not an HTTP error response — different code path, different message, and the one most apps get wrong.

### The network test checklist

Per client wrapper, once:

- [ ] Timeout fires, and the request is actually aborted
- [ ] 5xx retries; 4xx does not
- [ ] Non-idempotent methods don't retry without an idempotency key
- [ ] Backoff delays are what you think they are
- [ ] Caller-side cancellation propagates
- [ ] Transport failure (offline) is distinguishable from an HTTP error
- [ ] Malformed JSON / empty body / wrong content-type doesn't throw an unhandled error
- [ ] 401 triggers exactly one token refresh, even with five requests in flight
- [ ] Rate-limit `429` honours `Retry-After`
- [ ] Stale responses are discarded, not rendered

Per screen: loading, empty, error, retry ([17](17-tdd-frontend-web.md#the-four-states--the-checklist-for-every-data-driven-component)).

---

## Third-party APIs

You don't own them, so the strategy is different.

**In the fast tiers:** never call them. Wrap each in an adapter with a narrow interface, fake the adapter, and test _your_ code against the fake. Test the adapter itself against MSW handlers built from **recorded real responses** — copy an actual response body into a fixture file rather than inventing one, because the shape you imagine is never quite the shape they send.

**Nightly, non-gating (T5):** a canary that makes one real call per third party and asserts the response still parses against your schema.

```js
// tagged so it never runs in the PR suite
it.skipIf(!process.env.CANARY)("stripe still returns the shape we expect", async () => {
  const res = await stripe.paymentIntents.retrieve(KNOWN_TEST_ID)
  expect(() => PaymentIntentShape.parse(res)).not.toThrow()
})
```

When a provider changes something, this tells you at 3am with a clear message instead of at 3pm via a customer. Keep it out of the gating suite — a third party's outage must never block your deploys.

---

## Sockets and streams

WebSocket and SSE code is testable, on the same principle: the transport is a port.

1. **The message handling is a pure reducer.** `(state, message) => state`. Test every message type, out-of-order delivery, and duplicates at T0, with no socket anywhere.
2. **The connection lifecycle is an adapter** — a fake with `emit(message)`, `dropConnection()`, `open()`. Test reconnect-with-backoff, resubscribe-on-reconnect, and message buffering while disconnected against the fake.
3. **One integration test** against a real socket server proves the wiring.

The bugs in realtime code are almost always in category 1 and 2 — reconnect storms, lost subscriptions, duplicate messages after a reconnect — and none of them need a real socket to reproduce.

---

## 🛠 Mini-project — the resilient client

_One day._

1. Move every `fetch` call in one app behind a single `createHttpClient`, with `fetch`, `sleep` and `clock` injected.
2. Work down the checklist above, test-first. Expect at least two real bugs — the usual suspects are POST retries and unhandled transport failures.
3. Move one endpoint's response shape into `packages/contracts`, assert it in the API's T2 test, and build that endpoint's MSW handler by parsing through the schema.
4. Prove the loop closes: rename a field in the schema and confirm you get red tests in the API **and** in both clients, without touching them.
5. Add the stale-response test to your busiest search or filter screen.
6. Add one nightly canary per third-party dependency, non-gating.

**Deliverable:** one HTTP client with a checklist of network-failure tests, and one endpoint whose shape is enforced from a single source on all sides.

**Proves:** the two classes of cross-boundary bug that survive every other kind of testing — silent contract drift and bad behaviour under a bad network — are both cheap to catch once, and expensive to catch in production.

---

Next: [19. React Native →](19-tdd-react-native.md) · Related: [15. Node backend](15-tdd-node-backend.md) · [17. Frontend](17-tdd-frontend-web.md)
