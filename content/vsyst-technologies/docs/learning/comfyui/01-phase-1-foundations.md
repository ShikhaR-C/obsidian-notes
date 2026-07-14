# Phase 1 — Foundations: The Graph, and Your First Render

> Level: Easy | Time: ~45 min | Outcome: you can build the text→image graph from an empty canvas, from memory, and you know what every parameter does.

---

## 1. The One Idea

Every other tool (Midjourney, DALL·E, Firefly) gives you a **text box**. ComfyUI gives you the **pipeline that sits behind the text box**, with every stage exposed as a node you can rewire.

That's the whole trade. It is harder because nothing is hidden, and it is powerful for exactly the same reason. Once you internalise that a "workflow" is just data flowing through a graph, ComfyUI stops being intimidating — it's the same mental model as any pipeline you've built.

The universal shape, in every image workflow ever:

```
LOAD MODEL ─┐
            ├─→ SAMPLE (denoise) ─→ DECODE ─→ SAVE
ENCODE TEXT ┘        ↑
                 EMPTY LATENT
```

Four things happen, always, in this order:

1. **Load** the model weights.
2. **Encode** your prompt into numbers the model understands (this is the _text encoder_, and it is a separate model — remember that, it causes 90% of beginner errors).
3. **Sample** — start from pure noise and iteratively subtract noise, steered by your encoded prompt. This is the actual generation, and it's where all the time goes.
4. **Decode** the result from _latent space_ (a compressed 8×-smaller representation the model thinks in) back into pixels, using the **VAE**.

Latent space is worth one more sentence, because it explains a lot of the parameter names you're about to meet. The model never works on pixels — a 1024×1024 image is 3 million numbers, far too many. It works on a 128×128×16 _latent_ instead, ~50× smaller. The VAE is the codec that goes latent ↔ pixels. When you see `EmptySD3LatentImage`, that's "give me a canvas of pure noise, in latent space, at this size."

## 2. Launch

Open **Comfy Desktop** from Applications. It starts a local server (`http://127.0.0.1:8000`) and opens the UI. Nothing leaves your machine.

Orientation, in the order you'll need it:

| Thing                      | Where      | Why you care                                                                                                         |
| -------------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------- |
| **Canvas**                 | The middle | Your graph. Drag to pan, scroll to zoom.                                                                             |
| **Queue**                  | Bottom bar | `Run` submits. Multiple runs stack up and execute in order.                                                          |
| **Blueprints / Templates** | Sidebar    | 93 ready-made workflows ship with 0.27.1. Your cheat sheet.                                                          |
| **Workflows**              | Sidebar    | Your saved graphs. You already have 7 here.                                                                          |
| **Model Library**          | Sidebar    | What's on disk.                                                                                                      |
| **Manager**                | Sidebar    | Installs custom nodes. You currently have **zero** third-party nodes — that's fine, and honestly a good place to be. |

> **Add a node:** double-click empty canvas, type a name. **Connect:** drag from an output dot to an input dot. Colours must match — a purple `MODEL` output only accepts a purple `MODEL` input. The UI simply won't let you make a type error, which is more helpful than it sounds.

## 3. Build It Yourself

Don't load a template. Build the Z-Image Turbo graph from scratch — once — and it'll stick. Nine nodes.

Double-click the canvas and add each of these:

| #   | Node                      | Set it to                                                                          |
| --- | ------------------------- | ---------------------------------------------------------------------------------- |
| 1   | `UNETLoader`              | `z_image_turbo_bf16.safetensors`, weight_dtype `default`                           |
| 2   | `CLIPLoader`              | `qwen_3_4b.safetensors`, type **`lumina2`**, device `default`                      |
| 3   | `VAELoader`               | `ae.safetensors`                                                                   |
| 4   | `ModelSamplingAuraFlow`   | shift `3`                                                                          |
| 5   | `CLIPTextEncode`          | your prompt                                                                        |
| 6   | `ConditioningZeroOut`     | (no settings)                                                                      |
| 7   | `EmptySD3LatentImage`     | `1024 × 1024`, batch 1                                                             |
| 8   | `KSampler`                | steps **8**, cfg **1**, sampler `res_multistep`, scheduler `simple`, denoise `1.0` |
| 9   | `VAEDecode` → `SaveImage` | —                                                                                  |

Wire it:

```
UNETLoader ──→ ModelSamplingAuraFlow ──────────────→ KSampler.model
CLIPLoader ──→ CLIPTextEncode ──┬─────────────────→ KSampler.positive
                                └→ ConditioningZeroOut → KSampler.negative
EmptySD3LatentImage ──────────────────────────────→ KSampler.latent_image
KSampler ──→ VAEDecode.samples
VAELoader ──→ VAEDecode.vae
VAEDecode ──→ SaveImage
```

Prompt it with something concrete — vague prompts produce vague images:

```
A weathered brass compass on a folded nautical map, morning light
from a window, shallow depth of field, photographic
```

Hit **Run**. **~14 seconds.**

### Three things in that graph that will confuse you later

**Why is the model loaded by `UNETLoader` and not `CheckpointLoaderSimple`?** Two packaging formats exist. A _checkpoint_ (SDXL) bundles model + text encoder + VAE in one file, loaded with `CheckpointLoaderSimple` (three outputs). Modern models (Z-Image, FLUX, WAN, Qwen) ship the three pieces **separately**, so you load them with three nodes. More files to manage, but you can mix and match — and it's why the model↔encoder↔VAE matrix in [[08-reference]] exists.

**Why is the negative prompt zeroed out?** Because `cfg = 1`. CFG is the strength of "push toward positive, away from negative," and at exactly 1.0 the negative prompt is _mathematically ignored_. Turbo/Lightning models are distilled to run at cfg 1, so `ConditioningZeroOut` says "don't waste compute encoding a negative I'm going to ignore." **A negative prompt on Z-Image Turbo does nothing.** People burn hours on this.

**What is `ModelSamplingAuraFlow` / shift?** It reweights _when_ during the 8 steps the model does its coarse-structure work versus its fine-detail work. Shift 3 is the tuned default. Leave it alone until Phase 2.

## 4. The Six Parameters

This is the actual content of Phase 1. Everything else is wiring.

### Seed

The starting noise. Same seed + same everything else = **bit-identical image, every time**. This is your control variable: fix the seed while you tune a prompt, and any change you see came from the prompt. Set `randomize` to explore, `fixed` to refine. Reproducibility is a feature, not a footnote.

### Steps

How many denoising iterations. **Time scales linearly with steps** — this is your main cost dial.

More is _not_ better; it's asymptotic, and past the model's tuned range you're paying for nothing. Z-Image Turbo is _distilled_ to work in 8. Running it at 30 gives you a slightly different image, not a better one, in 4× the time.

| Model                                | Steps  | Why                   |
| ------------------------------------ | ------ | --------------------- |
| Z-Image Turbo                        | **8**  | Distilled             |
| FLUX.1-dev                           | **20** | Full model            |
| SDXL                                 | 20–30  | Full model            |
| Anything + a Lightning/LightX2V LoRA | **4**  | Distilled by the LoRA |

### CFG (Classifier-Free Guidance)

How hard to push toward the prompt. Low = the model improvises. High = it obeys, and past ~9 it obeys so hard the image goes contrasty, fried, and over-saturated.

| CFG     | Effect                                                                                                                           |
| ------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **1.0** | Guidance off. **Required** for all distilled models (Z-Image Turbo, FLUX-dev, anything + Lightning). Negative prompt is ignored. |
| 5–7     | Normal range for undistilled models (SDXL, WAN TI2V 5B).                                                                         |
| 9+      | Fried.                                                                                                                           |

The rule: **distilled model → cfg 1. Full model → cfg 5–7.** Getting this wrong is the #2 beginner error, right after the VAE mismatch.

### Sampler & Scheduler

The numerical method for solving the denoising ODE, and the spacing of the steps. You can lose a weekend here for very little payoff. Use the pairing the model was tuned with and move on:

| Model         | Sampler / Scheduler        |
| ------------- | -------------------------- |
| Z-Image Turbo | `res_multistep` / `simple` |
| FLUX.1-dev    | `euler` / `simple`         |
| SDXL          | `dpmpp_2m` / `karras`      |
| WAN video     | `uni_pc` / `simple`        |

### Denoise

How much of the input latent to destroy before rebuilding. `1.0` = ignore the input entirely (pure text→image). Below 1.0 it's the **img2img strength dial**, and it's the core of Phase 2. From an empty latent, always 1.0.

### Resolution

Models are trained at a native resolution and get _structurally_ worse away from it — not blurry, but wrong: duplicated limbs, repeated horizons, two heads. 1024×1024 is native for Z-Image, FLUX, and SDXL. Want 4K? Generate at 1024 and **upscale** (Phase 2). Never generate at 4K directly.

Total pixels drive time and memory, so 1024×1024 ≈ 1216×832 in cost. Useful ratios that stay near the native pixel budget:

| Ratio                    | Resolution  |
| ------------------------ | ----------- |
| 1:1                      | 1024 × 1024 |
| 3:2                      | 1216 × 832  |
| 16:9                     | 1344 × 768  |
| 9:16 (vertical / social) | 768 × 1344  |

## 5. Exercises

**5.1 — Isolate the seed.** Fix the seed at `42`. Run. Run again. Identical file. Now `randomize`, run 4 times. Same prompt, four different images. _This is the difference between a prompt and an image: a prompt is a distribution, a seed picks a sample from it._

**5.2 — Find the step floor.** Fixed seed, run at steps = 2, 4, 8, 16, 30. Look at where it stops improving. It's 8, and you just proved it — and you now know that 30 steps cost you 4× the time for nothing.

**5.3 — Break CFG on purpose.** Fixed seed, run at cfg = 1, 3, 6, 10. Watch it fry. Now you'll recognise the look instantly when it happens by accident.

**5.4 — Prove the negative is dead.** With cfg 1, replace `ConditioningZeroOut` with a `CLIPTextEncode` containing `"blurry, ugly, watermark, deformed"` and wire it to `negative`. Fixed seed. **The image will not change.** Confirms the theory and inoculates you against every "magic negative prompt" list on the internet.

**5.5 — Save it.** `Workflow → Save As` → `01-zimage-base`. This is your scratch template for Phase 2.

---

**Next:** [[02-phase-2-image-quality]] — FLUX, img2img, LoRAs, and turning 1024² into a clean 4096².
