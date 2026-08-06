# 16. MongoDB और Mongoose के साथ TDD

Database वही जगह है जहाँ TDD की सलाह आमतौर पर धुँधली हो जाती है। यह रहा ठोस संस्करण।

---

## दो नियम जो सब कुछ तय कर देते हैं

> **1. Mongoose को कभी mock मत कीजिए।**
> **2. अपने ज़्यादातर टेस्टों को Mongo छूने ही मत दीजिए।**

ये विरोधाभासी लगते हैं। हैं नहीं — यह एक ही फ़ैसला है, दोनों तरफ़ से देखा हुआ।

Mongoose को mock करने का मतलब है `expect(Model.findOne).toHaveBeenCalledWith({ email })` लिखना — ऐसा टेस्ट जो query सही हो या न हो, पास हो जाता है, `findById` में refactor करते ही टूट जाता है, और field का नाम ग़लत लिखा हो या index ग़ायब हो तब भी हरा रहता है। यह बस यह जाँचता है कि आपने वही function बुलाया जो आपने ख़ुद लिखा था। इसका मूल्य ऋणात्मक है: लागत है, संकेत नहीं, और यह उसी refactor को रोकता है जिसकी उसे रक्षा करनी चाहिए।

इसलिए जब आप data access टेस्ट करें, **असली MongoDB** इस्तेमाल कीजिए। और इसे किफ़ायती रखने के लिए ऐसा इंतज़ाम कीजिए कि **सिर्फ़ data-access टेस्टों** को उसकी ज़रूरत पड़े — बाक़ी सब in-memory repository पर चले। इसका तरीक़ा है repository port और साझा contract suite, नीचे देखिए।

---

## सेटअप: in-memory Mongo

```bash
npm i -D mongodb-memory-server
```

एक ही node वाला replica set, ताकि transactions और change streams चलें — सादा standalone server इन्हें नहीं चला सकता, और यह बात आपको पहली बार तब पता चलेगी जब आप कई-दस्तावेज़ वाला write टेस्ट करेंगे:

```js
// test/global-setup.js
import { MongoMemoryReplSet } from "mongodb-memory-server"

let replset

export async function setup() {
  replset = await MongoMemoryReplSet.create({ replSet: { count: 1, storageEngine: "wiredTiger" } })
  process.env.MONGO_URI = replset.getUri()
}

export async function teardown() {
  await replset.stop()
}
```

```js
// test/setup-db.js — हर टेस्ट फ़ाइल के लिए
import mongoose from "mongoose"
import { beforeAll, afterAll, afterEach } from "vitest"

beforeAll(async () => {
  // हर worker के लिए एक database: फ़ाइलें समानांतर चलती हैं बिना टकराए
  const db = `test_${process.env.VITEST_WORKER_ID ?? 0}`
  await mongoose.connect(process.env.MONGO_URI, { dbName: db })
  await Promise.all(Object.values(mongoose.models).map((m) => m.syncIndexes()))
})

afterEach(async () => {
  const { collections } = mongoose.connection
  await Promise.all(Object.values(collections).map((c) => c.deleteMany({})))
})

afterAll(() => mongoose.disconnect())
```

```js
// vitest.config.js
export default { test: { globalSetup: ["./test/global-setup.js"] } }
```

तीन बारीकियाँ जो दिखने से ज़्यादा मायने रखती हैं:

- **टेस्टों के बीच `deleteMany`, `dropDatabase` नहीं।** Drop करने से आपके indexes ख़त्म हो जाते हैं, इसलिए unique-constraint वाला टेस्ट पहली फ़ाइल के बाद हमेशा चुपचाप पास होता रहेगा। अगर drop करना ही है, तो `syncIndexes()` दोबारा चलाइए।
- **`beforeAll` में `syncIndexes()`।** Mongoose डिफ़ॉल्ट रूप से indexes पृष्ठभूमि में बनाता है, इसलिए हो सकता है कि पहला टेस्ट चलते समय नई collection पर unique index अभी न हो। इसके बिना unique-key टेस्ट अस्थिर रहते हैं।
- **हर worker के लिए एक DB**, `VITEST_WORKER_ID` के आधार पर। समानांतर चलने वाली टेस्ट फ़ाइलों का एक ही database साझा करना — "अकेले पास, suite में फेल" का सबसे आम कारण यही है।

> **Docker बेहतर लगे तो?** असली `mongo:7` image पर `testcontainers` शुरू होने में धीमा है (~5 s) पर वही server है जिसे आप deploy करते हैं। रोज़मर्रा की T1 suite के लिए in-memory रखिए, और अगर आप version-विशिष्ट व्यवहार पर निर्भर हैं तो असली image पर रात का एक run रखिए।

---

## Repository port, और contract suite

यही वह तरकीब है जिससे पूरी बात बनती है। Domain बताता है कि उसे क्या चाहिए; दो implementations उसे पूरा करती हैं।

```js
// packages/domain/ports.js — एक interface, दस्तावेज़ के रूप में लिखा हुआ
// OrderRepository:
//   create(order)        -> order with id
//   byId(id)             -> order | null
//   byUser(userId, {limit, cursor}) -> { items, nextCursor }
//   markShipped(id, at)  -> boolean (false if not found or already shipped)
```

**एक ही test suite** लिखिए और उसे दोनों implementations पर चलाइए:

```js
// packages/api/test/order-repository.contract.js
export function orderRepositoryContract(name, makeRepo) {
  describe(`OrderRepository contract — ${name}`, () => {
    let repo
    beforeEach(async () => {
      repo = await makeRepo()
    })

    it("returns null for an unknown id", async () => {
      expect(await repo.byId("64b7f0000000000000000000")).toBeNull()
    })

    it("round-trips an order", async () => {
      const saved = await repo.create(anOrder({ totalCents: 897 }))
      expect(await repo.byId(saved.id)).toMatchObject({ totalCents: 897 })
    })

    it("lists a user's orders, newest first", async () => {
      await repo.create(anOrder({ userId: "ada", createdAt: d("2026-01-01") }))
      await repo.create(anOrder({ userId: "ada", createdAt: d("2026-01-03") }))
      await repo.create(anOrder({ userId: "bob", createdAt: d("2026-01-02") }))

      const { items } = await repo.byUser("ada", { limit: 10 })
      expect(items.map((o) => o.createdAt)).toEqual([d("2026-01-03"), d("2026-01-01")])
    })

    it("markShipped is idempotent — the second call returns false", async () => {
      const { id } = await repo.create(anOrder({ status: "confirmed" }))
      expect(await repo.markShipped(id, d("2026-01-05"))).toBe(true)
      expect(await repo.markShipped(id, d("2026-01-06"))).toBe(false)
    })
  })
}
```

```js
// in-memory-order-repository.test.js  (T0 — milliseconds, कोई Mongo नहीं)
orderRepositoryContract("in-memory", () => new InMemoryOrderRepository())
```

```js
// mongo-order-repository.int.test.js   (T1 — असली Mongo)
orderRepositoryContract("mongo", () => new MongoOrderRepository(OrderModel))
```

इससे आपको क्या मिलता है:

- आपका तेज़ fake, हर उस व्यवहार पर असली चीज़ के **प्रमाणित रूप से** बराबर है जिस पर आप निर्भर हैं। In-memory fakes पर आम आपत्ति — "वे हक़ीक़त से हट जाते हैं" — का जवाब अनुशासन से नहीं, यंत्रवत मिल जाता है।
- नया व्यवहार contract में एक बार जाता है और दोनों implementations को उसे पूरा करना पड़ता है।
- बाद में Mongo की जगह Postgres लाना यानी एक नई implementation और एक हरी contract suite।

Codebase में बाक़ी सब कुछ — use cases, routes, 1,500 domain टेस्ट — in-memory वाले का इस्तेमाल करता है और कभी database चालू नहीं करता।

---

## असली Mongo किसे चाहिए

इस सूची को छोटा और सोच-समझकर रखिए। अगर कोई टेस्ट इनमें से किसी की जाँच नहीं कर रहा, तो उसकी जगह T0 है।

### Unique indexes

इसे किसी fake के ख़िलाफ़ टेस्ट नहीं किया जा सकता, और application स्तर पर "पहले जाँचो फिर डालो" एक race है, constraint नहीं:

```js
it("rejects a duplicate email at the database level", async () => {
  await UserModel.create(aUser({ email: "ada@example.com" }))

  await expect(UserModel.create(aUser({ email: "ada@example.com" }))).rejects.toMatchObject({
    code: 11000,
  })
})

it("treats emails case-insensitively", async () => {
  // collation strength: 2
  await UserModel.create(aUser({ email: "ada@example.com" }))
  await expect(UserModel.create(aUser({ email: "ADA@example.com" }))).rejects.toMatchObject({
    code: 11000,
  })
})
```

और उस `11000` को repository में किसी domain error से map कीजिए, उसके अपने टेस्ट के साथ — कच्चा driver code किसी use case तक पहुँचे, इसका कोई कारण नहीं।

### Query की सटीकता

हर ग़ैर-मामूली query का ऐसा टेस्ट हो जिसमें **ग़लत जवाब database में मौजूद हो**:

```js
it("excludes soft-deleted orders", async () => {
  await repo.create(anOrder({ userId: "ada" }))
  await repo.create(anOrder({ userId: "ada", deletedAt: d("2026-01-02") }))

  const { items } = await repo.byUser("ada", { limit: 10 })
  expect(items).toHaveLength(1)
})
```

जिस collection में सिर्फ़ मेल खाने वाली पंक्तियाँ हों, उस पर query टेस्ट कुछ साबित नहीं करता — `find({})` भी पास हो जाएगा।

### Pagination, उबाऊ हिस्सा भी

```js
it("paginates without skipping or repeating across a tie", async () => {
  const at = d("2026-01-01") // जान-बूझकर एक जैसे timestamps
  for (const i of [1, 2, 3, 4, 5])
    await repo.create(anOrder({ userId: "ada", createdAt: at, seq: i }))

  const page1 = await repo.byUser("ada", { limit: 2 })
  const page2 = await repo.byUser("ada", { limit: 2, cursor: page1.nextCursor })
  const page3 = await repo.byUser("ada", { limit: 2, cursor: page2.nextCursor })

  const ids = [...page1.items, ...page2.items, ...page3.items].map((o) => o.id)
  expect(new Set(ids).size).toBe(5)
})
```

यही वह टेस्ट है जो आपके sort में ग़ायब tie-breaker पकड़ता है। सिर्फ़ किसी ग़ैर-unique field पर sort करने से बराबर दस्तावेज़ों के बीच क्रम अनिर्धारित रहता है, और पंक्तियाँ चुपचाप पन्नों के बीच खिसकती रहती हैं।

### Schema validation और defaults

जो नियम आपने घोषित किए हैं उन्हें टेस्ट कीजिए, न कि Mongoose की उन्हें लागू करने की क्षमता:

```js
it("requires an email", async () => {
  await expect(new UserModel({ name: "Ada" }).validate()).rejects.toThrow(/email.*required/i)
})

it("defaults plan to free", async () => {
  const u = await UserModel.create({ email: "a@b.c", name: "A" })
  expect(u.plan).toBe("free")
})
```

हर उस नियम पर एक टेस्ट जिसे खोने पर आपको दुख होगा। हर field पर एक नहीं।

### Transactions

```js
it("rolls back the order when stock reservation fails", async () => {
  const session = await mongoose.startSession()
  await expect(
    placeOrderTransactionally(deps, session)({ items: [{ sku: "PEN-1", qty: 99 }] }),
  ).rejects.toThrow(InsufficientStock)

  expect(await OrderModel.countDocuments()).toBe(0) // कुछ भी आंशिक रूप से नहीं लिखा गया
})
```

इसीलिए सेटअप में replica set है। यही वह टेस्ट भी है जो क्लासिक बग पकड़ता है: transaction के अंदर किसी एक write को `{ session }` भेजना भूल जाना।

### Migrations

हर migration एक function है जिसका before/after टेस्ट होता है:

```js
it("backfills displayName from firstName + lastName", async () => {
  await UserModel.collection.insertOne({ firstName: "Ada", lastName: "Lovelace" })

  await migrations["005-display-name"].up(mongoose.connection.db)

  const u = await UserModel.collection.findOne({ firstName: "Ada" })
  expect(u.displayName).toBe("Ada Lovelace")
})

it("is safe to run twice", async () => {
  /* up() दो बार चलाइए, वही state assert कीजिए */
})
```

Migrations एक ही बार चलते हैं, production में, ऐसे डेटा पर जिसे आप आसानी से देख नहीं सकते। इन्हें ज़्यादातर कोड से ज़्यादा टेस्ट चाहिए और आमतौर पर बिल्कुल नहीं मिलते।

---

## जो नहीं करना चाहिए

| Anti-pattern                                          | क्या गड़बड़ होती है                                                                            |
| ----------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `vi.mock('mongoose')`                                 | टूटी queries के साथ टेस्ट पास होते हैं; refactoring उन्हें तोड़ती है; शून्य संकेत              |
| `jest-mongodb` शैली में फ़ाइलों के बीच साझा global DB | टेस्ट समानांतर चलते ही क्रम-निर्भर अस्थिरता                                                    |
| `beforeAll` में बड़ी fixture फ़ाइल seed करना          | टेस्ट ऐसे डेटा पर निर्भर हो जाते हैं जिसे वे घोषित नहीं करते; एक बदलाव पचास टेस्ट तोड़ देता है |
| `expect(Model.find).toHaveBeenCalled()`               | आपकी अपनी call पर assert, नतीजे पर नहीं                                                        |
| यह टेस्ट करना कि Mongoose `"1"` को `1` में बदलता है   | Library का व्यवहार                                                                             |
| टेस्टों के बीच एक ही document साझा करना               | Mutation रिसती है; क्लासिक "अकेले पास" वाली अस्थिरता                                           |
| `afterEach` में `dropDatabase()`                      | चुपचाप indexes नष्ट कर देता है; unique टेस्ट कुछ भी टेस्ट करना बंद कर देते हैं                 |

---

## रफ़्तार

अगर T1 एक मिनट पार करने लगे, तो इसी क्रम में:

1. **क्या ये टेस्ट सचमुच persistence के बारे में हैं?** ज़्यादातर suites में business नियम DB टेस्टों में छिपे होते हैं। उन्हें in-memory repo पर T0 में ले जाइए।
2. **Connection दोबारा इस्तेमाल कीजिए।** हर worker पर एक बार जुड़िए, हर टेस्ट पर नहीं।
3. **सिर्फ़ उन collections पर `deleteMany`** जिन्हें आपने छुआ, database की हर collection पर नहीं।
4. **समानांतर फ़ाइलें, हर worker के लिए एक DB।** ऊपर के सेटअप में यह पहले से है।
5. **ऐसा डेटा मत बनाइए जिस पर assert नहीं कर रहे।** Builders दस दस्तावेज़ बनाना सस्ता कर देते हैं; इसका मतलब मुफ़्त नहीं है।

---

## 🛠 मिनी-प्रोजेक्ट — दो implementations वाली repository

_आधा दिन।_

1. अपने ऐप की ऐसी एक collection चुनिए जिसमें असली query logic हो — सादी CRUD तालिका नहीं।
2. पहले contract suite लिखिए, domain के नज़रिए से। छह से दस व्यवहार, जिनमें एक soft-delete/filter मामला, एक क्रम वाला मामला, और एक idempotency मामला हो।
3. उसे `InMemoryXRepository` (T0) पर पास कराइए।
4. _वही_ suite in-memory Mongo के साथ `MongoXRepository` (T1) पर चलाइए। फ़र्क़ ठीक कीजिए — कुछ फ़र्क़ ज़रूर निकलेंगे, और हर एक वह बग है जो वरना production में चला जाता।
5. सिर्फ़-Mongo वाले टेस्ट जोड़िए: unique index, pagination का tie-break, एक schema नियम।
6. Codebase के हर use-case टेस्ट को in-memory implementation पर लाइए और suite का समय पहले-बाद नापिए।

**नतीजा:** एक port, दो implementations, एक साझा contract suite, और नापने लायक़ तेज़ suite।

**क्या साबित होता है:** आपके पास तेज़ टेस्ट और सच्चा fake, दोनों एक साथ हो सकते हैं — जबकि सब मानते हैं कि इनमें से एक चुनना पड़ता है।

---

आगे: [17. फ़्रंटएंड →](17-tdd-frontend-web.md) · संबंधित: [15. Node backend](15-tdd-node-backend.md) · [14. बड़े प्रोजेक्ट की रणनीति](14-large-project-strategy.md)
