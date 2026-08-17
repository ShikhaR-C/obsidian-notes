# Comfy Studio — Phase 3 Build Plan: Control Maps and Instruction Editing

> Scope: bring [[03-phase-3-control-and-editing]] into the Comfy Studio website | Status: **plan, not yet built** (written 2026-08-16) | Outcome: the ControlNet and Qwen-Image-Edit workflows become clickable options next to Create / Refine / Enlarge, with depth, canny and pose each their own choice.

Phases 1–2 already live in the website ([[02-phase-2-image-quality]] tooling note). This is the plan for Phase 3: **dictating geometry** and **editing with a sentence**. Everything below was checked against the actual install and the blueprints that ship with it on 2026-08-16 — not against the course text, which has drifted (§3).

---

## 1. What Gets Added

Two capabilities, five new clickable things:

| New UI option               | What it does                                                      | Engine underneath                    |
| --------------------------- | ----------------------------------------------------------------- | ------------------------------------ |
| **📐 Follow a layout**      | Keep the shape of a reference picture, replace everything else    | Z-Image Turbo + Fun ControlNet Union |
| → **Edges** (Canny)         | Trace exact contours — product silhouettes, logos, architecture   | core `Canny` node                    |
| → **Depth** _(recommended)_ | Keep 3D form and spatial layout, free the surface                 | `lotus-depth-d-v1-1`                 |
| → **Pose**                  | Lock a body position, free clothing/identity/setting              | `sdpose_wholebody_fp16`              |
| **✏️ Edit with a sentence** | "Replace the background with a warehouse" — everything else stays | Qwen-Image-Edit + Lightning 4-step   |

Depth, canny and pose are **three separate, equally prominent options in the form** — not a dropdown buried in Advanced. See the mockup in §5.

## 2. Verified Inventory (2026-08-16)

The install is now **ComfyUI 0.31.1** (00_README still says 0.29.2 observed 2026-08-01). **Everything Phase 3 needs is on disk** — the last gap closed 2026-08-16:

| File                                                  | Where                    | Status                                                        |
| ----------------------------------------------------- | ------------------------ | ------------------------------------------------------------- |
| `Z-Image-Turbo-Fun-Controlnet-Union.safetensors`      | `model_patches/`         | ✅ 3.1 GB                                                     |
| `lotus-depth-d-v1-1.safetensors`                      | `diffusion_models/`      | ✅ 1.7 GB                                                     |
| `vae-ft-mse-840000-ema-pruned.safetensors`            | `vae/`                   | ✅                                                            |
| `sdpose_wholebody_fp16.safetensors`                   | **`checkpoints/`**       | ✅ (not `detection/` — it loads via `CheckpointLoaderSimple`) |
| `rt_detr_v4-x-hgnet_fp16.safetensors`                 | `diffusion_models/`      | ✅ (optional — only needed for multi-person pose)             |
| `qwen_image_edit_fp8_e4m3fn.safetensors`              | `diffusion_models/`      | ✅ 20.4 GB                                                    |
| `qwen_image_edit_2509_fp8_e4m3fn.safetensors`         | `diffusion_models/`      | ✅ 20.4 GB                                                    |
| `qwen_2.5_vl_7b_fp8_scaled` + `qwen_image_vae`        | `text_encoders/`, `vae/` | ✅                                                            |
| `Qwen-Image-Edit-Lightning-4steps-V1.0-bf16`          | `loras/`                 | ✅ 0.85 GB                                                    |
| `Qwen-Image-Edit-**2509**-Lightning-4steps-V1.0-bf16` | `loras/`                 | ✅ 0.85 GB — downloaded 2026-08-16, see §9                    |

**The §3 workaround in [[03-phase-3-control-and-editing]] is dead.** The 2509 model arrived in the Tier-1 download on 2026-08-01. The `TextEncodeQwenImageEdit` / `...Plus` swap is now a _choice between two installed models_, not a workaround — and the app should expose both.

## 3. Three Corrections — the Blueprint Drifted

The course text describes an older revision of the shipped template. Read off `image_z_image_turbo_fun_union_controlnet.json` in 0.31.1:

| [[03-phase-3-control-and-editing]] says  | The blueprint actually ships                                   |
| ---------------------------------------- | -------------------------------------------------------------- |
| `ImageScaleToTotalPixels`, target 1.0 MP | **`ImageScaleToMaxDimension`**, lanczos, largest side **1024** |
| Canny thresholds `low 0.3 / high 0.4`    | **`0.1` / `0.32`**                                             |
| KSampler steps **9**                     | **8** (same as plain Z-Image)                                  |

We build against what ships. §3 of the phase doc should be edited to match once this lands — that is a task in §8, slice 4.

## 4. The Two Graphs

Verified node-by-node against `comfy_extras/nodes_model_patch.py`, `nodes_lotus.py`, `nodes_sdpose.py`, `nodes_qwen.py` and the shipped subgraphs. Node ids follow the existing scheme in `lib/workflows.js` — **new ids stay above 10** so the real output keeps landing at `images[0]` (history object keys iterate in ascending numeric order; `10 SaveImage` must come before any extra save).

### 4.1 Follow a layout (control)

```
11 LoadImage
   └→ 20 ImageScaleToMaxDimension (lanczos, 1024)
        ├→ 21 <control map>            ─────────────┬→ 25 QwenImageDiffsynthControlnet
        └→ 24 GetImageSize → 7 EmptySD3LatentImage  │     (model, model_patch, vae, image, strength)
                                                     │
  1 UNETLoader (z_image_turbo_bf16) ─────────────────┤
 22 ModelPatchLoader (Z-Image-Turbo-Fun-…-Union) ────┤
  3 VAELoader (ae) ──────────────────────────────────┘
                          ↓
        4 ModelSamplingAuraFlow (shift 3) → 8 KSampler (8 steps, cfg 1, res_multistep/simple, denoise 1)
                          ↓
        9 VAEDecode → 10 SaveImage          30 SaveImage("…-control")  ← the map itself
```

Node **21** is the only part that changes per control type:

| Type      | Node chain at 21                                                                                                                                                                                                                                 |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Edges** | `Canny(low 0.1, high 0.32)`                                                                                                                                                                                                                      |
| **Depth** | `VAEEncode(vae-ft-mse)` → `SamplerCustomAdvanced(noise=DisableNoise, guider=BasicGuider(lotus UNET, LotusConditioning), sampler=KSamplerSelect(euler), sigmas=SetFirstSigma(BasicScheduler(normal,1,1), 999))` → `VAEDecode` → **`ImageInvert`** |
| **Pose**  | `CheckpointLoaderSimple(sdpose_wholebody_fp16)` → `SDPoseKeypointExtractor(model, vae, image, batch_size 16)` → `SDPoseDrawKeypoints(body/hands/face on, feet off, stick 4, face_point 2, score 0.3, draw_head)`                                 |

Three traps, all confirmed in source:

- **The apply node needs the VAE** — it encodes the control image into latent space. (Course text is right about this one.)
- **`ImageInvert` is not optional on depth.** The shipped Lotus subgraph outputs _through_ it. Drop it and the near/far polarity flips, which the ControlNet will happily obey — badly.
- **`SDPoseDrawKeypoints` gained a `draw_head` input** in this version. In API format every required input must be supplied; the template's stored widget list predates it.

The `rt_detr` detector feeds the optional `bboxes` input and is only needed for **multi-person** detection. We skip it in v1.

### 4.2 Edit with a sentence

```
 1 UNETLoader (qwen_image_edit[_2509]_fp8_e4m3fn)
    └→ 15 LoraLoaderModelOnly (…Lightning-4steps, 1.0)   [when a matching Lightning LoRA exists]
         └→ 26 CFGNorm (1.0) → 4 ModelSamplingAuraFlow (shift 3)
              └→ 8 KSampler (4 steps, cfg 1, euler/simple, denoise 1)
 2 CLIPLoader (qwen_2.5_vl_7b_fp8_scaled, type qwen_image)
 3 VAELoader (qwen_image_vae)          ← NOT ae.safetensors
11 LoadImage → 27 FluxKontextImageScale
                  ├→ 5 TextEncodeQwenImageEdit[Plus] (clip, vae, image1, prompt)   → positive
                  └→ 7 VAEEncode → latent
 6 negative: ConditioningZeroOut at cfg 1 · a real empty-prompt encode above 1
 9 VAEDecode → 10 SaveImage
```

- **Encoder node is chosen by filename**: `2509` → `TextEncodeQwenImageEditPlus` (takes `image1/2/3`), anything else → `TextEncodeQwenImageEdit` (single image). One rule, and it makes the Advanced UNET dropdown Just Work.
- **Output size comes from `FluxKontextImageScale`**, which snaps to the nearest preferred Kontext resolution for the source's aspect ratio. So the size fields hide in this mode.
- **`qwen_image_vae`, not `ae`.** Wrong VAE here = garbled colour at the very end of a slow render.
- The blueprint wires a second full `TextEncode…Plus` as the negative. At cfg 1 that is a wasted pass through a 7B vision-language encoder, and mathematically dead — so we apply the app's existing rule (`ConditioningZeroOut` at cfg 1, real encode above it). `CFGNorm` is a no-op at cfg 1 but stays, for fidelity to the blueprint and correctness when cfg rises.

## 5. The UI

Mode row grows to five cards; picking **📐 Follow a layout** reveals a second, equally prominent row of three:

```
What do you want to do?
┌────────────┬────────────┬────────────┬──────────────┬──────────────────┐
│ ✨ Create  │ 🎨 Refine  │ 🔍 Enlarge │ 📐 Follow a  │ ✏️ Edit with a   │
│    new     │  an image  │  & sharpen │    layout    │     sentence     │
└────────────┴────────────┴────────────┴──────────────┴──────────────────┘

What should it copy?                                  ← only when "Follow a layout"
┌─────────────────────┬─────────────────────┬─────────────────────┐
│ 📏 Edges            │ 🗿 Depth            │ 🕺 Pose             │
│ Traces exact        │ Keeps 3D form and   │ Locks a body        │
│ contours. Use for   │ layout, frees the   │ position. Frees     │
│ products, logos,    │ surface. Usually    │ clothing, identity, │
│ architecture.       │ the right choice.   │ and setting.        │
└─────────────────────┴─────────────────────┴─────────────────────┘

Reference picture      [ thumbnail ]  Choose image…
How strictly to follow  ├──────●───┤   Suggestion 0.5 · Obey 0.9 · Traced 1.2
Describe the picture   [ … ]                    ← "Describe the edit" in Edit mode
```

**Why the three control types are one mode with an option, not three modes:** exercise 5.1 ("Depth vs Canny, same source") becomes a one-click Experiment only if `control_type` is a _parameter_ that a sweep axis can vary. Three separate modes would make the course's own comparison impossible to automate. The user-visible result is identical — three cards, three plain-language choices.

_(If you'd rather have all seven as one flat row of top-level cards, that is a change to one array in `public/app.js` and the `MODES` list — the graph builder does not care.)_

Engine cards get a compatibility matrix: `control → [zimage]`, `edit → [qwenedit]`, everything else → `[zimage, flux]`. Picking a mode auto-switches the engine when the current one can't serve it, and greys out the rest. The prompt textarea relabels itself to **"Describe the edit"** in Edit mode, with the §3 do/don't grammar in its help box.

## 6. Design Decisions

**1 — Control-map extraction lives inside the generation graph**, with a second `SaveImage` for the map, mirroring the `-gan` reference save that already exists for upscale. ComfyUI caches node outputs whose inputs are unchanged, so six variants over one source photo compute the depth pass **once**. One submit, one history entry, one code path, and the map is eyeball-able before you trust the render — which is exactly the lesson the `-gan` save exists to teach.

**2 — Qwen-Edit is a third _engine_, editing is a _mode_.** `qwenedit` joins `MODEL_DEFAULTS`/`WORKFLOW_MODELS` so the status panel's per-file checks work for it with no new machinery.

**3 — Edit mode reuses the existing `prompt` field as the instruction.** No new field means the prompt assistant, history, "Reuse settings" and refinement provenance all work untouched. It costs one new `PROMPT_GUIDES` entry matching `/qwen.*edit/i` so ✨ Refine with AI produces _instructions_ ("Change the jacket to dark green leather") instead of tag soup ("green jacket, 8k").

## 7. File-by-File

All paths relative to `comfy-studio/`.

**`lib/workflows.js`** — the bulk of the work.

- `MODES` += `control`, `edit`; `MODEL_DEFAULTS.qwenedit`; `MODE_ENGINES` matrix.
- New params: `control_type` (`canny|depth|pose`), `control_strength` (default 0.9), `canny_low` 0.1, `canny_high` 0.32.
- Replace the `mode === 'txt2img'` special case in `cleanParams` with a per-mode table (`{needsSource, denoise, allowsBatch}`) — control and edit both need a source _and_ denoise 1.0, a combination the current two-branch logic can't express.
- Two new `buildGraph` branches; `WORKFLOW_MODELS.qwenedit`; a `CONTROL_MODELS` map keyed by control type.
- `PROMPT_GUIDES` entry for Qwen-Edit.

**`lib/comfy.js`** — `status()` must additionally fetch `ModelPatchLoader` and `CheckpointLoaderSimple` object_info, to add `model_patches` and `checkpoints` to the choice lists. Without this the new file checks have nothing to resolve against and the status panel silently reports nothing.

**`server.js`** — source-missing error strings for the new modes; `SWEEP_AXES` gains numeric `control_strength` and a **categorical** `control_type`, which requires generalising the `values.filter(Number.isFinite)` guard in `hSweepPost` into a per-axis validator.

**`public/app.js`** — two `MODE_META` cards, one `MODEL_META` card, the three-card control-type picker, strength dial with named stops, `HELP` entries, engine greying, `updateVisibility` (hide size/denoise/batch in the new modes), `updateGenerateGate` (control models installed + reference picked), `estSeconds` branches, job-card and viewer-meta rows, mode-dependent prompt label.

**`README.md`** — modes list, `/api/generate` param table, the "Extending" recipe.

**New: `scripts/check-graph.mjs`** (~30 lines) — builds every engine × mode graph and validates each `class_type` and input name against ComfyUI's `/object_info`. This catches the one bug class that is otherwise invisible until ComfyUI 400s at submit, and it is the reason the node schemas above were read from source rather than trusted from the course text.

## 8. Slices

| #   | Slice                            | Contains                                                                                                                     | Verify by                                                                                                           |
| --- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 1   | **Control / Edges**              | Full mode plumbing + Canny. Cheapest extractor, no extra model load.                                                         | Render; confirm the `-control` map saves alongside; sweep strength 0.3→1.2 and watch it go rigid (**exercise 5.2**) |
| 2   | **Depth + Pose**                 | The two extractor chains behind the same picker.                                                                             | Same source through Depth and Canny at one seed (**exercise 5.1**)                                                  |
| 3   | **Edit**                         | `qwenedit` engine, edit mode, instruction prompt guide.                                                                      | Edit a photo — "replace the background with a warehouse loading bay" (**exercise 5.3**)                             |
| 4   | **Experiments + docs**           | The two new sweep axes; README; fix §2/§3 of [[03-phase-3-control-and-editing]] per §3 above and retire the 2509 workaround. | Both experiments run from the Experiments tab                                                                       |
| 5   | _(optional)_ **Multi-reference** | 2509's `image2`/`image3` — character + product + scene in one edit.                                                          | Unblocked (§9): the 2509 Lightning LoRA is on disk. This is the seed of the Phase 5 consistency work.               |

Slice 1 + 2 together deliver **exercise 5.4** (the six-variant product set) as: pick a photo → Depth → six prompts at fixed geometry → Enlarge the keeper.

## 9. The Download — Closed 2026-08-16

`Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors` (849,608,296 bytes) is in `loras/`. **The path trap was real**: unlike the v1 file, it is _not_ at the repo root — it sits in a `Qwen-Image-Edit-2509/` subfolder, exactly the way the [[08-reference]] §4 Stable Audio paths went stale. It is written **flat** into `loras/` so the dropdown shows the name the blueprint expects.

```bash
curl -fL -o ~/Documents/AI/ComfyUI/ComfyUI/models/loras/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors \
  "https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors"
```

Verified after download: 2160 BF16 tensors, `lora_up` / `lora_down` / `alpha` keys on `transformer_blocks.*`, declared end offset == file size. An **8-step** V1.0 variant sits beside it in the same subfolder if 4 steps ever proves too coarse.

**This changes the default engine.** With its Lightning LoRA present, 2509 is strictly better than the original edit model — same 4 steps at cfg 1, plus up to three reference images. So the §6 decision becomes:

> **`qwenedit` defaults to `qwen_image_edit_2509_fp8_e4m3fn` + `Qwen-Image-Edit-2509-Lightning-4steps` + `TextEncodeQwenImageEditPlus`.** The original `qwen_image_edit_fp8` and its v1 Lightning LoRA stay selectable in Advanced — the filename rule in §4.2 picks the matching encoder node automatically, so both pairings work without a special case.

Slice 5 (multi-reference) is no longer gated on a download — only on slice 3 shipping.

Estimated times for the new modes, all to be replaced with measured numbers on first run:

| Mode                             | Estimate                                               |
| -------------------------------- | ------------------------------------------------------ |
| Follow a layout — Edges          | ≈20–30 s (Z-Image 8 steps + control encode)            |
| Follow a layout — Depth          | + ≈10–20 s on the first render only; cached after      |
| Follow a layout — Pose           | + ≈10–20 s on the first render only; cached after      |
| Edit (2509 + Lightning, default) | ≈40–60 s                                               |
| Edit (Lightning switched off)    | ≈8–12 min ⚠ — the blueprint's 20-steps-at-cfg-4 branch |

## 10. Risks and Open Items

- **`batch_size > 1` with the control patch is unverified.** The patch encodes one control image; whether it broadcasts across a batched latent is untested. Pin batch to 1 in control mode for slice 1, lift it only after it renders correctly. This matters — batching at fixed geometry _is_ the six-variant product workflow.
- **Two big models resident at once.** Depth mode holds Lotus (1.7 GB) and Z-Image (12.3 GB) in the same graph. Fine in 48 GB, but if depth extraction ever starts re-running per render, that is the ComfyUI node cache having been evicted — check before blaming the graph.
- **Depth polarity.** If depth output looks inverted, the `ImageInvert` at the end of the Lotus chain is the first thing to check; the `-control` save exists so this is visible in one glance rather than after a wasted render.
- **`ZImageFunControlnet`** is the same class as `QwenImageDiffsynthControlnet` with `inpaint_image` + `mask` additionally exposed. We use the latter because it is what the blueprint ships — but the former is the upgrade path for ControlNet **and** inpainting from one model, and is worth a code comment at the call site.

---

**Next:** build slice 1. Course context: [[03-phase-3-control-and-editing]] · tooling so far: [[02-phase-2-image-quality]] · file/URL lookups: [[08-reference]]
