# Phase 2 — Image Quality: FLUX, img2img, LoRAs, Upscaling

> Level: Easy → Intermediate | Time: ~1 hr | Outcome: you can pick the right model for a job, refine an existing image instead of re-rolling the dice, and produce a clean 4096² print-quality file.
>
> **Tooling:** everything in this phase is now drivable from Comfy Studio (`comfy-studio/`, http://127.0.0.1:8787) — engine picker (Z-Image / FLUX), Refine (img2img), Enlarge & sharpen (upscale → tiled re-diffuse, with the `-gan` reference save), LoRA section, and the denoise ladder as a one-click experiment. Added 2026-08-11.

---

## 1. FLUX.1-dev — When Z-Image Isn't Enough

Z-Image Turbo is fast and genuinely good. FLUX is _better at listening_. Use FLUX when the prompt has structure the model must respect — text in the image, a specific count of objects, an unusual spatial relationship ("the cat is **under** the table, behind the chair"). Distilled models tend to smooth those away; FLUX holds them.

Build it (it's Phase 1's graph with two changes):

| Node                                     | Setting                                                                           |
| ---------------------------------------- | --------------------------------------------------------------------------------- |
| `UNETLoader`                             | `flux1-dev.safetensors`, weight_dtype `default`                                   |
| **`DualCLIPLoader`**                     | `clip_l.safetensors`, `t5xxl_fp16.safetensors`, type **`flux`**, device `default` |
| `VAELoader`                              | `ae.safetensors` — _same VAE as Z-Image_                                          |
| `EmptySD3LatentImage`                    | 1024 × 1024                                                                       |
| `CLIPTextEncode` → `ConditioningZeroOut` | positive / negative                                                               |
| `KSampler`                               | steps **20**, cfg **1**, `euler` / `simple`                                       |

Note there's **no `ModelSamplingAuraFlow`** here — that was Z-Image-specific. And note FLUX needs _two_ text encoders: `clip_l` (fast, keyword-ish) and `t5xxl` (a real language model that understands sentences). T5 is why FLUX follows instructions: it isn't matching keywords, it's reading English.

**~30 seconds** on your machine. Roughly 2× Z-Image's cost for a meaningful quality jump.

### FLUX's second guidance knob

FLUX has **two** guidance parameters and they are not the same thing:

- **CFG** on the KSampler → keep at **1.0**. FLUX-dev is distilled; raising this fries the image.
- **Guidance** (the `FluxGuidance` node) → the real dial. Default **3.5**.

The blueprint omits `FluxGuidance` entirely and relies on the internal default, which is fine. Insert one between `CLIPTextEncode` and `KSampler.positive` when you want the control:

| Guidance | Look                                               |
| -------- | -------------------------------------------------- |
| 1.5–2.5  | Loose, painterly, more variation                   |
| **3.5**  | Default. Balanced.                                 |
| 5–7      | Tight prompt adherence, flatter, more "AI-looking" |

### Choosing between them

| Use                                                          | Model                                 |
| ------------------------------------------------------------ | ------------------------------------- |
| Iterating, exploring, 20 variants of an idea                 | **Z-Image Turbo** (14 s)              |
| Text in the image, precise counts, complex spatial relations | **FLUX** (30 s)                       |
| Final hero asset                                             | **FLUX**                              |
| You need a specific community LoRA or ControlNet             | **SDXL** (huge ecosystem, older look) |

Practical loop: **explore in Z-Image, finish in FLUX.** Cheap to search, expensive to polish.

## 2. img2img — Stop Re-Rolling the Dice

Text→image is a slot machine. When you get an image that's 80% right, the beginner move is to re-roll and pray. The correct move is to **feed it back in** and denoise it _partially_.

Change three things in your Phase 1 graph:

1. Add `LoadImage` — pick your starting image.
2. Add `VAEEncode` — `LoadImage` → `VAEEncode.pixels`, `VAELoader` → `VAEEncode.vae`.
3. Replace `EmptySD3LatentImage` with `VAEEncode` into `KSampler.latent_image`.

Now **`denoise`** — dead at 1.0 in Phase 1 — becomes the most important dial you have:

| Denoise      | What survives                                                                                                      |
| ------------ | ------------------------------------------------------------------------------------------------------------------ |
| **0.2–0.3**  | Texture and detail change. Composition, colour, subject all identical. _Use this to add grain, fix skin, sharpen._ |
| **0.4–0.5**  | Style and materials shift. Composition holds. **The sweet spot for "same shot, different mood."**                  |
| **0.6–0.75** | Broad layout survives; content is substantially reinvented.                                                        |
| **0.9–1.0**  | The input is basically ignored.                                                                                    |

**Keep the seed fixed while you sweep denoise.** Otherwise you're changing two variables and learning nothing.

This is also the honest answer to "how do I get the same character twice?" — you don't re-roll, you _refine_. (The real answer is Phase 3 and Phase 5.)

## 3. LoRAs — Small Files That Change the Model

A LoRA is a small (0.1–2 GB) diff applied to a big model's weights. Two useful kinds:

- **Style/subject LoRAs** — teach a look or a face. You have none installed; Civitai and Hugging Face have thousands (mostly SDXL and FLUX).
- **Distillation LoRAs** — make a model run in 4 steps instead of 20. **You have three of these, and they're the reason video is tractable on this machine.**

Two loader nodes, and the difference matters:

| Node                  | Patches            | Use for                                                         |
| --------------------- | ------------------ | --------------------------------------------------------------- |
| `LoraLoaderModelOnly` | MODEL only         | **Distillation LoRAs** (Lightning, LightX2V, CausVid)           |
| `LoraLoader`          | MODEL **and** CLIP | Style/subject LoRAs that also shift how prompts are interpreted |

Wire it inline on the model path:

```
UNETLoader → LoraLoaderModelOnly → ModelSamplingAuraFlow → KSampler.model
```

`strength` 1.0 for distillation LoRAs (they're calibrated for it). 0.6–0.8 for style LoRAs — at 1.0 they usually bulldoze the prompt. Stack them by chaining loaders, but expect them to fight each other.

**When you attach a 4-step distillation LoRA, drop steps to 4 and cfg to 1.** The LoRA changes what the model _is_; leaving steps at 20 wastes 5× the time and often looks worse.

## 4. Upscaling — 1024² → 4096²

You now have `RealESRGAN_x4plus` and `4x-UltraSharp` (downloaded 2026-07-15). Two approaches, and the second is the one that matters.

### 4a. Straight GAN upscale (fast, dumb)

```
SaveImage's image → UpscaleModelLoader → ImageUpscaleWithModel → SaveImage
```

| Node                    | Setting                                    |
| ----------------------- | ------------------------------------------ |
| `UpscaleModelLoader`    | `RealESRGAN_x4plus.safetensors`            |
| `ImageUpscaleWithModel` | (no params — the model defines the factor) |

A few seconds. It enlarges cleanly and sharpens edges, but it **invents no new detail** — a blurry face becomes a big blurry face with crisp edges. `4x-UltraSharp` is the punchier of the two; RealESRGAN is more neutral and safer on faces.

### 4b. Upscale → re-diffuse (the good one)

This is how you actually get detail that wasn't there. Upscale to 4×, then run a **low-denoise img2img** over the enlarged image so the model _paints real detail into it_:

```
image → UpscaleModelLoader → ImageUpscaleWithModel   (1024² → 4096²)
      → VAEEncode → KSampler (denoise 0.25–0.35) → VAEDecode → SaveImage
```

Same model, same prompt, `denoise ≈ 0.3`, steps 8 (Z-Image) or 20 (FLUX). The GAN provides the structure; the diffusion model provides the pores, threads, and grain.

> **Watch your memory here.** A 4096² image is a 512×512×16 latent — 16× the compute of your 1024² render. With 48 GB you can do this in one pass, which most machines cannot. If it swaps, drop to a 2× upscale, re-diffuse, and repeat.
>
> **MPS reality check (see §7):** on this machine the plain `VAEEncode`/`VAEDecode` nodes hard-fail above 1024² — a Metal backend limit, not RAM — so the tiled variants (`VAEEncodeTiled`/`VAEDecodeTiled`, tile 1024) are mandatory for this pipeline. And the 4096² sampling pass costs ~45 min, not seconds; 2048² is the practical finish.

`ImageScaleBy` / `LatentUpscaleBy` also exist for plain resampling with no model — useful for quick downscales, useless for adding detail.

## 5. Prompt Craft (the 20% that's real)

Most "prompt engineering" advice is superstition. What actually holds up:

**Structure beats adjective soup.** Say subject → action → setting → lighting → shot → medium:

> `A brass compass on a folded nautical map | morning light through a window | shallow depth of field, 50mm | photographic`

**Be concrete.** "Beautiful lighting" means nothing. "Low golden hour sun raking from the left, long shadows" means something.

**Say the medium.** Models have seen labelled photos, oil paintings, 3D renders, and film stills. Naming one moves you decisively into that region. This is the single highest-leverage token in most prompts.

**Front-load.** Early tokens carry more weight. Bury the subject at the end and it gets diluted.

**Weighting:** `(word:1.3)` boosts, `(word:0.7)` suppresses. Stay in 0.7–1.4; beyond that you get artefacts.

**Negatives only work when CFG > 1.** On Z-Image Turbo, FLUX-dev, or anything with a Lightning LoRA, the negative prompt is **inert**. Those "ugly, deformed, watermark, bad hands" lists you see everywhere do literally nothing on distilled models. (You proved this in Phase 1, exercise 5.4.)

## 6. Exercises

**6.1 — Same prompt, both models.** Run one prompt with a specific requirement — _"a storefront with a hand-painted sign reading VSYST"_ — through Z-Image and FLUX at a fixed seed. FLUX will render legible text; Z-Image mostly won't. Now you know exactly what the extra 16 seconds buys.

**6.2 — Denoise ladder.** Take any output. img2img it at denoise 0.2 / 0.35 / 0.5 / 0.7 / 0.9, seed fixed. Line them up. Internalise this ladder — you'll reach for it constantly.

**6.3 — The finishing pipeline.** Build: Z-Image (1024²) → RealESRGAN 4× → VAEEncode → KSampler denoise 0.3 → SaveImage. Compare the 4096² output against the plain GAN upscale at 100% zoom. The difference is _invented detail_, and it's the entire game.

**6.4 — Save it.** `Workflow → Save As` → `02-finish-4k`. You'll use this as the final stage of nearly every image project from here on.

---

## 7. Lab Notes — FLUX, the Denoise Ladder, and the 4K Finish, Run on This Machine

_All exercises run 2026-08-02 via the local API at `http://127.0.0.1:8188`. Outputs are in `output/phase2/`; the base graph is Workflows → `02-zimage-base`, the finishing pipeline is saved as `02-finish-4k`. Storefront prompt: `a small storefront at street level with a hand-painted wooden sign above the door reading "VSYST", morning light, photographic` — seed 42 throughout._

### 6.1 — Z-Image rendered the sign too

The prediction failed in the interesting direction: **Z-Image Turbo rendered "VSYST" perfectly legibly on the first try** — and so did FLUX. A short all-caps word on a signboard is within Z-Image's reach; the text gap opens on longer phrases, mixed case, and small type, not five big letters.

What the extra seconds actually bought was scene understanding: the FLUX render has a more coherent street — brick facade, sign-mounting hardware, kerb and road, window displays whose objects read as actual merchandise — where Z-Image's is cleaner but flatter.

Timing, measured: Z-Image **16 s**; FLUX **144 s cold** (includes loading the 23 GB model), **108 s warm**. On this machine FLUX is **~7× Z-Image, not the "roughly 2×" claimed in §1** — the ~30 s figure is CUDA-speak. So the explore-in-Z-Image / finish-in-FLUX loop stands, but FLUX is a deliberate splurge, not a casual toggle.

### 6.2 — the ladder is real, but lighting doesn't move until 0.7

Run on the Z-Image storefront with a mood-shifted prompt (same scene, `at dusk in light rain, warm tungsten glow from the windows, cinematic`), seed 42, ~26 s per rung. Measured against the table in §2:

| Denoise | What actually happened                                                                                                |
| ------- | --------------------------------------------------------------------------------------------------------------------- |
| 0.2–0.5 | Texture and micro-detail only. The dusk/rain/tungsten mood **did not take at all** — the image stays morning-lit      |
| 0.7     | First real movement: rain streaks, wet pavement — but still daylight                                                  |
| 0.9     | Full mood: dusk, rain, glowing windows. And the input was **not** ignored — storefront, sign, and layout all survived |

The correction worth internalising: **global lighting is decided in the earliest, lowest-frequency steps of diffusion — exactly the steps that denoise ≤ 0.5 never re-runs.** Low denoise changes _surfaces_, not _light_. "Same shot, different mood" is a **0.7–0.9** operation (with the prompt describing the same scene — which is what preserved composition even at 0.9). The 0.4–0.5 band is the sweet spot for _material and style_ shifts, not lighting.

### 6.3 — the finish works, and MPS hides two landmines in it

The comparison delivers exactly as promised. At 100% zoom on the sign, the GAN-only 4× is waxy — smooth wood, soft letter edges, no fibre. The re-diffused version (denoise 0.3, 8 steps) has plank seams, wood grain, and paint texture in the letters. Invented detail — the entire game.

But the pipeline as drawn in §4b does not run on this machine unmodified:

**Landmine 1 — the plain VAE nodes fail above 1024².** `VAEEncode` at 4096² dies with `convolution_overrideable not implemented`; at 2048² with `MPSGraph does not support tensor dims larger than INT_MAX`. Not a RAM problem — a Metal addressing limit (an internal VAE layer crosses 2³¹ tensor elements). **`VAEEncodeTiled` / `VAEDecodeTiled` at tile 1024 are mandatory**, and are what `02-finish-4k` uses.

**Landmine 2 — the GAN stage can corrupt silently.** The first RealESRGAN 1024→4096 pass, run right after the FLUX renders with memory under pressure, produced a ghosted, doubled, stripe-interleaved mess — no error, node reported success. The identical graph re-run later was clean (6 s). The corruption was only caught _after_ burning a 43-minute re-diffuse on the garbage. **Eyeball the GAN output before re-diffusing it.**

Timings, measured (Z-Image, 8 steps, denoise 0.3, tiled VAE):

| Stage                | Time       |
| -------------------- | ---------- |
| RealESRGAN 1024→4096 | 6 s        |
| Re-diffuse at 2048²  | ~2.5 min   |
| Re-diffuse at 4096²  | **43 min** |

Why 4096² is so much worse than "16× the pixels": Z-Image is a DiT — the image becomes ~65k tokens instead of ~4k, and attention scales with the _square_ of that. So the practical recipe on this machine: **finish at 2048² (insert `ImageScaleBy 0.5` after the GAN — ~3 min end to end) and reserve the one-pass 4096² for hero assets**, or GAN-upscale the finished 2048² when you only need the pixel count. (The clean 4096² pass was deliberately cancelled mid-run to free the machine; `02-finish-4k` reproduces it whenever you can spare the 45 minutes.)

### 6.4 — saved

`02-finish-4k` is in Workflows: `LoadImage` → RealESRGAN 4× → (GAN-only save) → `VAEEncodeTiled` → `KSampler` denoise 0.3 → `VAEDecodeTiled` → save. Swap the source image and the prompt; keep everything else.

---

**Next:** [[03-phase-3-control-and-editing]] — stop rolling dice. Start giving orders.
