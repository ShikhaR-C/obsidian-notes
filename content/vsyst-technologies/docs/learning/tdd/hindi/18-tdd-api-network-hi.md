# 18. API और network टेस्ट

दो अलग काम, जो आपस में गड्डमड्ड कर दिए जाते हैं:

- **API contract टेस्ट** — _आकार सही है या नहीं, और क्या server और उसके तीनों clients उस पर सहमत हैं?_
- **Network टेस्ट** — _network बदमाशी करे तो क्या होता है?_ Timeouts, 500s, retries, offline, cancellation।

पहला आपके clients को API बदलने पर टूटने से बचाता है। दूसरा आपके ऐप को अटकने, दो बार पैसे काटने, या ट्रेन में crash होने से बचाता है। दूसरी क़िस्म लगभग कोई तब तक नहीं लिखता जब तक कोई हादसा मजबूर न कर दे, जबकि पूरे दस्तावेज़ में लिखने में सबसे आसान टेस्ट यही हैं।

---

## पहले contract

[14](14-large-project-strategy-hi.md) वाली नाम-परिवर्तन की समस्या: API किसी field का नाम बदलती है, हर suite हरी रहती है, और React Native ऐप production में टूट जाता है। ऐसा इसलिए होता है क्योंकि server के टेस्ट और हर client के mocks **एक ही धारणा के अलग-अलग बयान** हैं।

इलाज: एक schema, जिसे दोनों पक्ष import करें।

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

### Server साबित करता है कि वह यही आकार बनाता है

```js
// orders.api.test.js  (T2)
it("GET /orders returns the documented shape", async () => {
  await seedOrders(3)
  const res = await asUser(request(app).get("/orders?limit=2"))

  expect(res.status).toBe(200)
  expect(() => OrderListResponse.parse(res.body)).not.toThrow()
})
```

यह **हर** endpoint पर कीजिए। यह एक लाइन है, और यही वह लाइन है जो उसी पल फेल होती है जब कोई field का नाम बदलता है, type ढीला करता है, या तारीख़ serialise करना भूल जाता है।

Errors पर भी assert कीजिए — error envelope भी उतना ही contract है जितना success वाला body, और clients इसी को सबसे ख़राब ढंग से संभालते हैं:

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

### Clients अपने mocks उसी schema से बनाते हैं

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
  }) // ← parse, ताकि ग़लत fixture build के समय ज़ोर से फेल हो

export const handlers = [
  http.get("*/api/orders", () =>
    HttpResponse.json(OrderListResponse.parse({ items: [anOrderDto()], nextCursor: null })),
  ),
]
```

```js
// test-support/msw/server.js  (node + jsdom)   |   server.native.js भी setupServer इस्तेमाल करता है
import { setupServer } from "msw/node"
export const server = setupServer(...handlers)
```

अब fixture भटक ही नहीं सकता: schema बदलते ही `OrderDto.parse` हर client के टेस्ट run में throw करता है। `totalCents` का नाम बदलिए और आपको एक ही बदलाव से, commit के समय, लाल API टेस्ट _और_ लाल web टेस्ट _और_ लाल React Native टेस्ट मिलेंगे।

> **यह भी करने लायक़:** API से कहिए कि वह ग़ैर-production builds में अपने भेजे जाने वाले responses को schema के ख़िलाफ़ जाँचे। जिस contract को आप सिर्फ़ टेस्टों में जाँचते हैं, उसका उल्लंघन आप आख़िरकार runtime पर करेंगे।

**पहले से OpenAPI spec है?** वही अनुशासन: spec से client types और MSW handlers बनाइए, और T2 में responses को उसके ख़िलाफ़ assert कीजिए। तरीक़ा अलग है, नियम नहीं — _एक कलाकृति, दोनों पक्ष_।

---

## Contract से endpoint को test-drive करना

Workflow, जिसकी शुरुआत schema से होती है:

1. नए endpoint का **schema लिखिए**। यही डिज़ाइन की बातचीत है, और इसमें दस मिनट लगते हैं।
2. ठोस request और अपेक्षित response के साथ **T2 टेस्ट लिखिए**। लाल — route मौजूद ही नहीं।
3. **`handlers.js` में handler जोड़िए** ताकि clients तुरंत, समानांतर रूप से, उसके सहारे काम शुरू कर सकें।
4. **Implementation को भीतर की ओर चलाइए**, T0 पर ([15](15-tdd-node-backend-hi.md))।
5. **T2 टेस्ट हरा हो जाता है**, और mock के सहारे किया गया client का काम अब असली चीज़ के साथ चलता है।

Step 3 वहीं है जहाँ टीम के पैमाने पर फ़ायदा है: फ़्रंटएंड backend के इंतज़ार में नहीं रुकता, और जब दोनों मिलते हैं, तो एक ऐसे schema पर मिलते हैं जिसके ख़िलाफ़ दोनों पक्ष टेस्ट किए जा चुके हैं।

---

## Network टेस्ट

ऊपर की हर बात मानकर चलती है कि request पूरी होती है। ये टेस्ट उस स्थिति के लिए हैं जब वह पूरी नहीं होती।

हर request को **एक ही client wrapper** से गुज़ारिए और उस wrapper को कसकर टेस्ट कीजिए। फिर किसी feature कोड को इनमें से कुछ भी सोचने की ज़रूरत नहीं।

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

`fetch`, `sleep` और `clock` inject किए गए हैं — इसी वजह से नीचे के सारे टेस्ट तुरंत और deterministic हैं।

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

फिर उस बात पर assert कीजिए जो सटीकता के लिए असल में मायने रखती है: **socket छोड़ दिया गया।** ऐसा "timeout" जो request को चलता छोड़ दे, बाद में भी आपका `.then()` handler चलाएगा और उस स्क्रीन का state बदल देगा जिसे user छोड़ चुका है।

### Retry, और — इससे भी अहम — retry न करना

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
  expect(calls).toBe(1) // client error पर retry करना बग है
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
  expect(calls).toBe(1) // ← वह टेस्ट जो दोहरी वसूली रोकता है
})
```

आख़िरी वाला इस पूरे दस्तावेज़ का सबसे मूल्यवान network टेस्ट है। हर 5xx पर आँख मूँदकर retry और साथ में एक POST — पेमेंट दो बार कटने का यही रास्ता है, और यह गड़बड़ सिर्फ़ भार पड़ने पर सामने आती है।

### बिना इंतज़ार किए backoff

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

`sleep` inject करने का मतलब है टेस्ट तुरंत चलता है। अगर असली timers इस्तेमाल करने ही पड़ें, तो `vi.advanceTimersByTimeAsync` — sync वाला `advanceTimersByTime` लंबित promises को पूरा नहीं होने देगा।

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

और component स्तर पर वह टेस्ट जो "unmount के बाद setState" वाली श्रेणी के बग पकड़ता है: request शुरू कीजिए, unmount कीजिए, request पूरी कीजिए, और assert कीजिए कि कुछ throw नहीं हुआ और कुछ render नहीं हुआ।

### Race conditions — वह बग जो production तक पहुँचता है

```js
it("ignores a stale response that arrives after a newer one", async () => {
  server.use(
    http.get("*/search", async ({ request }) => {
      const q = new URL(request.url).searchParams.get("q")
      await delay(q === "ab" ? 200 : 10) // पुरानी request धीमी है
      return HttpResponse.json({ items: [q] })
    }),
  )
  render(<Search />)

  await userEvent.type(screen.getByRole("searchbox"), "ab")
  await userEvent.type(screen.getByRole("searchbox"), "c")

  await waitFor(() => expect(screen.getByRole("list")).toHaveTextContent("abc"))
  await delay(300)
  expect(screen.getByRole("list")).toHaveTextContent("abc") // 'ab' नहीं
})
```

Type-ahead ऐसी query के नतीजे दिखा रहा है जिसे user पहले ही बदल चुका है। लगभग हर search box में यह बग है, और तेज़ connection पर यह लगभग अदृश्य रहता है — इसीलिए आप इसे उम्मीद के भरोसे नहीं, नियंत्रित delay के साथ assert करते हैं।

### Offline और error की सतहें

```js
it("shows an offline message rather than a generic error", async () => {
  server.use(http.get("*/orders", () => HttpResponse.error())) // network स्तर की विफलता
  render(<OrderPage />)

  expect(await screen.findByRole("alert")).toHaveTextContent(/check your connection/i)
})
```

`HttpResponse.error()` transport की विफलता है, HTTP error response नहीं — अलग code path, अलग संदेश, और ज़्यादातर ऐप इसी को ग़लत करते हैं।

### Network टेस्ट की चेकलिस्ट

हर client wrapper पर, एक बार:

- [ ] Timeout चलता है, और request सचमुच abort होती है
- [ ] 5xx पर retry होता है; 4xx पर नहीं
- [ ] Idempotency key के बिना ग़ैर-idempotent methods retry नहीं होतीं
- [ ] Backoff के अंतराल वही हैं जो आप समझते हैं
- [ ] Caller की ओर से cancellation आगे पहुँचती है
- [ ] Transport विफलता (offline) HTTP error से अलग पहचानी जा सकती है
- [ ] बिगड़ा JSON / ख़ाली body / ग़लत content-type कोई unhandled error नहीं फेंकता
- [ ] 401 पर ठीक एक token refresh होता है, भले पाँच requests चल रही हों
- [ ] Rate-limit `429`, `Retry-After` का पालन करता है
- [ ] बासी responses फेंक दिए जाते हैं, render नहीं होते

हर स्क्रीन पर: loading, ख़ाली, error, retry ([17](17-tdd-frontend-web-hi.md))।

---

## तीसरे पक्ष की APIs

वे आपकी नहीं हैं, इसलिए रणनीति अलग है।

**तेज़ परतों में:** उन्हें कभी मत बुलाइए। हर एक को एक संकरे interface वाले adapter में लपेटिए, adapter को fake कीजिए, और _अपने_ कोड को उस fake के ख़िलाफ़ टेस्ट कीजिए। ख़ुद adapter को उन MSW handlers के ख़िलाफ़ टेस्ट कीजिए जो **रिकॉर्ड किए गए असली responses** से बने हों — कोई असली response body किसी fixture फ़ाइल में कॉपी कीजिए, गढ़िए मत, क्योंकि जो आकार आप कल्पना करते हैं वह कभी ठीक वैसा नहीं होता जैसा वे भेजते हैं।

**रात में, ग़ैर-gating (T5):** एक canary जो हर तीसरे पक्ष पर एक असली call करे और assert करे कि response अब भी आपके schema से parse होता है।

```js
// इस तरह tag किया गया कि यह PR suite में कभी न चले
it.skipIf(!process.env.CANARY)("stripe still returns the shape we expect", async () => {
  const res = await stripe.paymentIntents.retrieve(KNOWN_TEST_ID)
  expect(() => PaymentIntentShape.parse(res)).not.toThrow()
})
```

जब कोई provider कुछ बदलता है, तो यह आपको रात तीन बजे साफ़ संदेश के साथ बता देता है, बजाय इसके कि दोपहर तीन बजे कोई ग्राहक बताए। इसे gating suite से बाहर रखिए — किसी तीसरे पक्ष का outage आपके deploys कभी न रोके।

---

## Sockets और streams

WebSocket और SSE कोड टेस्ट करने लायक़ है, उसी सिद्धांत पर: transport एक port है।

1. **संदेशों का प्रबंधन एक शुद्ध reducer है।** `(state, message) => state`। हर संदेश-प्रकार, बेतरतीब क्रम में पहुँचना, और डुप्लिकेट — सब T0 पर टेस्ट कीजिए, बिना किसी socket के।
2. **Connection का जीवन-चक्र एक adapter है** — `emit(message)`, `dropConnection()`, `open()` वाला fake। Backoff के साथ reconnect, reconnect पर दोबारा subscribe, और disconnect रहते संदेशों का buffer होना — यह सब fake के ख़िलाफ़ टेस्ट कीजिए।
3. **एक integration टेस्ट** असली socket server के ख़िलाफ़ यह साबित करता है कि तार सही जुड़े हैं।

Realtime कोड के बग लगभग हमेशा श्रेणी 1 और 2 में होते हैं — reconnect की आँधी, खोई हुई subscriptions, reconnect के बाद दोहरे संदेश — और इनमें से किसी को दोहराने के लिए असली socket की ज़रूरत नहीं।

---

## 🛠 मिनी-प्रोजेक्ट — मज़बूत client

_एक दिन।_

1. किसी एक ऐप की हर `fetch` call को एक ही `createHttpClient` के पीछे ले जाइए, जिसमें `fetch`, `sleep` और `clock` inject हों।
2. ऊपर वाली चेकलिस्ट पर test-first काम कीजिए। कम से कम दो असली बग की उम्मीद रखिए — आम अपराधी हैं POST पर retries और unhandled transport विफलताएँ।
3. किसी एक endpoint के response का आकार `packages/contracts` में ले जाइए, API के T2 टेस्ट में उस पर assert कीजिए, और उस endpoint का MSW handler schema से parse करके बनाइए।
4. साबित कीजिए कि चक्र पूरा होता है: schema में किसी field का नाम बदलिए और पुष्टि कीजिए कि API **और** दोनों clients में, बिना उन्हें छुए, टेस्ट लाल हो जाते हैं।
5. अपनी सबसे व्यस्त search या filter स्क्रीन पर बासी-response वाला टेस्ट जोड़िए।
6. हर तीसरे पक्ष की dependency पर रात का एक canary जोड़िए, ग़ैर-gating।

**नतीजा:** एक HTTP client जिसके पास network-विफलता टेस्टों की चेकलिस्ट है, और एक endpoint जिसका आकार हर तरफ़ एक ही स्रोत से लागू होता है।

**क्या साबित होता है:** सीमा-पार बग की वे दो श्रेणियाँ जो बाक़ी हर तरह की टेस्टिंग से बच निकलती हैं — चुपचाप होता contract drift, और ख़राब network में ख़राब व्यवहार — दोनों एक बार में पकड़ना सस्ता है, और production में पकड़ना महँगा।

---

आगे: [19. React Native →](19-tdd-react-native-hi.md) · संबंधित: [15. Node backend](15-tdd-node-backend-hi.md) · [17. फ़्रंटएंड](17-tdd-frontend-web-hi.md)
