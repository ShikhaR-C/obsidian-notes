#!/usr/bin/env python3
"""
comfy_mcp_server — a dependency-free MCP server that drives a local ComfyUI.

Speaks JSON-RPC 2.0 over stdio (the MCP stdio transport) using nothing but the
Python standard library, so there is no third-party package to trust or update.

Register it with:
    claude mcp add comfyui -- python3 /absolute/path/to/comfy_mcp_server.py

Assumes ComfyUI is reachable at COMFY_HOST (default http://127.0.0.1:8000).
Comfy Desktop serves on :8000; a manual `python main.py` serves on :8188.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

COMFY_HOST = os.environ.get("COMFY_HOST", "http://127.0.0.1:8000")
CLIENT_ID = "claude-mcp"
PROTOCOL_VERSION = "2024-11-05"

# Model wiring, lifted verbatim from the blueprints that ship with ComfyUI 0.27.1.
# Changing these numbers is how you get a worse image slowly.
MODELS = {
    "z-image": {
        "unet": "z_image_turbo_bf16.safetensors",
        "clip": "qwen_3_4b.safetensors",
        "clip_type": "lumina2",
        "vae": "ae.safetensors",
        "steps": 8,
        "cfg": 1.0,
        "sampler": "res_multistep",
        "scheduler": "simple",
        "shift": 3.0,
    },
    "flux": {
        "unet": "flux1-dev.safetensors",
        "clip": ("clip_l.safetensors", "t5xxl_fp16.safetensors"),
        "clip_type": "flux",
        "vae": "ae.safetensors",
        "steps": 20,
        "cfg": 1.0,
        "sampler": "euler",
        "scheduler": "simple",
        "shift": None,  # FLUX uses no ModelSamplingAuraFlow node
    },
}


# ---------------------------------------------------------------- ComfyUI HTTP

def _get(path):
    with urllib.request.urlopen(f"{COMFY_HOST}{path}", timeout=10) as r:
        return json.loads(r.read())


def _post(path, payload):
    req = urllib.request.Request(
        f"{COMFY_HOST}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def comfy_up():
    try:
        _get("/system_stats")
        return True
    except Exception:
        return False


def build_t2i_graph(prompt, model="z-image", width=1024, height=1024,
                    seed=0, steps=None, batch=1):
    """Assemble a text-to-image graph in ComfyUI's *API* format.

    API format is a flat dict of node_id -> {class_type, inputs}, where a link
    to another node is the 2-tuple [node_id, output_index]. It is NOT the same
    shape as the .json you get from 'Save' in the UI — see Phase 6 §2.
    """
    m = MODELS[model]
    steps = steps or m["steps"]
    g = {}

    g["1"] = {"class_type": "UNETLoader",
              "inputs": {"unet_name": m["unet"], "weight_dtype": "default"}}

    if model == "flux":
        g["2"] = {"class_type": "DualCLIPLoader",
                  "inputs": {"clip_name1": m["clip"][0], "clip_name2": m["clip"][1],
                             "type": m["clip_type"], "device": "default"}}
    else:
        g["2"] = {"class_type": "CLIPLoader",
                  "inputs": {"clip_name": m["clip"], "type": m["clip_type"],
                             "device": "default"}}

    g["3"] = {"class_type": "VAELoader", "inputs": {"vae_name": m["vae"]}}
    g["5"] = {"class_type": "CLIPTextEncode",
              "inputs": {"clip": ["2", 0], "text": prompt}}
    g["6"] = {"class_type": "ConditioningZeroOut",
              "inputs": {"conditioning": ["5", 0]}}
    g["7"] = {"class_type": "EmptySD3LatentImage",
              "inputs": {"width": width, "height": height, "batch_size": batch}}

    # Z-Image needs the AuraFlow shift node; FLUX does not.
    if m["shift"] is not None:
        g["4"] = {"class_type": "ModelSamplingAuraFlow",
                  "inputs": {"model": ["1", 0], "shift": m["shift"]}}
        model_src = ["4", 0]
    else:
        model_src = ["1", 0]

    g["8"] = {"class_type": "KSampler",
              "inputs": {"model": model_src, "positive": ["5", 0],
                         "negative": ["6", 0], "latent_image": ["7", 0],
                         "seed": seed, "steps": steps, "cfg": m["cfg"],
                         "sampler_name": m["sampler"], "scheduler": m["scheduler"],
                         "denoise": 1.0}}
    g["9"] = {"class_type": "VAEDecode",
              "inputs": {"samples": ["8", 0], "vae": ["3", 0]}}
    g["10"] = {"class_type": "SaveImage",
               "inputs": {"images": ["9", 0], "filename_prefix": "claude/gen"}}
    return g


def queue_and_wait(graph, timeout=900):
    """Submit a graph and block until it finishes. Returns output file paths."""
    res = _post("/prompt", {"prompt": graph, "client_id": CLIENT_ID})
    pid = res["prompt_id"]

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            hist = _get(f"/history/{pid}")
        except Exception:
            time.sleep(1)
            continue
        if pid in hist:
            entry = hist[pid]
            status = entry.get("status", {})
            if status.get("status_str") == "error" or status.get("completed") is False:
                msgs = status.get("messages", [])
                raise RuntimeError(f"ComfyUI reported an error: {msgs}")
            files = []
            for node_out in entry.get("outputs", {}).values():
                for key in ("images", "gifs", "video"):
                    for f in node_out.get(key, []) or []:
                        files.append({"filename": f.get("filename"),
                                      "subfolder": f.get("subfolder", ""),
                                      "type": f.get("type", "output")})
            return {"prompt_id": pid, "files": files}
        time.sleep(1)
    raise TimeoutError(f"Timed out after {timeout}s (prompt_id={pid}). "
                       f"It may still be running — check the ComfyUI queue.")


def output_path(f):
    root = os.path.expanduser("~/Documents/AI/ComfyUI/ComfyUI/output")
    return os.path.join(root, f.get("subfolder", ""), f["filename"])


# --------------------------------------------------------------------- Tools

TOOLS = [
    {
        "name": "comfy_status",
        "description": "Check whether the local ComfyUI server is running, and report queue depth.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "comfy_generate_image",
        "description": ("Generate an image locally. 'z-image' is fast (~14s, 8 steps); "
                        "'flux' is higher quality and better at text/counts (~30s, 20 steps). "
                        "Blocks until the render completes and returns the file path."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "What to generate."},
                "model": {"type": "string", "enum": ["z-image", "flux"], "default": "z-image"},
                "width": {"type": "integer", "default": 1024},
                "height": {"type": "integer", "default": 1024},
                "seed": {"type": "integer", "default": 0, "description": "0 = random."},
                "steps": {"type": "integer", "description": "Omit to use the model's tuned default."},
                "batch": {"type": "integer", "default": 1},
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "comfy_list_models",
        "description": "List installed models in a folder (checkpoints, diffusion_models, loras, vae, upscale_models, ...).",
        "inputSchema": {
            "type": "object",
            "properties": {"folder": {"type": "string", "default": "diffusion_models"}},
        },
    },
    {
        "name": "comfy_run_workflow",
        "description": ("Run a saved API-format workflow JSON from disk. Optionally override node "
                        "inputs before queueing, e.g. {\"6\": {\"text\": \"a red car\"}}."),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Absolute path to an API-format workflow .json"},
                "overrides": {"type": "object", "description": "node_id -> {input_name: value}"},
                "timeout": {"type": "integer", "default": 900},
            },
            "required": ["path"],
        },
    },
]


def call_tool(name, args):
    if name == "comfy_status":
        if not comfy_up():
            return (f"ComfyUI is NOT running at {COMFY_HOST}.\n"
                    "Start the Comfy Desktop app, or set COMFY_HOST if it's on another port "
                    "(Desktop uses :8000, `python main.py` uses :8188).")
        stats = _get("/system_stats")
        q = _get("/queue")
        dev = (stats.get("devices") or [{}])[0]
        running = len(q.get("queue_running", []))
        pending = len(q.get("queue_pending", []))
        return (f"ComfyUI is up at {COMFY_HOST}\n"
                f"Device : {dev.get('name', '?')}\n"
                f"VRAM   : {dev.get('vram_total', 0) / 1e9:.1f} GB total, "
                f"{dev.get('vram_free', 0) / 1e9:.1f} GB free\n"
                f"Queue  : {running} running, {pending} pending")

    if name == "comfy_generate_image":
        if not comfy_up():
            return f"ComfyUI is not running at {COMFY_HOST}. Start Comfy Desktop first."
        seed = args.get("seed", 0) or int(time.time() * 1000) % (2**31)
        graph = build_t2i_graph(
            prompt=args["prompt"],
            model=args.get("model", "z-image"),
            width=args.get("width", 1024),
            height=args.get("height", 1024),
            seed=seed,
            steps=args.get("steps"),
            batch=args.get("batch", 1),
        )
        t0 = time.time()
        res = queue_and_wait(graph)
        paths = [output_path(f) for f in res["files"]]
        return (f"Generated {len(paths)} image(s) in {time.time() - t0:.1f}s "
                f"(model={args.get('model', 'z-image')}, seed={seed}):\n"
                + "\n".join(paths))

    if name == "comfy_list_models":
        folder = args.get("folder", "diffusion_models")
        root = os.path.expanduser(f"~/Documents/AI/ComfyUI/ComfyUI/models/{folder}")
        if not os.path.isdir(root):
            return f"No such model folder: {folder}"
        out = []
        for f in sorted(os.listdir(root)):
            p = os.path.join(root, f)
            if os.path.isfile(p) and not f.startswith(("put_", ".")):
                out.append(f"{f}  ({os.path.getsize(p) / 1e9:.1f} GB)")
        return f"{folder}/\n" + ("\n".join(out) if out else "  (empty)")

    if name == "comfy_run_workflow":
        if not comfy_up():
            return f"ComfyUI is not running at {COMFY_HOST}. Start Comfy Desktop first."
        with open(os.path.expanduser(args["path"])) as fh:
            graph = json.load(fh)
        if "nodes" in graph and isinstance(graph.get("nodes"), list):
            return ("That file is in UI format, not API format. In ComfyUI: Settings → enable "
                    "Dev Mode, then Workflow → 'Export (API)'. See Phase 6 §2.")
        for node_id, inputs in (args.get("overrides") or {}).items():
            if node_id not in graph:
                return f"Override failed: node '{node_id}' is not in this workflow."
            graph[node_id].setdefault("inputs", {}).update(inputs)
        t0 = time.time()
        res = queue_and_wait(graph, timeout=args.get("timeout", 900))
        paths = [output_path(f) for f in res["files"]]
        return (f"Workflow finished in {time.time() - t0:.1f}s:\n"
                + ("\n".join(paths) if paths else "(completed, no file outputs)"))

    return f"Unknown tool: {name}"


# ----------------------------------------------------------- JSON-RPC / stdio

def respond(msg):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = req.get("method")
        rid = req.get("id")

        # Notifications have no id and must not be answered.
        if rid is None:
            continue

        if method == "initialize":
            respond({"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "comfyui", "version": "1.0.0"},
            }})

        elif method == "tools/list":
            respond({"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}})

        elif method == "tools/call":
            params = req.get("params", {})
            try:
                text = call_tool(params.get("name"), params.get("arguments") or {})
                respond({"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": text}]}})
            except Exception as e:
                respond({"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": f"Error: {type(e).__name__}: {e}"}],
                    "isError": True}})

        elif method == "ping":
            respond({"jsonrpc": "2.0", "id": rid, "result": {}})

        else:
            respond({"jsonrpc": "2.0", "id": rid,
                     "error": {"code": -32601, "message": f"Method not found: {method}"}})


if __name__ == "__main__":
    main()
