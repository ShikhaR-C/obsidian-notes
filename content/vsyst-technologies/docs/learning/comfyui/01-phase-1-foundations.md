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

## 6. Lab Notes — Seed, Steps, CFG, and the Dead Negative, Proven

_All exercises above were run on this machine (2026-08-02), Z-Image Turbo bf16 at 1024×1024, via the local API. These are the results — and what each one actually means._

> Note: on this install the server runs at `http://127.0.0.1:8188`, not `:8000`. Outputs from this session are in `output/phase1/`, and the graph is saved in Workflows as `01-zimage-base`.

### Seed — the starting noise, and why it makes renders reproducible

Generation starts from a canvas of random noise, and the seed is the number that generates that noise. Same seed → same starting noise → same denoising path → **the same image, down to the last pixel**. The prompt is a _distribution_ of possible images; the seed picks one sample from it.

**Proven:** seed 42 rendered twice — with four other seeds rendered in between so the second run couldn't come from ComfyUI's cache — produced pixel-identical files (hash `30e880cf…` both times). The four in-between seeds (7111, 82634, 555001, 30928) each gave a different compass from the same prompt.

**Why it matters:** the seed is your control variable. Fix it while tuning a prompt and any change you see came from the prompt, not luck. Randomize to explore; fix to refine.

### Steps — denoising iterations, and where the floor is

Each step removes a slice of noise. Time scales linearly with steps, so this is the cost dial — and past the model's tuned range, extra steps change the image without improving it.

**Proven** (fixed seed 42):

| Steps | Time | Result                                                                  |
| ----- | ---- | ----------------------------------------------------------------------- |
| 2     | 6 s  | Recognisable compass — distillation at work — but soft, less map detail |
| 4     | 10 s | Close to final quality                                                  |
| 8     | 18 s | The tuned sweet spot. This is the keeper.                               |
| 16    | 34 s | Different, not better                                                   |
| 30    | 60 s | **3.3× the time** of 8 steps for a slightly different image             |

The floor is 8, exactly as the distillation promises. Paying for 30 buys you nothing but wait.

### CFG — guidance strength, and what "fried" really looks like

CFG pushes the image toward the positive prompt and away from the negative, and each step at cfg > 1 costs **two** model passes instead of one (the cfg 6 render took 36 s vs 18 s at cfg 1). Distilled models like Z-Image Turbo are trained to run at exactly cfg 1 — guidance off.

**Proven** (fixed seed 42): cfg 3 and 6 progressively over-commit, and at **cfg 10 the image is not "over-saturated" — it is destroyed**: clipped orange-and-white bands, no compass, no map, pure abstract wreckage. On a distilled model, raising CFG doesn't gradually fry the image; it obliterates it. If you ever see that look, check your CFG before anything else.

The rule stands: **distilled → cfg 1; full model → cfg 5–7.**

### The dead negative — why negative prompts do nothing here

The CFG math at each step is: `output = negative_prediction + cfg × (positive_prediction − negative_prediction)`. Set cfg = 1 and the negative terms cancel exactly — the negative prompt contributes zero, whatever you write in it.

**Proven:** replacing `ConditioningZeroOut` with a real encoded negative (`"blurry, ugly, watermark, deformed"`) at cfg 1 produced a **pixel-identical image** to the zeroed-out version — same hash, bit for bit. Not "similar": identical.

**Why it matters:** every "essential negative prompt list" you'll find online is a no-op on Z-Image Turbo, FLUX-dev, and anything running Lightning at cfg 1. `ConditioningZeroOut` isn't a trick — it's just honesty about the math, plus a saved text-encoder pass.

---

**Next:** [[02-phase-2-image-quality]] — FLUX, img2img, LoRAs, and turning 1024² into a clean 4096².
