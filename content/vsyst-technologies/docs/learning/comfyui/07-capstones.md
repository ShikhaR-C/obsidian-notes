# Phase 7 — Capstones

> Level: Capstone | Three projects, three tracks. Each one is a real deliverable, not an exercise. Do the one you actually need; do all three if you want to genuinely own this.

---

## Capstone A — Product Launch Kit (Marketing)

**Deliverable:** 6 hero images at 4096² + one 5-second ad loop, from a single flat product photo.

### Pipeline

```
product photo (one flat shot)
   │
   ├─→ [Lotus Depth] ────────────→ depth map
   │
   ├─→ [Z-Image + ControlNet(depth) @ 0.9]  × 6 environment prompts
   │        · modern fuel depot, morning light
   │        · clean studio, white cyc, softbox
   │        · industrial warehouse, dramatic side light
   │        · outdoor forecourt, golden hour
   │        · dark technical backdrop, rim light
   │        · overhead flat-lay on concrete
   │                    ↓
   │        6 images, product geometry IDENTICAL, worlds different
   │                    ↓
   │        [RealESRGAN 4×] → [re-diffuse @ denoise 0.3] → 6 × 4096²
   │
   └─→ pick the best → [WAN 2.2 I2V 14B + LightX2V] → 640×640×81
                              ↓
                       [RealESRGAN 4×] → [FILM ×2]
                              ↓
                       5 s @ 32 fps ad loop
```

### Why each choice

- **Depth, not Canny** — you want the product's _form_ locked while the model relights the surface per scene. Canny traces reflections and gives you a pasted-on look ([[03-phase-3-control-and-editing]] §2).
- **ControlNet, not six separate Qwen edits** — six variants must _agree_ on geometry. ControlNet enforces that from a single depth map; six independent edits will drift.
- **I2V, not T2V** — you already have the perfect still. Animating it preserves everything you got right ([[04-phase-4-video]] §6).
- **Generate small, finish big** — 640² + upscale + interpolate beats a native high-res render by ~15× in cost, at higher fps ([[04-phase-4-video]] §5).

### Success criteria

Open all six at 100% zoom. **The product must be pixel-identical in shape across all six.** If it isn't, raise ControlNet strength toward 1.0. If it's identical but looks pasted-on, you're using Canny — switch to depth.

### Then automate it

Once the graph is right, export API format and run it as a loop over your SKU list ([[06-phase-6-automation-api-mcp]] §4). That's the difference between "I made six images" and "I have a product image pipeline."

---

## Capstone B — Character in Three Shots (Narrative)

**Deliverable:** one character, three different shots, recognisably the same person, cut together.

### Pipeline

```
1. LOCK THE CHARACTER
   FLUX.1-dev, iterate until the hero still is exactly right.
   (~30 s per try. Iterate HERE, not in video — this is the whole point.)
        ↓
   hero_still.png
        ↓
2. SHOT LIST — three control videos
   Film 3 s of yourself on your phone, three times:
     · shot 1: turns toward camera
     · shot 2: walks left to right
     · shot 3: looks up, reacts
        ↓
   [SDPose] → three pose videos
        ↓
3. GENERATE — VACE 14B, once per shot
   reference_image = hero_still.png   ← identity comes from here
   control_video   = pose video N     ← motion comes from here
   ⚠ weight_dtype = fp8_e4m3fn
   ⚠ CausVid LoRA @ 0.30, 4 steps, cfg 1, uni_pc
   ⚠ wire TrimVideoLatent (or your reference frame flashes at the start)
        ↓
4. FINISH
   [RealESRGAN 4×] → [FILM ×2] → three clips @ 32 fps
        ↓
5. CUT
   [Merge Videos] blueprint, or any editor.
```

### The core idea

**Identity comes from one input, motion from another.** That separation is what VACE exists for, and it's why this works when prompt-only approaches don't ([[05-phase-5-advanced-video]] §3).

### Success criteria

Show the three clips to someone who hasn't seen the hero still. Ask: _"is this the same person?"_ If they hesitate, your `reference_image` isn't strong enough — check that it's a clean, well-lit, front-facing still. A muddy reference gives a muddy identity.

### Expect

~10–15 min per shot after the Phase 5 fixes _(est.)_. Before them, ~80 min per shot. **Do the fixes first** or this capstone will eat your whole day.

---

## Capstone C — The Full Stack (Broad)

**Deliverable:** one object, carried through every capability you own. This is the "I actually understand ComfyUI now" project.

| #   | Stage        | Tool                                       | Out                                         |
| --- | ------------ | ------------------------------------------ | ------------------------------------------- |
| 1   | **Generate** | Z-Image Turbo, 8 steps                     | An object on a plain background (14 s)      |
| 2   | **Refine**   | FLUX, img2img @ denoise 0.4                | Same object, better materials (30 s)        |
| 3   | **Edit**     | Qwen-Image-Edit + Lightning                | "place it on a workbench in a garage"       |
| 4   | **Control**  | Depth → ControlNet                         | Same object, 3 more environments            |
| 5   | **Upscale**  | RealESRGAN → re-diffuse @ 0.3              | 4096²                                       |
| 6   | **Animate**  | WAN 2.2 I2V 14B + LightX2V                 | 640×640×81, camera orbits it                |
| 7   | **Finish**   | RealESRGAN + FILM ×2                       | 2560² @ 32 fps                              |
| 8   | **3D**       | Hunyuan3D 2.1 (`Image to Model` blueprint) | A textured `.glb` mesh                      |
| 9   | **Automate** | MCP / API                                  | Regenerate the whole thing from one command |

Step 8 is the one nobody expects to work. Hunyuan3D 2.1 turns your single image into an actual 3D mesh you can open in Blender. The `Image to Model (Hunyuan3d 2.1)` blueprint is installed and your model is on disk — it will run today.

### Success criteria

You did every step without looking up how. When that's true, you're done with this course.

---

## Where to Go Next

**Fill the gaps.** [[08-reference]] has the download list — CausVid first (biggest win), then a proper `clip_vision`, then WAN 2.2 T2V 14B if you want native text→video.

**Train a LoRA.** The one thing this course doesn't cover. 20–30 images of a face, product, or style, and you get a model that knows it natively — stronger than any reference-image trick. `ComfyUI-FluxTrainer` via the Manager, or Kohya outside ComfyUI. This is the real answer to character consistency.

**Custom nodes.** You currently have **zero** third-party nodes, which is a clean and enviable place to be. Add them one at a time, with a reason. The three worth knowing about:

- `ComfyUI-VideoHelperSuite` — better video I/O than core
- `ComfyUI-Impact-Pack` — face/hand detail fixing
- `rgthree-comfy` — quality-of-life for large graphs

Resist installing a 40-node bundle because a YouTube tutorial did. That's how ComfyUI installs become unmaintainable, and it's how you end up unable to tell whether a bug is yours or a node's.

**Measure and write it down.** Several tables in these docs are marked _(est.)_. Replace them with your real numbers as you go — that's what turns this from a tutorial into _your_ reference.

---

← [[06-phase-6-automation-api-mcp]] · [[08-reference]] →
