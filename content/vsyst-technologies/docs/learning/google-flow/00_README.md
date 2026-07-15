# Google Flow — A Robot Film Crew for Marketing, Ads & Tutorials

> Audience: me (Shikhar) + the vsyst / DZZLO content team | Plan: **Google AI Pro** — ~1,000 Flow credits/month, **not** Ultra | Goal: marketing, advertising, promos, tutorial videos, and images at professional quality, on a budget | Status: written & web-verified **2026-07-15** against **Veo 3.1** (released 13 Jan 2026) and the current Google AI stack.

## Explain-it-like-I'm-5

Imagine you hired a **film crew made of magic robots**. You don't hand them a camera — you hand them a **note**. The note says who is in the shot, what they do, where they are, how the camera moves, and what we hear. About ten seconds later the robots hand you back a finished movie clip — **with sound, music, and people talking whose lips actually move**.

That's Google Flow. It is real, it is this good in 2026, and it runs in a browser tab.

Three catches, and this whole folder exists because of them:

1. **The crew forgets everything after ~8 seconds.** Every clip is made by a fresh crew who never met the last one. Keeping the _same_ actor, the _same_ logo, and the _same_ voice across ten clips is a **skill you have to learn** — that's Phases 5, 6, and 7.
2. **Every shot costs coins.** On our **AI Pro** plan we get a jar of about **1,000 coins a month**. A rough draft shot costs ~10 coins; a top-quality shot costs ~100. Blow coins on bad notes and the jar is empty by the 10th. Efficiency isn't a nice-to-have here — it's the whole game.
3. **The note is everything.** "Make a cool ad" gets you a vague, wasted clip. A precise, well-structured note gets you a usable one. Writing the note **is the job** — Phases 2, 3, and 4.

Everything below teaches you to write great notes, keep your characters consistent, and never waste a coin.

## What This Folder Is

An **eight-phase, hands-on course** in producing professional marketing content with Google Flow and the tools around it — from "make your first talking clip" to "run a whole brand-consistent content pipeline off a knowledge base." It is written for **our actual plan** (AI Pro, credit-limited) and **our actual goal** (content for DZZLO / vsyst — ads, promos, tutorials, product images), not a generic tour.

Read the phases in order. Each ends with an exercise that produces a file you can look at — a prompt, an image, a clip, or a reusable template.

## The One Fact That Governs Everything: Credits

On an unlimited plan you'd just brute-force every shot at max quality until it looked right. **We can't.** This single table is the reason the whole course is shaped the way it is.

| Our plan        | Flow credits / month | Roughly buys                                     |
| --------------- | -------------------- | ------------------------------------------------ |
| **AI Pro** ← us | **~1,000**           | ~100 draft clips **or** ~50 mid **or** ~10 final |

And what each shot _costs_ (Veo 3.1 tiers, credits per generation — **verify live, Google tunes these**):

| Veo 3.1 tier | ~Credits / clip | Use it for                                             |
| ------------ | --------------- | ------------------------------------------------------ |
| **Lite**     | ~10             | Blocking, testing a prompt, "does the idea even work?" |
| **Fast**     | ~20             | Iterating a shot you like; near-final drafts           |
| **Quality**  | ~100            | The **locked, final** shot only — never a test         |

> **The Prime Directive of this course: _draft cheap, commit expensive._** You get your prompt, camera, character, and timing _right_ on Lite/Fast (10–20 coins), and you spend a 100-coin Quality render **only once**, on a shot you already know is good. A team that internalises this makes ~10× more content per month than one that renders everything at Quality. Every phase reinforces it.

## The Full Google Stack (use all of it — one tool is not a pipeline)

Flow is the camera, but a camera alone doesn't make a marketing department. On AI Pro you already own a whole studio. Here's the cast, in 5-year-old terms and in job terms:

| Tool                      | ELI5                                             | Its job in our pipeline                                                          |
| ------------------------- | ------------------------------------------------ | -------------------------------------------------------------------------------- |
| **Gemini app** (3 Pro)    | The clever assistant who writes things for you   | The **brain**: scripts, shot lists, and turning ideas into Veo-ready prompts     |
| **NotebookLM**            | A memory box that has _read_ all our brand stuff | The **brand brain** (custom RAG): grounds everything in _our_ facts & voice      |
| **Gemini Gems**           | An assistant who memorised the memory box        | On-brand **prompt & script generator** you reuse forever (Phase 7)               |
| **Imagen 4**              | An instant illustrator                           | **Stills**: ad images, thumbnails, product shots, character reference sheets     |
| **Whisk**                 | A remix machine (mix a subject + scene + style)  | Fast **ingredients & mood boards**; Whisk Animate turns a still into video       |
| **Flow (Veo 3.1)**        | The robot film crew                              | The **video** itself — text→video, image→video, extend, scene-build              |
| **Veo native audio**      | The crew's sound department                      | **Voice, lip-sync, sound effects, ambience, music** — generated _with_ the video |
| **Lyria / MusicFX**       | A jukebox that composes on demand                | Custom **music beds / jingles** when Veo's built-in music isn't enough           |
| **Google Vids**           | The editor who assembles the final cut           | **Stitch** Veo clips + screen recordings + captions into tutorials & explainers  |
| **Drive / Docs / Sheets** | The filing cabinet & calendar                    | **Asset library**, script docs, and the content calendar                         |
| **Flow TV**               | A channel of "here's how they did it"            | **Learning**: real clips shown _with the prompt that made them_                  |
| **YouTube Shorts**        | The megaphone                                    | **Distribution** — Veo is wired straight into Shorts                             |

The whole pipeline, one picture:

```
   IDEA
    │
    ▼
NotebookLM (brand brain) ──grounds──► Gemini Gem  ── writes ──►  script + shot list + per-shot prompts
                                          │
                    ┌─────────────────────┼───────────────────────┐
                    ▼                     ▼                       ▼
              Imagen 4 / Whisk       Flow / Veo 3.1           Lyria / MusicFX
            (stills + ingredients)  (video + native audio)     (music bed)
                    │                     │                       │
                    └───── ingredients ──►│◄──────────────────────┘
                                          ▼
                                  Google Vids (assemble + captions)
                                          ▼
                              Drive (archive)  →  YouTube / site / ads
```

Read that top to bottom and you've read the whole course. Phases 2–4 are the "write the note" arrows; 5 is the "ingredients" loop; 6 is the sound department; 7 is the brand-brain box on the top-left; 8 is running the whole diagram for real.

## What Veo 3.1 Can Actually Do (2026, measured against the current release)

So you calibrate expectations before spending a coin:

| Capability                   | Reality in mid-2026                                                                  |
| ---------------------------- | ------------------------------------------------------------------------------------ |
| Clip length                  | ~**8 seconds** per generation; **Scene Extension** chains them past **60 s**         |
| Native audio                 | **Yes** — dialogue, SFX, ambience, and music, generated _in sync_ with the picture   |
| Lip-sync                     | **Yes, automatic** when you write quoted dialogue — the mouth matches the words      |
| Character/object consistency | **Ingredients to Video** — up to **3 reference images** (character, product, style)  |
| Start/end control            | **Frames to Video** — give a first frame (and optional last frame) to steer the shot |
| Resolution / format          | Up to **4K** upscaling; native **9:16 vertical** for Shorts/Reels and **16:9**       |
| Editing / continuity         | **Scenebuilder** ("Jump To"): extend, re-time, and stitch shots on a timeline        |

**The honest summary:** for 8-second, single-idea shots — a product beauty shot, a spokesperson line, a UI-in-a-lifestyle-scene — Veo 3.1 is genuinely broadcast-adjacent. Long, multi-character, plot-heavy films are still a _stitching_ job you do in Scenebuilder + Vids, one good 8-second shot at a time. Plan in **shots**, not scenes. Anyone promising you a finished 2-minute ad from one prompt is selling something.

## The Phases

| Phase | File                                                                                     | Level        |
| ----- | ---------------------------------------------------------------------------------------- | ------------ |
| 1     | [[01-phase-1-the-big-picture]] — the mental model, the stack hand-offs, the credit math  | Easy         |
| 2     | [[02-phase-2-prompting-basics]] — the 7-part note, templates, the word-count rule        | Easy         |
| 3     | [[03-phase-3-context-and-script-planning]] — Gemini: idea → script → shot list → prompts | Easy → Mid   |
| 4     | [[04-phase-4-camera-control]] — shots, angles, movement, lens — talking to the camera    | Intermediate |
| 5     | [[05-phase-5-character-consistency]] — Ingredients, reference sheets, keeping one face   | Intermediate |
| 6     | [[06-phase-6-voice-lipsync-audio]] — voices, dialogue, lip-sync, SFX, music              | Intermediate |
| 7     | [[07-phase-7-custom-rag-brand-brain]] — NotebookLM + a Gemini Gem = your brand's memory  | Advanced     |
| 8     | [[08-phase-8-pro-workflow-and-playbooks]] — the full pipeline + per-content-type recipes | Capstone     |
| —     | [[09-reference]] — prompt library, camera cheat-sheet, credit table, glossary, sources   | Reference    |

Start with [[01-phase-1-the-big-picture]].

---

> **A note on honesty (the vault rule).** Flow, Veo, and the credit prices move _fast_ — Veo went 3 → 3.1 → 3.1 Lite in the first quarter of 2026 alone. Every capability above was web-verified on 2026-07-15, but **credit costs and exact tier names are the first things Google re-tunes.** Where a number matters to your budget, confirm it live in Flow before you rely on it. Sources are listed in [[09-reference]] §Sources.
