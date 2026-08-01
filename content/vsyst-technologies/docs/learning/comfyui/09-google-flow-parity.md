# Google Flow Parity — Replicating the Veo 3.1 Stack Locally

> Written **2026-08-01**, web-verified the same day. Companion to the [[../google-flow/00_README|Google Flow course]] on one side and [[00_README]] / [[08-reference]] on the other. Question answered here: **which Flow capabilities does this machine already replicate, which land with the 2026-08-01 download batch, and what else to pull.** Machine facts unchanged from [[00_README]] — except ComfyUI itself, observed live today at **0.29.2** (docs elsewhere were written against 0.27.1).

## The Verdict in Four Sentences

Most of Flow is replicable locally, and several pieces come out **better** (real negative prompts, unlimited free stills, actual voice cloning — which Flow refuses to do, deterministic seeds). The one thing with no good local equivalent is Veo 3.1's signature: **video + synchronized audio generated in a single pass** — locally that stays a compositional pipeline (TTS → talking-presenter model → music/SFX layered in the edit), which is more steps but _more_ controllable. The economics invert: Flow charges ~10–100 credits per 8-second clip from a 1,000/month budget; local costs nothing per render but pays in wall-clock (a 14B 5-second clip is minutes, not seconds). Treat Flow as the fast-iteration/final-polish tier and this machine as the unlimited-volume tier — they are complements, not rivals.

## Capability Map — Flow Feature → Local Equivalent

Status legend: ✅ on disk · ⬇ landing in the 2026-08-01 batch · 🛒 recommended pull (see plan below) · 🧪 experimental · ❌ no local equivalent.

### Generation modes

| Flow capability                     | Flow detail                                  | Local equivalent                                                                                                                                                                                              | Status                  |
| ----------------------------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| Text → Video                        | Veo 3.1, ~8 s/clip                           | WAN 2.2 TI2V 5B (drafts); FLUX-still → I2V 14B for quality (the [[04-phase-4-video]] §6 verdict)                                                                                                              | ✅                      |
| Image → Video                       | animate a still                              | WAN 2.2 I2V 14B MoE pair + LightX2V 4-step LoRAs                                                                                                                                                              | ✅                      |
| Frames → Video (first ± last frame) | "most controllable path in Flow"             | **Native WAN 2.2 FLF2V** — `WanFirstLastFrameToVideo` node uses the I2V 14B weights _already on disk_. Zero new downloads. Old plan's Fun-InP pair (28.6 GB) demoted to fallback if FLF2V quality disappoints | ✅ (new finding)        |
| Ingredients → Video (≤3 refs)       | pin character/product/style                  | Stills side: Qwen-Image-Edit 2509 (1–3 refs). Video side: VACE `reference_image` (single-ref, on disk); Phantom-WAN 14B for true multi-subject (frozen at WAN 2.1, still unmatched)                           | ⬇ + 🛒                  |
| Scene Extension (past 60 s)         | next clip grows from last frame              | **SVI 2.0 Pro** LoRA pair on I2V 14B — error-recycling beats naive last-frame chaining; still current (no SVI 3 exists as of 2026-08). Add `Well-Made/ComfyUI-Wan-SVI2Pro-FLF` nodes for FLF-aware stitching  | ✅ (landed today)       |
| Scenebuilder / Jump-To timeline     | extend, re-time, stitch                      | External editor (DaVinci/FCP/Vids) — same as Flow, which also defers assembly to Vids                                                                                                                         | ✅ (out of model scope) |
| Up-to-4K upscale, 9:16/16:9         | asserted, never operationalized in Flow docs | RealESRGAN ×4 / 4x-UltraSharp + FILM interpolation — fully operationalized in [[04-phase-4-video]]                                                                                                            | ✅ (parity or better)   |

### The consistency stack (Flow's 4 layers → local 5)

Flow locks identity with: identical words + ingredient photos + start frame + extension. Every layer has a local twin, plus one layer Flow cannot offer:

| Layer                 | Flow                   | Local                                                                                                                               |
| --------------------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------- | -------- |
| 1. Identical words    | character-bible line   | same discipline, same text — free                                                                                                   |
| 2. Reference images   | ≤3 ingredients         | Qwen-Edit 2509 multi-ref stills ⬇; Phantom-WAN video refs 🛒                                                                        |
| 3. Start frame        | Frames→Video           | native FLF2V ✅                                                                                                                     |
| 4. Extension          | Scene Extension        | SVI 2.0 Pro ✅                                                                                                                      |
| 5. **Character LoRA** | — impossible in Flow — | Z-Image base (12.3 GB, Tier 2) + LoRA training: the mascot/presenter becomes a _weight_, not a prompt. The ceiling Flow can't reach | 🛒 later |

### Audio & the talking presenter

| Flow capability                                         | Local equivalent                                                                                                                                                                                        | Status          |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| Native synced audio (dialogue+SFX+ambience in one pass) | **No single-model equivalent that works on this Mac.** Compose instead: script → TTS → S2V presenter → music/SFX in edit. The only credible single-pass candidate is LTX-2.3 fp8 — see experiment below | ❌ → pipeline   |
| Automatic lip-sync from quoted dialogue                 | WAN 2.2 S2V 14B (voice track + still → lip-synced video) ⬇; Sonic (portrait talking head on the `svd_xt` already on disk) ⬇; Wav2Lip for existing footage (0.4 GB, Tier 2)                              | ⬇               |
| Voice casting by description                            | Chatterbox TTS (MIT, official MPS) — and it does **zero-shot voice cloning**, which Flow explicitly cannot. Install `diodiogod/TTS-Audio-Suite` node; weights auto-fetch (~3.2 GB)                      | 🛒 node install |
| Music (generic, non-reusable in Veo)                    | ACE-Step 1.5 turbo — full songs, reusable, MIT                                                                                                                                                          | ⬇               |
| Lyria-style signature track                             | same ACE-Step, prompt saved = track re-generable                                                                                                                                                        | ⬇               |
| SFX                                                     | Stable Audio 3 small_sfx + t5gemma (landed today — note: repo moved files; lives in `checkpoints/`, commands fixed in [[08-reference]] §4)                                                              | ✅              |

### Camera control

Flow's four-part vocabulary (size + angle + movement + lens) and one-move-per-clip rule transfer **as prompt discipline** — WAN understands the same film language, just with weaker adherence than Veo. For Flow's _preset-grade_ control:

| Option                              | What                                                                                                                 | Verdict                                                                                                                                            |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Prompt-level camera language        | free, works today on WAN 2.2                                                                                         | ✅ baseline                                                                                                                                        |
| **WAN 2.2 Fun Camera-Control A14B** | preset pan/tilt/zoom/orbit embeddings — the closest thing to Flow's camera presets; official native ComfyUI template | 🛒 **the** camera pull — take GGUF Q5_K_M (~11.8 GB × 2, `QuantStack/Wan2.2-Fun-A14B-Control-Camera-GGUF`, Apache-2.0) via `ComfyUI-GGUF`, not fp8 |
| Uni3C / ReCamMaster / Stand-In      | wrapper-only (Kijai) — dead on MPS upstream, but a maintained Mac fork exists: `sienadrayy/ComfyUI-WanVideoWrapper`  | 🧪 only if the fork earns trust                                                                                                                    |

### Workflow layers (the part that ports verbatim)

| Flow layer                                                                   | Local twin                                                                                                           |
| ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| Imagen stills, "generate generously"                                         | Z-Image Turbo 14 s / FLUX 30 s — literally free, even more generous ✅                                               |
| Whisk remixing                                                               | Qwen-Edit 2509 multi-ref ⬇                                                                                           |
| Storyboard-first (still as approval gate → start frame)                      | identical pipeline, better: stills cost nothing, so _every_ shot gets a storyboard ✅                                |
| NotebookLM Brand Brain (RAG)                                                 | Obsidian vault + `qwen3.6:35b-mlx` (256K ctx, already pulled) as the grounded writer                                 |
| Gemini Gem "Content Director" (PACT)                                         | same PACT block as a system prompt on qwen3.6 via Ollama; `stavsap/comfyui-ollama` node wires it into graphs 🛒 node |
| Prompt expansion, 7-part prompt, winning-prompt flywheel, archive discipline | model-agnostic habits — adopt unchanged ✅                                                                           |
| Lite→Fast→Quality credit ladder                                              | maps to: TI2V 5B drafts → 14B + 4-step LoRAs → 14B full steps. Currency is minutes, not credits ✅                   |
| Vids assembly, captions, CTA cards                                           | external editor, same as Flow ✅                                                                                     |
| Negative prompts (Veo: effectively none)                                     | real negative prompts at cfg > 1 — a _local advantage_ ✅                                                            |
| Seeds / determinism (Veo: none)                                              | full seed control — a _local advantage_ ✅                                                                           |

## The 2026-08-01 Batch (what landed today)

Tier 1 + Sonic, per [[08-reference]] §4: SVI 2.0 Pro pair ✓ · clip_vision_h ✓ · wav2vec2 ✓ · Stable Audio 3 small_sfx + t5gemma ✓ (corrected paths) · Sonic full set (incl. whisper-tiny, RIFE) · ACE-Step 1.5 turbo · WAN 2.2 S2V 14B fp8 · Qwen-Image-Edit 2509 fp8 · Ollama `gemma4:12b-mlx` + `qwen3.5:4b-mlx`. Manual step remaining: **Chatterbox** via the TTS-Audio-Suite custom node (weights auto-fetch on first use).

## The Remaining Gap Plan — what to pull, in order

Ranked by Flow-parity value per GB. GGUF preferred over fp8 wherever both exist, pending the fp8-on-MPS measurement (below).

| #   | Pull                                                      | GB                         | Closes                                                                  | Path                                                                                                                             |
| --- | --------------------------------------------------------- | -------------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| 1   | _(nothing)_ — native WAN 2.2 FLF2V template               | 0                          | Frames→Video                                                            | already-owned I2V 14B weights; just use the template                                                                             |
| 2   | WAN 2.2 Fun Camera GGUF Q5 pair + `ComfyUI-GGUF` node     | ~24                        | camera presets                                                          | `QuantStack/Wan2.2-Fun-A14B-Control-Camera-GGUF`                                                                                 |
| 3   | Chatterbox via `TTS-Audio-Suite` node                     | 3.2                        | voice + cloning                                                         | node manager; MIT                                                                                                                |
| 4   | Phantom-WAN 14B fp8 (+1.3B draft, 2.9)                    | 15                         | multi-subject ingredients                                               | `Kijai/WanVideo_comfy` — still nothing better for "N stills → one scene"; MAGREF is the only rival, wrapper-only                 |
| 5   | `Well-Made/ComfyUI-Wan-SVI2Pro-FLF` nodes                 | 0                          | extension + keyframes combined                                          | GitHub node, rides existing SVI LoRAs                                                                                            |
| 6   | **SCAIL-2** (June 2026, official ComfyUI tutorial exists) | ~14B-class, GGUF available | character animate/replace — the 2026 successor-in-spirit to WAN Animate | `docs.comfy.org/tutorials/video/zai/scail2`; **check license before commercial use**; no Mac reports yet — you'd write the first |
| 7   | Z-Image base + LoRA training                              | 12.3                       | consistency layer 5                                                     | Tier 2 as planned; [[07-capstones]]                                                                                              |
| 8   | HunyuanVideo-Foley **fp16** (not fp8)                     | 10.3                       | video→SFX foley                                                         | ⚠ unverified on Mac; ⚠ license excludes EU/UK/KR — Stable Audio 3 covers most needs                                              |

### The LTX-2.3 experiment (single-pass audio+video — Veo's actual trick)

New since the July plan (which skipped LTX as Metal-broken): the encoder problem is solved (`gemma_3_12B_it_fp4_mixed` single-file), a community **fp8-on-MPS patch exists** (Comfy-Org discussion #13273 — patches `comfy/float.py` to bounce fp8 through CPU; validated on the LTX-2.3 workflow), and there's an MLX route (`noreff/ComfyUI-LTX-MLX-A2V`, benchmarked on an M5 Max). Honest constraints: 29.5 GB model, audio decode only reliable at 21/61-frame counts on Mac, the MLX route wants ~50 GB RAM — right at this machine's ceiling. **Verdict: worth one weekend as an experiment, not the backbone.** If it works, it's the only true "prompt → talking video with sound" on this Mac.

### Verified dead ends (don't re-research)

Ovi 1.1 (fp8 blocked, native loader rejects it, zero Mac successes) · MOVA (needs 50–80 GB RAM, CUDA SageAttention) · "open" WAN 2.5/2.6/2.7 (API-only on Comfy Cloud; HF repos claiming otherwise are mislabeled) · LongCat-2.0 (weights unreleased; v1 is wrapper-only) · everything in the [[00_README]] skip list still stands.

## The Flow-Shaped Local Pipeline

```
brief ──────────── qwen3.6 w/ PACT system prompt   (Brand Brain + Gem)
   ↓
stills, generously ─ Z-Image / FLUX                 (Imagen, but free)
   ↓
character sheet +
per-shot keyframes ─ Qwen-Edit 2509 multi-ref       (Ingredients)
   ↓
video ─┬─ FLF2V from keyframe pairs                 (Frames→Video)
       ├─ I2V + SVI 2.0 Pro chains                  (Scene Extension)
       ├─ Fun Camera GGUF for preset moves          (camera presets)
       └─ Chatterbox voice → S2V / Sonic presenter  (audio + lip-sync)
   ↓
audio ─── ACE-Step music + Stable Audio 3 SFX       (Lyria + native SFX)
   ↓
finish ── FILM ×2 + RealESRGAN 4K                   (upscale)
   ↓
QC ────── gemma4 vision: same face? on-brand?       (no Flow equivalent)
```

## ~~Open Item~~ MEASURED — fp8 on MPS Is Broken, Not Merely Wasteful

Run 2026-08-01, ComfyUI 0.29.2, via the API: WAN 2.2 I2V 14B fp8_scaled, 512², 33 frames, 4 steps. Result:

- **Load is honest**: `loaded completely; 13631.42 MB loaded, full load: True` — the 13.6 GB fp8 UNet occupies 13.6 GB, no upcast. The memory-halving assumption was _right_.
- **Compute is broken**: sampling crashes with `TypeError: Trying to convert Float8_e4m3fn to the MPS backend but it does not have support for that dtype`, thrown from comfy-kitchen's `dequantize_fp8` (upstream #8785). Reproduced **with and without** the LightX2V LoRAs — it's the scaled-fp8 dequant path itself.
- **Text encoders are exempt**: the umt5 fp8 encoder completed its part of the same run.

**Casualties on this disk**: the WAN 2.2 I2V 14B pair (which every fp8 timing estimated but — it turns out — had never actually run), WAN 2.2 S2V 14B, and both Qwen-Edit fp8 files. fp16/bf16 models (Z-Image, FLUX, TI2V 5B, VACE) are unaffected.

**The two exits** (per-file GGUFs verified on Hugging Face 2026-08-01):

| Route                                   | Cost                                                                                                                      | Trade                                                                                                                              |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **GGUF variants** + `ComfyUI-GGUF` node | I2V pair Q5_K_M 10.8 GB ×2 · S2V Q5 15.0 GB · Qwen-Edit-2509 Q5 14.9 GB (all `QuantStack/…-GGUF`) ≈ 51.5 GB (Q4: ≈ 46 GB) | supported, quantized-in-RAM (helps the 48 GB ceiling), slight quality cost vs fp8; first custom node enters the install            |
| **#13273 CPU-bounce patch**             | 0 GB                                                                                                                      | rescues the fp8 files already on disk; unofficial, must be reapplied after every ComfyUI update; one user report of it not working |

These aren't exclusive — the patch is worth one attempt since the fp8 files are already paid for; GGUF is the durable path either way and was already the pick for Fun Camera and LTX-2.3 alternatives above.
