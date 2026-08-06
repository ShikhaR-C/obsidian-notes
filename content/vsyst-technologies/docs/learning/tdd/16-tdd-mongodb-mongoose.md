# 16. TDD with MongoDB and Mongoose

The database is where TDD advice usually goes vague. Here's the concrete version.

---

## Two rules that decide everything

> **1. Never mock Mongoose.**
> **2. Never let most of your tests touch Mongo.**

They sound contradictory. They aren't — they're the same decision seen from both sides.

Mocking Mongoose means writing `expect(Model.findOne).toHaveBeenCalledWith({ email })` — a test that passes whether or not the query is correct, breaks when you refactor to `findById`, and would still be green if the field were misspelled or the index missing. It asserts that you called the function you wrote yourself. It has negative value: cost, no signal, and it blocks the refactor it should be protecting.

So when you test data access, use **real MongoDB**. And to keep that affordable, arrange for **only the data-access tests** to need it — everything else runs against an in-memory repository. The mechanism is the repository port plus a shared contract suite, below.

---

## Setup: in-memory Mongo

```bash
npm i -D mongodb-memory-server
```

A replica set of one, so transactions and change streams work — a plain standalone server can't run them, and you'll hit that the first time you test a multi-document write:

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
// test/setup-db.js — per test file
import mongoose from "mongoose"
import { beforeAll, afterAll, afterEach } from "vitest"

beforeAll(async () => {
  // one database per worker: files run in parallel without colliding
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

Three details that matter more than they look:

- **`deleteMany` between tests, not `dropDatabase`.** Dropping destroys your indexes, so a unique-constraint test would silently pass forever after the first file. If you do drop, re-run `syncIndexes()`.
- **`syncIndexes()` in `beforeAll`.** Mongoose builds indexes in the background by default, so a fresh collection may not have the unique index yet when your first test runs. Without this, unique-key tests are flaky.
- **One DB per worker**, keyed on `VITEST_WORKER_ID`. Parallel test files that share a database is the single most common source of "passes alone, fails in the suite".

> **Docker instead?** `testcontainers` against a real `mongo:7` image is slower to start (~5 s) but is the actual server you deploy. Use in-memory for the everyday T1 suite and a nightly run against the real image if you rely on version-specific behaviour.

---

## The repository port, and the contract suite

The trick that makes the whole thing work. The domain defines what it needs; two implementations satisfy it.

```js
// packages/domain/ports.js — an interface, expressed as documentation
// OrderRepository:
//   create(order)        -> order with id
//   byId(id)             -> order | null
//   byUser(userId, {limit, cursor}) -> { items, nextCursor }
//   markShipped(id, at)  -> boolean (false if not found or already shipped)
```

Write **one test suite** and run it against both implementations:

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
// in-memory-order-repository.test.js  (T0 — milliseconds, no Mongo)
orderRepositoryContract("in-memory", () => new InMemoryOrderRepository())
```

```js
// mongo-order-repository.int.test.js   (T1 — real Mongo)
orderRepositoryContract("mongo", () => new MongoOrderRepository(OrderModel))
```

What this buys you:

- Your fast fake is **provably** equivalent to the real thing on every behaviour you depend on. The usual objection to in-memory fakes — "they drift from reality" — is answered mechanically rather than by discipline.
- New behaviour goes in the contract once and both implementations must satisfy it.
- Swapping Mongo for Postgres later is a new implementation plus a green contract suite.

Everything else in the codebase — use cases, routes, the 1,500 domain tests — uses the in-memory one and never boots a database.

---

## What actually needs real Mongo

Keep this list short and deliberate. If a test isn't checking one of these, it belongs at T0.

### Unique indexes

You cannot test this against a fake, and application-level "check then insert" is a race, not a constraint:

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

And map that `11000` to a domain error in the repository, with its own test — a raw driver code has no business escaping into a use case.

### Query correctness

Every non-trivial query gets a test where **the wrong answer is present in the database**:

```js
it("excludes soft-deleted orders", async () => {
  await repo.create(anOrder({ userId: "ada" }))
  await repo.create(anOrder({ userId: "ada", deletedAt: d("2026-01-02") }))

  const { items } = await repo.byUser("ada", { limit: 10 })
  expect(items).toHaveLength(1)
})
```

A query test with only matching rows in the collection proves nothing — `find({})` would pass it.

### Pagination, including the boring bit

```js
it("paginates without skipping or repeating across a tie", async () => {
  const at = d("2026-01-01") // identical timestamps on purpose
  for (const i of [1, 2, 3, 4, 5])
    await repo.create(anOrder({ userId: "ada", createdAt: at, seq: i }))

  const page1 = await repo.byUser("ada", { limit: 2 })
  const page2 = await repo.byUser("ada", { limit: 2, cursor: page1.nextCursor })
  const page3 = await repo.byUser("ada", { limit: 2, cursor: page2.nextCursor })

  const ids = [...page1.items, ...page2.items, ...page3.items].map((o) => o.id)
  expect(new Set(ids).size).toBe(5)
})
```

This is the test that finds the missing tie-breaker in your sort. Sorting by a non-unique field alone gives an undefined order between equal documents, and rows quietly move between pages.

### Schema validation and defaults

Test the rules you declared, not Mongoose's ability to enforce them:

```js
it("requires an email", async () => {
  await expect(new UserModel({ name: "Ada" }).validate()).rejects.toThrow(/email.*required/i)
})

it("defaults plan to free", async () => {
  const u = await UserModel.create({ email: "a@b.c", name: "A" })
  expect(u.plan).toBe("free")
})
```

One test per rule you'd be upset to lose. Not one per field.

### Transactions

```js
it("rolls back the order when stock reservation fails", async () => {
  const session = await mongoose.startSession()
  await expect(
    placeOrderTransactionally(deps, session)({ items: [{ sku: "PEN-1", qty: 99 }] }),
  ).rejects.toThrow(InsufficientStock)

  expect(await OrderModel.countDocuments()).toBe(0) // nothing partially written
})
```

This is why the setup uses a replica set. It's also the test that catches the classic bug: forgetting to pass `{ session }` to one of the writes inside the transaction.

### Migrations

Each migration is a function that gets a before/after test:

```js
it("backfills displayName from firstName + lastName", async () => {
  await UserModel.collection.insertOne({ firstName: "Ada", lastName: "Lovelace" })

  await migrations["005-display-name"].up(mongoose.connection.db)

  const u = await UserModel.collection.findOne({ firstName: "Ada" })
  expect(u.displayName).toBe("Ada Lovelace")
})

it("is safe to run twice", async () => {
  /* run up() twice, assert same state */
})
```

Migrations are run-once, in production, against data you can't easily inspect. They deserve tests more than most code and usually get none.

---

## Things not to do

| Anti-pattern                                       | What goes wrong                                                        |
| -------------------------------------------------- | ---------------------------------------------------------------------- |
| `vi.mock('mongoose')`                              | Tests pass with broken queries; refactoring breaks them; zero signal   |
| `jest-mongodb` style shared global DB across files | Order-dependent flakes as soon as tests run in parallel                |
| Seeding a big fixture file in `beforeAll`          | Tests depend on data they don't declare; one change breaks fifty tests |
| `expect(Model.find).toHaveBeenCalled()`            | Asserts your own call, not the result                                  |
| Testing that Mongoose casts `"1"` to `1`           | Library behaviour                                                      |
| Sharing one document between tests                 | Mutation leaks; the classic "passes alone" flake                       |
| A `dropDatabase()` in `afterEach`                  | Silently destroys indexes; unique tests stop testing anything          |

---

## Speed

If T1 creeps past a minute, in order:

1. **Are these tests actually about persistence?** Most suites have business rules hiding in DB tests. Move them to T0 against the in-memory repo.
2. **Reuse the connection.** Connect once per worker, not per test.
3. **`deleteMany` on the collections you touched**, not every collection in the database.
4. **Parallel files, one DB per worker.** Already in the setup above.
5. **Don't create data you don't assert on.** Builders make it cheap to create ten documents; that doesn't make it free.

---

## 🛠 Mini-project — the two-implementation repository

_Half a day._

1. Pick one collection in your app with real query logic — not a plain CRUD table.
2. Write the contract suite first, from the domain's point of view. Six to ten behaviours, including one soft-delete/filter case, one ordering case, and one idempotency case.
3. Make it pass against `InMemoryXRepository` (T0).
4. Run the _same_ suite against `MongoXRepository` with in-memory Mongo (T1). Fix the differences — there will be some, and each one is a bug you'd otherwise have shipped.
5. Add the Mongo-only tests: unique index, pagination tie-break, one schema rule.
6. Switch every use-case test in the codebase to the in-memory implementation and time the suite before and after.

**Deliverable:** one port, two implementations, one shared contract suite, and a measurably faster suite.

**Proves:** you can have fast tests and a truthful fake at the same time — which is the thing everyone assumes you have to choose between.

---

Next: [17. Frontend →](17-tdd-frontend-web.md) · Related: [15. Node backend](15-tdd-node-backend.md) · [14. Large-project strategy](14-large-project-strategy.md)
