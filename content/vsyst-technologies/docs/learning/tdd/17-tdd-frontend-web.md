# 17. TDD on the frontend — vanilla JS and React

Two frontends, one principle:

> **Test what a user can perceive and do. Never how the component is built.**

Everything else in this doc follows from that. A test that knows about state variables, class names, hook call order or component internals will break on every refactor while passing through real bugs. A test that clicks a button and reads the screen survives a rewrite from vanilla JS to React — and that's not hypothetical, it's exactly the migration most admin pages eventually go through.

**Stack:** Vitest + jsdom, `@testing-library/dom` for vanilla, `@testing-library/react` + `user-event` for React, MSW for anything over the network.

---

## Setup

```bash
npm i -D vitest jsdom @testing-library/dom @testing-library/react \
         @testing-library/user-event @testing-library/jest-dom msw
```

```js
// vitest.config.js
export default {
  test: {
    environment: "jsdom",
    setupFiles: ["./test/setup.js"],
    globals: true,
  },
}
```

```js
// test/setup.js
import "@testing-library/jest-dom/vitest"
import { cleanup } from "@testing-library/react"
import { afterEach, beforeAll, afterAll } from "vitest"
import { server } from "../../test-support/msw/server.js"

beforeAll(() => server.listen({ onUnhandledRequest: "error" }))
afterEach(() => {
  cleanup()
  server.resetHandlers()
})
afterAll(() => server.close())
```

`onUnhandledRequest: 'error'` is not optional. It's what stops a component from quietly hitting the real network in CI and turning your suite into a weather report.

---

## Before anything else: get the logic out of the view

The highest-value frontend testing move isn't a testing technique at all.

```js
// ❌ inside a component
const label =
  order.total > 10000
    ? `${(order.total / 100).toFixed(2)} — free shipping`
    : `${(order.total / 100).toFixed(2)} + ${SHIP / 100} shipping`
```

```js
// ✅ packages/domain/order-summary.js — pure, T0, tested in microseconds
export const summarise = (order) => ({
  total: formatMoney(order.total),
  shipping: order.total > FREE_SHIPPING_THRESHOLD ? "free" : formatMoney(SHIP),
})
```

Currency, dates, pluralisation, validation rules, sort/filter logic, permission checks: all of it is pure, all of it belongs in `packages/domain`, and all of it is then shared by the React app, the vanilla admin pages and the React Native app ([18](18-tdd-api-network.md) shares the network layer the same way). What's left in the component is _rendering_ — and rendering needs far fewer tests than people write.

---

## Part 1 — Vanilla JS + HTML

No framework doesn't mean no tests. It means being deliberate about two things: **the module owns a DOM node**, and **the module is imported, not `<script>`-tagged**.

### The shape that's testable

```js
// admin/src/order-list.js
export function mountOrderList(root, { api, onSelect }) {
  root.innerHTML = `
    <h2>Orders</h2>
    <p data-state="loading">Loading orders…</p>
    <ul hidden></ul>`

  const list = root.querySelector("ul")

  api
    .listOrders()
    .then((orders) => {
      root.querySelector("[data-state]").remove()
      list.hidden = false
      list.append(...orders.map(renderRow))
      if (!orders.length) list.replaceWith(emptyState())
    })
    .catch(() => root.replaceChildren(errorState(() => mountOrderList(root, { api, onSelect }))))

  // one delegated listener, not one per row
  list.addEventListener("click", (e) => {
    const row = e.target.closest("li[data-id]")
    if (row) onSelect(row.dataset.id)
  })

  return () => root.replaceChildren() // teardown, so tests (and pages) can unmount
}
```

Takes its root and its dependencies as arguments; returns a teardown. That's the whole trick — the same dependency injection as the backend, applied to a DOM node.

### Driving it test-first

```js
// order-list.test.js
import { screen, within } from "@testing-library/dom"
import userEvent from "@testing-library/user-event"
import { mountOrderList } from "../src/order-list.js"

const mount = (overrides = {}) => {
  const root = document.createElement("div")
  document.body.append(root)
  const api = { listOrders: async () => [anOrder({ id: "1", ref: "A-100" })], ...overrides }
  const onSelect = vi.fn()
  mountOrderList(root, { api, onSelect })
  return { root, onSelect }
}

it("shows a loading state, then the orders", async () => {
  mount()
  expect(screen.getByText(/loading orders/i)).toBeInTheDocument()

  expect(await screen.findByRole("listitem")).toHaveTextContent("A-100")
  expect(screen.queryByText(/loading orders/i)).not.toBeInTheDocument()
})

it("reports the clicked order", async () => {
  const { onSelect } = mount()
  await userEvent.click(await screen.findByRole("listitem"))
  expect(onSelect).toHaveBeenCalledWith("1")
})

it("offers a retry when loading fails", async () => {
  const listOrders = vi
    .fn()
    .mockRejectedValueOnce(new Error("network"))
    .mockResolvedValueOnce([anOrder({ ref: "A-100" })])
  mount({ listOrders })

  await userEvent.click(await screen.findByRole("button", { name: /try again/i }))
  expect(await screen.findByText("A-100")).toBeInTheDocument()
})
```

The tests never mention `innerHTML`, `querySelector`, class names or the template. Rewrite the rendering with `<template>` elements, or move it to React tomorrow, and they still pass.

### The vanilla-specific test worth writing

Manual string templating means you own escaping. Write this one, on every module that interpolates user data:

```js
it("escapes user-supplied text", async () => {
  mount({ listOrders: async () => [anOrder({ ref: "<img src=x onerror=alert(1)>" })] })

  const row = await screen.findByRole("listitem")
  expect(row.querySelector("img")).toBeNull()
  expect(row).toHaveTextContent("<img src=x onerror=alert(1)>")
})
```

React does this for you. Your `innerHTML` template does not.

Also worth pinning in vanilla code specifically: that teardown **removes listeners** (mount and unmount 100 times, assert `document.body.children` and any global listeners are back to zero), and that event delegation still works for rows added after mount.

---

## Part 2 — React

Same principle, better tooling.

### Query priority — this is the whole discipline

```
getByRole            ← default. Accessible to everyone, including your tests
getByLabelText       ← form fields
getByPlaceholderText
getByText            ← non-interactive content
getByDisplayValue
─────────────────────  everything above is how a user finds things
getByTestId          ← last resort, for things with no accessible identity
```

Reaching for `data-testid` on a button is a smell twice over: the test is coupled to markup, **and** the button probably isn't reachable by a screen reader either. `getByRole('button', { name: /save/i })` fails if you break the accessible name — which is a bug you wanted to know about.

### Driving a component test-first

The ticket: _"the checkout form disables submit while saving, shows the server's field errors, and never double-submits."_

```jsx
// checkout-form.test.jsx
const renderForm = (props = {}) => render(<CheckoutForm onSubmit={vi.fn()} {...props} />)

it("submits the entered address", async () => {
  const onSubmit = vi.fn().mockResolvedValue({ ok: true })
  renderForm({ onSubmit })

  await userEvent.type(screen.getByLabelText(/postcode/i), "SW1A 1AA")
  await userEvent.click(screen.getByRole("button", { name: /place order/i }))

  expect(onSubmit).toHaveBeenCalledWith({ postcode: "SW1A 1AA" })
})

it("cannot be submitted twice", async () => {
  const onSubmit = vi.fn(() => new Promise(() => {})) // never resolves: mid-flight
  renderForm({ onSubmit })
  const button = screen.getByRole("button", { name: /place order/i })

  await userEvent.click(button)
  expect(button).toBeDisabled()
  await userEvent.click(button)

  expect(onSubmit).toHaveBeenCalledTimes(1)
})

it("shows the server's field error against the field", async () => {
  const onSubmit = vi.fn().mockResolvedValue({
    ok: false,
    errors: { postcode: "We do not deliver to this postcode" },
  })
  renderForm({ onSubmit })
  await userEvent.click(screen.getByRole("button", { name: /place order/i }))

  expect(await screen.findByText(/do not deliver/i)).toBeInTheDocument()
  expect(screen.getByLabelText(/postcode/i)).toHaveAccessibleDescription(/do not deliver/i)
})
```

That last assertion is the one that matters and the one that's always missing: an error message rendered _somewhere_ on the page isn't the same as an error message associated with its field.

### The four states — the checklist for every data-driven component

Almost every UI bug that reaches production is a missing one of these:

| State       | Test                                                      |
| ----------- | --------------------------------------------------------- |
| **Loading** | a busy indicator is present, content is not               |
| **Empty**   | the empty message, not a blank box or "0 results" spinner |
| **Error**   | a human message and a working retry                       |
| **Success** | the data, and the loading indicator gone                  |

Four tests per data component. Write them as a checklist and the rest of the component's tests get easier.

### Network: MSW at the boundary, never `vi.mock('./api')`

```jsx
// order-page.test.jsx
import { http, HttpResponse, delay } from "msw"
import { server } from "../../test-support/msw/server.js"

it("shows an error and recovers on retry", async () => {
  server.use(
    http.get("/api/orders", () => new HttpResponse(null, { status: 500 }), { once: true }),
    http.get("/api/orders", () => HttpResponse.json({ items: [anOrderDto({ ref: "A-100" })] })),
  )
  render(<OrderPage />)

  expect(await screen.findByRole("alert")).toHaveTextContent(/something went wrong/i)
  await userEvent.click(screen.getByRole("button", { name: /try again/i }))
  expect(await screen.findByText("A-100")).toBeInTheDocument()
})

it("shows a spinner while the request is in flight", async () => {
  server.use(
    http.get("/api/orders", async () => {
      await delay(100)
      return HttpResponse.json({ items: [] })
    }),
  )
  render(<OrderPage />)

  expect(screen.getByRole("status")).toBeInTheDocument()
  expect(await screen.findByText(/no orders yet/i)).toBeInTheDocument()
})
```

Mocking your own `api` module tests your app against your assumption of what the server sends. MSW tests it against a real HTTP response — the same handlers the API's own contract tests validate ([18](18-tdd-api-network.md#contract-first)). That's the difference between catching a `total_cents` → `totalCents` rename and shipping it.

### The provider problem

Every real app wraps components in a router, a query client, a theme, an auth context. Solve it once:

```jsx
// test-support/render.jsx
export function renderApp(ui, { route = "/", user = aUser(), ...options } = {}) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })

  const Wrapper = ({ children }) => (
    <MemoryRouter initialEntries={[route]}>
      <QueryClientProvider client={queryClient}>
        <AuthProvider value={user}>{children}</AuthProvider>
      </QueryClientProvider>
    </MemoryRouter>
  )
  return { user: userEvent.setup(), ...render(ui, { wrapper: Wrapper, ...options }) }
}
```

`retry: false` on the query client matters — the default retry policy makes error-state tests take seconds and then pass for the wrong reason.

### Async, without sleeping

```jsx
await screen.findByText("A-100") // ✅ retries until it appears
await waitFor(() => expect(onSave).toHaveBeenCalled()) // ✅ for non-DOM conditions
await waitForElementToBeRemoved(screen.getByRole("status"))

await new Promise((r) => setTimeout(r, 500)) // ❌ flaky on a loaded CI box
```

And use `queryBy*` — never `getBy*` — when asserting something is **absent**; `getBy*` throws instead of returning null.

### Custom hooks

Test them through a component that uses them. If a hook is complicated enough that that's painful, the logic inside it probably isn't React-specific and belongs in `packages/domain` as a plain function. `renderHook` exists for genuinely reusable library-grade hooks; reach for it rarely.

---

## What not to test on the frontend

| Don't                                         | Why                                                | Instead                                                                 |
| --------------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------------------- |
| Snapshot the whole component tree             | Nobody reviews a 400-line diff; everyone runs `-u` | Assert the two or three things that matter                              |
| CSS, layout, pixel positions                  | jsdom doesn't lay out; the test would lie          | Visual regression tooling, or your eyes                                 |
| `useState` values, hook call counts           | Implementation. Breaks on every refactor           | The rendered output                                                     |
| Third-party components (date pickers, charts) | Their tests, not yours                             | Your usage: does selecting a date call your handler?                    |
| Every prop permutation                        | Combinatorial and low-value                        | The states that behave differently                                      |
| Routing between every page                    | Framework behaviour                                | One test that the route renders the page; links via `getByRole('link')` |

---

## Where E2E fits

Playwright, 5–15 tests, against a real browser and a real deployed stack. They exist to catch what jsdom structurally cannot: the real build output, CORS, auth cookies, CSP, service workers, third-party scripts, actual layout.

Signup → login → place an order → see it in the list. That's a smoke test. It is _not_ where you test that a discount stacks correctly.

---

## 🛠 Mini-project — one screen, both ways

_One day._

1. Pick a small screen that exists in both your React app and an admin page — a list with a filter, say.
2. Extract every non-rendering decision (filtering, sorting, formatting, permission checks) into `packages/domain`, test-first, at T0.
3. Write the four-states checklist for the React version: loading, empty, error, success — with MSW, no module mocking.
4. Write the same four for the vanilla version using `@testing-library/dom`, plus the escaping test and the teardown test.
5. Compare the two test files. The assertions should be nearly identical — if they aren't, one of the implementations has logic the other doesn't.
6. Delete any test that would survive replacing the component's entire markup with something wrong. Those tests were assertions about implementation.

**Deliverable:** two implementations, one shared domain package, two behaviourally identical test files.

**Proves:** UI tests written against behaviour are portable across frameworks — and that most of what feels like "frontend logic" isn't frontend at all.

---

Next: [18. API & network tests →](18-tdd-api-network.md) · Related: [19. React Native](19-tdd-react-native.md) · [14. Large-project strategy](14-large-project-strategy.md)
