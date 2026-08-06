# 15. Node backend के लिए TDD

एक Express API को outside-in test-drive करना, बिना तेज़ परत में database लाए।

**Stack:** Node 20+, Express, Vitest, supertest। Mongo को अलग से [16](16-tdd-mongodb-mongoose.md) में लिया गया है — जान-बूझकर, क्योंकि आपके ज़्यादातर backend टेस्टों को उसे छूना ही नहीं चाहिए।

---

## सेटअप

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

तीन अलग suites जिन्हें आप स्वतंत्र रूप से चला सकें — यही मक़सद है। `test:t0` वही है जिसे आप दिन भर watch mode में छोड़ देते हैं।

---

## App factory — सेटअप की सबसे अहम एक लाइन

**जिस module को कोई टेस्ट import करता है, उसमें `app.listen()` कभी मत बुलाइए।** App को server से अलग कीजिए:

```js
// src/app.js
import express from "express"

export function createApp(deps) {
  // deps inject होती हैं, import नहीं
  const app = express()
  app.use(express.json())
  app.use("/orders", ordersRouter(deps))
  app.use(errorHandler)
  return app
}
```

```js
// src/server.js — इकलौती फ़ाइल जो port से जुड़ती है। कोई टेस्ट इसे import नहीं करता।
import { createApp } from "./app.js"
import { buildProductionDeps } from "./composition-root.js"

createApp(await buildProductionDeps()).listen(process.env.PORT)
```

supertest आपके लिए हर टेस्ट पर एक क्षणिक server चालू कर देता है, इसलिए टेस्ट कभी ports के लिए नहीं झगड़ते और सुरक्षित रूप से समानांतर चलते हैं:

```js
const res = await request(createApp(deps)).get("/orders/42")
```

`deps` ही वह seam है जो इस दस्तावेज़ के हर टेस्ट को मुमकिन बनाता है। इसी से कोई टेस्ट असली Mongo repository की जगह in-memory वाला, या असली Stripe client की जगह fake रख देता है — बिना किसी module mocking के।

---

## Outside-in: एक endpoint चलाना

Ticket: _"POST /orders एक order बनाता है और stock आरक्षित करता है; stock कम हो तो यह फेल हो और कुछ भी आरक्षित न करे।"_

### Step 1 — 🔴 HTTP किनारे पर acceptance test

वह request और response लिखिए जो आप _चाहते_ हैं कि मौजूद हो। यह किसी भी कोड से पहले API डिज़ाइन कर देता है।

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

इसे लाल रहने दीजिए। यह "पूरा हुआ" की परिभाषा है, कोई फेरा नहीं ([11, चरण 5](11-tutorial-first-feature.md))।

### Step 2 — T0 पर भीतर की ओर बढ़िए, सेकंडों में

दिलचस्प logic है pricing और stock का नियम। दोनों को न Express चाहिए, न Mongo:

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

`placeOrder` एक शुद्ध function है: state अंदर, फ़ैसला बाहर। यह न कुछ आरक्षित करता है, न कुछ लिखता है। हर pricing नियम, discount, tax band और आंशिक-पूर्ति का मामला यहीं ~0.2 ms में टेस्ट होता है।

### Step 3 — Use case ports को आपस में जोड़ता है

```js
// packages/api/src/use-cases/place-order.js
export function placeOrderUseCase({ products, orders, clock, events }) {
  return async (command) => {
    const stock = await products.stockFor(command.items.map((i) => i.sku))
    const decision = placeOrder(command, stock) // ← शुद्ध हिस्सा
    if (!decision.ok) return decision

    const order = await orders.create({ ...decision.order, createdAt: clock.now() })
    await products.reserve(decision.reservations)
    await events.publish("order.confirmed", { orderId: order.id })
    return { ok: true, order }
  }
}
```

इसे T0 पर in-memory ports के साथ टेस्ट कीजिए — न DB, न HTTP:

```js
it("publishes order.confirmed exactly once", async () => {
  const deps = buildTestDeps() // सब कुछ in-memory
  await deps.products.save(aProduct({ sku: "PEN-1", stock: 10 }))

  await placeOrderUseCase(deps)({ items: [{ sku: "PEN-1", qty: 1 }] })

  expect(deps.events.published).toEqual([
    { topic: "order.confirmed", payload: { orderId: expect.any(String) } },
  ])
})
```

और असफलता वाले रास्ते पर अनुपस्थिति की जाँच कीजिए — वही टेस्ट जो लोग भूल जाते हैं:

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

### Step 4 — HTTP परत पतली रहे

```js
// routes/orders.js
router.post("/", async (req, res, next) => {
  const parsed = CreateOrderRequest.safeParse(req.body) // साझा schema
  if (!parsed.success) return next(new BadRequest(parsed.error))

  const result = await deps.placeOrder({ ...parsed.data, userId: req.user.id })
  if (!result.ok) return next(toHttpError(result.error))

  res.status(201).location(`/orders/${result.order.id}`).json(present(result.order))
})
```

Parse, सौंपो, map, जवाब दो। अगर यहाँ business नियमों वाला कोई `if` है, तो वह ग़लत परत में है — और आपको पता चल जाएगा, क्योंकि उसे टेस्ट करने के लिए Express चालू करना पड़ा।

### Step 5 — Acceptance test को हरा होते देखिए

यह अपने आप पलट जाता है। आपने उसे पास कराने के लिए कभी छुआ नहीं।

---

## T2 पर क्या टेस्ट करें (और क्या नहीं)

T2 महँगा है। इसमें वही चीज़ें आनी चाहिए जो **सिर्फ़ HTTP सीमा पर मौजूद हैं**:

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

एक तालिका आपके पूरे error contract को ढक लेती है। ध्यान दीजिए कि यह **error envelope** पर assert करती है, जिस पर तीन clients निर्भर हैं — यह contract है, implementation की बारीकी नहीं।

ये भी सिर्फ़ T2 पर, और लागत के लायक़:

- **Auth matrix** — anonymous, ग़लत user, सही user, admin, expired token। हर सुरक्षित route पर एक `it.each`।
- **Response का आकार साझा schema से parse हो** — देखिए [18](18-tdd-api-network.md)।
- **Pagination** — `?limit`, `?cursor`, पन्नों के बीच स्थिर क्रम, आख़िरी पन्ने का cursor।
- **Content negotiation और बड़े payloads**, अगर वे आपके लिए मायने रखते हैं।

Pricing के किनारे के मामले, tax नियम या discount का ढेर यहाँ **मत** डालिए। T0 में जाने वाले नियमों के लिए पचास T2 टेस्ट — suite के आठ मिनट तक पहुँचने का यही रास्ता है।

---

## टेस्टों में Auth

हर टेस्ट में HTTP के ज़रिए लॉग इन मत कीजिए — यह धीमा है और हर टेस्ट को login flow से बाँध देता है।

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

फिर **ख़ुद login flow** को एक बार, ढंग से, अपनी अलग फ़ाइल में टेस्ट कीजिए: ग़लत पासवर्ड, बंद account, expired token, refresh rotation, और logout के बाद token का सचमुच ठुकराया जाना।

---

## Async काम: queues, jobs, webhooks

पृष्ठभूमि का काम वहीं है जहाँ "थोड़ा रुको और उम्मीद करो" वाले टेस्ट पनपते हैं। दो नियम।

**1. Handler एक function है। उसे सीधे टेस्ट कीजिए।**

```js
it("marks the order shipped when the carrier webhook arrives", async () => {
  const deps = buildTestDeps()
  const order = await deps.orders.create(anOrder({ status: "confirmed" }))

  await handleCarrierWebhook(deps)({ type: "shipment.dispatched", orderId: order.id })

  expect((await deps.orders.byId(order.id)).status).toBe("shipped")
})
```

न queue, न broker, न polling। Queue का काम पहुँचाना है; उसे टेस्ट करने की ज़रूरत आपको नहीं।

**2. Queue adapter को `drain()` वाला fake दीजिए।**

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

अब कोई टेस्ट assert कर सकता है कि _"order देने पर ठीक एक `send-receipt` job क़तार में लगती है"_, और अलग से कि _"उसे drain करने पर ईमेल जाता है"_ — दोनों तुरंत, दोनों deterministic।

**Retries और idempotency के अपने टेस्ट होने चाहिए**, क्योंकि असली बग वहीं होते हैं:

```js
it("is idempotent — the same webhook twice ships once", async () => {
  const evt = { id: "evt_1", type: "shipment.dispatched", orderId: order.id }
  await handleCarrierWebhook(deps)(evt)
  await handleCarrierWebhook(deps)(evt)

  expect(deps.events.published.filter((e) => e.topic === "order.shipped")).toHaveLength(1)
})
```

---

## समय, randomness, IDs

तीन बेक़ाबू dependencies, एक ही चाल — उन्हें inject कीजिए।

```js
export const fixedClock = (iso = "2026-01-15T12:00:00Z") => ({
  now: () => new Date(iso),
})
```

जिस कोड में आप inject नहीं कर सकते (कोई library जो अंदर ही `Date.now()` बुलाती है), वहाँ fake timers इस्तेमाल कीजिए, और async advance helpers को प्राथमिकता दीजिए ताकि लंबित promises सचमुच पूरे हों:

```js
vi.useFakeTimers({ now: new Date("2026-01-15T12:00:00Z") })
await vi.advanceTimersByTimeAsync(30_000) // advanceTimersByTime नहीं
vi.useRealTimers()
```

IDs के लिए seed किया हुआ generator inject कीजिए ताकि assertions में मान का नाम लिया जा सके: `ids: seq('order')` → `order-1`, `order-2`।

---

## इस परत पर लोग किन चीज़ों का हद से ज़्यादा टेस्ट करते हैं

| यह मत टेस्ट कीजिए                                | क्यों                                                               | इसके बजाय क्या                                                         |
| ------------------------------------------------ | ------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| कि Express आपके handler तक route करता है         | यह framework का व्यवहार है                                          | Endpoint का response, एक बार, T2 पर                                    |
| हर middleware को अलग से mock `req`/`res` के साथ  | Mocks आपकी धारणाएँ दर्ज करते हैं, Express का व्यवहार नहीं           | एक T2 टेस्ट जो असली stack से होकर किसी route तक जाए                    |
| Getters, DTO mapping, `present()` की एक-एक field | कुछ भी स्वतंत्र रूप से टूट नहीं सकता                                | Response का आकार, साझा schema के मुक़ाबले                              |
| Log की पंक्तियाँ                                 | ये लगातार बदलती हैं, टेस्ट तोड़ती हैं, और assertions कोई नहीं पढ़ता | संरचित events, _अगर_ किसी की उन पर निर्भरता है                         |
| Mongoose का व्यवहार                              | यह पहले से टेस्ट की गई library है                                   | आपकी queries, असली Mongo के ख़िलाफ़ — [16](16-tdd-mongodb-mongoose.md) |

---

## 🛠 मिनी-प्रोजेक्ट — एक endpoint, नीचे तक

_आधा दिन।_

1. ऐसा endpoint चुनिए जिसमें असली नियम हो — CRUD नहीं।
2. पहले supertest acceptance test लिखिए। उसे लाल छोड़ दीजिए।
3. नियम को `packages/domain` में निकालिए और वहीं test-drive कीजिए, ≥ 6 मामले, सब T0।
4. In-memory ports के साथ use case बनाइए; असफलता वाले रास्ते पर एक _अनुपस्थिति_ टेस्ट भी रखिए।
5. Route को पतला कीजिए: parse → सौंपो → map → जवाब दो।
6. T2 की error-contract तालिका और auth matrix जोड़िए।
7. हर परत का समय नापिए। T0 एक सेकंड से कम होना चाहिए।

**नतीजा:** ऐसा endpoint जिसके business नियम बिना Express या Mongo के चलते हैं, और एक T2 तालिका जो उसके पूरे HTTP contract को ढकती है।

**क्या साबित होता है:** [14](14-large-project-strategy.md) वाला ढाँचा असली कोड पर काम करता है — और यह भी कि जिन चीज़ों के लिए आपको लगता था कि चलता हुआ server चाहिए, उनमें से ज़्यादातर के लिए नहीं चाहिए था।

---

आगे: [16. MongoDB और Mongoose →](16-tdd-mongodb-mongoose.md) · संबंधित: [14. बड़े प्रोजेक्ट की रणनीति](14-large-project-strategy.md) · [18. API और network टेस्ट](18-tdd-api-network.md)
