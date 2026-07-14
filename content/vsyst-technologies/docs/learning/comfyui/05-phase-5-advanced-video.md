# Phase 5 — VACE, Consistency, and Fixing Your 80-Minute Render

> Level: Advanced | Time: ~2 hr | Outcome: your VACE renders drop from 80 minutes to roughly 10, and you can hold a character's identity across multiple shots.

---

## 1. First — Fix the 80 Minutes

Your logs contain runs of `00:32:28`, `00:40:41`, and `01:20:15`. That last one is 80 minutes for a five-second clip. It is not a hardware limit. It's two configuration choices, and both have a fix.

### Diagnosis

Your `video_wan_vace_flf2v.json` loads `wan2.1_vace_14B_fp16.safetensors` with **`weight_dtype = default`** and samples **20 steps at cfg 6**.

`default` means "load in native precision" — and this checkpoint is **fp16, 32 GB**. Add the 6.3 GB text encoder, the VAE, and activations for an 81-frame latent, and you are asking for well over 40 GB on a 48 GB machine that also has to run macOS. You don't get an out-of-memory error. You get **swap** — and the render crawls.

### Fix 1 — Load VACE as fp8 (32 GB → ~16 GB)

On the `UNETLoader`, change `weight_dtype`:

| Option            | Effect on this machine                              |
| ----------------- | --------------------------------------------------- |
| `default`         | 32 GB of weights. **Swaps. This is your bug.**      |
| **`fp8_e4m3fn`**  | ~16 GB of weights. **Use this.**                    |
| `fp8_e4m3fn_fast` | Identical to the above on Apple Silicon — see below |
| `fp8_e5m2`        | Alternative fp8 format; rarely better               |

> **An Apple-Silicon detail worth knowing.** The shipped blueprint uses `fp8_e4m3fn_fast`, and on an NVIDIA card the `_fast` suffix enables a hardware fp8 matmul path that's genuinely faster. It does nothing here. ComfyUI's `supports_fp8_compute()` returns `False` for any non-NVIDIA device, so the fast path silently falls back. `_fast` is _harmless_ but _inert_ on your machine — use plain `fp8_e4m3fn` so the graph says what it means.
>
> The win is **not** faster math. The win is that 16 GB fits and 32 GB doesn't, and fitting is worth more than every other optimisation on this page combined.

### Fix 2 — CausVid LoRA (20 steps → 4)

You don't have this LoRA. It is 319 MB and it is the highest-leverage file you could put on this disk.

```bash
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/loras/Wan21_CausVid_14B_T2V_lora_rank32.safetensors \
  https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan21_CausVid_14B_T2V_lora_rank32.safetensors
```

_(Verified live: HTTP 200, 319 MB.)_

Then, exactly as the `Video Inpainting (Wan2.1 VACE)` blueprint does it:

| Node                  | Setting                                                            |
| --------------------- | ------------------------------------------------------------------ |
| `LoraLoaderModelOnly` | `Wan21_CausVid_14B_T2V_lora_rank32.safetensors`, strength **0.30** |
| `KSampler`            | steps **4**, cfg **1**, `uni_pc` / `simple`                        |
| `ModelSamplingSD3`    | shift 5–8                                                          |

**Strength 0.30, not 1.0.** CausVid at full strength flattens motion — the video goes static and plasticky. 0.30 is the blueprint's tuned value: enough to collapse the step count, not enough to kill the movement. This is unusual for a distillation LoRA and it's why people report bad results with it — they set it to 1.0.

### Expected result

|                      | Steps      | Weights               | Time                   |
| -------------------- | ---------- | --------------------- | ---------------------- |
| **Now**              | 20 @ cfg 6 | 32 GB fp16 (swapping) | **80 min** ✅ measured |
| **After both fixes** | 4 @ cfg 1  | ~16 GB fp8 (resident) | **~8–15 min** _(est.)_ |

5× fewer steps, and no swapping. Measure it and write the real number here.

### Also: two dead references in that workflow

`video_wan_vace_flf2v.json` also points at `umt5_xxl_fp16.safetensors` and `wan2.1_vace_1.3B_fp16.safetensors`. **Neither is on your disk** (you have `umt5_xxl_fp8_e4m3fn_scaled` and only the 14B VACE). Those nodes are presumably muted or bypassed — but clean them up, because a bypassed node that looks live is how you lose an hour.

## 2. What VACE Actually Is

WAN 2.1 VACE is not "another video model." It's a **conditioning framework** — one 14B model that absorbs several different kinds of guidance through a single node.

`WanVaceToVideo` (verified signature):

| Input                         | Type          | Gives you                                                  |
| ----------------------------- | ------------- | ---------------------------------------------------------- |
| `positive` / `negative`       | Conditioning  | Text prompt                                                |
| `vae`                         | VAE           | `wan_2.1_vae.safetensors`                                  |
| `width` / `height` / `length` | Int           | Default **832 × 480 × 81** — VACE's native size            |
| `strength`                    | Float         | How hard the control binds                                 |
| **`control_video`**           | Image _(opt)_ | **Structural control** — pose/depth/edge video → new video |
| **`control_masks`**           | Mask _(opt)_  | **Inpainting** — change only the masked region             |
| **`reference_image`**         | Image _(opt)_ | **Identity** — keep this subject across the clip           |

Outputs: `positive`, `negative`, `latent`, and **`trim_latent`** (an int).

Mix and match the optional inputs and you get, from one model:

| Give it                             | You get                                                      |
| ----------------------------------- | ------------------------------------------------------------ |
| `reference_image` only              | **Ref→Video** — your character, new motion                   |
| `control_video` only                | **Structure transfer** — a pose video drives a new subject   |
| `control_video` + `control_masks`   | **Video inpainting** — swap one object, keep the rest        |
| First + last frame                  | **Interpolation** — your existing `flf2v` workflow           |
| `reference_image` + `control_video` | **Your character, doing a specific motion.** The money shot. |

### The `trim_latent` gotcha

When you pass a `reference_image`, VACE **prepends it as extra latent frames**. If you decode straight from the KSampler you'll see your reference image flash at the head of the video.

That's what the `trim_latent` output is for. Wire it up:

```
WanVaceToVideo ──latent──→ KSampler ──→ TrimVideoLatent ──→ VAEDecode → CreateVideo
               └─trim_latent───────────────→ (trim_amount)
```

Miss this and every ref-guided clip has a one-frame artefact at the start. It looks like a model bug. It isn't.

## 3. Character Consistency

The thing everyone wants and nobody explains properly. There is no magic switch — there's a hierarchy of increasingly strong mechanisms, and you combine them.

| Mechanism                                         | Strength             | Cost                  |
| ------------------------------------------------- | -------------------- | --------------------- |
| Fixed seed + detailed prompt                      | Weak                 | Free                  |
| Same source image → img2img at low denoise        | Moderate             | Cheap                 |
| **VACE `reference_image`**                        | **Strong**           | The main tool         |
| **VACE `reference_image` + pose `control_video`** | **Strongest**        | Best-in-class locally |
| Training a character LoRA                         | Strongest, most work | Hours + a dataset     |

### The practical multi-shot recipe

For a sequence where one character appears in several shots:

1. **Lock the character once.** Generate the hero still in FLUX until it's exactly right. Iterate here — it costs 30 seconds a try, not 10 minutes.
2. **Build a shot list.** For each shot, get a pose/depth control video — film yourself on a phone, or use an existing clip, then run it through the Pose or Depth preprocessor from [[03-phase-3-control-and-editing]].
3. **For each shot:** VACE with `reference_image` = your hero still, `control_video` = that shot's pose video.
4. **Finish** each clip with FILM interpolation + RealESRGAN ([[04-phase-4-video]] §5).

The character stays the same because every shot is anchored to the _same reference image_. The motion differs because every shot has a _different control video_. That separation — identity from one input, motion from another — is the whole trick, and it's what VACE is for.

## 4. The Experimental One

`causal_forcing-framewise.safetensors` (5.3 GB). Its metadata says `{"transformer": {"causal_ar": true}}` and its tensor names are WAN-family — so it's an **autoregressive / causal** WAN variant, the family that generates frames _sequentially_ rather than denoising the whole clip at once.

The appeal is **unbounded length** and streaming: a standard WAN clip is capped by what fits in memory, but a causal model can in principle keep going frame after frame.

No blueprint in 0.27.1 targets it, so you'll need the loader/sampler from wherever you obtained it. Treat this as a research afternoon, not part of the main path. Come back to it once Phases 1–6 are second nature.

## 5. Exercises

**5.1 — Fix it and measure it.** Open `video_wan_vace_flf2v.json`. Set `weight_dtype = fp8_e4m3fn`. Run once, note the time. Then add the CausVid LoRA @ 0.30, drop to 4 steps / cfg 1 / `uni_pc`. Run again. **Write both numbers in §1.** This is the single most valuable hour in the whole course.

**5.2 — Prove CausVid strength matters.** Same graph at LoRA strength 0.3 vs 1.0. At 1.0 the motion will visibly deaden. Now you know why the blueprint says 0.3.

**5.3 — Ref→Video.** Generate a character in FLUX. Feed it to VACE as `reference_image` with a motion prompt and no control video. Wire `TrimVideoLatent` properly. Then deliberately remove it and watch the reference frame flash at the start.

**5.4 — Your character, your motion.** Film 3 seconds of yourself on your phone. Extract a pose video. VACE with `reference_image` = your FLUX character + `control_video` = your pose. Your character now performs your motion. This is the capability that most people believe requires a studio.

**5.5 — Two shots, one character.** Do 5.4 twice with different pose videos and different prompts. Check the character survives both. That's a _sequence_, and it's the foundation of [[07-capstones]].

---

**Next:** [[06-phase-6-automation-api-mcp]] — drive all of this from code, and from Claude.
