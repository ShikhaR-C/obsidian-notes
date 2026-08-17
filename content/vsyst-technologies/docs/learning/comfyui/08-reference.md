# Reference — Matrices, Downloads, Troubleshooting

> The lookup tables. Bookmark this one.

---

## 1. The Model ↔ Text Encoder ↔ VAE Matrix

**This is the most useful table in the folder.** Modern models ship as three separate files, and pairing them wrong is the cause of nearly every "why is my output noise?" moment. Everything here is copied from the blueprints shipped with ComfyUI 0.27.1.

| Model                | `UNETLoader`                                 | Text encoder (`CLIPLoader`)                  | type         | VAE                 |
| -------------------- | -------------------------------------------- | -------------------------------------------- | ------------ | ------------------- |
| **Z-Image Turbo**    | `z_image_turbo_bf16`                         | `qwen_3_4b`                                  | `lumina2`    | `ae.safetensors`    |
| **FLUX.1-dev**       | `flux1-dev`                                  | `clip_l` + `t5xxl_fp16` (**Dual**CLIPLoader) | `flux`       | `ae.safetensors`    |
| **SDXL**             | _(checkpoint — all three baked in)_          | —                                            | —            | —                   |
| **Qwen-Image-Edit**  | `qwen_image_edit_fp8_e4m3fn`                 | `qwen_2.5_vl_7b_fp8_scaled`                  | `qwen_image` | `qwen_image_vae`    |
| **WAN 2.2 TI2V 5B**  | `wan2.2_ti2v_5B_fp16`                        | `umt5_xxl_fp8_e4m3fn_scaled`                 | `wan`        | ⚠ **`wan2.2_vae`**  |
| **WAN 2.2 I2V 14B**  | `wan2.2_i2v_{high,low}_noise_14B_fp8_scaled` | `umt5_xxl_fp8_e4m3fn_scaled`                 | `wan`        | ⚠ **`wan_2.1_vae`** |
| **WAN 2.1 VACE 14B** | `wan2.1_vace_14B_fp16`                       | `umt5_xxl_fp8_e4m3fn_scaled`                 | `wan`        | ⚠ **`wan_2.1_vae`** |

> ⚠ **The WAN VAE trap.** Only the **5B** uses `wan2.2_vae`. Both **14B** models — including the WAN _2.2_ one — use `wan_2.1_vae`. Get this wrong and you get coloured noise after a long render, with no error message.

## 2. Sampler Settings

| Model                       | Steps             | CFG   | Sampler / Scheduler        | Shift node                              |
| --------------------------- | ----------------- | ----- | -------------------------- | --------------------------------------- |
| Z-Image Turbo               | **8**             | 1     | `res_multistep` / `simple` | `ModelSamplingAuraFlow` 3               |
| Z-Image + ControlNet        | 9                 | 1     | `res_multistep` / `simple` | `ModelSamplingAuraFlow` 3               |
| FLUX.1-dev                  | **20**            | 1     | `euler` / `simple`         | — (`FluxGuidance` 3.5 optional)         |
| SDXL                        | 20–30             | 5–8   | `dpmpp_2m` / `karras`      | —                                       |
| Qwen-Image-Edit + Lightning | **4**             | 1     | `euler` / `simple`         | `ModelSamplingAuraFlow` 3 + `CFGNorm` 1 |
| WAN 2.2 TI2V 5B             | **20**            | **5** | `uni_pc` / `simple`        | `ModelSamplingSD3` 8                    |
| WAN 2.2 I2V 14B + LightX2V  | **4** (2+2 split) | 1     | `euler` / `simple`         | `ModelSamplingSD3` 5                    |
| WAN 2.1 VACE + CausVid      | **4**             | 1     | `uni_pc` / `simple`        | `ModelSamplingSD3` 5–8                  |

**The rule that generalises:** _distilled model (Turbo / Lightning / LightX2V / CausVid) → cfg 1 and few steps. Full model → cfg 5–7 and 20+ steps._ When in doubt, open the blueprint and copy it.

## 3. Performance (this machine)

✅ = measured on your hardware. _(est.)_ = extrapolated; replace with your real numbers.

| Task                                              | Settings                 | Time               |
| ------------------------------------------------- | ------------------------ | ------------------ |
| Z-Image Turbo — **cold** (first run after launch) | 1024², 8 steps           | **29.2 s** ✅      |
| Z-Image Turbo — **warm**                          | 1024², 8 steps           | **14.0 s** ✅      |
| FLUX.1-dev                                        | 1024², 20 steps          | **28–33 s** ✅     |
| Qwen-Image-Edit + Lightning                       | 4 steps                  | ~40–60 s _(est.)_  |
| WAN 2.2 TI2V 5B                                   | 640², 81f, 20 steps      | **65–105 s** ✅    |
| WAN 2.2 TI2V 5B                                   | 1280×704, 121f, 20 steps | **32–40 min** ✅   |
| WAN 2.2 I2V 14B + LightX2V                        | 640², 81f, 4 steps       | ~4–8 min _(est.)_  |
| VACE 14B — fp16, 20 steps _(current)_             | —                        | **80 min** ✅      |
| VACE 14B — fp8 + CausVid, 4 steps _(fixed)_       | —                        | ~8–15 min _(est.)_ |
| RealESRGAN 4×                                     | 1024² → 4096²            | seconds            |
| FILM ×2                                           | 81 → 161 frames          | seconds            |

**Cold vs warm is a 2× difference on images** — it's the ~15 s to page 18.5 GB (Z-Image + Qwen3-4B encoder) into memory. Never benchmark a cold run; keep the process warm when batching.

## 4. Recommended Downloads

> Restructured **2026-07-15** after a web-verified research pass (files checked against Hugging Face and the ComfyUI docs; Mac/MPS status against issue trackers). The tier logic and summary tables live in [[00_README]] — this is the exact-files companion. **Status 2026-08-01: the whole Tier 1 section below plus Sonic was downloaded** (Chatterbox's node install still manual); Tier 2/3 remain staged. If a curl 404s, the file moved inside its repo — open the repo page and adjust the path (this happened to both Stable Audio 3 files; paths below are corrected). Flow-parity view of the remaining gaps: [[09-google-flow-parity]].

### ✅ Done — CausVid LoRA (installed 2026-07-15)

`loras/Wan21_CausVid_14B_T2V_lora_rank32.safetensors` (319 MB) is on disk. Strength **0.30** — 1.0 kills the motion. Wiring in [[05-phase-5-advanced-video]] §1.

### Tier 1 — the content-studio core (~58 GB) — ✅ downloaded 2026-08-01

**SVI 2.0 Pro — storyline continuity** (2 × 1.23 GB → `loras/`). Chains unlimited 5-second segments on your existing WAN 2.2 I2V pair, with error-recycling so identity doesn't drift shot-to-shot.

```bash
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/loras/SVI_v2_PRO_Wan2.2-I2V-A14B_HIGH_lora_rank_128_fp16.safetensors \
  "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/LoRAs/Stable-Video-Infinity/v2.0/SVI_v2_PRO_Wan2.2-I2V-A14B_HIGH_lora_rank_128_fp16.safetensors"
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/loras/SVI_v2_PRO_Wan2.2-I2V-A14B_LOW_lora_rank_128_fp16.safetensors \
  "https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/LoRAs/Stable-Video-Infinity/v2.0/SVI_v2_PRO_Wan2.2-I2V-A14B_LOW_lora_rank_128_fp16.safetensors"
```

**Qwen-Image-Edit-2509 — character consistency in stills** (20.4 GB → `diffusion_models/`). Takes 1–3 reference images per edit (character + product + scene). Reuses your existing `qwen_2.5_vl_7b` encoder and `qwen_image_vae`. Makes the shipped `Image Edit (Qwen 2509)` blueprint run unmodified — the [[03-phase-3-control-and-editing]] §3 workaround retires.

```bash
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors \
  https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors
```

**Its speed LoRA — added 2026-08-16** (0.85 GB → `loras/`). Without this the 2509 blueprint takes the slow branch: **20 steps at cfg 4**, an estimated 8–12 min per edit here. With it: 4 steps at cfg 1. ⚠ **The file is not at the repo root** — unlike the v1 LoRA it lives in a `Qwen-Image-Edit-2509/` subfolder, so a curl copied from the v1 line 404s. Write it flat into `loras/` so the dropdown shows the name the blueprint expects. An 8-step variant sits beside it if 4 proves too coarse.

```bash
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/loras/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors \
  "https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors"
```

**WAN 2.2 S2V 14B — the speaking presenter** (16.4 GB → `diffusion_models/`, plus a 0.63 GB audio encoder → `audio_encoders/`, a folder you'll create). Still image + voice track → lip-synced talking video. Native template since core 0.3.53; reuses umt5 and `wan_2.1_vae`. No published Apple-Silicon benchmark exists — your first run writes the first number.

```bash
mkdir -p ~/Documents/AI/ComfyUI/ComfyUI/models/audio_encoders
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/diffusion_models/wan2.2_s2v_14B_fp8_scaled.safetensors \
  https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_s2v_14B_fp8_scaled.safetensors
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/audio_encoders/wav2vec2_large_english_fp16.safetensors \
  https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/audio_encoders/wav2vec2_large_english_fp16.safetensors
```

If fp8 turns out to upcast on MPS (the [[00_README]] measurement), the fallback is `QuantStack/Wan2.2-S2V-14B-GGUF` (Q4_K_M, 13.9 GB) + the `ComfyUI-GGUF` custom node.

**Chatterbox — voiceover + voice cloning** (~3.2 GB, MIT, official MPS support). No curl: install the `diodiogod/TTS-Audio-Suite` custom node and it fetches the `ResembleAI/chatterbox` weights on first use. The 23-language multilingual t3 is ~2.1 GB extra.

**ACE-Step 1.5 turbo — music beds** (10.0 GB → `checkpoints/`). MIT, native template, and the upstream repo ships Mac/MLX launch scripts — expect roughly 3–10× slower than the CUDA numbers people quote.

```bash
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/checkpoints/ace_step_1.5_turbo_aio.safetensors \
  https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/checkpoints/ace_step_1.5_turbo_aio.safetensors
```

**Stable Audio 3 small_sfx — sound effects** (2.3 GB + 1.2 GB t5gemma text encoder). Commercially licensed and small enough to run on CPU — the lowest-risk audio model on this machine. Folders below are the template's expectation; if a dropdown can't see a file, §5 last row.

```bash
# Paths corrected 2026-08-01 — the repo moved these into checkpoints/ and text_encoders/ subfolders
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/checkpoints/stable_audio_3_small_sfx.safetensors \
  https://huggingface.co/Comfy-Org/stable-audio-3/resolve/main/checkpoints/stable_audio_3_small_sfx.safetensors
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/text_encoders/t5gemma_b_b_ul2.safetensors \
  https://huggingface.co/Comfy-Org/stable-audio-3/resolve/main/text_encoders/t5gemma_b_b_ul2.safetensors
```

**CLIP-Vision H** (1.2 GB → `clip_vision/`, currently empty). Needed for WAN 2.1 I2V workflows, IPAdapter-style reference work, and WAN Animate in Tier 2.

```bash
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/clip_vision/clip_vision_h.safetensors \
  https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors
```

**Ollama side (not ComfyUI disk):** `ollama pull gemma4:12b-mlx` (7.7 GB, vision QC) · `ollama pull qwen3.5:4b-mlx` (4.0 GB, batch prompt expansion) · custom node `stavsap/comfyui-ollama` to call them from inside graphs.

### Tier 2 / Tier 3 — exact files (verified to exist 2026-07-15)

Rationale per row in [[00_README]]. GGUF rows need the `ComfyUI-GGUF` custom node.

| Capability                                       | Repo → file                                                                                                                                                                                        | GB          | Folder                                        |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | --------------------------------------------- |
| Character animate/replace (video)                | `Kijai/WanVideo_comfy_fp8_scaled` → `Wan22Animate/Wan2_2-Animate-14B_fp8_e4m3fn_scaled_KJ.safetensors` + Comfy-Org `wan2.2_animate_14B_relight_lora_bf16` (avoid the `_KJ_v2` files — load issues) | 18.4 + 1.4  | `diffusion_models/`, `loras/`                 |
| Multi-subject ref→video                          | `Kijai/WanVideo_comfy` → `Phantom-Wan-14B_fp8_e4m3fn.safetensors` (draft: `Phantom-Wan-1_3B_fp16`, 2.9)                                                                                            | 15.0        | `diffusion_models/`                           |
| Keyframe bridging (FLF, 2.2)                     | `Comfy-Org/Wan_2.2_ComfyUI_Repackaged` → `split_files/diffusion_models/wan2.2_fun_inpaint_{high,low}_noise_14B_fp8_scaled.safetensors`                                                             | 14.3 × 2    | `diffusion_models/`                           |
| Newest character-edit (stills)                   | `Comfy-Org/Qwen-Image-Edit_ComfyUI` → `qwen_image_edit_2511_fp8mixed.safetensors`, or `unsloth/Qwen-Image-Edit-2511-GGUF` Q4_K_M                                                                   | 20.5 / 13.2 | `diffusion_models/` / `unet/`                 |
| FLUX-family identity edit                        | `QuantStack/FLUX.1-Kontext-dev-GGUF` → `flux1-kontext-dev-Q4_K_M.gguf` (reuses your FLUX TEs + VAE; ⚠ non-commercial weights)                                                                      | 6.9         | `unet/`                                       |
| Apache multi-ref gen + edit                      | `Comfy-Org/flux2-klein-4B` → `flux-2-klein-4b.safetensors` + `flux2-vae` (0.34); TE is `qwen_3_4b` — verify your existing file is accepted                                                         | 7.8         | `diffusion_models/`, `vae/`                   |
| Talking head (Mac-verified) ✅ pulled 2026-08-01 | `LeonJoe13/Sonic` → `unet.pth` + `audio2token.pth` + `audio2bucket.pth` + `yoloface_v5m.pt` + `RIFE/flownet.pkl` + `whisper-tiny/`, via `smthemex/ComfyUI_Sonic`; base = your existing `svd_xt`    | 6.7         | `sonic/` (node README layout)                 |
| Lip-sync existing footage                        | `Nekochu/Wav2Lip` → `wav2lip_gan.pth`, via `ShmuelRonen/ComfyUI_wav2lip`                                                                                                                           | 0.4         | per node README                               |
| TTS quality leader                               | `Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice` (Apache-2.0; via TTS-Audio-Suite or `mlx-audio`)                                                                                                            | 4.5         | node-managed                                  |
| LoRA-training base                               | `Comfy-Org/z_image` → `z_image_bf16.safetensors` (undistilled; TE + VAE already on disk)                                                                                                           | 12.3        | `diffusion_models/`                           |
| Native T2V (the old Priority 3)                  | `Comfy-Org/Wan_2.2_ComfyUI_Repackaged` → `wan2.2_t2v_{high,low}_noise_14B_fp8_scaled` + `wan2.2_t2v_lightx2v_4steps_lora_v1.1_{high,low}_noise`                                                    | 27 + 2      | `diffusion_models/`, `loras/`                 |
| VACE at 2.2 quality                              | same repo → `wan2.2_fun_vace_{high,low}_noise_14B_fp8_scaled`                                                                                                                                      | 17.3 × 2    | `diffusion_models/`                           |
| Second motion opinion                            | `Comfy-Org/HunyuanVideo_1.5_repackaged` → `hunyuanvideo1.5_720p_i2v_cfg_distilled_fp8_scaled` + `byt5_small_glyphxl_fp16` + `hunyuanvideo15_vae_fp16` (reuses your `qwen_2.5_vl_7b` TE)            | ~10.4       | `diffusion_models/`, `text_encoders/`, `vae/` |
| Unlimited dubbing                                | `MeiGen-AI/InfiniteTalk` → `comfyui/infinitetalk_single.safetensors` — needs the WAN 2.1 I2V 14B base (~16 GB) you don't have                                                                      | 2.7 (+16)   | `diffusion_models/`                           |
| Long-form multi-speaker TTS                      | `microsoft/VibeVoice-1.5B` (Large: official repo pulled — mirror `aoi-ot/VibeVoice-Large`)                                                                                                         | 5.4 / 18.4  | node-managed                                  |

For the old Priority-3 verdict: unchanged — **try FLUX-still → I2V 14B first** ([[04-phase-4-video]] §6); it's usually better _and_ cheaper, because you iterate on the still in 30 s.

### Deliberately skipped (checked 2026-07-15)

FLUX.2 dev · LTX-2.3 · Ovi · LatentSync-in-ComfyUI · MMAudio / HunyuanVideo-Foley · F5-TTS (CC-BY-NC) · PuLID / InstantID / FaceID · "open" WAN 2.5/2.6/2.7 (API-only) · kijai WanVideoWrapper on MPS. One-line reasons in [[00_README]].

### Still nice to have (unchanged)

| Want                                                 | Get                                     |
| ---------------------------------------------------- | --------------------------------------- |
| Qwen-Image **base** (text→image; you only have Edit) | `Comfy-Org/Qwen-Image_ComfyUI` (~20 GB) |
| SAM3 (masking → VACE video inpainting)               | `sam3.1_multiplex_fp16.safetensors`     |
| Anime/illustration upscale                           | `4x-AnimeSharp.pth`                     |

### Already installed 2026-07-15

`RealESRGAN_x4plus` · `4x-UltraSharp` · `film_net_fp16` · `Z-Image-Turbo-Fun-Controlnet-Union` · `lotus-depth-d-v1-1` · `vae-ft-mse-840000-ema-pruned` · `sdpose_wholebody_fp16` · `rt_detr_v4-x-hgnet_fp16` · `Wan21_CausVid_14B_T2V_lora_rank32`

### Already installed 2026-08-01 (Tier 1 + Sonic batch)

`SVI_v2_PRO_..._{HIGH,LOW}` LoRAs · `clip_vision_h` · `wav2vec2_large_english_fp16` · `stable_audio_3_small_sfx` (→ `checkpoints/`) · `t5gemma_b_b_ul2` · `ace_step_1.5_turbo_aio` · `wan2.2_s2v_14B_fp8_scaled` · `qwen_image_edit_2509_fp8_e4m3fn` · full `sonic/` set · Ollama `gemma4:12b-mlx` + `qwen3.5:4b-mlx`. Remaining manual: Chatterbox via `TTS-Audio-Suite` node.

## 5. Troubleshooting (Apple Silicon)

| Symptom                                             | Cause                                                                       | Fix                                                                                                             |
| --------------------------------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Output is coloured noise / smeared**              | Wrong VAE                                                                   | §1. It's almost always the WAN VAE.                                                                             |
| **Render takes absurdly long**                      | Model doesn't fit → swap                                                    | Set `weight_dtype` to `fp8_e4m3fn`. Lower resolution/frames.                                                    |
| **Image looks fried, over-contrasty**               | CFG too high on a distilled model                                           | cfg → 1                                                                                                         |
| **Negative prompt does nothing**                    | cfg = 1 → negatives are mathematically ignored                              | Expected. Not a bug.                                                                                            |
| **Blurry, mushy, undercooked**                      | Too few steps for a _full_ model                                            | Full models need 20+. Only distilled ones do 4–8.                                                               |
| **Anatomy is wrong / duplicated subjects**          | Generating far from native resolution                                       | Generate at 1024², then upscale.                                                                                |
| **Reference image flashes at video start**          | Missing `TrimVideoLatent`                                                   | Wire `trim_latent` → `TrimVideoLatent`. [[05-phase-5-advanced-video]] §2                                        |
| **`/prompt` returns 400**                           | You POSTed a UI-format workflow                                             | Dev Mode → **Export (API)**. [[06-phase-6-automation-api-mcp]] §2                                               |
| **Model not in the dropdown**                       | Wrong folder, or ComfyUI not restarted                                      | Check §1 for the right folder; restart.                                                                         |
| **Video motion is dead/static**                     | CausVid LoRA at strength 1.0                                                | Drop to **0.30**.                                                                                               |
| **`TypeError: … Float8_e4m3fn to the MPS backend`** | fp8/fp8_scaled UNet on MPS — dequant has no fp8 dtype (measured 2026-08-01) | Use the GGUF variant of the model (+ `ComfyUI-GGUF`), or the #13273 CPU-bounce patch. [[09-google-flow-parity]] |

### Apple-Silicon specifics

- **fp8_scaled diffusion models are broken on MPS — measured 2026-08-01 on 0.29.2.** The I2V 14B fp8 UNet loads at true fp8 size (`loaded completely; 13631.42 MB`) but sampling crashes with `TypeError: Trying to convert Float8_e4m3fn to the MPS backend` in comfy-kitchen's `dequantize_fp8` (upstream #8785). Reproduced with and without speed LoRAs. Affects every fp8_scaled/fp8 **UNet** on disk (I2V 14B pair, S2V 14B, both Qwen-Edit files); **text encoders are fine** (umt5 fp8 encoded in the same failed run). Exits: GGUF variants + `ComfyUI-GGUF` node, or the Comfy-Org #13273 CPU-bounce patch — details in [[09-google-flow-parity]]. The old fp8_e4m3fn_fast note is moot: `supports_fp8_compute()` is `False` off-NVIDIA anyway.
- **No xformers / flash-attention.** ComfyUI falls back to split or PyTorch attention on MPS. Expected; don't chase it.
- **Unified memory doesn't hard-fail.** Unlike CUDA, you rarely see a clean OOM — you get swap and a 10× slowdown instead. **A mysteriously slow render is a memory problem until proven otherwise.**
- **Close other apps for the big runs.** A 32 GB model on a 48 GB machine leaves very little headroom, and Chrome will happily eat it.

## 6. Glossary

| Term                  | Meaning                                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------- |
| **Latent**            | The compressed space the model works in (~8× smaller than pixels). The VAE converts latent ↔ pixels.    |
| **UNet / DiT**        | The denoising network — the actual "model".                                                             |
| **Text encoder**      | Separate model (T5, Qwen, UMT5) that turns your prompt into conditioning vectors.                       |
| **VAE**               | The codec between latent and pixels. Model-specific. Mismatch = noise.                                  |
| **CFG**               | Classifier-Free Guidance. Prompt adherence strength. 1 = off.                                           |
| **Denoise**           | How much of the input latent to destroy. 1.0 = ignore input. <1.0 = img2img.                            |
| **Shift**             | Reweights the noise schedule (`ModelSamplingSD3` / `ModelSamplingAuraFlow`).                            |
| **Distillation**      | Training a model (or LoRA) to do in 4–8 steps what took 20–50. Requires cfg 1.                          |
| **LoRA**              | A small weight diff applied to a big model.                                                             |
| **MoE**               | Mixture-of-Experts. WAN 2.2 14B: separate high-noise and low-noise experts across the step schedule.    |
| **fp8 / bf16 / fp16** | Weight precision. fp8 ≈ half the memory of fp16.                                                        |
| **Blueprint**         | ComfyUI 0.27's built-in workflow templates (93 of them). The authoritative source for correct settings. |
| **API format**        | The flat `{node_id: {class_type, inputs}}` dict that `/prompt` accepts. Not the same as a UI save.      |

## 7. Paths

| What                   | Where                                                    |
| ---------------------- | -------------------------------------------------------- |
| ComfyUI root           | `~/Documents/AI/ComfyUI/ComfyUI`                         |
| Models                 | `~/Documents/AI/ComfyUI/ComfyUI/models/`                 |
| Your workflows         | `~/Documents/AI/ComfyUI/ComfyUI/user/default/workflows/` |
| Blueprints             | `~/Documents/AI/ComfyUI/ComfyUI/blueprints/`             |
| Outputs                | `~/Documents/AI/ComfyUI/ComfyUI/output/`                 |
| Logs                   | `~/Documents/AI/ComfyUI/logs/`                           |
| MCP server             | `./assets/comfy_mcp_server.py`                           |
| API (Desktop / manual) | `:8000` / `:8188`                                        |

---

← [[07-capstones]] · [[00_README]]
