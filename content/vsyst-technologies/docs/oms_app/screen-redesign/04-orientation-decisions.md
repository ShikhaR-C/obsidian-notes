# 04 — Orientation and large screens: the questions, answered

> **What this is:** the three questions the user asked on **2026-09-10**, recorded **verbatim**, each answered from the code as it stood that day. This is a **decision-reference** doc, not a plan — it exists so that the next person (or the next session) who proposes "let's just turn on landscape" can be shown the measurements instead of re-deriving them.
> **Companions:** [[02-foundations#F-APP-9 — Orientation and large screens|02 §F-APP-9]] (the foundation as specified and built), `dzzlo_oms_app/docs/testing.md` → "Window classes and orientation (F-APP-9)" (the mechanism as it works), `dzzlo_oms_app/AI.md` (the non-negotiable).
> **Status:** Q1 and Q2 are **settled** — they describe how the app already works. Q3 is **open**, with a recommended first step.

---

## The state of things on 2026-09-10

Worth stating plainly, because it surprises people: **the native unlock already shipped.** F-APP-9 did it.

| Layer             | State                                                                                                           |
| ----------------- | --------------------------------------------------------------------------------------------------------------- |
| iOS `Info.plist`  | `UISupportedInterfaceOrientations` = Portrait + LandscapeLeft + LandscapeRight; `~ipad` adds PortraitUpsideDown |
| Android manifest  | `screenOrientation="unspecified"`, `resizeableActivity="true"`, `configChanges` absorbs rotation/fold           |
| JS                | **8 native stacks** each pin `orientation: 'portrait'` in their shared `screenOptions`                          |
| The one exception | `Dealer/Customers` (v2) takes `'all'` via `screenOptionsFor` in the registry                                    |

So the operating system is ready today. What holds the app portrait is **six lines of JavaScript** across `Dealer/Main.js`, `Dealer/TrnTab.js`, `Customer/Main.js`, `Customer/TrnTab.js`, `Common/Details.js`, `Auth/index.js`, `Auth/ValidateUser.js` and `Guest/Main.js`.

That is precisely why the question below is the right one to ask — and why the answer is no.

---

## Q1 — "why cant we just remove the portrait pin."

**Answer: because the pin is not what makes v1 portrait-only. It is what protects v1 from a portrait assumption already baked into its layout arithmetic.** Removing the pin does not make v1 responsive. It makes v1 _wrong_, and it does so silently.

### The mechanism

**133 v1 files** execute this at **module scope** — at import, once:

```js
const { width: totalWidth, height: totalHeight } = Dimensions.get("window")
```

The captured shapes, counted across `src/` on 2026-09-10:

| Form                                             | Files                                                   |
| ------------------------------------------------ | ------------------------------------------------------- |
| `{ width: totalWidth, height: totalHeight }`     | 76                                                      |
| `{ width: totalWidth }`                          | 34                                                      |
| `{ width: SCREEN_WIDTH, height: SCREEN_HEIGHT }` | 9                                                       |
| `{ height: totalHeight }`                        | 7                                                       |
| other (`SIZE`, `DEVICE_WIDTH`, …)                | 7                                                       |
| **module-scope total**                           | **133** (of 137 files touching `Dimensions.get` at all) |

`configChanges` **deliberately** keeps the JS context alive across rotation and fold — that is the correct choice, since restarting it would blank the user's in-progress order — so those constants **never update for the life of the process**. **518 sites** then do arithmetic on them, with roughly forty magic divisors:

`totalWidth / 1.1` (54×) · `totalHeight / 2` (39×) · `totalWidth / 4` (14×) · `totalHeight / 3` (13×) · `totalWidth / 1.3` (11×) · `totalWidth / 1.02` (10×) · …

### What that costs, concretely

`src/screens/Dealer/Customers/index.js:398`

```js
height: totalHeight / 2,
```

- Launch **portrait** on an iPhone 17 → `totalHeight` = 844 → the spacer is **422 pt**. Rotate → the window is **390 pt tall**. The spacer is now taller than the entire window.
- Launch **in landscape** (Fold opened, iPad, autorotate on) → `totalHeight` = 390 → the spacer is **195 pt**, and rotating to portrait strands it at 195 in an 844 pt window.

**Which way it breaks depends on launch orientation, which is a race.** The same pattern sits at `Discount.js:465`, `CustSettings.js:1261`, `PsocProds.js:592`, `SetProductRate.js:201`, `NewVoucher/index.js:703`, `AttachInvs.js:681` (`/3`), `NewInvSummary.js:1279` (`* 0.2`) and ~35 more.

Add the surrounding surface area: **78 bottom-sheet files** (`@gorhom/bottom-sheet`), **109** `position: 'absolute'` sites, **64** percentage heights.

### The part that makes it dangerous rather than merely wrong

**No test would go red.** v1 has essentially no screen tests, and the Tier 3 rule in `AI.md` is that screen tests assert **decisions, never layout**. The 65-suite run stays green. The breakage ships, and the first report is a dealer who cannot complete an invoice.

### The verdict

Removing the pin is a **one-line change with a 518-site blast radius and zero test coverage**. The objection is not that every screen would break — it is that **you cannot know which ones would**, and you would find out in production, from customers.

The pin stays. A screen earns `'all'` when someone has looked at it.

---

## Q2 — "do we need to redesign screen for different orientation or do can we have som egeneral designs."

**Answer: general designs. And this is already demonstrated in the codebase, not merely asserted.**

### The evidence

The Customers v2 screen ships `orientation: 'all'` today. Search every screen and component for `isLandscape` → **zero hits**. `useWindowClass()` returns `isLandscape` and `compactHeight`, and **no screen uses either one**.

What screens actually branch on is `sizeClass` and `contentWidth`:

- `v2/Dealer/Customers/index.js:199` — `const shareChromeRow = sizeClass !== 'compact';`
- `components/CustomerRow.js:229` — `tilesStack(fontScale, contentWidth)`
- `components/SortMenu.js:142` — `sortMenuWidth(fontScale, contentWidth)`
- `components/CreditSheet.js:468` — `sizeClass === 'compact' ? … : …`

### The principle

**Landscape is not a design target.** It is one of several ways to arrive at a wide window. A phone on its side (844 × 390), a Fold unfolded (~673), an iPad in Split View, a resized window on a Mac — all pose the same two questions, asked once: **how much room across, and how much down.** Design for the window and orientation stops being a case at all.

Hence the rule: **one responsive layout per screen, keyed to width class** — never two layouts keyed to orientation. `Container` is the default answer (contain at `READABLE_WIDTH` = 640 pt from `medium` up, full width in `compact`), and a screen branches further only where it earns it. This is also why the classes are Material's window size classes and not "phone / tablet": the device is not the question.

### The one real exception — height

A wide-**short** window (a phone on its side) genuinely differs from a wide-**tall** one (a tablet). A half-height sheet, a tall header, a two-line title stop fitting. That is what `COMPACT_HEIGHT = 500` and F-APP-9 decision 4 are for.

Note the framing carefully: it is expressed as **`height < 500`**, not as "landscape". Same discipline — the shape of the window, not the posture of the device.

**Open, from [[02-foundations]] decision 4:** `compactHeight` is defined and tested but **no screen consumes it yet**. The first screen with a tall header or a half-height sheet in a short window is where it earns its keep.

---

## Q3 — "can we split the screen or use multiple screens for phones that can unfold - having one screen for lists, other for filter etc.?"

**Answer: yes, and the architecture deliberately left the door open — but the cost is in navigation, not layout, and the two examples in the question differ enormously in price.**

### It was anticipated

`src/components/v2/Container.js`, in its own docstring:

> That is the DEFAULT answer, not the only one. A screen that genuinely earns the width (a two-pane list/detail, a table) branches on `useWindowClass()` itself.

And [[02-foundations]] F-APP-9 decision 3 deferred it in as many words: _"Two-pane layouts (list + detail) are a later, per-screen design decision, not a foundation."_

### Why list + detail is expensive

In `compact`, tapping a customer **pushes a route**. In `expanded`, it should fill the right pane **without pushing**. The same tap means two different things — and **the window can change while the app is running**. Three hard cases follow:

1. **Unfold with a route pushed.** The user taps a customer in compact (detail is on the stack), then unfolds. The detail must _collapse out of the stack_ and become the right pane, or a detail screen sits on top of a two-pane layout.
2. **Fold with a pane open.** The reverse: the right pane must _become_ a pushed route, or the selection is silently lost.
3. **Back.** In compact, back pops the detail. In expanded there is nothing to pop — back should either leave the screen or clear the selection. Deep links and notification taps land in whichever mode is current at the time.

**React Navigation 7 ships no split-view navigator.** (`@react-navigation/native` 7.2, `native-stack` 7.14 — checked 2026-09-10.) This would be a house mechanism, and it is a change to the navigation model, not a stylesheet.

### Why list + filter is cheap — and why it should go first

The question's own example is the easy one, and the distinction is the useful output of this discussion:

| Pairing           | What the second pane holds                                             | Cost                                                                                                            |
| ----------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **list + filter** | **screen state** — `FilterChips`, `SortMenu`, `CreditSheet` selections | **Low.** A pure layout branch on `sizeClass`. No route pushed, no back-button question, no fold-transition case |
| **list + detail** | **navigation state** — a route                                         | **High.** All three cases above, plus a house navigator                                                         |

Filter/sort is not navigation. It is state the screen already owns. Turning the filter sheet into a **persistent rail from `expanded`** — sheet in compact, rail when there is room — changes nothing about routing, is testable with the existing `withWindow({ width, height })` harness, and delivers the visible foldable and tablet win.

### Recommendation (not yet decided)

1. **First:** filter-as-a-rail on a redesigned screen, as a per-screen design decision inside [[03-per-screen-playbook]] Step 3. Cheap, reversible, no new mechanism.
2. **Later:** list/detail two-pane, only after a screen genuinely wants it, and with its own design session — because it buys a navigation-model change.

Deliberately **not** decided here: whether the two-pane ever happens, and on which screen. The playbook decides that per screen, and the door is open either way.

---

## What follows from all three

The route forward is the one F-APP-9 was built for, and these answers do not change it:

- **v1 stays pinned.** Not forever — until each screen is either redesigned or deliberately examined. The 518 sites are the reason, and they belong to code that is scheduled for replacement anyway. Converting them in place would cost redesign-sized effort on screens about to be deleted.
- **A v2 screen is born unlocked**, because it was built against window classes from the start. The registry ties orientation to the rollback toggle, so one flag moves both — a screen rolled back to v1 takes its portrait pin back with it.
- **Landscape arrives screen by screen**, as a property of being redesigned, not as a release-day switch.

If the app is ever wanted in landscape _sooner_ than the redesign delivers it, the honest options are to unlock a **chosen subset** of v1 routes after actually examining them (the registry currently expects a v1/v2 pair, so a v1-only unlock needs a small extension), or to accept the risk described in Q1. Both are decisions for the user; neither is the default.

---

## Follow-on

The **2026-09-10** follow-up question — _"if we make them landscape now, the keyboard would eat up half of the screen; the header, search and filter would cover the other half"_ — is answered with measurements and a build plan in **[[05-landscape-chrome-and-keyboard]]**. Short version: the question understated it. At normal text size a landscape phone fits **one** row before the keyboard appears and **none** after; and the same screen already fits **zero** rows in PORTRAIT at `fontScale` 2.143 with the keyboard open, which is a live bug rather than an orientation question.

### Two amendments to Q3, from that research (2026-09-10)

Q3's answer above stands in substance — chrome should go vertical in a wide window — but the platform research corrected the component and narrowed the scope. Recorded here rather than edited into Q3, so the original reasoning and its correction both stay visible.

1. **Filters go in a SIDE SHEET, not a navigation rail.** Q3 and the recommendation said "filter-as-a-rail". M3 forbids that: the navigation rail's anatomy admits only destinations, a menu and a FAB, and the expanded-breakpoint page says _"For sorting, filtering, or secondary navigation, use tabs or other components directly in the pane."_ The sanctioned component is a **side sheet** — max 400 dp, spanning the screen height, on the **trailing** edge, whose own documented example use is _"a list of actions that affect the screen's primary content, such as filters."_ Same geometry, right component, opposite edge.
2. **Two-pane list/detail is a TABLET/FOLDABLE pattern, not a landscape-phone one.** Q3 called it "expensive but possible". On a landscape phone it is closer to impossible: Android states two-pane layouts are _"not practical"_ at compact height, and Apple's size-class table puts standard and Pro iPhones at **compact width even in landscape**, so `UISplitViewController` collapses automatically — one pane whether you asked or not. Only Plus / Max / Air report regular width. Two-pane remains available where width **and** height are regular; it is not the answer for a phone on its side.

---

## Settled 2026-09-10: landscape is v2-only

The user decided: **landscape is for redesigned v2 screens only; v1 is never unlocked.**

This closes the last option left open in §What follows above. There is no "unlock a chosen subset of v1 after examining them", so the registry needs no extension for v1-only routes, and **no v1 screen is ever audited for landscape**. The eight v1 stacks keep `orientation: 'portrait'` for the life of every screen in them; a route becomes rotatable only by being redesigned, and takes its orientation from `screenOptionsFor` when it does.

The practical consequence for the numbers in Q1: the **133** module-scope `Dimensions.get` files and their **518** consumption sites are now formally _never fixed_. They are deleted along with their screen when it is replaced. The measurements in Q1 stop being a work estimate and become the standing justification for the pin.

Build plan for the v2 side: [[05-landscape-chrome-and-keyboard]].
