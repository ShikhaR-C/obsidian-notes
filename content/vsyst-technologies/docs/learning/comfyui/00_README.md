# ComfyUI — Local Image & Video Generation on Apple Silicon

> Audience: me (Shikhar) | Machine: MacBook Pro M5 Max, 48 GB unified memory | Status: hands-on tutorial, written against **this** install — every filename, setting, and timing below was read off the actual machine on 2026-07-15.

## What This Folder Is

A seven-phase, hands-on course in ComfyUI that goes from "render your first image in 14 seconds" to "drive the whole thing from Claude over MCP." It is **not** a generic tutorial. Every workflow uses models that are already on this disk, every sampler setting is copied from the blueprint that ships with this ComfyUI version, and every performance number is either measured from the logs or explicitly labelled as an estimate.

Read the phases in order. Each one ends with an exercise that produces a file you can look at.

## The Machine (measured)

|                    |                                                                           |
| ------------------ | ------------------------------------------------------------------------- |
| **Chip**           | Apple M5 Max — 18 CPU cores, **40 GPU cores**                             |
| **Memory**         | **48 GB unified** (CPU and GPU share one pool — no separate VRAM)         |
| **Disk**           | 1.5 TB free                                                               |
| **OS**             | macOS 26.5.2                                                              |
| **ComfyUI**        | **0.29.2** (observed live 2026-08-01; course text written against 0.27.1) |
| **Python / Torch** | 3.13.12 / **torch 2.10.0**, MPS backend active                            |
| **Install root**   | `~/Documents/AI/ComfyUI/ComfyUI`                                          |

**Unified memory is the single fact that governs everything else in this course.** On an NVIDIA box, a model must fit in VRAM or it does not run. Here, a model that "doesn't fit" doesn't fail — it silently spills into swap and the render takes 80 minutes instead of 8. Most of the performance advice in Phase 5 is really memory advice.

## What's Installed (~255 GB)

### Image

| Model               | File                                             | What it's for                                                 |
| ------------------- | ------------------------------------------------ | ------------------------------------------------------------- |
| **Z-Image Turbo**   | `z_image_turbo_bf16.safetensors` (11 GB)         | Your workhorse. 8 steps, ~14 s. Start here.                   |
| **FLUX.1-dev**      | `flux1-dev.safetensors` (22 GB)                  | Top-tier quality, prompt adherence. ~30 s.                    |
| **SDXL base**       | `sd_xl_base_1.0.safetensors` (6.5 GB)            | Legacy. Huge LoRA/ControlNet ecosystem, otherwise superseded. |
| **Qwen-Image-Edit** | `qwen_image_edit_fp8_e4m3fn.safetensors` (19 GB) | Instruction editing — "change the background to a warehouse." |

### Video

| Model                | File                                                                 | What it's for                                                         |
| -------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------- |
| **WAN 2.2 TI2V 5B**  | `wan2.2_ti2v_5B_fp16.safetensors` (9.3 GB)                           | Text→video **and** image→video in one model. The efficient one.       |
| **WAN 2.2 I2V 14B**  | `wan2.2_i2v_{high,low}_noise_14B_fp8_scaled.safetensors` (13 GB × 2) | Highest-quality image→video. A **MoE pair** — see Phase 4.            |
| **WAN 2.1 VACE 14B** | `wan2.1_vace_14B_fp16.safetensors` (32 GB)                           | Video _editing_ + control: ref→video, first/last-frame, inpainting.   |
| **SVD-XT**           | `svd_xt.safetensors` (8.9 GB)                                        | Legacy (2023). WAN beats it on every axis. Ignore.                    |
| **Causal-forcing**   | `causal_forcing-framewise.safetensors` (5.3 GB)                      | Experimental autoregressive/streaming WAN variant. Phase 5 side-note. |

### 3D

| **Hunyuan3D 2.1** | `hunyuan_3d_v2.1.safetensors` (6.9 GB) | Single image → textured 3D mesh. |
| ----------------- | -------------------------------------- | -------------------------------- |

### Speed LoRAs (these matter enormously)

| LoRA                                                     | Effect                                                       |
| -------------------------------------------------------- | ------------------------------------------------------------ |
| `wan2.2_i2v_lightx2v_4steps_lora_v1_{high,low}_noise`    | WAN 2.2 I2V 14B: **20 steps → 4 steps**                      |
| `Qwen-Image-Edit-Lightning-4steps-V1.0-bf16`             | Qwen edit: **20 steps → 4 steps**                            |
| `Wan21_CausVid_14B_T2V_lora_rank32` _(added 2026-07-15)_ | VACE 14B: **20 steps → 4** — at strength **0.30**, never 1.0 |

### Just added (2026-07-15, ~6.9 GB)

These filled the gaps that were blocking blueprints already shipping in 0.27.1:

| File                                                                          | Folder                              | Unlocks                                           |
| ----------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------- |
| `RealESRGAN_x4plus.safetensors`                                               | `upscale_models/`                   | Image + video 4× upscale                          |
| `4x-UltraSharp.pth`                                                           | `upscale_models/`                   | Sharper alternative upscaler                      |
| `film_net_fp16.safetensors`                                                   | `frame_interpolation/`              | **FILM** frame interpolation — 16 fps → 32/48 fps |
| `Z-Image-Turbo-Fun-Controlnet-Union.safetensors`                              | `model_patches/`                    | Canny / Depth / Pose control for Z-Image          |
| `lotus-depth-d-v1-1.safetensors` + `vae-ft-mse-840000-ema-pruned.safetensors` | `diffusion_models/`, `vae/`         | Depth map extraction                              |
| `sdpose_wholebody_fp16.safetensors` + `rt_detr_v4-x-hgnet_fp16.safetensors`   | `checkpoints/`, `diffusion_models/` | Human pose extraction                             |

Two things worth knowing, because guessing gets both wrong: the Z-Image ControlNet goes in **`model_patches/`**, not `controlnet/`. And 0.27.1's frame interpolation is **FILM** (`FrameInterpolationModelLoader`, a core node), not RIFE.

### Added 2026-08-01 — Tier 1 + Sonic (~62 GB)

The Download Plan below was executed: all of **Tier 1** plus **Sonic** from Tier 2. Rationale per model in the tier tables; exact files and URLs in [[08-reference]] §4; how these map to Google Flow capabilities in [[09-google-flow-parity]].

| Model                                      | Folder                                 | Unlocks                                                                             |
| ------------------------------------------ | -------------------------------------- | ----------------------------------------------------------------------------------- |
| SVI 2.0 Pro LoRA pair                      | `loras/`                               | Scene extension / storyline continuity                                              |
| Qwen-Image-Edit 2509 fp8                   | `diffusion_models/`                    | Multi-ref character consistency; fixes item 3 below                                 |
| WAN 2.2 S2V 14B fp8 + wav2vec2             | `diffusion_models/`, `audio_encoders/` | Speaking presenter (voice → lip-synced video)                                       |
| ACE-Step 1.5 turbo AIO                     | `checkpoints/`                         | Music beds                                                                          |
| Stable Audio 3 small_sfx + t5gemma         | `checkpoints/`, `text_encoders/`       | SFX ≤ 2 min (repo moved these into subfolders — paths fixed in [[08-reference]] §4) |
| clip_vision_h                              | `clip_vision/`                         | WAN 2.1 I2V flows, WAN Animate prereq                                               |
| Sonic full set (incl. whisper-tiny, RIFE)  | `sonic/`                               | Talking head from a portrait, on existing `svd_xt`                                  |
| Ollama `gemma4:12b-mlx` + `qwen3.5:4b-mlx` | (Ollama)                               | Vision QC + batch prompt expansion                                                  |

Still manual: **Chatterbox** — install the `diodiogod/TTS-Audio-Suite` custom node; it fetches the weights on first use.

## Four Things Wrong With This Install (found while writing this)

These are read off your actual files. Fix them before you start.

1. **Your VACE workflow is the reason renders take 80 minutes.** `video_wan_vace_flf2v.json` loads the 32 GB fp16 VACE model with `weight_dtype = default` and runs **20 steps at cfg 6**. 32 GB of weights + a 6.3 GB text encoder + activations does not fit in 48 GB alongside macOS — so it swaps. Fix in [[05-phase-5-advanced-video]].

2. **The "Text to Video (Wan 2.2)" blueprint cannot run here.** It wants `wan2.2_t2v_{high,low}_noise_14B` — you have the **I2V** 14B pair, not T2V. Use TI2V 5B for text→video instead ([[04-phase-4-video]]).

3. ~~The "Image Edit (Qwen 2509)" blueprint won't load your files.~~ **Fixed 2026-08-01.** `qwen_image_edit_2509_fp8_e4m3fn.safetensors` is now in `diffusion_models/` — the shipped blueprint runs unmodified. The [[03-phase-3-control-and-editing]] workaround is only needed for the old v1 file.

4. ~~You have no CausVid LoRA.~~ **Fixed 2026-07-15.** `Wan21_CausVid_14B_T2V_lora_rank32.safetensors` (319 MB) is now in `loras/`. Wire it at strength **0.30** per [[05-phase-5-advanced-video]] §1 — and remember the 80-minute fix also needs the fp8 `weight_dtype` change from item 1.

## What to Expect Locally

Measured from your own `comfyui.log` files unless marked _(est.)_.

| Task       | Model                       | Settings                           | Time                                                            |
| ---------- | --------------------------- | ---------------------------------- | --------------------------------------------------------------- |
| Image      | Z-Image Turbo               | 1024², 8 steps                     | **13–15 s** ✅ measured                                         |
| Image      | FLUX.1-dev                  | 1024², 20 steps                    | **28–33 s** ✅ measured                                         |
| Image edit | Qwen-Image-Edit + Lightning | 4 steps                            | ~40–60 s _(est.)_                                               |
| Video 5 s  | WAN 2.2 TI2V 5B             | 640², 81 frames, 20 steps          | **65–105 s** ✅ measured                                        |
| Video 5 s  | WAN 2.2 I2V 14B + LightX2V  | 640², 81 frames, 4 steps           | ~4–8 min _(est.)_                                               |
| Video 5 s  | WAN 2.2 TI2V 5B             | **1280×704, 121 frames, 20 steps** | **32–40 min** ✅ measured — this is your current saved workflow |
| Video      | VACE 14B fp16, 20 steps     | as currently configured            | **80 min** ✅ measured                                          |
| Video      | VACE 14B **fp8 + CausVid**  | 4 steps                            | ~8–15 min _(est., after fixes)_                                 |

**The honest summary:** stills are effectively instant, and this machine is genuinely excellent at them. Video is real but it is a _batch_ medium here — you set one going and come back. Anyone promising you real-time local video on a laptop is selling something. The 48 GB is what makes 14B video possible at all; an 18 GB Mac simply cannot run these models.

## The Download Plan — Filling the Content-Studio Gaps

> Researched and web-verified **2026-07-15**. **Status 2026-08-01: Tier 1 (plus Sonic from Tier 2) is downloaded** — only Chatterbox's node install remains manual. Tier 2/3 rows are still plan-only. Exact files, repos, and staged commands live in [[08-reference]] §4; the Google-Flow-parity view of these gaps is [[09-google-flow-parity]]. Sizes are Hugging Face decimal GB.

The install above makes stills and silent video. Producing tutorial and marketing content for an app or website needs six capabilities it doesn't have yet — and each has a specific fix:

| Feature wanted                     | Today                                                            | The fix                                                 |
| ---------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------- |
| Character consistency — **images** | Partial: Qwen-Edit v1 is single-reference only                   | Qwen-Edit **2509** multi-ref (T1) → character LoRA (T2) |
| Character consistency — **video**  | Works via VACE `reference_image` ([[05-phase-5-advanced-video]]) | Stronger: WAN **Animate** / **Phantom** (T2)            |
| **Storyline continuity**           | Manual last-frame chaining; identity drifts                      | **SVI 2.0 Pro** LoRAs (T1) + keyframe-first pipeline    |
| **Speech + lip sync**              | None                                                             | **Chatterbox** TTS + **WAN S2V** talking presenter (T1) |
| **Music + SFX**                    | None                                                             | **ACE-Step 1.5** + **Stable Audio 3** (T1)              |
| **Script writing + frame QC**      | `qwen3.6:35b-mlx` already pulled in Ollama                       | + **gemma4** vision QC + `comfyui-ollama` node (T1)     |

One licensing sentence, because this is marketing output: everything in Tier 1 is Apache-2.0 / MIT / commercially licensed; FLUX-dev-family weights (including Kontext) are non-commercial and flagged where they appear.

### Tier 1 — the core (~58 GB in ComfyUI, ~12 GB in Ollama) — ✅ downloaded 2026-08-01

| Model                                  | Size GB | Use                                                                                                                        | Note                                                                            |
| -------------------------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| **SVI 2.0 Pro** LoRA pair              | 2.5     | Storyline continuity: chain unlimited 5-s segments on your existing I2V 14B pair; error-recycling stops shot-to-shot drift | Best capability-per-GB in this table (ICLR'26)                                  |
| **Qwen-Image-Edit 2509** fp8           | 20.4    | Character consistency in stills: 1–3 reference images per edit (character + product + scene); identity holds across edits  | Apache-2.0; unlocks the shipped blueprint unmodified; reuses your Qwen TE + VAE |
| **WAN 2.2 S2V 14B** + wav2vec2         | 17.0    | The speaking presenter: still image + voice track → lip-synced talking video                                               | Native template; fp8 — do the measurement below first; GGUF fallback is 13.9    |
| **Chatterbox** (TTS-Audio-Suite)       | 3.2     | Voiceover TTS + zero-shot voice cloning, 23 languages                                                                      | MIT, official MPS support — the license-safe cloner                             |
| **ACE-Step 1.5 turbo** (AIO)           | 10.0    | Music beds: full songs from a text prompt                                                                                  | MIT, native template, upstream ships Mac/MLX launch scripts                     |
| **Stable Audio 3 small_sfx** + t5gemma | 3.5     | Sound effects ≤ 2 min: UI clicks, whooshes, ambience                                                                       | Commercially licensed; CPU-capable — the lowest-risk audio model                |
| **clip_vision_h**                      | 1.2     | Fills the empty `clip_vision/`; prerequisite for WAN 2.1 I2V flows and WAN Animate (T2)                                    | Was Priority 2 in [[08-reference]] §4                                           |

**The language layer (Ollama, not ComfyUI):**

| Ollama tag                  | Size GB   | Use                                                                               | Note                                                                |
| --------------------------- | --------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `gemma4:12b-mlx` ✅ pulled  | 7.7       | Vision QC: look at rendered frames, catch character drift, caption assets         | Small enough to sit beside a 14B render                             |
| `qwen3.5:4b-mlx` ✅ pulled  | 4.0       | Batch prompt expansion: one storyline → thirty shot prompts                       | —                                                                   |
| `qwen3.6:35b-mlx` ✅ pulled | 21 (have) | The writer: scripts, shot lists, scene-by-scene prompts. Vision-capable, 256K ctx | Too big to coexist with a render — `keep_alive: 0` before rendering |

Glue: the `stavsap/comfyui-ollama` custom node calls these from inside a graph. And to settle the ollama.com question directly: it hosts LLMs/VLMs only, plus two **experimental Mac-only text-to-image** models added Jan 2026 (`x/z-image-turbo`, `x/flux2-klein`) and **zero video models** — you already run better than both in ComfyUI. Ollama's job in this stack is words, not pixels.

### Tier 2 — pull when a project demands one (~118 GB if you took it all; you won't)

| Model                                      | Size GB              | Use                                                                                                        | Note                                                                                                                                                                                      |
| ------------------------------------------ | -------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Qwen-Image-Edit 2511**                   | 13.2 GGUF / 20.5 fp8 | Successor to 2509 — changelog is literally "Improved Character Consistency," "Mitigate Image Drift"        | Its template needs a ComfyUI app update; GGUF path needs `ComfyUI-GGUF`                                                                                                                   |
| **FLUX.1 Kontext dev**                     | 6.9 (GGUF Q4)        | Identity-preserving edits in the FLUX family; reuses your FLUX encoders + VAE                              | ⚠ weights non-commercial                                                                                                                                                                  |
| **FLUX.2 klein 4B**                        | 7.8                  | Multi-reference generate **and** edit in one small model                                                   | Apache-2.0; its TE is `qwen_3_4b` — already on your disk                                                                                                                                  |
| **WAN 2.2 Animate 14B** fp8 + relight LoRA | 19.8                 | Your character performs a reference video's motion; replace a person in existing footage                   | Native template; zero published Mac runs — you'd write the first numbers                                                                                                                  |
| **Phantom-WAN 14B** fp8                    | 15.0                 | Multi-subject reference→video: mascot + product together in one shot, from 1–4 stills                      | Native node; frozen at WAN 2.1 but still the only tool that does this                                                                                                                     |
| Phantom-WAN 1.3B                           | 2.9                  | Draft-speed Phantom for iterating composition                                                              | —                                                                                                                                                                                         |
| **WAN 2.2 Fun-InP** pair                   | 28.6                 | Keyframe→keyframe bridging (first/last frame) at 2.2 quality — the storyboard pipeline's connective tissue | Demoted 2026-08-01: core now ships a native **FLF2V** template that runs on the I2V 14B pair already on disk — pull Fun-InP only if FLF2V quality disappoints ([[09-google-flow-parity]]) |
| **Sonic** ✅ pulled 2026-08-01             | 6.7                  | Talking head from a portrait photo                                                                         | The only avatar model with a confirmed Mac fix; runs on your `svd_xt` — the first real reason to keep it                                                                                  |
| **Qwen3-TTS 1.7B**                         | 4.5                  | 2026 TTS quality leader; 3-second voice clone                                                              | Apache-2.0; verified in `mlx-audio`                                                                                                                                                       |
| **Wav2Lip**                                | 0.4                  | Quick lip-sync onto existing footage (screen-recorded presenter)                                           | 96-px mouth region — utility, not hero shots                                                                                                                                              |
| **Z-Image base** (non-turbo)               | 12.3                 | The LoRA-training foundation: train your mascot/presenter once, use it natively everywhere                 | Apache-2.0; TE + VAE already on disk; training notes in [[07-capstones]]                                                                                                                  |

### Tier 3 — heavy options, only with a concrete need

| Model                                 | Size GB    | Use                                                                   | Note                                                                |
| ------------------------------------- | ---------- | --------------------------------------------------------------------- | ------------------------------------------------------------------- |
| WAN 2.2 **T2V 14B** pair + LoRAs      | 29         | Native text→video (the blueprint that can't run today)                | Verdict unchanged: FLUX-still → I2V is usually better _and_ cheaper |
| WAN 2.2 **Fun-VACE** pair             | 34.6       | VACE at 2.2 quality (ref→video, edit)                                 | Your 2.1 VACE covers most of this today                             |
| **HunyuanVideo 1.5** (720p i2v)       | ~10        | Second opinion on motion/physics — best open per mid-2026 comparisons | Reuses your `qwen_2.5_vl_7b` encoder; adds its own VAE + byt5       |
| **InfiniteTalk** (+ WAN 2.1 I2V base) | 2.7 + 16   | Unlimited-length dubbing for long tutorials                           | Native since core v0.11 — but needs a 16 GB base you don't have     |
| **VibeVoice** 1.5B / Large            | 5.4 / 18.4 | Long-form multi-speaker TTS (podcast-style narration)                 | MIT; Large exists only as a mirror — Microsoft pulled the repo      |

### Checked and deliberately skipped

| Model                                | Why not                                                                                    |
| ------------------------------------ | ------------------------------------------------------------------------------------------ |
| FLUX.2 dev                           | 53.5 GB fp8 pair (32B + Mistral TE) — doesn't fit 48 GB in any usable form                 |
| LTX-2.3 22B                          | fp8 text encoder broken on Metal; GGUF route marginal at 22B + a 12B TE                    |
| Ovi                                  | CUDA-only, confirmed broken on MPS — and it generates its own voice, can't sync your track |
| LatentSync 1.5 / 1.6                 | CUDA-hardcoded + no macOS `decord` wheels; nearest Mac path is an unmerged fork, CLI-only  |
| MMAudio / HunyuanVideo-Foley         | Video→SFX, custom-node-only, zero Mac evidence; Stable Audio 3 small_sfx covers the need   |
| F5-TTS                               | Fine cloner, but CC-BY-NC — cannot voice marketing content                                 |
| PuLID / InstantID / IPAdapter FaceID | 2024-era face adapters; nodes frozen since 2025-04; Qwen-Edit / Kontext do it better       |
| "Open" WAN 2.5 / 2.6 / 2.7           | API-only; no open weights exist — ignore the SEO posts claiming otherwise                  |
| kijai WanVideoWrapper (node)         | Effectively dead on MPS (unfixed issues since 2025-02) — stay on native nodes              |

### The pipeline these enable

```
script + shot list ──── qwen3.6 (Ollama)
        ↓
hero stills ──────────── Z-Image / FLUX            (have)
        ↓
character sheet +
per-shot keyframes ───── Qwen-Edit 2509            (T1)
        ↓
video ─┬─ I2V 14B + SVI chains → storyline         (T1)
       └─ S2V presenter + Chatterbox voice         (T1)
        ↓
audio ─── ACE-Step music + Stable Audio 3 SFX      (T1)
        ↓
finish ── FILM ×2 + RealESRGAN                     (have)
        ↓
QC ────── gemma4 vision via comfyui-ollama:        (T1)
          "same character? on-brand? artefacts?"
```

Three custom nodes earn a slot for this (you currently run zero — [[07-capstones]] explains why that's been a feature): `ComfyUI-GGUF` (quantized model loading), `comfyui-ollama` (the LLM layer), `TTS-Audio-Suite` (speech). Add them one at a time, with a reason, as ever.

### ~~One measurement before the big pulls~~ — MEASURED 2026-08-01, and the answer is worse than either hypothesis

The question was "does fp8 halve RAM or only disk?" The measured answer on ComfyUI **0.29.2**: **fp8_scaled diffusion models do not run on MPS at all.** A WAN 2.2 I2V 14B fp8 render (512², 33 frames, 4 steps, via the API) loaded the UNet at its true fp8 size — log: `loaded completely; 13631.42 MB loaded, full load: True`, so no upcast, the memory saving is real — then crashed in the sampler: `TypeError: Trying to convert Float8_e4m3fn to the MPS backend` from comfy-kitchen's `dequantize_fp8` (upstream issue #8785; torch 2.10 has no MPS fp8 dtype). Reproduced with and without the LightX2V LoRAs, so it's the dequant path itself, not LoRA patching.

What this means for this disk: the WAN 2.2 **I2V 14B pair**, **S2V 14B**, and both **Qwen-Edit fp8** files are currently unrunnable as-is — which retroactively explains why every fp8 timing in these docs was _(est.)_: none had ever actually run. **Text encoders are unaffected** (umt5 fp8 encoded fine in the same run — its path handles fp8 differently). fp16/bf16 models are untouched by any of this.

Two exits, detailed in [[09-google-flow-parity]]: **(a) GGUF variants** via the `ComfyUI-GGUF` node — verified to exist for all three casualties (I2V pair Q5 10.8 GB ×2, S2V Q5 15.0 GB, Qwen-Edit-2509 Q5 14.9 GB); **(b)** the community fp8-on-MPS patch (Comfy-Org discussion #13273 — bounces dequant through CPU; must be reapplied after every update).

## The Phases

| Phase | File                                                                                | Level               |
| ----- | ----------------------------------------------------------------------------------- | ------------------- |
| 1     | [[01-phase-1-foundations]] — the graph, your first render, the 6 params that matter | Easy                |
| 2     | [[02-phase-2-image-quality]] — FLUX, img2img, upscaling, LoRAs, prompt craft        | Easy → Intermediate |
| 3     | [[03-phase-3-control-and-editing]] — ControlNet, Qwen-Image-Edit, product shots     | Intermediate        |
| 4     | [[04-phase-4-video]] — WAN 2.2, the MoE pair, interpolation, upscale                | Intermediate        |
| 5     | [[05-phase-5-advanced-video]] — VACE, consistency, and fixing your 80-min problem   | Advanced            |
| 6     | [[06-phase-6-automation-api-mcp]] — the HTTP API and driving ComfyUI from Claude    | Advanced            |
| 7     | [[07-capstones]] — three end-to-end projects                                        | Capstone            |
| —     | [[08-reference]] — model↔encoder↔VAE matrix, troubleshooting, downloads             | Reference           |
| —     | [[09-google-flow-parity]] — Flow/Veo 3.1 capability map → local stack + gap plan    | Reference           |

Start with [[01-phase-1-foundations]].
