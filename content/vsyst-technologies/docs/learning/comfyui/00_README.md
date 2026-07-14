# ComfyUI — Local Image & Video Generation on Apple Silicon

> Audience: me (Shikhar) | Machine: MacBook Pro M5 Max, 48 GB unified memory | Status: hands-on tutorial, written against **this** install — every filename, setting, and timing below was read off the actual machine on 2026-07-15.

## What This Folder Is

A seven-phase, hands-on course in ComfyUI that goes from "render your first image in 14 seconds" to "drive the whole thing from Claude over MCP." It is **not** a generic tutorial. Every workflow uses models that are already on this disk, every sampler setting is copied from the blueprint that ships with this ComfyUI version, and every performance number is either measured from the logs or explicitly labelled as an estimate.

Read the phases in order. Each one ends with an exercise that produces a file you can look at.

## The Machine (measured)

|                    |                                                                   |
| ------------------ | ----------------------------------------------------------------- |
| **Chip**           | Apple M5 Max — 18 CPU cores, **40 GPU cores**                     |
| **Memory**         | **48 GB unified** (CPU and GPU share one pool — no separate VRAM) |
| **Disk**           | 1.5 TB free                                                       |
| **OS**             | macOS 26.5.2                                                      |
| **ComfyUI**        | **0.27.1** (Desktop app 1.0.28)                                   |
| **Python / Torch** | 3.13.12 / **torch 2.10.0**, MPS backend active                    |
| **Install root**   | `~/Documents/AI/ComfyUI/ComfyUI`                                  |

**Unified memory is the single fact that governs everything else in this course.** On an NVIDIA box, a model must fit in VRAM or it does not run. Here, a model that "doesn't fit" doesn't fail — it silently spills into swap and the render takes 80 minutes instead of 8. Most of the performance advice in Phase 5 is really memory advice.

## What's Installed (185 GB)

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

| LoRA                                                  | Effect                                  |
| ----------------------------------------------------- | --------------------------------------- |
| `wan2.2_i2v_lightx2v_4steps_lora_v1_{high,low}_noise` | WAN 2.2 I2V 14B: **20 steps → 4 steps** |
| `Qwen-Image-Edit-Lightning-4steps-V1.0-bf16`          | Qwen edit: **20 steps → 4 steps**       |

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

## Four Things Wrong With This Install (found while writing this)

These are read off your actual files. Fix them before you start.

1. **Your VACE workflow is the reason renders take 80 minutes.** `video_wan_vace_flf2v.json` loads the 32 GB fp16 VACE model with `weight_dtype = default` and runs **20 steps at cfg 6**. 32 GB of weights + a 6.3 GB text encoder + activations does not fit in 48 GB alongside macOS — so it swaps. Fix in [[05-phase-5-advanced-video]].

2. **The "Text to Video (Wan 2.2)" blueprint cannot run here.** It wants `wan2.2_t2v_{high,low}_noise_14B` — you have the **I2V** 14B pair, not T2V. Use TI2V 5B for text→video instead ([[04-phase-4-video]]).

3. **The "Image Edit (Qwen 2509)" blueprint won't load your files.** It expects `qwen_image_edit_2509_*`; you have the original `qwen_image_edit_*`. Two dropdowns to change — details in [[03-phase-3-control-and-editing]].

4. **You have no CausVid LoRA.** This is the single biggest speed win available to you and it's ~600 MB. It takes VACE 14B from 20 steps to 4. Download command in [[08-reference]].

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

Start with [[01-phase-1-foundations]].
