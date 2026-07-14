# Phase 6 — Automation: The API, and Driving ComfyUI From Claude

> Level: Advanced | Time: ~1 hr | Outcome: you can generate images from a script, from a shell, and by asking Claude in plain English. **The MCP server in this phase is written, tested, and confirmed working on your machine — see §5.**

---

## 1. Why Bother

The GUI is for exploring. It's a bad fit for the moment you need _forty product shots, one per SKU, same lighting, filenames matching your catalogue._ That's a loop, and loops belong in code.

ComfyUI is a **web server with an HTTP API**. The GUI is just one client of it. Anything the GUI can do, you can do over HTTP.

## 2. Two Workflow Formats (this trips up everyone)

| Format         | What it is                                                                                                              | How to get it                                              |
| -------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| **UI format**  | What `Workflow → Save` writes. Has `nodes[]`, positions, colours, link routing — everything needed to _draw_ the graph. | Save in the UI                                             |
| **API format** | A flat `{node_id: {class_type, inputs}}` dict. No cosmetics. **This is the only thing `/prompt` accepts.**              | Settings → enable **Dev Mode** → `Workflow → Export (API)` |

**The API endpoint will reject a UI-format file.** If you're getting confusing 400s, this is why 90% of the time. (The MCP server in §4 detects this specific mistake and tells you plainly.)

API format is small enough to write by hand. A link to another node is the 2-tuple `[node_id, output_index]`:

```json
{
  "1": {
    "class_type": "UNETLoader",
    "inputs": { "unet_name": "z_image_turbo_bf16.safetensors", "weight_dtype": "default" }
  },
  "2": {
    "class_type": "CLIPLoader",
    "inputs": { "clip_name": "qwen_3_4b.safetensors", "type": "lumina2", "device": "default" }
  },
  "3": { "class_type": "VAELoader", "inputs": { "vae_name": "ae.safetensors" } },
  "4": { "class_type": "ModelSamplingAuraFlow", "inputs": { "model": ["1", 0], "shift": 3.0 } },
  "5": {
    "class_type": "CLIPTextEncode",
    "inputs": { "clip": ["2", 0], "text": "a brass compass" }
  },
  "6": { "class_type": "ConditioningZeroOut", "inputs": { "conditioning": ["5", 0] } },
  "7": {
    "class_type": "EmptySD3LatentImage",
    "inputs": { "width": 1024, "height": 1024, "batch_size": 1 }
  },
  "8": {
    "class_type": "KSampler",
    "inputs": {
      "model": ["4", 0],
      "positive": ["5", 0],
      "negative": ["6", 0],
      "latent_image": ["7", 0],
      "seed": 42,
      "steps": 8,
      "cfg": 1.0,
      "sampler_name": "res_multistep",
      "scheduler": "simple",
      "denoise": 1.0
    }
  },
  "9": { "class_type": "VAEDecode", "inputs": { "samples": ["8", 0], "vae": ["3", 0] } },
  "10": {
    "class_type": "SaveImage",
    "inputs": { "images": ["9", 0], "filename_prefix": "api/test" }
  }
}
```

That's Phase 1's graph, exactly. **This is verified working** — it's the graph the MCP server builds, and it produced a real image on your machine at 13.98 s warm.

## 3. The Endpoints

Comfy Desktop serves on **`:8000`**. A manual `python main.py` serves on **`:8188`**.

| Method | Endpoint                                   | Use                                                                             |
| ------ | ------------------------------------------ | ------------------------------------------------------------------------------- |
| `GET`  | `/system_stats`                            | Is it up? What device? How much memory free?                                    |
| `GET`  | `/object_info`                             | **Every node, with its exact inputs and valid values.** The real API reference. |
| `POST` | `/prompt`                                  | Queue a graph: `{"prompt": {...}, "client_id": "..."}` → returns `prompt_id`    |
| `GET`  | `/history/{prompt_id}`                     | Poll for completion + output filenames                                          |
| `GET`  | `/queue`                                   | What's running / pending                                                        |
| `GET`  | `/view?filename=…&subfolder=…&type=output` | Download a result                                                               |
| `WS`   | `/ws?clientId=…`                           | Live progress (per-step), instead of polling                                    |

> `/object_info` is the single most useful endpoint and nobody mentions it. Every node, every input, every valid enum value — generated from the live install, so it's never out of date. When you're unsure what a node takes, `curl` it rather than searching a forum:
>
> ```bash
> curl -s http://127.0.0.1:8000/object_info/KSampler | python3 -m json.tool
> ```

## 4. A Batch Script

Forty SKUs, one loop. This is the thing the GUI can't do.

```python
import json, urllib.request, time

HOST = "http://127.0.0.1:8000"   # :8188 if you launched via `python main.py`

def queue(graph):
    req = urllib.request.Request(f"{HOST}/prompt",
        data=json.dumps({"prompt": graph, "client_id": "batch"}).encode(),
        headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req).read())["prompt_id"]

def wait(pid):
    while True:
        h = json.loads(urllib.request.urlopen(f"{HOST}/history/{pid}").read())
        if pid in h:
            return [f["filename"]
                    for o in h[pid]["outputs"].values()
                    for f in o.get("images", [])]
        time.sleep(1)

base = json.load(open("zimage_api.json"))   # exported via Dev Mode → Export (API)

for i, sku in enumerate(["nozzle-a", "nozzle-b", "dispenser-c"]):
    g = json.loads(json.dumps(base))                    # deep copy per run
    g["5"]["inputs"]["text"] = f"product photo of {sku}, studio lighting, white background"
    g["8"]["inputs"]["seed"] = 1000 + i                 # deterministic + reproducible
    g["10"]["inputs"]["filename_prefix"] = f"catalog/{sku}"
    print(sku, "→", wait(queue(g)))
```

Two habits worth keeping: **deep-copy the graph per iteration** (mutating a shared dict is a classic silent bug), and **derive the seed from the index** so any single image can be regenerated exactly.

## 5. The MCP Server — Ask Claude for an Image

MCP (Model Context Protocol) lets Claude call local tools. Wire ComfyUI up as one and you can say _"generate me three variants of a fuel nozzle on white"_ in chat, and the images land in your output folder.

**`assets/comfy_mcp_server.py`** (in this folder) is a complete, **dependency-free** MCP server — pure Python standard library, no `pip install`, no third-party package in your supply chain. It speaks JSON-RPC 2.0 over stdio and wraps the endpoints in §3.

### Register it

```bash
claude mcp add comfyui -- python3 ~/Documents/KIT/GITHUB/DZZLO_OMS/v1_79/obsidian-notes/content/vsyst-technologies/docs/learning/comfyui/assets/comfy_mcp_server.py
```

Then start Comfy Desktop and, in any Claude Code session, just ask.

> If you run ComfyUI manually on :8188 instead of Desktop's :8000, set the host:
> `claude mcp add comfyui --env COMFY_HOST=http://127.0.0.1:8188 -- python3 /path/to/comfy_mcp_server.py`

### The tools it exposes

| Tool                   | Does                                                                            |
| ---------------------- | ------------------------------------------------------------------------------- |
| `comfy_status`         | Is ComfyUI up? Device, free memory, queue depth.                                |
| `comfy_generate_image` | Text→image via Z-Image (fast) or FLUX (quality). Blocks, returns the file path. |
| `comfy_list_models`    | What's installed in any model folder.                                           |
| `comfy_run_workflow`   | Run a saved **API-format** workflow, with optional per-node input overrides.    |

### Verified working — 2026-07-15

This isn't aspirational. It was run end-to-end against your install:

```
initialize          → protocolVersion 2024-11-05 ✓
tools/list          → 4 tools ✓
comfy_status        → "ComfyUI is up · Device: mps · 51.5 GB total, 33.9 GB free · Queue 0/0" ✓
comfy_generate_image → output/claude/gen_00001_.png   29.2 s  (cold — model load)
comfy_generate_image → output/claude/gen_00002_.png   14.1 s  (warm)
```

Two things worth taking from that:

- **The warm number is 13.98 s**, which independently confirms the 13–15 s figure in [[00_README]] that was read from your historical logs. The number is real.
- **Cold vs warm is a 2× difference**, entirely model-load time. The first render after launching ComfyUI always pays ~15 s to page 18.5 GB of weights (Z-Image + the Qwen3-4B text encoder) into memory. **Don't benchmark on a cold run**, and if you're batching, keep the process warm rather than restarting it per image.

### How it works, briefly

MCP over stdio is simpler than its reputation: newline-delimited JSON-RPC 2.0 on stdin/stdout. You handle three methods (`initialize`, `tools/list`, `tools/call`), respond with `{"content": [{"type": "text", ...}]}`, and **never answer a notification** (a message with no `id`). That's the entire protocol surface for a tool server. ~90 lines of the file is protocol; the rest is the ComfyUI graph-building from §2.

Worth reading the file rather than treating it as a black box — it's the clearest possible demonstration that the API format in §2 is _just data_.

## 6. What This Unlocks

- **Catalogue generation** — a loop over SKUs, deterministic seeds, filenames that match your database.
- **A/B prompt testing** — same seed, N prompts, compare.
- **Pipelines** — generate → upscale → save, chained without a human clicking.
- **Claude as the front end** — "make me a hero image for the DZZLO landing page, 16:9, warm morning light" and it appears.
- **Scheduled jobs** — cron a nightly batch.

## 7. Exercises

**7.1 — Export API format.** Settings → Dev Mode. Export your Phase 1 graph as API. Diff it against the UI-format save. Understand what got thrown away and why `/prompt` only wants the one.

**7.2 — Curl a render.** `POST /prompt` with the JSON from §2. Poll `/history/{id}`. Fetch via `/view`. No Python, no GUI — just HTTP. This makes it concrete.

**7.3 — Register the MCP server.** Run the `claude mcp add` command above. Start Comfy Desktop. Ask Claude: _"what's my ComfyUI status?"_ then _"generate a photo of a brass compass on a nautical map."_

**7.4 — Batch it.** Adapt §4 to generate 5 variants of one product with 5 different backgrounds. Confirm all 5 land in `output/catalog/`.

**7.5 — Extend the server.** Add a `comfy_generate_video` tool wrapping the TI2V 5B graph from [[04-phase-4-video]]. Everything you need is in `build_t2i_graph()` — it's the same pattern with `Wan22ImageToVideoLatent` and `CreateVideo` swapped in. Bump the timeout; video is slow.

---

**Next:** [[07-capstones]] — three projects that use all of it.
