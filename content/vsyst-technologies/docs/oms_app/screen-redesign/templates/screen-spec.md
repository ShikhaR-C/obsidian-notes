# Screen spec — `<ScreenName>` (template)

> Copy this file to `../screens/NN-<screen-slug>.md` and fill every section **before** any API or app code is written for the screen. The spec is the contract that the API tests, the design review and the screen tests all derive from. Sections marked ⛔ block the next step until filled; sections marked ◌ may be refined during the discussion session.
>
> **Status line (keep current):** Spec draft → Spec agreed (date) → API red → API green (PR #) → Design agreed (date) → Screen red → Screen green (PR #) → Shipped in app vX.Y → Old screen removed (PR #)

## 1. Purpose ⛔

- **One sentence:** what the user comes to this screen to do.
- **Replaces:** current screen(s) and file path(s), e.g. `src/screens/Customer/NewOrder/index.js`.
- **Roles:** dealer / customer / both / superadmin. Note any per-role differences in what is shown or allowed.
- **Entry points:** which screens navigate here and with what params. **Exit points:** where the user goes next.

## 2. What the user sees ⛔

List every piece of information on the screen, top to bottom, as a table. This table becomes the API response shape.

| #   | Element               | Data (source collection · field)                 | Derived? (formula)                                               | Role-visible  | Loading / empty / error state       |
| --- | --------------------- | ------------------------------------------------ | ---------------------------------------------------------------- | ------------- | ----------------------------------- |
| 1   | e.g. Available credit | `dealer_custs.max_cr_lmt`, `month_crdrs` balance | `available = limit − balance + adv_dep` (shared helper `Credit`) | customer only | skeleton / "No credit set" / banner |

Rule: **if it is not in this table, the API does not return it.** Field projection is decided here, not in the controller.

## 3. What the user can do ⛔

| #   | Action           | Trigger       | Precondition (business rule)           | API command           | Optimistic? | Success feedback           | Failure feedback               |
| --- | ---------------- | ------------- | -------------------------------------- | --------------------- | ----------- | -------------------------- | ------------------------------ |
| 1   | e.g. Place order | Submit button | credit not BLOCKED, qty ≤ diesel limit | `POST /api/v4/orders` | no          | toast + navigate to Orders | inline error from `error.code` |

Rule: every precondition here must already be enforced server-side (v3 service) or gets a v4 service rule **with an API test first**.

## 4. Design references ◌

- Figma image(s): `../designs/<screen-slug>/*.png` (drop the exported frames here; name them `01-default.png`, `02-empty.png`, `03-error.png`, …). If a live Figma file exists, paste the frame URL — it can be read directly through the Figma MCP.
- Design-system tokens used: typography variants, color roles, spacing (from `src/theme/`, built in foundation step F-APP-3 — see [[../02-foundations]]).
- States that need their own frame: loading, empty, error, offline, role variants, font-scale 200 %.
- **Discussion-session notes (dated):** decisions taken, alternatives rejected, open items.

## 5. API contract (v4) ⛔

One read endpoint per screen, plus one command endpoint per action that needs new behaviour. Write the contract as the test will assert it.

### 5.1 Read model

```
GET  /api/v4/screens/<screen-slug>?<id>=…&cursor=…&limit=…   (≤ 3 scalar ids + cursor)
POST /api/v4/screens/<screen-slug>                             (when the body carries filters)
Auth: Bearer (protect) · Roles: authorize(<roles>) · Tenant: derived from token, never from body
Body/query (validated, unknown keys rejected):
  { <ids the screen is parameterised by>, cursor?: string, limit?: number ≤ 100 (default 25) }
200:
  { success: true, data: { ...one key per §2 group... }, page?: { next: string|null, hasMore: boolean }, meta: { generatedAt, limit? } }
Errors (envelope { success: false, error: <message>, error_code, details? }):
  400 VALIDATION · 401 UNAUTHENTICATED · 403 FORBIDDEN / FORBIDDEN_ROLE (tenant or role mismatch) · 404 NOT_FOUND
Partial failure policy: critical sub-queries = fail whole request; optional sub-queries = null + `errors.<key>` enum code
```

### 5.2 Commands

```
POST /api/v4/<resource>/<verb>      (one per §3 action that is not already served by a v3 endpoint the new screen can keep using)
Idempotency: header `Idempotency-Key` where a double-tap would double-post
Side effects on Mongo (assert in test): …
Invalidation: which v4 read models must refetch (RTK tags): …
```

### 5.3 Test list — API (write these first, watch them fail)

`test/api_v4/screens/<screen-slug>.test.js`

- [ ] happy path: seeded world → every §2 key present, shape pinned by helper
- [ ] tenancy: user of company B gets 403/404 and **zero** foreign fields for every id the body accepts
- [ ] validation: bad ObjectId / unknown key → 400 VALIDATION with field name
- [ ] role: each role in §1 sees exactly its §2 subset
- [ ] pagination: `limit+1` probe, stable cursor across an insert
- [ ] partial failure: optional sub-query throws → 200 with `errors.<key>`
- [ ] each §3 command: precondition red case + green case + Mongo side effect + invalidation tag echo
- [ ] contract fixture captured (`yarn fixtures:export` → `fixtures/api_v4/screens_<slug>.json`)
- [ ] mutation smoke recorded in PR (rule disabled → exact tests red → revert)

## 6. Screen build plan ⛔

- **Folder:** `src/screens/v2/<Role>/<ScreenName>/` (`index.js`, `__tests__/<ScreenName>.test.js`, `components/`, `useScreenModel.js`, `strings.js`) — `<Role>` is `Dealer` or `Customer`, mirroring `src/screens/{Role}/`
- **Pure logic to extract first (Tier 1, TDD):** selectors/formatters/decisions this screen carries — list them; each is a `src/utils` or `src/helpers` function with its own `__tests__`.
- **RTK Query endpoint (Tier 2, MSW):** `getScreen_<Name>` + `<verb>_<Resource>` mutations in `src/store/apis/v4/<slug>.js`, `providesTags`/`invalidatesTags` per §5.2.
- **Screen test (Tier 3, RNTL) — decision cases only:** one test per row in §2 that is conditional, one per row in §3 (precondition true/false), loading/empty/error states, and the navigation on success. Uses the generated v4 fixture, never hand-rolled success bodies.
- **Cutover:** route name stays the same; the screen is registered in `src/navigation/screenRegistry.js` under the key `<Role>/<Route>`, behind the `screen_v2_<role>_<slug>` toggle (D10: house toggle managed from the superadmin DB-Actions page, default on); the old component is deleted in the release after.

## 7. Definition of done

- [ ] Spec agreed and dated; discussion notes captured in §4
- [ ] API PR: tests first (red commit → green commit), fixtures exported, flow-map row added in `docs/testing.md`, `yarn test:full` green
- [ ] App PR: Tier 1 → Tier 2 → Tier 3 tests, `yarn fixtures:pull`, `yarn test` green, no-network guard intact
- [ ] Manual: one request on screen open (v4), old screen still works on v3 for a v1.78 build
- [ ] Release gate green; screen listed in the release notes; backlog row updated
