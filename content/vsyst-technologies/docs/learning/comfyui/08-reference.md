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

### Priority 1 — CausVid LoRA (319 MB) · biggest win available

Cuts VACE 14B from 20 steps to 4. See [[05-phase-5-advanced-video]] §1.

```bash
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/loras/Wan21_CausVid_14B_T2V_lora_rank32.safetensors \
  https://huggingface.co/Kijai/WanVideo_comfy/resolve/main/Wan21_CausVid_14B_T2V_lora_rank32.safetensors
```

_(Verified: HTTP 200, 319 MB.)_ Use at **strength 0.30** — 1.0 kills the motion.

### Priority 2 — CLIP-Vision (1.2 GB)

Your `clip_vision/` folder is empty. Needed for WAN 2.1 I2V workflows and any IPAdapter-style reference work.

```bash
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/clip_vision/clip_vision_h.safetensors \
  https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/clip_vision/clip_vision_h.safetensors
```

### Priority 3 — WAN 2.2 T2V 14B (~28 GB) · only if you need native text→video

Unblocks the `Text to Video (Wan 2.2)` blueprint. Honestly: **try FLUX-still → I2V 14B first** ([[04-phase-4-video]] §6). It's usually better _and_ cheaper, because you can iterate on the still in 30 s.

Needs: `wan2.2_t2v_{high,low}_noise_14B_fp8_scaled.safetensors` + `wan2.2_t2v_lightx2v_4steps_lora_v1.1_{high,low}_noise.safetensors` (`Comfy-Org/Wan_2.2_ComfyUI_Repackaged`).

### Priority 4 — nice to have

| Want                                                                         | Get                                     |
| ---------------------------------------------------------------------------- | --------------------------------------- |
| Qwen-Image **base** (text→image; you only have Edit)                         | `Comfy-Org/Qwen-Image_ComfyUI` (~20 GB) |
| Qwen-Image-Edit **2509** (multi-reference; unlocks the blueprint as shipped) | `Comfy-Org/Qwen-Image-Edit_ComfyUI`     |
| SAM3 (masking → VACE video inpainting)                                       | `sam3.1_multiplex_fp16.safetensors`     |
| Anime/illustration upscale                                                   | `4x-AnimeSharp.pth`                     |

### Already installed 2026-07-15

`RealESRGAN_x4plus` · `4x-UltraSharp` · `film_net_fp16` · `Z-Image-Turbo-Fun-Controlnet-Union` · `lotus-depth-d-v1-1` · `vae-ft-mse-840000-ema-pruned` · `sdpose_wholebody_fp16` · `rt_detr_v4-x-hgnet_fp16`

## 5. Troubleshooting (Apple Silicon)

| Symptom                                    | Cause                                          | Fix                                                                      |
| ------------------------------------------ | ---------------------------------------------- | ------------------------------------------------------------------------ |
| **Output is coloured noise / smeared**     | Wrong VAE                                      | §1. It's almost always the WAN VAE.                                      |
| **Render takes absurdly long**             | Model doesn't fit → swap                       | Set `weight_dtype` to `fp8_e4m3fn`. Lower resolution/frames.             |
| **Image looks fried, over-contrasty**      | CFG too high on a distilled model              | cfg → 1                                                                  |
| **Negative prompt does nothing**           | cfg = 1 → negatives are mathematically ignored | Expected. Not a bug.                                                     |
| **Blurry, mushy, undercooked**             | Too few steps for a _full_ model               | Full models need 20+. Only distilled ones do 4–8.                        |
| **Anatomy is wrong / duplicated subjects** | Generating far from native resolution          | Generate at 1024², then upscale.                                         |
| **Reference image flashes at video start** | Missing `TrimVideoLatent`                      | Wire `trim_latent` → `TrimVideoLatent`. [[05-phase-5-advanced-video]] §2 |
| **`/prompt` returns 400**                  | You POSTed a UI-format workflow                | Dev Mode → **Export (API)**. [[06-phase-6-automation-api-mcp]] §2        |
| **Model not in the dropdown**              | Wrong folder, or ComfyUI not restarted         | Check §1 for the right folder; restart.                                  |
| **Video motion is dead/static**            | CausVid LoRA at strength 1.0                   | Drop to **0.30**.                                                        |

### Apple-Silicon specifics

- **`fp8_e4m3fn_fast` gives no speedup here.** ComfyUI's `supports_fp8_compute()` returns `False` on any non-NVIDIA device, so the fast fp8 matmul path never engages. It's harmless but inert — use plain `fp8_e4m3fn`. You still get the **memory** halving, which is the thing that actually matters at 48 GB.
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
