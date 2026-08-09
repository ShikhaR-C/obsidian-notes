# 19. TDD for React Native

Everything in [17. Frontend](17-tdd-frontend-web.md) applies — query by what the user perceives, MSW at the network boundary, the four states. This doc covers what's _different_, which is mostly: **the platform is much harder to reach, so push more logic off it.**

**Stack:** Jest (RN's ecosystem is Jest-first — `react-native`/`jest-expo` presets, and the Metro transform assumptions are baked in), `@testing-library/react-native`, MSW, Detox or Maestro for the handful of device tests.

---

## Setup

```bash
npm i -D jest @testing-library/react-native react-test-renderer msw
```

```js
// jest.config.js
module.exports = {
  preset: "jest-expo", // or 'react-native' for bare RN
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

`transformIgnorePatterns` is the line everyone loses an afternoon to. RN ships untranspiled ESM in `node_modules`, so Jest must be told to transform those packages instead of skipping them. When you see `SyntaxError: Cannot use import statement outside a module`, add the offending package to that list.

---

## The RN-specific principle: most of your app shouldn't import React Native

Mobile has more genuinely hard logic than web — offline queues, sync conflict resolution, background refresh, retry-on-reconnect, local cache invalidation, migration of on-device data. All of it is where the real bugs are, and **none of it needs React Native to run.**

```
packages/
├── domain/       rules, sync, conflict resolution   ← no RN import. Runs in ms.
├── api-client/   http + retry + offline queue       ← no RN import
└── mobile/
    ├── screens/  thin. Renders state, dispatches intents.
    └── native/   the only files that touch device APIs
```

The sync engine tested as a pure state machine is worth more than any amount of screen testing:

```js
// packages/domain/sync.test.js — no RN, no device, no network
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

Reproducing that second case on a device means: turn on airplane mode, edit, have someone else edit on another device, turn wifi on, watch. As a reducer test it's four lines and runs in half a millisecond. **This is the single biggest TDD win available on mobile.**

---

## Querying: accessibility props are your selectors

RNTL's queries map onto RN's accessibility props. Use them in this order:

| Query                                    | Backed by                                             |
| ---------------------------------------- | ----------------------------------------------------- |
| `getByRole('button', { name: /save/i })` | `accessibilityRole` + `accessibilityLabel`/child text |
| `getByLabelText(/postcode/i)`            | `accessibilityLabel`                                  |
| `getByText(/no orders yet/i)`            | rendered text                                         |
| `getByDisplayValue('SW1A 1AA')`          | `TextInput` value                                     |
| `getByTestId('order-row')`               | last resort                                           |

```jsx
// ❌ untestable and inaccessible
<TouchableOpacity onPress={save}><Text>Save</Text></TouchableOpacity>

// ✅
<Pressable accessibilityRole="button" accessibilityLabel="Save order" onPress={save}>
  <Text>Save</Text>
</Pressable>
```

Same payoff as on web: writing tests the accessible way makes the app usable with VoiceOver and TalkBack as a side effect. On mobile that's often a compliance requirement, so this is the rare case where the testing discipline pays for itself twice.

`testID` is fine for things with no natural accessible identity — a list container, a chart. It's a smell on anything a user taps.

---

## Driving a screen test-first

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

Note `userEvent.setup()` and `await user.press(...)` — RNTL's `userEvent` simulates the real press sequence (pressIn, delay, pressOut) rather than calling `onPress` directly, so it catches components that only respond to the wrong half of the gesture. `fireEvent.press` remains fine for simple cases and is faster.

The **offline test is not optional on mobile.** It's the normal case, not the edge case — lifts, tunnels, trains, basements.

---

## Native modules: mock at the module edge, own the adapter

You cannot run the camera in jsdom. So: one thin adapter per native capability, mocked in tests, with all decision logic outside it.

```js
// mobile/native/permissions.js  — no logic, just the call
import * as ImagePicker from "expo-image-picker"
export const requestCamera = () => ImagePicker.requestCameraPermissionsAsync()
```

```js
// domain/photo-flow.js  — all the branching, pure
export const nextStep = ({ permission, hasDraft }) =>
  permission === "granted"
    ? "capture"
    : permission === "denied"
      ? "explain-and-open-settings"
      : hasDraft
        ? "resume-draft"
        : "ask"
```

Then the screen test mocks only the adapter:

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

The four permission states — granted, denied, blocked-forever, not-yet-asked — are a table test at T0 in `nextStep`, and one screen test each for the two that render differently. Standard mocks worth having in `test/setup.js`: AsyncStorage (official mock), `react-native-reanimated` (its own `/mock`), push notifications, geolocation, biometrics.

---

## Navigation

Test with a real navigator, not a mocked `navigation` prop. Mocking `navigate` gives you a test that asserts you called your own function with a string.

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

Worth testing here, because these break silently: deep links resolving to the right screen with the right params, back behaviour from a deep-linked screen, and that a screen unmounting cancels its in-flight requests.

---

## Platform differences

```js
it.each(["ios", "android"])("uses the %s date format", (os) => {
  jest.spyOn(Platform, "OS", "get").mockReturnValue(os)
  expect(formatDate(d("2026-01-15"))).toBe(os === "ios" ? "15 Jan 2026" : "15/01/2026")
})
```

Better still: don't branch on `Platform.OS` in logic at all — pass the difference in as a value, and the branch becomes a pure parameter you can table-test. `Platform.select` inside a component is fine; `Platform.OS` inside a business rule is a testability problem you're choosing to have.

---

## What device tests are for

Detox or Maestro, **5–10 tests, nightly, non-gating**. They're slow (minutes each), need simulators or a device farm, and are the flakiest tests you will own.

Reserve them for what genuinely cannot be checked anywhere else:

- The app launches and reaches the first screen on a real build
- Login, including the OS keychain/biometric prompt
- One core flow end to end on a real device
- Push notification tap → correct screen
- Deep link from cold start
- Permission dialogs, which are OS UI

Everything else — every rule, every state, every error path — belongs in the tiers above, where it runs in milliseconds. A team with 200 Detox tests has a suite that takes 90 minutes, fails a fifth of the time, and gets ignored; that's worse than having none, because it consumes the budget that would have paid for fast tests.

---

## Speed and CI

| Symptom                                    | Fix                                                                                                       |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| Jest takes minutes on a small suite        | `maxWorkers=50%`; check `transformIgnorePatterns` isn't transforming all of `node_modules`                |
| `SyntaxError: Cannot use import statement` | Add the package to `transformIgnorePatterns`                                                              |
| Animations hang tests                      | `jest.mock('react-native-reanimated', () => require('react-native-reanimated/mock'))`                     |
| Tests pass alone, fail together            | AsyncStorage or module state leaking — `clearMocks: true`, and clear the storage mock in `afterEach`      |
| `act()` warnings                           | You asserted before an async update settled — use `findBy*`/`waitFor`, not `fireEvent` + immediate assert |

Run the domain and api-client packages **outside** the RN Jest project, under Vitest, with no preset. They import nothing from React Native, so they shouldn't pay for its transform pipeline — and that's most of your tests.

---

## 🛠 Mini-project — offline-first, tested without a device

_One day._

1. Pick a feature that must work offline — a form, a favourite, a status change.
2. Model it as a pure reducer in `packages/domain`: `{ docs, pending, conflicts }` plus actions for `mutation`, `went-offline`, `came-online`, `server-update`.
3. Test-drive at least these, all at T0: queue while offline; replay in order; deduplicate the same edit twice; server-wins on a version conflict, recording the discarded value; a replay that fails with 409 doesn't retry forever.
4. Wire it to the screen. One RNTL test per visible state: pending badge, synced, conflict banner.
5. Mock AsyncStorage and test that a queue persisted before a kill is replayed after a restart.
6. Only now, run it on a real device with airplane mode — and count how many of the bugs you'd already caught.

**Deliverable:** an offline sync engine with a full test suite that runs in under a second, plus four screen tests.

**Proves:** the hardest part of mobile is not mobile-specific. Once it's a reducer, it's just [12. Katas](12-tutorial-katas.md) with better stakes.

---

Back to: [14. Large-project strategy](14-large-project-strategy.md) · Related: [17. Frontend](17-tdd-frontend-web.md) · [18. API & network tests](18-tdd-api-network.md) · [README](vsyst-technologies/docs/learning/tdd/README.md)
