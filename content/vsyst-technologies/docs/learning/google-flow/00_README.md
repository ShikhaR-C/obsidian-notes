# Google Flow — A Robot Film Crew for Marketing, Ads & Tutorials

> Audience: me (Shikhar) + the vsyst / DZZLO content team | Plan: **Google AI Pro** — 1,000 Flow credits a month + 50 a day, **not** Ultra | Goal: marketing, advertising, promos, tutorial videos, and images at professional quality, on a budget | Status: written & web-verified **2026-07-15** against **Veo 3.1** (launched 15 Oct 2025) and the current Google AI stack; **tool facts re-verified and corrected 2026-10-01**.

## Explain-it-like-I'm-5

Imagine you hired a **film crew made of magic robots**. You don't hand them a camera — you hand them a **note**. The note says who is in the shot, what they do, where they are, how the camera moves, and what we hear. Within minutes the robots hand you back a finished movie clip — **with sound, music, and people talking whose lips actually move**.

That's Google Flow. It is real, it is this good in 2026, and it runs in a browser tab.

Three catches, and this whole folder exists because of them:

1. **The crew forgets everything after ~8 seconds.** Every clip is made by a fresh crew who never met the last one. Keeping the _same_ actor, the _same_ logo, and the _same_ voice across ten clips is a **skill you have to learn** — that's Phases 5, 6, and 7.
2. **Every shot costs coins.** On our **AI Pro** plan we get a jar of **about 1,000 coins a month, plus 50 a day; neither rolls over.** A rough draft shot costs ~10 coins; a top-quality shot costs ~100. Blow coins on bad notes and the jar is empty by the 10th. Efficiency isn't a nice-to-have here — it's the whole game.
3. **The note is everything.** "Make a cool ad" gets you a vague, wasted clip. A precise, well-structured note gets you a usable one. Writing the note **is the job** — Phases 2, 3, and 4.

Everything below teaches you to write great notes, keep your characters consistent, and never waste a coin.

## What This Folder Is

An **eight-phase, hands-on course** in producing professional marketing content with Google Flow and the tools around it — from "make your first talking clip" to "run a whole brand-consistent content pipeline off a knowledge base." It is written for **our actual plan** (AI Pro, credit-limited) and **our actual goal** (content for DZZLO / vsyst — ads, promos, tutorials, product images), not a generic tour.

Read the phases in order. Each ends with an exercise that produces a file you can look at — a prompt, an image, a clip, or a reusable template.

## The One Fact That Governs Everything: Credits

On an unlimited plan you'd just brute-force every shot at max quality until it looked right. **We can't.** This single table is the reason the whole course is shaped the way it is.

| Our plan        | Flow credits | Roughly buys |
| --------------- | ------------ | ------------ |
| **AI Pro** ← us | **1,000 a month + 50 a day**; neither rolls over | ~100 draft clips **or** ~50 mid **or** ~10 final a month, plus 5 drafts a day |

And what each shot _costs_, **per output** — four takes cost four times; a failed one costs nothing (**verify live** in the prompt box → **Settings**; Google tunes these):

| Model · tier              | ~Credits per output            | Use it for                                                        |
| ------------------------- | ------------------------------ | ----------------------------------------------------------------- |
| Veo 3.1 Lite              | 10                             | Drafts. The only tier that can Extend                             |
| Veo 3.1 Fast              | 20                             | Iterating; the lock for most shots; takes Ingredients             |
| Veo 3.1 Quality           | 100                            | The locked hero shot only. No Ingredients — start from a still    |
| Omni Flash 1.1 (720p)     | 7 / 10 / 12 / 15 (4/6/8/10 s)  | Second unit: an alternative take, the saved-voice route           |
| Omni Flash 1.1 (360p)     | 4 / 5 / 6 / 7                  | Blocking tests — action and timing only, never look               |
| Omni Flash edit           | 40                             | Changing up to 10 s of an existing clip by prompt                 |
| Upscale to 1080p          | 0                              | Every finished shot (4K is Ultra-only)                            |

Our picture model is **Veo 3.1**, so a draft predicts its lock; Flow's second video model, **Gemini Omni Flash 1.1**, is the second unit.

> **The Prime Directive of this course: _draft cheap, commit expensive._** You get your prompt, camera, character, and timing _right_ on Lite/Fast (10–20 coins), and you spend a 100-coin Quality render **only once**, on a shot you already know is good — and many shots lock at Fast and never need it. A team that internalises this makes ~10× more content per month than one that renders everything at Quality. Every phase reinforces it.

## The Full Google Stack (use all of it — one tool is not a pipeline)

Flow is the camera, but a camera alone doesn't make a marketing department. On AI Pro you already own a whole studio. Here's the cast, in 5-year-old terms and in job terms:

| Tool                      | ELI5                                             | Its job in our pipeline                                                          |
| ------------------------- | ------------------------------------------------ | -------------------------------------------------------------------------------- |
| **Gemini app** (3.1 Pro)  | The clever assistant who writes things for you   | The **brain**: scripts, shot lists, and turning ideas into Veo-ready prompts     |
| **Gemini Notebook** (formerly NotebookLM) | A memory box that has _read_ all our brand stuff | The **brand brain** (custom RAG): grounds everything in _our_ facts & voice |
| **Gemini Gems**           | An assistant who memorised the memory box        | On-brand **prompt & script generator** you reuse forever (Phase 7); on personal accounts Gems become **skills** from November 2026, moved across automatically |
| **Nano Banana** (in Flow) | An instant illustrator                           | **Stills**: ad images, thumbnails, product shots, character sheets — and the **start frames** shots are animated from |
| **Flow** (Veo 3.1 + Omni Flash) | The robot film crew                        | The **video** itself — text, frames or ingredients → video; **Characters** (`@Name`) reuse a face and a voice |
| **Veo native audio**      | The crew's sound department                      | **Voice, lip-sync, sound effects, ambience, music** — generated _with_ the video |
| **Google Flow Music** (Lyria 3.5) | A jukebox that composes on demand        | Custom **music beds / jingles** when Veo's built-in music isn't enough — included with AI Pro; read its terms before you publish |
| **Google Vids**           | The editor who assembles the final cut           | **Stitch** clips + screen recordings + captions + AI voice-over (Hindi included) into tutorials & explainers |
| **DaVinci Resolve** (free edition) | The finishing room                      | **Finish** a film: the precise cut, the mix, the colour match, the 1080 × 1920 master (files 17–20) |
| **Drive / Docs / Sheets** | The filing cabinet & calendar                    | **Asset library**, script docs, and the content calendar                         |
| **Flow TV**               | A channel of "here's how they did it"            | **Learning**: real clips shown _with the prompt that made them_                  |
| **YouTube Shorts**        | The megaphone                                    | **Distribution** — Flow publishes single clips, and Vids whole videos, straight to YouTube |

The whole pipeline, one picture:

```
   IDEA
    │
    ▼
Gemini Notebook (brain) ──grounds──► Gemini Gem  ── writes ──►  script + shot list + per-shot prompts
                                          │
                    ┌─────────────────────┼───────────────────────┐
                    ▼                     ▼                       ▼
          Nano Banana (in Flow)      Flow / Veo 3.1       Google Flow Music
          (boards + ingredients)  (video + native audio)     (music bed)
                    │                     │                       │
                    └────── stills ──────►│◄──────────────────────┘
                                          ▼
                     Google Vids (assemble + captions) or DaVinci Resolve (finish)
                                          ▼
                              Drive (archive)  →  YouTube / site / ads
```

Read that top to bottom and you've read the whole course. Phases 2–4 are the "write the note" arrows; 5 is the "stills and ingredients" loop; 6 is the sound department; 7 is the brand-brain box on the top-left; 8 is running the whole diagram for real.

## What Veo 3.1 Can Actually Do (2026, measured against the current release)

So you calibrate expectations before spending a coin:

| Capability                   | Reality (re-verified 2026-10-01)                                                     |
| ---------------------------- | ------------------------------------------------------------------------------------ |
| Clip length                  | **4, 6 or 8 s** per Veo clip (Ingredients: 8 s; Omni Flash: 4–10 s). **Extend** continues an 8-second Veo clip, and only Veo 3.1 Lite extends (check in Flow) — a longer moment is usually a cut ([[10-deep-dive-scene-continuity]]) |
| Native audio                 | **Yes** — dialogue, SFX, ambience, and music, generated _in sync_ with the picture   |
| Lip-sync                     | **Yes, automatic** when you write quoted dialogue — the mouth matches the words. Google has evaluated English only: hear every Hindi or Hinglish line on a Lite draft |
| Character/object consistency | **Ingredients→Video** on Lite and Fast (8 s) and Omni Flash — **not Quality**; Flow states no image limit. **Characters** (`@Name`) bundle one or two images with a voice |
| Start/end control            | **Frames→Video** — give a first frame (and optional last frame) to steer the shot, on every tier. Changed in 2026: Quality takes no Ingredients, so a **Quality** shot gets its face from a still you make first (Nano Banana) |
| Resolution / format          | **1080p upscale free** on AI Pro (4K is Ultra-only); native **9:16 vertical** for Shorts/Reels and **16:9** |
| Editing / continuity         | **Scenebuilder** arranges, reorders, trims and previews shots — no transitions, no audio tools. **Omni Flash** edits up to 10 s of a clip by prompt (⏣40). Changed in 2026: *Jump To* is in no current Flow Help page |
| Watermark                    | Every output carries an invisible **SynthID** mark; for people living in India, Flow adds a **visible watermark** automatically. Leave it, and disclose AI use ([[20-colour-finishing-and-delivery]] §12) |

**The honest summary:** for 8-second, single-idea shots — a product beauty shot, a spokesperson line, a UI-in-a-lifestyle-scene — Veo 3.1 is genuinely broadcast-adjacent. Long, multi-character, plot-heavy films are still a _stitching_ job you do in the edit — Vids, or DaVinci Resolve for a film — one good 8-second shot at a time. Plan in **shots**, not scenes. Anyone promising you a finished 2-minute ad from one prompt is selling something.

## The Phases

| Phase | File                                                                                     | Level        |
| ----- | ---------------------------------------------------------------------------------------- | ------------ |
| 1     | [[01-phase-1-the-big-picture]] — the mental model, the stack hand-offs, the credit math  | Easy         |
| 2     | [[02-phase-2-prompting-basics]] — the 7-part note, templates, the word-count habit       | Easy         |
| 3     | [[03-phase-3-context-and-script-planning]] — Gemini: idea → script → shot list → prompts | Easy → Mid   |
| 4     | [[04-phase-4-camera-control]] — shots, angles, movement, lens — talking to the camera    | Intermediate |
| 5     | [[05-phase-5-character-consistency]] — Ingredients, reference sheets, keeping one face   | Intermediate |
| 6     | [[06-phase-6-voice-lipsync-audio]] — voices, dialogue, lip-sync, SFX, music              | Intermediate |
| 7     | [[07-phase-7-custom-rag-brand-brain]] — Gemini Notebook + a Gemini Gem = your brand's memory  | Advanced     |
| 8     | [[08-phase-8-pro-workflow-and-playbooks]] — the full pipeline + per-content-type recipes | Capstone     |
| —     | [[09-reference]] — prompt library, camera cheat-sheet, credit table, glossary, sources   | Reference    |
| —     | [[10-deep-dive-scene-continuity]] — past 8 s: what Extend really does, why the last-frame trick goes soft, the fixes; how a director breaks a scene into shots, which transition goes where, and the cohesion stack that makes a stitched cut look like one film | Deep dive    |

Start with [[01-phase-1-the-big-picture]].

## The Director's & Editor's Track (files 11–22)

The eight phases teach you to make **one good clip**. This track teaches you to make **one seamless film** out of thirty of them — to work the way a professional director does before the crews arrive, and the way a professional editing director does after they leave. It starts where [[10-deep-dive-scene-continuity]] stops, runs from beginner to pro, and works one film — *Saaf Hisaab*, a 90-second, 32-shot DZZLO short — from a single sentence to a delivered master.

| #  | File                                                                                                   | Level                   | Hat               |
| -- | ------------------------------------------------------------------------------------------------------ | ----------------------- | ----------------- |
| 11 | [[11-directors-track-roadmap]] — the level ladder, the track map, the film's fixed facts, what changed in Flow | Start here      | —                 |
| 12 | [[12-story-engine-seamless-storytelling]] — want, cause and change; the logline; *but / therefore*     | Beginner                | Director          |
| 13 | [[13-visual-language-composition-blocking-light]] — the 9:16 frame, blocking, light, the colour script | Beginner → Intermediate | Director          |
| 14 | [[14-previs-storyboard-floorplan-animatic]] — floor plan, boards, animatic, the generation plan        | Intermediate            | Director          |
| 15 | [[15-continuity-bible-script-supervisor]] — the state table, frozen prompt blocks, the frame-pair check | Intermediate           | Continuity        |
| 16 | [[16-directing-performance-and-dialogue-scenes]] — playable verbs, matched singles, one voice across clips | Intermediate → Advanced | Director       |
| 17 | [[17-editing-1-workflow-and-the-cut]] — Resolve set-up, dailies, the four trims, finding the cut frame | Beginner → Intermediate | Editor            |
| 18 | [[18-editing-2-rhythm-structure-and-rescue]] — rhythm, time, re-cutting, the AI rescue kit, picture lock | Advanced              | Editor            |
| 19 | [[19-sound-edit-design-and-mix]] — dialogue edit, beds, split edits, music spotting, the mix           | Intermediate → Advanced | Editor            |
| 20 | [[20-colour-finishing-and-delivery]] — match, look, captions, safe zones, export, QC, AI disclosure    | Advanced                | Editor            |
| 21 | [[21-long-form-multi-scene-production]] — the production bible, the coin calendar, gates, series       | Pro                     | Producer-director |
| 22 | [[22-capstone-saaf-hisaab-workbook]] — the whole film end to end, a rubric, a failure clinic            | Beginner → Pro          | Both              |

Finish Phases 1–8 and file 10 first, then start at [[11-directors-track-roadmap]].

---

> **A note on honesty (the vault rule).** Flow, Veo, and the credit prices move _fast_ — Veo 3.1 arrived in October 2025, Lite in March 2026, and Flow's second video model, Gemini Omni Flash, in May 2026 (1.1 in August). Every capability above was web-verified on 2026-07-15 and re-verified on 2026-10-01, but **credit costs and exact tier names are the first things Google re-tunes.** Where a number matters to your budget, confirm it live in Flow (the prompt box → **Settings**) before you rely on it. Sources: Flow Help — [Models](https://support.google.com/flow/answer/16352836), [Credits](https://support.google.com/flow/answer/16526234), [Get started](https://support.google.com/flow/answer/16353333), [Characters & YouTube](https://support.google.com/flow/answer/16935308), [Flow Music](https://support.google.com/flow/answer/17083870) · [Veo — Gemini API](https://ai.google.dev/gemini-api/docs/veo) · [Gemini release notes](https://gemini.google/release-notes/) · [Gems → skills](https://support.google.com/gemini/answer/18560919?hl=en) · [Gemini Notebook](https://blog.google/innovation-and-ai/products/gemini-notebook/notebooklm-gemini-notebook/) · [Vids limits](https://support.google.com/docs/answer/15609411); more in [[09-reference]] §9 and [[11-directors-track-roadmap]] §10.
