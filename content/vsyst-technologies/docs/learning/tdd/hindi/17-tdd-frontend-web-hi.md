# 17. फ़्रंटएंड पर TDD — vanilla JS और React

दो फ़्रंटएंड, एक ही सिद्धांत:

> **वह टेस्ट कीजिए जो user देख और कर सकता है। यह कभी नहीं कि component बना कैसे है।**

इस दस्तावेज़ की बाक़ी हर बात इसी से निकलती है। जो टेस्ट state variables, class नामों, hook के call क्रम या component के internals को जानता है, वह हर refactor पर टूटेगा और असली बग को गुज़र जाने देगा। जो टेस्ट बटन दबाता है और स्क्रीन पढ़ता है, वह vanilla JS से React तक की पूरी दोबारा-लिखाई झेल जाता है — और यह काल्पनिक नहीं है, ज़्यादातर admin पेज आख़िरकार यही सफ़र करते हैं।

**Stack:** Vitest + jsdom, vanilla के लिए `@testing-library/dom`, React के लिए `@testing-library/react` + `user-event`, और network वाली हर चीज़ के लिए MSW।

---

## सेटअप

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

`onUnhandledRequest: 'error'` वैकल्पिक नहीं है। यही किसी component को CI में चुपचाप असली network से टकराने और आपकी suite को मौसम की रिपोर्ट बनने से रोकता है।

---

## सबसे पहले: logic को view से बाहर निकालिए

फ़्रंटएंड टेस्टिंग की सबसे मूल्यवान चाल कोई टेस्टिंग तकनीक है ही नहीं।

```js
// ❌ component के अंदर
const label =
  order.total > 10000
    ? `${(order.total / 100).toFixed(2)} — free shipping`
    : `${(order.total / 100).toFixed(2)} + ${SHIP / 100} shipping`
```

```js
// ✅ packages/domain/order-summary.js — शुद्ध, T0, microseconds में टेस्ट
export const summarise = (order) => ({
  total: formatMoney(order.total),
  shipping: order.total > FREE_SHIPPING_THRESHOLD ? "free" : formatMoney(SHIP),
})
```

Currency, तारीख़ें, बहुवचन, validation नियम, sort/filter logic, अनुमति की जाँच: यह सब शुद्ध है, यह सब `packages/domain` में जाता है, और फिर इसे React ऐप, vanilla admin पेज और React Native ऐप सब साझा करते हैं ([18](18-tdd-api-network-hi.md) network परत को इसी तरह साझा करता है)। Component में जो बचता है वह है _rendering_ — और rendering को उतने टेस्ट नहीं चाहिए जितने लोग लिखते हैं।

---

## भाग 1 — Vanilla JS + HTML

कोई framework न होने का मतलब कोई टेस्ट न होना नहीं है। मतलब है दो चीज़ों में सोच-समझकर काम करना: **module एक DOM node का मालिक हो**, और **module import किया जाए, `<script>` tag से नहीं**।

### जो ढाँचा टेस्ट करने लायक़ है

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

  // एक ही delegated listener, हर row पर एक नहीं
  list.addEventListener("click", (e) => {
    const row = e.target.closest("li[data-id]")
    if (row) onSelect(row.dataset.id)
  })

  return () => root.replaceChildren() // teardown, ताकि टेस्ट (और पेज) unmount कर सकें
}
```

यह अपना root और अपनी dependencies arguments के रूप में लेता है; और teardown लौटाता है। पूरी तरकीब यही है — backend जैसा ही dependency injection, बस एक DOM node पर लागू।

### इसे test-first बनाना

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

ये टेस्ट कभी `innerHTML`, `querySelector`, class नामों या template का ज़िक्र नहीं करते। rendering को `<template>` elements से दोबारा लिखिए, या कल React में ले जाइए — ये फिर भी पास होंगे।

### Vanilla के लिए ख़ास तौर पर लिखने लायक़ टेस्ट

हाथ से string templating का मतलब है escaping की ज़िम्मेदारी आपकी। जो भी module user का डेटा interpolate करता है, उस पर यह टेस्ट लिखिए:

```js
it("escapes user-supplied text", async () => {
  mount({ listOrders: async () => [anOrder({ ref: "<img src=x onerror=alert(1)>" })] })

  const row = await screen.findByRole("listitem")
  expect(row.querySelector("img")).toBeNull()
  expect(row).toHaveTextContent("<img src=x onerror=alert(1)>")
})
```

React यह आपके लिए कर देता है। आपका `innerHTML` template नहीं करता।

Vanilla कोड में ख़ास तौर पर ये भी कील ठोंकने लायक़ हैं: teardown **listeners हटाता है** (100 बार mount और unmount कीजिए, assert कीजिए कि `document.body.children` और कोई भी global listeners शून्य पर लौट आए), और mount के बाद जोड़ी गई rows पर भी event delegation चलता है।

---

## भाग 2 — React

वही सिद्धांत, बेहतर औज़ार।

### Query की प्राथमिकता — पूरा अनुशासन यही है

```
getByRole            ← डिफ़ॉल्ट। सबके लिए सुलभ, आपके टेस्टों के लिए भी
getByLabelText       ← form fields
getByPlaceholderText
getByText            ← ग़ैर-interactive सामग्री
getByDisplayValue
─────────────────────  ऊपर की हर चीज़ वही है जैसे कोई user चीज़ें ढूँढ़ता है
getByTestId          ← आख़िरी सहारा, उन चीज़ों के लिए जिनकी कोई सुलभ पहचान नहीं
```

किसी बटन पर `data-testid` लगाना दोहरी बदबू है: टेस्ट markup से बँध जाता है, **और** वह बटन शायद screen reader के लिए भी पहुँच से बाहर है। `getByRole('button', { name: /save/i })` तब फेल होता है जब आप उसका सुलभ नाम तोड़ते हैं — और यह वही बग है जिसका आपको पता चलना चाहिए था।

### Component को test-first बनाना

Ticket: _"checkout form save होते समय submit बंद कर दे, server की field errors दिखाए, और कभी दो बार submit न हो।"_

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
  const onSubmit = vi.fn(() => new Promise(() => {})) // कभी resolve नहीं होता: बीच रास्ते
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

आख़िरी assertion ही सबसे अहम है और वही हमेशा ग़ायब रहता है: पेज पर _कहीं_ दिख रहा error संदेश, उस संदेश जैसा नहीं है जो अपनी field से जुड़ा हो।

### चार स्थितियाँ — हर डेटा-आधारित component की चेकलिस्ट

Production तक पहुँचने वाला लगभग हर UI बग इन्हीं में से किसी एक की कमी होता है:

| स्थिति      | टेस्ट                                                             |
| ----------- | ----------------------------------------------------------------- |
| **Loading** | कोई busy संकेतक मौजूद है, सामग्री नहीं                            |
| **ख़ाली**   | ख़ाली होने का संदेश, न कि सूना डिब्बा या "0 results" वाला spinner |
| **Error**   | इंसानी संदेश और चलता हुआ retry                                    |
| **Success** | डेटा, और loading संकेतक ग़ायब                                     |

हर डेटा component पर चार टेस्ट। इन्हें चेकलिस्ट की तरह लिखिए और component के बाक़ी टेस्ट आसान हो जाएँगे।

### Network: सीमा पर MSW, कभी `vi.mock('./api')` नहीं

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

अपने ही `api` module को mock करना आपके ऐप को इस धारणा के ख़िलाफ़ टेस्ट करता है कि server क्या भेजता है। MSW उसे असली HTTP response के ख़िलाफ़ टेस्ट करता है — वही handlers जिन्हें API के अपने contract टेस्ट मान्य करते हैं ([18](18-tdd-api-network-hi.md))। `total_cents` → `totalCents` वाला नाम-परिवर्तन पकड़ने और उसे production में भेज देने के बीच यही फ़र्क़ है।

### Provider की समस्या

हर असली ऐप components को router, query client, theme, auth context में लपेटता है। इसे एक बार हल कीजिए:

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

Query client पर `retry: false` मायने रखता है — डिफ़ॉल्ट retry नीति error-state टेस्टों को सेकंडों लंबा कर देती है और फिर वे ग़लत कारण से पास होते हैं।

### Async, बिना sleep किए

```jsx
await screen.findByText("A-100") // ✅ दिखने तक दोबारा कोशिश करता है
await waitFor(() => expect(onSave).toHaveBeenCalled()) // ✅ ग़ैर-DOM शर्तों के लिए
await waitForElementToBeRemoved(screen.getByRole("status"))

await new Promise((r) => setTimeout(r, 500)) // ❌ व्यस्त CI मशीन पर अस्थिर
```

और जब किसी चीज़ की **अनुपस्थिति** पर assert कर रहे हों तो `queryBy*` इस्तेमाल कीजिए — कभी `getBy*` नहीं; `getBy*` null लौटाने के बजाय throw करता है।

### Custom hooks

इन्हें उस component के ज़रिए टेस्ट कीजिए जो इन्हें इस्तेमाल करता है। अगर कोई hook इतना पेचीदा है कि यह तकलीफ़देह हो, तो उसके अंदर का logic शायद React-विशिष्ट है ही नहीं और सादे function के रूप में `packages/domain` में जाना चाहिए। `renderHook` सचमुच पुन:प्रयोज्य, library-स्तर के hooks के लिए है; इसका इस्तेमाल कम ही कीजिए।

---

## फ़्रंटएंड पर क्या टेस्ट न करें

| यह नहीं                                         | क्यों                                                         | इसके बजाय                                                          |
| ----------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------ |
| पूरे component tree का snapshot                 | 400 लाइनों का diff कोई review नहीं करता; सब `-u` चला देते हैं | वे दो-तीन चीज़ें assert कीजिए जो मायने रखती हैं                    |
| CSS, layout, pixel की जगहें                     | jsdom layout करता ही नहीं; टेस्ट झूठ बोलेगा                   | Visual regression के औज़ार, या आपकी आँखें                          |
| `useState` के मान, hook calls की गिनती          | Implementation। हर refactor पर टूटता है                       | Render किया हुआ output                                             |
| तीसरे पक्ष के components (date pickers, charts) | वे उनके टेस्ट हैं, आपके नहीं                                  | आपका इस्तेमाल: तारीख़ चुनने पर क्या आपका handler चलता है?          |
| हर prop का हर संयोजन                            | संयोजनात्मक और कम मूल्य का                                    | वे स्थितियाँ जिनका व्यवहार अलग है                                  |
| हर पेज के बीच routing                           | Framework का व्यवहार                                          | एक टेस्ट कि route पेज render करता है; links `getByRole('link')` से |

---

## E2E कहाँ बैठता है

Playwright, 5–15 टेस्ट, असली browser और असली deployed stack के ख़िलाफ़। ये वही पकड़ने के लिए हैं जो jsdom ढाँचागत रूप से नहीं पकड़ सकता: असली build output, CORS, auth cookies, CSP, service workers, तीसरे पक्ष की scripts, असली layout।

Signup → login → order देना → उसे सूची में देखना। यह smoke test है। यह वह जगह _नहीं_ है जहाँ आप जाँचें कि discount सही ढंग से जुड़ता है।

---

## 🛠 मिनी-प्रोजेक्ट — एक स्क्रीन, दोनों तरीक़ों से

_एक दिन।_

1. ऐसी छोटी स्क्रीन चुनिए जो आपके React ऐप और किसी admin पेज दोनों में मौजूद है — मान लीजिए filter वाली कोई सूची।
2. हर ग़ैर-rendering फ़ैसला (filtering, sorting, formatting, अनुमति की जाँच) `packages/domain` में निकालिए, test-first, T0 पर।
3. React संस्करण के लिए चार-स्थितियों की चेकलिस्ट लिखिए: loading, ख़ाली, error, success — MSW के साथ, बिना module mocking।
4. वही चार vanilla संस्करण के लिए `@testing-library/dom` से लिखिए, साथ में escaping वाला टेस्ट और teardown वाला टेस्ट।
5. दोनों टेस्ट फ़ाइलें मिलाइए। Assertions लगभग एक जैसी होनी चाहिए — अगर नहीं हैं, तो किसी एक implementation में ऐसा logic है जो दूसरी में नहीं।
6. ऐसा कोई भी टेस्ट हटा दीजिए जो component का पूरा markup किसी ग़लत चीज़ से बदल देने पर भी बचा रहे। वे टेस्ट implementation के बारे में assertions थे।

**नतीजा:** दो implementations, एक साझा domain package, दो व्यवहार में एक-जैसी टेस्ट फ़ाइलें।

**क्या साबित होता है:** व्यवहार के आधार पर लिखे UI टेस्ट frameworks के बीच ले जाए जा सकते हैं — और जो "फ़्रंटएंड logic" लगता है उसका ज़्यादातर हिस्सा फ़्रंटएंड का है ही नहीं।

---

आगे: [18. API और network टेस्ट →](18-tdd-api-network-hi.md) · संबंधित: [19. React Native](19-tdd-react-native-hi.md) · [14. बड़े प्रोजेक्ट की रणनीति](14-large-project-strategy-hi.md)
