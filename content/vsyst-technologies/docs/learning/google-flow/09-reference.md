# Reference — Templates, Cheat-Sheets, Credits, Glossary & Sources

> Keep this open in a second pane while you work. Everything scattered across the phases, gathered here for fast copy-paste. Web-verified **2026-07-15**.

---

## 1. The 7-Ingredient Checklist (tape to monitor)

Every prompt, run this list — like a pilot's pre-flight:

```
☐ 1. SUBJECT   — who/what, specifically
☐ 2. ACTION    — one main thing, present tense
☐ 3. SCENE     — where + time of day
☐ 4. CAMERA    — movement + size + angle + lens
☐ 5. STYLE     — cinematic / cartoon / product-render / VHS…
☐ 6. LIGHTING  — quality of light + mood
☐ 7. AUDIO     — ambience + SFX + (dialogue in quotes)
```

Rules: **100–150 words · 3–6 sentences · present tense · one action + one camera move per 8 s · "no subtitles" on dialogue shots.**

## 2. Prompt Template Library

**Master fill-in:**

```
[CAMERA: move + size + angle + lens] of [SUBJECT: specific look] who
[ACTION: one thing, present tense] in/at [SCENE: place + time]. [STYLE]
with [LIGHTING + MOOD]. [AUDIO: ambience + SFX]; [SPEAKER, voice desc]
says: "[≤20-word line]". No subtitles.
```

**Spokesperson / testimonial:**

```
Slow push-in medium shot at eye level of [CHARACTER BIBLE LINE], sitting in
[setting], shallow depth of field. Warm, trustworthy corporate style, soft
even lighting, confident friendly mood. Quiet room tone; a [voice desc]
voice says: "[line]". No subtitles.
```

**Product hero (ad):**

```
Slow orbiting close-up, low angle, on 35mm with soft bokeh, of [PRODUCT]
on [surface], screen showing [app view], in a dark premium studio. High-end
product-render style, dramatic rim lighting with one soft key, aspirational
mood. Deep ambient hum and a soft whoosh as the camera arcs.
```

**Lifestyle / UGC:**

```
Handheld tracking medium-wide shot at eye level following [CHARACTER] as they
[action] in [everyday place] at [time]. Natural, authentic documentary style,
natural light, genuine mood. Real ambient sounds of [place]; [optional line].
No subtitles.
```

**Dashboard / app reveal:**

```
Static top-down shot, deep focus, of [device] showing the DZZLO dashboard
with [live map / order count] updating, on a clean desk. Crisp modern UI
style, bright even lighting. Soft interface chimes as data updates.
```

**Problem → Solution pair:**

```
PROBLEM: High-angle static wide shot of [CHARACTER] looking overwhelmed,
juggling [old way], cluttered scene, cool dim light, stressed mood. Tense
ambience.

SOLUTION: Low-angle slow push-in of the same [CHARACTER], calm and in
command, using DZZLO, clean bright scene, warm light, relieved confident
mood. Uplifting ambience; they say: "[payoff line]". No subtitles.
```

## 3. Camera Cheat-Sheet

**Size:** EWS · WS · MS (workhorse) · CU · ECU · OTS
**Angle:** eye-level (trust) · low (power) · high (vulnerable) · top-down (clarity) · aerial (scale) · Dutch (unease)
**Move:** static · pan · tilt · dolly-in/push-in · dolly-out/pull-back · tracking/follow · crane/jib · orbit/arc · zoom · handheld · FPV/drone
**Lens:** shallow DoF/bokeh · deep focus · wide-angle · telephoto/85mm · macro · rack focus · 35mm film

**Recipe by type:** product = orbit + CU + low + shallow · spokesperson = static/push-in + MS + eye-level · lifestyle = handheld tracking + eye-level · dashboard = static top-down + deep focus · opener = crane/aerial + EWS · problem = high-angle · solution = low-angle push-in.

**Stacking order:** `[move] + [size] + [angle] + [lens]` → *"slow dolly-in medium shot at eye level, shallow depth of field."*

## 4. Voice & Audio Cheat-Sheet

**Dialogue format:** `Speaker (voice desc) says: "line"` + `No subtitles`. **≤20 words / one breath / ~2–3 words per second.**

**Voice dials:** age · gender · accent · pitch-tone (deep/warm ↔ bright/light) · pace (slow/reassuring ↔ brisk) · emotion (calm/confident/excited/gentle/authoritative).

**Lip-sync:** automatic with quoted dialogue → help it with **one speaker · facing camera · named · medium-or-closer · same-face ingredient.**

**Sound layers (separate sentences):** SFX (one distinct sound) · ambience (background bed) · music (mood/genre) — or a reusable **Lyria** bed added in Vids.

**Locked brand voice:** Veo *generates* voice from description (no in-Flow cloning). For a pixel-locked voice, cut a dedicated VO track in Vids instead.

## 5. Credit Budget Table

> ⚠ Costs are Google's to change — **verify live in Flow.** Values below are the mid-2026 web-reported figures used across this course.

| Tier            | ~Credits | When                          |
| --------------- | -------- | ----------------------------- |
| Veo 3.1 Lite    | ~10      | Drafting, testing ideas       |
| Veo 3.1 Fast    | ~20      | Iterating a keeper            |
| Veo 3.1 Quality | ~100     | Final, locked shot only       |

**Our jar (AI Pro):** ~1,000 credits/month. **Images (Imagen/Whisk)** are cheap/separate — generate freely.

| Content type    | Typical budget | Shots           |
| --------------- | -------------- | --------------- |
| Promo           | ~140           | 1 + overlay     |
| Ad              | ~300           | 2               |
| Tutorial        | ~260           | 2 human + screen-rec |
| Brand film      | ~520           | 4–5             |
| Images          | ~0 (vs video jar) | n/a          |

**Prime Directive:** draft cheap (Lite) → iterate (Fast) → **commit expensive once** (Quality). Batch drafts; reuse ingredients; never Quality-render an unproven shot.

## 6. Starting-Point Decision

```
Need the SAME face/product/style again?  → Ingredients→Video  (Phase 5)
Have an approved still to animate?        → Frames→ or Image→Video
Brand-new throwaway idea?                 → Text→Video
Need it longer than 8 s?                  → Scene Extension / Scenebuilder
```

## 7. Glossary

| Term                | Plain meaning                                                        |
| ------------------- | ------------------------------------------------------------------- |
| **Flow**            | Google's AI filmmaking app (the film set)                           |
| **Veo 3.1**         | The video+audio model inside Flow (the crew)                        |
| **Imagen 4**        | Google's still-image model                                          |
| **Whisk**           | Remix a subject + scene + style image into a new image/video        |
| **Ingredients**     | Up to 3 reference images that pin character/object/style consistency |
| **Frames→Video**    | Give a first (± last) image; Veo animates from it                   |
| **Scene Extension** | Grow a clip past 8 s by generating from its last frame              |
| **Scenebuilder / "Jump To"** | Flow's timeline for extending/stitching shots              |
| **Credits**         | The coins each render costs; ~1,000/month on AI Pro                 |
| **RAG**             | AI that reads *your* documents before answering (Phase 7)          |
| **NotebookLM**      | Google's tool that turns your docs into a queryable knowledge base  |
| **Gem**             | A saved, custom Gemini persona (e.g. the Content Director)          |
| **PACT**            | Gem-writing frame: Persona · Assignment · Context · Template        |
| **Lyria / MusicFX** | Google's music-generation tool                                     |
| **Vids**            | Google's AI video-assembly app (the editing bench)                 |

## 8. Troubleshooting

| Problem                                   | Fix                                                                     |
| ----------------------------------------- | ----------------------------------------------------------------------- |
| Different face every clip                 | Use **Ingredients** + identical character-bible text ([[05-phase-5-character-consistency]]) |
| Unwanted subtitles burned in              | `no subtitles` + colon dialogue format ([[06-phase-6-voice-lipsync-audio]]) |
| Camera is boring / static                 | You forgot to specify movement — always state it ([[04-phase-4-camera-control]]) |
| Clip ignores half my prompt               | Too long / too many actions — cut to 100–150 words, one action          |
| Prompt details contradict → random result | Read it back; delete the fights (bright+moody, etc.)                     |
| Dialogue rushed or cut off                | Line too long — ≤20 words, one breath                                    |
| Blew the monthly budget                   | You Quality-rendered tests — draft on Lite, lock on Quality only         |
| Character drifts over a long clip         | Keep clips short; use start-frame + ingredient; hide cuts in the edit    |
| Ingredient consistency is weak            | Reference photo is blurry/busy — use sharp, plain-background stills      |
| Ingredient reference blurry / low-res     | Regenerate a clean plain-background still in Imagen; sharp refs only     |
| Gem writes off-brand / wrong facts        | Add the missing info to the NotebookLM notebook; re-ground ([[07-phase-7-custom-rag-brand-brain]]) |
| Voice timbre changes between clips        | Describe voice identically, or cut a locked VO in Vids                   |

## 9. Sources (web-verified 2026-07-15)

Primary (Google):

- [Veo 3.1 — Google DeepMind](https://deepmind.google/models/veo/)
- [How to create effective prompts with Veo 3 — DeepMind prompt guide](https://deepmind.google/models/veo/prompt-guide/)
- [Ultimate prompting guide for Veo 3.1 — Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)
- [Veo 3.1 Ingredients to Video — The Keyword (blog.google)](https://blog.google/innovation-and-ai/technology/ai/veo-3-1-ingredients-to-video/)
- [5 tips for using Flow — The Keyword](https://blog.google/innovation-and-ai/products/flow-video-tips/)
- [Create videos in Google Flow — Flow Help](https://support.google.com/flow/answer/16353334)
- [Manage your Google Flow credits — Flow Help](https://support.google.com/flow/answer/16526234)
- [Everything new in Google AI subscriptions (I/O 2026) — The Keyword](https://blog.google/products-and-platforms/products/google-one/google-ai-subscriptions/)
- [NotebookLM as a source in the Gemini app — Workspace Updates](https://workspaceupdates.googleblog.com/2026/01/take-notebooks-further-notebooklm-gemini.html)

Secondary (context / credit pricing — third-party, treat as indicative):

- [Google Flow Pricing Explained — MindStudio](https://www.mindstudio.ai/blog/google-flow-pricing-credits-tiers-explained)
- [Google Veo Pricing Calculator (Jul 2026) — CostGoat](https://costgoat.com/pricing/google-veo)
- [Build a Pro Knowledge Base: Gemini & NotebookLM 2026 — AI Fire](https://www.aifire.co/p/build-a-pro-knowledge-base-gemini-notebooklm-2026)

> **Reminder (vault rule):** credit costs and tier names are the first things Google re-tunes. Where a number touches your budget, confirm it live in Flow before relying on it.

---

**Back to:** [[00_README]] · Start over at [[01-phase-1-the-big-picture]]
