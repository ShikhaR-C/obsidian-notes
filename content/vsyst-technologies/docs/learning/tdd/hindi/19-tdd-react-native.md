# 19. React Native के लिए TDD

[17. फ़्रंटएंड](17-tdd-frontend-web.md) की हर बात यहाँ भी लागू होती है — user जो देखता है उससे query कीजिए, network सीमा पर MSW, और चार स्थितियाँ। यह दस्तावेज़ उस पर है जो _अलग_ है, और वह ज़्यादातर यह है: **platform तक पहुँचना कहीं मुश्किल है, इसलिए ज़्यादा logic उससे बाहर धकेलिए।**

**Stack:** Jest (RN का ecosystem Jest-पहला है — `react-native`/`jest-expo` presets, और Metro transform की धारणाएँ इसी में बनी हैं), `@testing-library/react-native`, MSW, और गिनती के device टेस्टों के लिए Detox या Maestro।

---

## सेटअप

```bash
npm i -D jest @testing-library/react-native react-test-renderer msw
```

```js
// jest.config.js
module.exports = {
  preset: "jest-expo", // या bare RN के लिए 'react-native'
  setupFilesAfterEnv: ["<rootDir>/test/setup.js"],
  transformIgnorePatterns: [
    "node_modules/(?!(?:@react-native|react-native|expo(nent)?|@expo|react-navigation|@react-navigation)/)",
  ],
}
```

```js
// test/setup.js
import "@testing-library/react-native/extend-expect"
import { server } from "@app/test-support/msw/server"

beforeAll(() => server.listen({ onUnhandledRequest: "error" }))
afterEach(() => server.resetHandlers())
afterAll(() => server.close())

jest.mock("@react-native-async-storage/async-storage", () =>
  require("@react-native-async-storage/async-storage/jest/async-storage-mock"),
)
```

`transformIgnorePatterns` वही लाइन है जिस पर हर कोई एक दोपहर गँवाता है। RN, `node_modules` में बिना transpile किया ESM भेजता है, इसलिए Jest को बताना पड़ता है कि उन packages को छोड़ने के बजाय transform करे। जब `SyntaxError: Cannot use import statement outside a module` दिखे, तो दोषी package को उस सूची में जोड़ दीजिए।

---

## RN का ख़ास सिद्धांत: आपके ज़्यादातर ऐप को React Native import ही नहीं करना चाहिए

Mobile में web से ज़्यादा सचमुच कठिन logic होता है — offline queues, sync conflict का निपटारा, पृष्ठभूमि में refresh, reconnect पर retry, local cache का अमान्य होना, device पर रखे डेटा का migration। असली बग यहीं होते हैं, और **इनमें से किसी को चलने के लिए React Native नहीं चाहिए।**

```
packages/
├── domain/       नियम, sync, conflict का निपटारा      ← कोई RN import नहीं। ms में चलता है।
├── api-client/   http + retry + offline queue        ← कोई RN import नहीं
└── mobile/
    ├── screens/  पतली। State render करती हैं, intents भेजती हैं।
    └── native/   इकलौती फ़ाइलें जो device APIs छूती हैं
```

शुद्ध state machine के रूप में टेस्ट किया गया sync engine, किसी भी मात्रा की screen टेस्टिंग से ज़्यादा क़ीमती है:

```js
// packages/domain/sync.test.js — कोई RN नहीं, कोई device नहीं, कोई network नहीं
it("replays queued mutations in order when the connection returns", () => {
  let state = syncReducer(initial, { type: "went-offline" })
  state = syncReducer(state, { type: "mutation", op: renameOrder("1", "A") })
  state = syncReducer(state, { type: "mutation", op: renameOrder("1", "B") })

  const { effects } = syncReducer(state, { type: "came-online" })

  expect(effects).toEqual([{ type: "send", ops: [renameOrder("1", "A"), renameOrder("1", "B")] }])
})

it("drops a local edit that loses to a newer server version", () => {
  const state = syncReducer(withPending("1", { name: "B", version: 3 }), {
    type: "server-update",
    id: "1",
    doc: { name: "C", version: 5 },
  })

  expect(state.docs["1"].name).toBe("C")
  expect(state.pending).toEqual([])
  expect(state.conflicts).toEqual([{ id: "1", discarded: { name: "B" } }])
})
```

दूसरे मामले को device पर दोहराने का मतलब है: airplane mode चालू कीजिए, संपादन कीजिए, किसी और से दूसरे device पर संपादन कराइए, wifi चालू कीजिए, और देखिए। Reducer टेस्ट के रूप में यह चार लाइनों का है और आधे millisecond में चलता है। **Mobile पर उपलब्ध TDD की सबसे बड़ी जीत यही है।**

---

## Querying: accessibility props ही आपके selectors हैं

RNTL की queries, RN की accessibility props पर टिकी हैं। इन्हें इसी क्रम में इस्तेमाल कीजिए:

| Query                                    | किस पर टिकी है                                        |
| ---------------------------------------- | ----------------------------------------------------- |
| `getByRole('button', { name: /save/i })` | `accessibilityRole` + `accessibilityLabel`/child text |
| `getByLabelText(/postcode/i)`            | `accessibilityLabel`                                  |
| `getByText(/no orders yet/i)`            | render किया हुआ text                                  |
| `getByDisplayValue('SW1A 1AA')`          | `TextInput` का value                                  |
| `getByTestId('order-row')`               | आख़िरी सहारा                                          |

```jsx
// ❌ न टेस्ट करने लायक़, न सुलभ
<TouchableOpacity onPress={save}><Text>Save</Text></TouchableOpacity>

// ✅
<Pressable accessibilityRole="button" accessibilityLabel="Save order" onPress={save}>
  <Text>Save</Text>
</Pressable>
```

फ़ायदा web जैसा ही: सुलभ तरीक़े से टेस्ट लिखने से ऐप VoiceOver और TalkBack के साथ इस्तेमाल लायक़ बन जाता है, वह भी साइड इफ़ेक्ट के रूप में। Mobile पर यह अक्सर अनुपालन की शर्त होती है, इसलिए यह उन दुर्लभ मामलों में है जहाँ टेस्टिंग का अनुशासन दोहरी क़ीमत वसूल करता है।

`testID` उन चीज़ों के लिए ठीक है जिनकी कोई स्वाभाविक सुलभ पहचान नहीं — कोई list container, कोई chart। जिस चीज़ को user छूता है, उस पर यह बदबू है।

---

## किसी स्क्रीन को test-first बनाना

```jsx
// orders-screen.test.jsx
import { render, screen, userEvent, waitFor } from "@testing-library/react-native"

const renderScreen = (ui, { route = "Orders" } = {}) => ({
  user: userEvent.setup(),
  ...render(<TestProviders initialRoute={route}>{ui}</TestProviders>),
})

it("shows the orders once loaded", async () => {
  server.use(
    http.get("*/api/orders", () =>
      HttpResponse.json({ items: [anOrderDto({ ref: "A-100" })], nextCursor: null }),
    ),
  )

  renderScreen(<OrdersScreen />)

  expect(screen.getByLabelText(/loading/i)).toBeOnTheScreen()
  expect(await screen.findByText("A-100")).toBeOnTheScreen()
})

it("shows an offline message and retries", async () => {
  server.use(http.get("*/api/orders", () => HttpResponse.error()))
  const { user } = renderScreen(<OrdersScreen />)

  expect(await screen.findByText(/check your connection/i)).toBeOnTheScreen()

  server.use(
    http.get("*/api/orders", () =>
      HttpResponse.json({ items: [anOrderDto({ ref: "A-100" })], nextCursor: null }),
    ),
  )
  await user.press(screen.getByRole("button", { name: /try again/i }))

  expect(await screen.findByText("A-100")).toBeOnTheScreen()
})
```

`userEvent.setup()` और `await user.press(...)` पर ध्यान दीजिए — RNTL का `userEvent` सीधे `onPress` बुलाने के बजाय असली press का क्रम (pressIn, delay, pressOut) दोहराता है, इसलिए यह उन components को पकड़ता है जो gesture के सिर्फ़ ग़लत आधे हिस्से पर जवाब देते हैं। सरल मामलों के लिए `fireEvent.press` अब भी ठीक है और तेज़ है।

**Mobile पर offline टेस्ट वैकल्पिक नहीं है।** यह सामान्य स्थिति है, किनारे का मामला नहीं — लिफ़्ट, सुरंगें, ट्रेनें, तहख़ाने।

---

## Native modules: module के किनारे पर mock, adapter की ज़िम्मेदारी आपकी

आप jsdom में कैमरा नहीं चला सकते। इसलिए: हर native क्षमता के लिए एक पतला adapter, टेस्टों में mock किया हुआ, और सारा फ़ैसला-logic उसके बाहर।

```js
// mobile/native/permissions.js  — कोई logic नहीं, बस call
import * as ImagePicker from "expo-image-picker"
export const requestCamera = () => ImagePicker.requestCameraPermissionsAsync()
```

```js
// domain/photo-flow.js  — सारी शाखाएँ, शुद्ध
export const nextStep = ({ permission, hasDraft }) =>
  permission === "granted"
    ? "capture"
    : permission === "denied"
      ? "explain-and-open-settings"
      : hasDraft
        ? "resume-draft"
        : "ask"
```

फिर screen टेस्ट सिर्फ़ adapter को mock करता है:

```jsx
jest.mock("../native/permissions")

it("explains and offers settings when the camera is denied", async () => {
  requestCamera.mockResolvedValue({ status: "denied", canAskAgain: false })
  const { user } = renderScreen(<PhotoScreen />)

  await user.press(screen.getByRole("button", { name: /add photo/i }))

  expect(await screen.findByText(/enable camera access in settings/i)).toBeOnTheScreen()
  expect(screen.getByRole("button", { name: /open settings/i })).toBeOnTheScreen()
})
```

अनुमति की चार स्थितियाँ — granted, denied, हमेशा के लिए blocked, अभी नहीं पूछा — `nextStep` में T0 पर एक तालिका टेस्ट हैं, और जिन दो का render अलग होता है उनके लिए एक-एक screen टेस्ट। `test/setup.js` में रखने लायक़ मानक mocks: AsyncStorage (आधिकारिक mock), `react-native-reanimated` (उसका अपना `/mock`), push notifications, geolocation, biometrics।

---

## Navigation

असली navigator के साथ टेस्ट कीजिए, mock किए `navigation` prop के साथ नहीं। `navigate` को mock करने से आपको ऐसा टेस्ट मिलता है जो जाँचता है कि आपने अपना ही function एक string के साथ बुलाया।

```jsx
export const TestProviders = ({ children, initialRoute = "Orders" }) => (
  <NavigationContainer>
    <Stack.Navigator initialRouteName={initialRoute}>
      <Stack.Screen name="Orders" component={OrdersScreen} />
      <Stack.Screen name="OrderDetail" component={OrderDetailScreen} />
    </Stack.Navigator>
  </NavigationContainer>
)
```

```jsx
it("opens the order detail when a row is tapped", async () => {
  const { user } = renderScreen(<TestProviders />)
  await user.press(await screen.findByText("A-100"))

  expect(await screen.findByRole("header", { name: /order a-100/i })).toBeOnTheScreen()
})
```

यहाँ ये टेस्ट करने लायक़ हैं, क्योंकि ये चुपचाप टूटते हैं: deep links सही params के साथ सही स्क्रीन पर पहुँचना, deep-link वाली स्क्रीन से back का व्यवहार, और स्क्रीन unmount होने पर उसकी चल रही requests का रद्द होना।

---

## Platform के फ़र्क़

```js
it.each(["ios", "android"])("uses the %s date format", (os) => {
  jest.spyOn(Platform, "OS", "get").mockReturnValue(os)
  expect(formatDate(d("2026-01-15"))).toBe(os === "ios" ? "15 Jan 2026" : "15/01/2026")
})
```

इससे भी बेहतर: logic में `Platform.OS` पर शाखा बनाइए ही मत — फ़र्क़ को एक मान के रूप में भेजिए, और शाखा एक शुद्ध parameter बन जाएगी जिसे आप तालिका से टेस्ट कर सकते हैं। किसी component के अंदर `Platform.select` ठीक है; किसी business नियम के अंदर `Platform.OS` एक ऐसी टेस्ट-योग्यता की समस्या है जिसे आप ख़ुद चुन रहे हैं।

---

## Device टेस्ट किसलिए हैं

Detox या Maestro, **5–10 टेस्ट, रात में, ग़ैर-gating**। ये धीमे हैं (हर एक मिनटों का), इन्हें simulators या device farm चाहिए, और ये आपके सबसे अस्थिर टेस्ट होंगे।

इन्हें सिर्फ़ उसके लिए बचाकर रखिए जिसे और कहीं जाँचा ही नहीं जा सकता:

- ऐप असली build पर चालू होकर पहली स्क्रीन तक पहुँचता है
- Login, OS के keychain/biometric prompt समेत
- असली device पर एक मुख्य flow, शुरू से आख़िर तक
- Push notification पर tap → सही स्क्रीन
- ठंडी शुरुआत से deep link
- अनुमति के dialogs, जो OS का UI हैं

बाक़ी सब कुछ — हर नियम, हर स्थिति, हर error का रास्ता — ऊपर वाली परतों में जाता है, जहाँ यह milliseconds में चलता है। जिस टीम के पास 200 Detox टेस्ट हैं, उसकी suite 90 मिनट लेती है, पाँच में से एक बार फेल होती है, और नज़रअंदाज़ कर दी जाती है; यह कोई टेस्ट न होने से भी बुरा है, क्योंकि यह वह बजट खा जाती है जो तेज़ टेस्टों पर लगता।

---

## रफ़्तार और CI

| लक्षण                                      | इलाज                                                                                                                               |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| छोटी suite पर Jest मिनटों लेता है          | `maxWorkers=50%`; जाँचिए कि `transformIgnorePatterns` पूरे `node_modules` को transform तो नहीं कर रहा                              |
| `SyntaxError: Cannot use import statement` | उस package को `transformIgnorePatterns` में जोड़िए                                                                                 |
| Animations टेस्ट अटका देती हैं             | `jest.mock('react-native-reanimated', () => require('react-native-reanimated/mock'))`                                              |
| टेस्ट अकेले पास, साथ में फेल               | AsyncStorage या module state रिस रही है — `clearMocks: true`, और `afterEach` में storage mock साफ़ कीजिए                           |
| `act()` की चेतावनियाँ                      | आपने किसी async update के पूरा होने से पहले assert कर दिया — `fireEvent` + तुरंत assert के बजाय `findBy*`/`waitFor` इस्तेमाल कीजिए |

Domain और api-client packages को RN के Jest प्रोजेक्ट से **बाहर**, Vitest के नीचे, बिना किसी preset के चलाइए। वे React Native से कुछ import नहीं करते, इसलिए उन्हें उसकी transform pipeline की क़ीमत नहीं चुकानी चाहिए — और आपके ज़्यादातर टेस्ट वही हैं।

---

## 🛠 मिनी-प्रोजेक्ट — offline-first, बिना device के टेस्ट किया हुआ

_एक दिन।_

1. ऐसा फ़ीचर चुनिए जिसे offline चलना ही चाहिए — कोई form, कोई favourite, कोई status बदलाव।
2. उसे `packages/domain` में एक शुद्ध reducer के रूप में गढ़िए: `{ docs, pending, conflicts }` और `mutation`, `went-offline`, `came-online`, `server-update` के लिए actions।
3. कम से कम इन्हें test-drive कीजिए, सब T0 पर: offline रहते क़तार बनाना; क्रम से replay; एक ही संपादन दो बार होने पर deduplicate; version टकराव पर server जीते और छोड़ा गया मान दर्ज हो; 409 से फेल होता replay हमेशा retry न करता रहे।
4. इसे स्क्रीन से जोड़िए। हर दिखने वाली स्थिति पर एक RNTL टेस्ट: pending badge, synced, conflict banner।
5. AsyncStorage को mock कीजिए और टेस्ट कीजिए कि ऐप बंद होने से पहले सहेजी गई क़तार, दोबारा चालू होने पर replay होती है।
6. अब जाकर इसे असली device पर airplane mode में चलाइए — और गिनिए कि इनमें से कितने बग आप पहले ही पकड़ चुके थे।

**नतीजा:** एक offline sync engine जिसकी पूरी test suite एक सेकंड से कम में चलती है, और चार screen टेस्ट।

**क्या साबित होता है:** mobile का सबसे कठिन हिस्सा mobile-विशिष्ट है ही नहीं। एक बार यह reducer बन जाए, तो यह बस [12. Katas](12-tutorial-katas.md) है — बस दाँव ऊँचे हैं।

---

वापस: [14. बड़े प्रोजेक्ट की रणनीति](14-large-project-strategy.md) · संबंधित: [17. फ़्रंटएंड](17-tdd-frontend-web.md) · [18. API और network टेस्ट](18-tdd-api-network.md) · [README](README.md)
