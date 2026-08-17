# Phase 3 — Directed Generation: ControlNet and Instruction Editing

> Level: Intermediate | Time: ~1.5 hr | Outcome: you can dictate the _structure_ of an image (not just describe it), and edit an existing image with a sentence. This is where generation stops being a lottery.
>
> **Tooling (planned):** this phase is being built into Comfy Studio — **Edges / Depth / Pose** as three separate options, plus **instruction editing** with Qwen. The build plan is [[10-comfy-studio-phase-3-plan]] (2026-08-16); it also carries three corrections to §2 and §3 below, where the shipped blueprint has moved on from this text.

---

## 1. The Shift

Phases 1–2 are all _description_. You say what you want and the model interprets. Even at cfg 7 with a perfect prompt, you cannot say **"the product sits exactly here, at exactly this angle."**

Two techniques fix that, and together they're the whole professional workflow:

| Technique               | You supply                             | The model must obey                        |
| ----------------------- | -------------------------------------- | ------------------------------------------ |
| **ControlNet**          | A structure map (edges / depth / pose) | The geometry                               |
| **Instruction editing** | An existing image + a sentence         | Everything except what you asked to change |

## 2. ControlNet — Dictating Geometry

A ControlNet conditions generation on a **structure map** extracted from a reference image. You keep the composition, replace everything else.

You downloaded `Z-Image-Turbo-Fun-Controlnet-Union.safetensors` — a **Union** model, meaning one file handles Canny _and_ Depth _and_ Pose. It lives in `model_patches/`, not `controlnet/`, and this matters because it's loaded differently from a classic SDXL ControlNet.

### Wiring (verified against the shipped blueprint)

```
UNETLoader ─────────┐
ModelPatchLoader ───┤
VAELoader ──────────┼→ QwenImageDiffsynthControlnet → ModelSamplingAuraFlow → KSampler.model
control image ──────┘         (strength)
```

| Node                           | Setting                                                                      |
| ------------------------------ | ---------------------------------------------------------------------------- |
| `ModelPatchLoader`             | `Z-Image-Turbo-Fun-Controlnet-Union.safetensors`                             |
| `QwenImageDiffsynthControlnet` | inputs: `model`, `model_patch`, **`vae`**, `image`, `strength` (default 1.0) |
| `KSampler`                     | steps **9**, cfg 1, `res_multistep` / `simple`                               |

Three traps here:

- **The apply node needs the VAE.** It encodes your control image into latent space. Forget it and you get a type error, or worse, confusion.
- **The node is called `QwenImageDiffsynthControlnet`** even though you're using Z-Image. That's not a mistake — it's a shared implementation, and it's what the shipped blueprint uses. There is _also_ a `ZImageFunControlnet` node (category `model/patch/z-image`) that takes the same patch and additionally exposes `inpaint_image` + `mask`. Use that one when you want ControlNet **and** inpainting from the same model.
- **Steps go to 9, not 8.** Minor, but it's what the blueprint ships.

### The three control types

**Canny (edges)** — core `Canny` node, thresholds `low 0.3 / high 0.4`. Hard line art. Use when you want to preserve _exact_ contours: a product silhouette, a logo, an architectural line.

**Depth** — you downloaded `lotus-depth-d-v1-1.safetensors` (+ its `vae-ft-mse-840000-ema-pruned.safetensors`). Produces a greyscale distance map. Preserves 3D _form_ and spatial layout while giving the model freedom on surface detail. **This is usually the right choice** — Canny is often too literal, forcing the model to trace every stray edge.

**Pose** — `sdpose_wholebody_fp16.safetensors` + `rt_detr_v4-x-hgnet_fp16.safetensors` (detector). Extracts a human skeleton. Locks body position, frees everything else — clothing, identity, setting.

Fastest route: open the **`Canny to Image (Z-Image-Turbo)`**, **`Depth to Image (Z-Image-Turbo)`**, and **`Pose to Image (Z-Image-Turbo)`** blueprints. As of today all three have their models and will run. Drop an image in and hit Run.

### Strength

| Strength    | Effect                                              |
| ----------- | --------------------------------------------------- |
| 0.4–0.6     | Suggestion. Model may deviate.                      |
| **0.8–1.0** | Obey. The default.                                  |
| > 1.0       | Over-constrained — artefacts, rigid, "traced" look. |

### Normalising the input

The blueprint feeds the control image through `ImageScaleToTotalPixels` (target **1.0 megapixel**) and derives the latent size from `GetImageSize`. Copy this. It means any input resolution gets normalised to the model's comfort zone while preserving aspect ratio, and your output matches the control image's shape automatically. It's a small thing that prevents a lot of stretched, doubled output.

## 3. Qwen-Image-Edit — Editing With a Sentence

ControlNet controls _generation_. Qwen-Image-Edit controls _modification_: give it an image and an instruction — "replace the background with a warehouse loading bay" — and it changes that and leaves everything else alone.

### ⚠️ Read this before you open the blueprint

**The `Image Edit (Qwen 2509)` blueprint will not run on your install.** It expects the _2509_ release; you have the original. Three changes:

| Blueprint wants                                               | You have                                                     |
| ------------------------------------------------------------- | ------------------------------------------------------------ |
| `qwen_image_edit_2509_fp8_e4m3fn.safetensors`                 | **`qwen_image_edit_fp8_e4m3fn.safetensors`**                 |
| `Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors` | **`Qwen-Image-Edit-Lightning-4steps-V1.0-bf16.safetensors`** |
| node `TextEncodeQwenImageEditPlus`                            | swap to **`TextEncodeQwenImageEdit`**                        |

That last one is the non-obvious one. The `...Plus` node is built for 2509's multi-reference-image capability. Your original model uses the single-image `TextEncodeQwenImageEdit`. Swap the node, don't just swap the dropdowns.

_(Planned exit from this workaround: the Tier-1 plan in [[00_README]] stages the 2509 model itself — once downloaded, the blueprint runs as shipped and this section becomes historical.)_

### The graph

| Node                      | Setting                                                                |
| ------------------------- | ---------------------------------------------------------------------- |
| `UNETLoader`              | `qwen_image_edit_fp8_e4m3fn.safetensors`                               |
| `CLIPLoader`              | `qwen_2.5_vl_7b_fp8_scaled.safetensors`, type **`qwen_image`**         |
| `VAELoader`               | **`qwen_image_vae.safetensors`** ← not `ae.safetensors`                |
| `LoraLoaderModelOnly`     | `Qwen-Image-Edit-Lightning-4steps-V1.0-bf16.safetensors`, strength 1.0 |
| `ModelSamplingAuraFlow`   | shift 3                                                                |
| `CFGNorm`                 | 1.0                                                                    |
| `TextEncodeQwenImageEdit` | your instruction + the source image                                    |
| `KSampler`                | steps **4**, cfg **1**, `euler` / `simple`                             |

`qwen_2.5_vl_7b` is a **vision-language** model — it _looks at your image_ while reading your instruction. That's why you can say "make **his** jacket red" and it knows who "he" is. It's a different mechanism from ControlNet entirely.

### Writing instructions

| Do                                                                                   | Don't                                     |
| ------------------------------------------------------------------------------------ | ----------------------------------------- |
| "Replace the background with a modern warehouse interior, keep the product lighting" | "warehouse, industrial, 8k, professional" |
| "Change the jacket to dark green leather"                                            | "green jacket"                            |
| "Remove the person on the left"                                                      | "no person"                               |

Describe the **edit**, not the destination. It's an instruction-following model, not a prompt-matching one — the grammar you use with Claude works better here than the grammar you use with Midjourney.

## 4. Putting It Together — The Product Shot Pipeline

Your marketing use case, end to end. Say you have one flat photo of a nozzle/dispenser and you need six on-brand marketing images.

```
                                  ┌→ [Qwen-Image-Edit] "place on a clean concrete
                                  │   floor in a modern fuel depot, morning light"
[photo] → [Lotus Depth] → depth ──┤
                                  └→ [Z-Image + ControlNet(depth), strength 0.9]
                                        6 different settings, product geometry locked
                                              ↓
                                     [RealESRGAN 4×] → [re-diffuse @ 0.3]
                                              ↓
                                          4096² hero assets
```

**Why depth and not canny:** you want the product's _form_ preserved, and the model free to relight the surface for each scene. Canny would force it to trace every edge including reflections, and you'd get a rigid, pasted-on look.

**Why ControlNet and not just Qwen-Edit:** Qwen-Edit is superb at one-off, targeted changes. ControlNet is what you want when you need _six variants that all agree on geometry_ — the product must be identical across the set, only the world changes.

For a character instead of a product, swap Depth for **Pose** and the same structure gives you one character in six poses/settings. That's the seed of the consistency work in Phase 5.

## 5. Exercises

**5.1 — Depth vs. Canny, same source.** Take one photo. Run the Depth blueprint and the Canny blueprint with the same prompt and seed. Canny will feel traced; depth will feel _reinterpreted_. This single comparison tells you which to reach for forever after.

**5.2 — Strength sweep.** Depth ControlNet at strength 0.3 / 0.6 / 0.9 / 1.2. Watch it go from "loosely inspired by" to "rigidly traced."

**5.3 — Fix the Qwen blueprint.** Open `Image Edit (Qwen 2509)`, apply the three changes above, run an edit on a photo. Save as `03-qwen-edit-fixed` so you never have to rediscover it.

**5.4 — Six-variant product set.** Run the pipeline in §4. Photo → depth → six ControlNet renders with different environment prompts → upscale. Check at 100% that the product geometry is genuinely identical across all six. That's the deliverable a client would actually accept.

---

**Next:** [[04-phase-4-video]] — WAN 2.2, and why your video model is secretly two models.
