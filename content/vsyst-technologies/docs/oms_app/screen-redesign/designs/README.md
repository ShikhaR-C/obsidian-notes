# Design frames — drop folder

One sub-folder per screen, named with the screen slug used by its spec (`screens/NN-<slug>.md`):

```
designs/
  <screen-slug>/
    01-default.png
    02-empty.png
    03-error.png
    04-loading.png        (optional)
    05-<role-variant>.png (optional)
    notes.md              (optional: what the frame shows that the image cannot — interactions, gestures)
```

- Export frames from Figma at 2× so text is legible in review; PNG or JPG.
- If a **live Figma file** exists, record its URL and the frame links here — frames can then be read directly through the Figma MCP during a session instead of exporting images:

| Screen slug | Figma frame URL                                                                                                                                                                  | Last synced |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- |
| `customers` | no live file — `customers/01-default.png` is the customer-side **"Dealers"** frame (1×, 414 × 896, from `~/Downloads/Dealers Screen3sep.png`); Customers mirrors it with the substitutions in [[../screens/01-customers#2. What the user sees ⛔\|spec §2]]. `customers/02-filter-sheet.png` is the **Customers filter sheet** (1×, from `~/Downloads/Filter 3sep Customers Screen.png`, dropped by the user) — input to sub-spec `01b` | 2026-09-03  |

- Frames are inputs to Step 1 (plan) and Step 3 (design) of [[../03-per-screen-playbook]]; decisions taken against them are written into the spec's §4, dated. The frame itself is never the spec.
