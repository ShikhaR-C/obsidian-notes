# Phase 4 — Video: WAN 2.2, and Why Your Model Is Secretly Two Models

> Level: Intermediate | Time: ~2 hr (plus render time — go make coffee) | Outcome: you can generate 5-second video from text or from an image, you understand the MoE sampler split, and you can finish a clip to 32 fps at 4× resolution without re-rendering it.

---

## 1. What Changes When You Add Time

A video latent is a **4D** tensor: frames × height × width × channels. Two consequences that drive everything in this phase:

**Attention is quadratic in sequence length.** Doubling the frame count more than doubles the cost. Your own logs show this brutally: TI2V 5B at 640×640×81 takes **~90 seconds**. The same model at 1280×704×121 — only 3.3× the tokens — takes **32–40 minutes**. That's ~25× the time for 3.3× the data. Part of that is O(n²) attention; part is that you've crossed into memory pressure and started swapping.

**The VAE compresses time, not just space.** WAN's VAE packs 4 frames into 1 latent frame. This is why **frame counts must be 4n+1**: 81 = 4(20)+1 ✓, 121 = 4(30)+1 ✓. Ask for 80 and you'll get an error or a corrupted final frame.

Useful arithmetic:

| Frames  | @ 16 fps  | @ 24 fps  |
| ------- | --------- | --------- |
| 49      | 3.1 s     | 2.0 s     |
| **81**  | **5.1 s** | 3.4 s     |
| **121** | 7.6 s     | **5.0 s** |

## 2. ⚠️ The VAE Trap — Read This Twice

You have two WAN VAEs and **they are not interchangeable**:

| Model                | VAE                           | Size   |
| -------------------- | ----------------------------- | ------ |
| WAN 2.2 **TI2V 5B**  | **`wan2.2_vae.safetensors`**  | 1.3 GB |
| WAN 2.2 **I2V 14B**  | **`wan_2.1_vae.safetensors`** | 242 MB |
| WAN 2.1 **VACE 14B** | **`wan_2.1_vae.safetensors`** | 242 MB |

Yes — the _2.2_ 14B models use the _2.1_ VAE. Only the 5B uses the 2.2 VAE. Mix them and you don't get an error, you get **coloured noise or a smeared mess after a 20-minute render**. This is the single most expensive mistake in local WAN work, and the naming actively invites it.

## 3. Track A — WAN 2.2 TI2V 5B (start here)

One model, both text→video and image→video. 9.3 GB. Your fastest path to a moving picture.

| Node                      | Setting                                                  |
| ------------------------- | -------------------------------------------------------- |
| `UNETLoader`              | `wan2.2_ti2v_5B_fp16.safetensors`                        |
| `CLIPLoader`              | `umt5_xxl_fp8_e4m3fn_scaled.safetensors`, type **`wan`** |
| `VAELoader`               | **`wan2.2_vae.safetensors`**                             |
| `ModelSamplingSD3`        | shift **8**                                              |
| `Wan22ImageToVideoLatent` | width, height, length, batch                             |
| `KSampler`                | steps **20**, cfg **5**, `uni_pc` / `simple`             |
| `CreateVideo`             | fps **24** → `SaveVideo`                                 |

Note **cfg 5**, not 1 — the 5B is _not_ distilled, and you have no speed LoRA for it. It's a full model and it needs real guidance.

`Wan22ImageToVideoLatent` does double duty: give it a `start_image` for image→video, leave it empty for text→video.

### Your saved workflow is misconfigured for iteration

`video_wan2_2_5B_ti2v.json` is set to **1280×704, 121 frames, 20 steps** — that's the 32–40 minute run. It's a fine _final_ setting and a terrible _iteration_ setting.

Work at these instead, then finish big (§6):

| Purpose     | Resolution | Frames | Expect                |
| ----------- | ---------- | ------ | --------------------- |
| **Iterate** | 640×640    | 81     | ~90 s ✅ measured     |
| Draft       | 832×480    | 81     | ~2 min _(est.)_       |
| **Final**   | 1280×704   | 121    | 32–40 min ✅ measured |

You will throw away most of your first attempts. Throw them away at 90 seconds each, not 35 minutes each.

### Prompting motion

The prompt must describe **change over time**, not a still. This is the mistake everyone makes coming from image work.

| Weak (a description)      | Strong (a shot)                                                                            |
| ------------------------- | ------------------------------------------------------------------------------------------ |
| "a fuel truck at a depot" | "a fuel truck pulls slowly into frame from the left, dust drifting, camera holds steady"   |
| "a woman smiling"         | "a woman turns toward the camera and breaks into a smile, hair shifting with the movement" |

Name the **camera** ("slow dolly in", "static locked-off shot", "handheld pan right") and the **subject motion** separately. If you don't specify camera movement, WAN will invent some — usually a slow drift you didn't want.

## 4. Track B — WAN 2.2 I2V 14B, and the MoE Split

This is the quality tier, and it's the most conceptually interesting graph in the course.

**Why two 13 GB files?** WAN 2.2 14B is a **Mixture-of-Experts over the denoising timestep**. Not two models blended — two models that run in _sequence_, each handling a different phase of denoising:

- **High-noise expert** — early steps. The image is mostly noise; this expert decides _composition and motion_.
- **Low-noise expert** — late steps. Structure is settled; this expert renders _detail and texture_.

Specialising each half is what buys 14B quality without paying 28B compute.

### The graph (verified against the shipped blueprint)

```
UNETLoader(high_noise) → LoraLoaderModelOnly(lightx2v_high) → ModelSamplingSD3(5) → KSamplerAdvanced #1
UNETLoader(low_noise)  → LoraLoaderModelOnly(lightx2v_low)  → ModelSamplingSD3(5) → KSamplerAdvanced #2
                                                          #1.LATENT ────────────────→ #2.latent_image
```

| Node                       | Setting                                                                          |
| -------------------------- | -------------------------------------------------------------------------------- |
| `CLIPLoader`               | `umt5_xxl_fp8_e4m3fn_scaled.safetensors`, type `wan`                             |
| `VAELoader`                | **`wan_2.1_vae.safetensors`** ← the 242 MB one!                                  |
| Both `LoraLoaderModelOnly` | matching `wan2.2_i2v_lightx2v_4steps_lora_v1_{high,low}_noise`, strength **1.0** |
| Both `ModelSamplingSD3`    | shift **5**                                                                      |
| `WanImageToVideo`          | 640 × 640, length **81**                                                         |
| `CreateVideo`              | fps **16**                                                                       |

### The sampler handoff — the bit that looks wrong but isn't

|                              | KSamplerAdvanced #1 (high) | KSamplerAdvanced #2 (low) |
| ---------------------------- | -------------------------- | ------------------------- |
| `add_noise`                  | **enable**                 | **disable**               |
| `steps`                      | 4                          | 4                         |
| `start_at_step`              | **0**                      | **2**                     |
| `end_at_step`                | **2**                      | **4**                     |
| `return_with_leftover_noise` | **enable**                 | disable                   |
| cfg / sampler                | 1 / `euler` `simple`       | 1 / `euler` `simple`      |

Read it as: _the schedule is 4 steps long. Expert 1 runs steps 0→2 and hands over a **still-noisy** latent (`return_with_leftover_noise = enable`). Expert 2 picks up at step 2 with `add_noise = disable` (the noise is already there) and finishes 2→4._

Both nodes say `steps: 4` because that's the **total schedule length**, not each one's workload. Set it to 2 on each and you'd get a completely different (wrong) noise schedule. This trips up everyone the first time.

`cfg 1` and 4 total steps are only possible because of the **LightX2V LoRAs**. Without them this model wants ~20 steps at cfg 3.5–5 — a 5× longer render. Those two 1.1 GB files are doing enormous work.

**Expect ~4–8 minutes** at 640×640×81 _(est. — you haven't logged this configuration yet; measure it and write the number here)_.

## 5. Finishing: Interpolate and Upscale

Here's the leverage. **Never generate at final resolution and frame rate.** Generate small and short, then finish. Same principle as Phase 2, worth 10× more here.

### Frame interpolation (FILM)

WAN outputs 16 fps, which reads as slightly stuttery. `film_net_fp16.safetensors` (downloaded today) synthesises in-between frames.

```
VAEDecode → FrameInterpolationModelLoader → FrameInterpolate(multiplier 2) → CreateVideo(fps 32) → SaveVideo
```

| Node                            | Setting                                   |
| ------------------------------- | ----------------------------------------- |
| `FrameInterpolationModelLoader` | `film_net_fp16.safetensors`               |
| `FrameInterpolate`              | multiplier **2** (or 3)                   |
| `CreateVideo`                   | fps = original × multiplier (16 → **32**) |

Takes seconds. It is by far the biggest perceived-quality gain per unit of compute available to you. 16 fps → 32 fps is the difference between "AI video" and "video."

> Note: 0.27.1's interpolation is **FILM**, a core node — not RIFE, and not a custom node. If you go looking for `ComfyUI-Frame-Interpolation` on the Manager, you don't need it.

### Video upscale

`ImageUpscaleWithModel` operates on the whole decoded frame batch:

```
VAEDecode → UpscaleModelLoader(RealESRGAN_x4plus) → ImageUpscaleWithModel → FrameInterpolate → CreateVideo
```

Upscale **before** interpolating — you upscale fewer frames that way, and FILM does a cleaner job with more pixels to work with.

### The economics

| Route                                           | Cost                                              |
| ----------------------------------------------- | ------------------------------------------------- |
| Generate 1280×704 @ 121 frames directly         | **32–40 min** ✅ measured                         |
| Generate 640×640 @ 81 → RealESRGAN 4× → FILM ×2 | **~90 s + ~1 min finishing** → 2560×2560 @ 32 fps |

The second is roughly **15× cheaper** and gives you a _higher_ resolution at _double_ the frame rate. It won't have the fine detail a native high-res render would, but for anything that isn't a hero shot it's not close.

## 6. Model Selection

| Need                               | Use                                                   |
| ---------------------------------- | ----------------------------------------------------- |
| Text → video                       | **TI2V 5B** (your only text→video option — see below) |
| Image → video, iterating           | TI2V 5B                                               |
| Image → video, final quality       | **I2V 14B + LightX2V**                                |
| Editing / extending existing video | **VACE 14B** → [[05-phase-5-advanced-video]]          |

> **The `Text to Video (Wan 2.2)` blueprint will not run.** It requires `wan2.2_t2v_{high,low}_noise_14B` + the T2V LightX2V LoRAs. You have the **I2V** 14B pair, not T2V. Either use TI2V 5B for text→video, or download the T2V pair (~26 GB + 2 GB LoRAs — see [[08-reference]]).
>
> There's also a legitimate two-step route that's often _better_ than native T2V: **generate a still in FLUX or Z-Image, then feed it to I2V 14B.** You get FLUX's composition and prompt adherence plus 14B's motion, and you can iterate on the still for 14 seconds instead of re-rendering video. For most work this beats text→video outright.

## 7. Exercises

**7.1 — First video.** TI2V 5B, 640×640, 81 frames, text→video. Prompt a specific camera move. ~90 s.

**7.2 — Prove the VAE trap.** Same graph, swap the VAE to `wan_2.1_vae.safetensors`. Run. Watch it produce garbage. Now you'll recognise the failure mode in one second instead of losing an afternoon.

**7.3 — Still → video.** Generate a still in FLUX. Feed it to TI2V 5B as `start_image`. Compare against pure text→video with the same prompt. The FLUX-seeded one will be better composed nearly every time.

**7.4 — The MoE graph.** Build the I2V 14B two-expert graph from §4. Get the KSamplerAdvanced handoff right. Then deliberately break it — set `return_with_leftover_noise` to `disable` on #1 — and watch the output degrade. That's the concept landing.

**7.5 — Finish it.** Take your 640×640 @ 16 fps clip → RealESRGAN 4× → FILM ×2 → 32 fps. Play it next to the original. Save the graph as `04-video-finish`.

**7.6 — Log your numbers.** Time 7.4 and write it in the table in §4. Estimates are fine to start with; measurements are better.

---

**Next:** [[05-phase-5-advanced-video]] — VACE, character consistency, and fixing your 80-minute render.
