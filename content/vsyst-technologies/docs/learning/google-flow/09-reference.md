# Reference — Templates, Cheat-Sheets, Credits, Glossary & Sources

> Keep this open in a second pane while you work. Everything scattered across the phases, gathered here for fast copy-paste. Status: web-verified **2026-07-15**; **tool facts re-verified and corrected 2026-10-01** (what moved in 2026: [[11-directors-track-roadmap]] §8).

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

Course habits, not Google's rules: **100–150 words · 3–6 sentences · present tense · one action + one camera move per clip · "No subtitles." on dialogue shots.** Google's own: speech in quotation marks; Veo reads up to 1,024 tokens.

## 2. Prompt Template Library

**Master fill-in:**

```
[CAMERA: move + size + angle + lens] of [SUBJECT: specific look] who
[ACTION: one thing, present tense] in/at [SCENE: place + time]. [STYLE]
with [LIGHTING + MOOD]. [AUDIO: ambience + SFX]; [SPEAKER, voice desc]
says: "[≤20-word line]". No subtitles.
```

**Spokesperson / testimonial:** *(label it as AI; never pass it off as a real customer — [[20-colour-finishing-and-delivery]] §12)*

```
Slow push-in medium shot at eye level of [CHARACTER BIBLE LINE], sitting in
[setting], shallow depth of field. Warm, trustworthy corporate style, soft
even lighting, confident friendly mood. Quiet room tone; a [voice desc]
voice says: "[line]". No subtitles.
```

**Product hero (ad):**

```
Slow orbiting close-up, low angle, on 35mm with soft bokeh, of [PRODUCT]
on [surface], its screen a plain soft glow, in a dark premium studio. High-end
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

**Dashboard / app reveal:** *(never generate the app: composite a real recording into the glow — [[20-colour-finishing-and-delivery]] §8.3)*

```
Static top-down shot, deep focus, of [device] on a clean desk, its screen
a plain bright glow with all four corners visible. Crisp modern style,
bright even lighting. Soft interface chimes as data updates.
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

**Two set-ups in one Veo 3.1 clip:** `[00:00-00:04] Wide shot of … [00:04-00:08] Close-up of …`. **Omni Flash** cuts between shots unless told "single continuous shot, no scene cuts". **New angle on an existing clip:** an Omni Flash edit (⏣40, up to 10 s).

## 4. Voice & Audio Cheat-Sheet

**Dialogue format:** `Speaker (voice desc) says: "line"` + `No subtitles.` (the quotes are Google's rule; "No subtitles." is a course habit). **≤20 words / one breath / ~2–3 words per second.**

**Voice dials:** age · gender · accent · pitch-tone (deep/warm ↔ bright/light) · pace (slow/reassuring ↔ brisk) · emotion (calm/confident/excited/gentle/authoritative).

**Lip-sync:** automatic with quoted dialogue → help it with **one speaker · facing camera · named · medium-or-closer · same face in the still or ingredient.**

**Hindi / Hinglish:** Google says languages other than English "have not been evaluated" for Veo or Omni — hear every line on a Lite draft before you lock it.

**Sound layers (separate sentences):** SFX (one distinct sound) · ambience (background bed) · music (mood/genre) — or a reusable bed from **Google Flow Music** (included with AI Pro), the Gemini app or Vids, laid in the edit; Google lists "commercial use rights" among AI Pro's Flow Music benefits — still read the terms before an ad, and label AI music where a platform asks.

**One voice across clips:** Veo re-rolls the voice every clip — describe it identically, judge by ear. Held voices (Google's claim): an **Omni Flash voice reference** (only with Ingredients) or a **Character** (`@Name`); a narrator: **Vids AI voice-over** (unlimited on AI Pro, Hindi included). Cloning an uploaded voice is not documented. Which route: [[16-directing-performance-and-dialogue-scenes]] §11.

## 5. Credit Budget Table

> ⚠ Costs are Google's to change — **verify live in Flow** (prompt box → **Settings**). Values: Flow Help, AI Pro, read 2026-10-01.

| Model · tier              | ~Credits per output            | Use it for                                                        |
| ------------------------- | ------------------------------ | ----------------------------------------------------------------- |
| Veo 3.1 Lite              | 10                             | Drafts. The only tier that can Extend                             |
| Veo 3.1 Fast              | 20                             | Iterating; the lock for most shots; takes Ingredients             |
| Veo 3.1 Quality           | 100                            | The locked hero shot only. No Ingredients — start from a still    |
| Omni Flash 1.1 (720p)     | 7 / 10 / 12 / 15 (4/6/8/10 s)  | Second unit: an alternative take, the saved-voice route           |
| Omni Flash 1.1 (360p)     | 4 / 5 / 6 / 7                  | Blocking tests — action and timing only, never look               |
| Omni Flash edit           | 40                             | Changing up to 10 s of an existing clip by prompt                 |
| Upscale to 1080p          | 0                              | Every finished shot (4K is Ultra-only)                            |

**Our jar (AI Pro):** about 1,000 coins a month, plus 50 a day; neither rolls over. A day's 50 is five Lite drafts — drafts from the day, Fast and Quality from the month ([[21-long-form-multi-scene-production]] §7). Charged **per output**: four takes cost four times, a failed one nothing. Stills are cheap — Nano Banana 2 Lite is free; check the cost Flow shows for the other image models.

| Content type    | Typical budget (Lite · Fast · Quality renders) | Shots           |
| --------------- | -------------- | --------------- |
| Promo           | ~140 (2 · 1 · 1) | 1 + overlay     |
| Ad              | ~300 (4 · 3 · 2) | 2               |
| Tutorial        | ~260 (2 · 2 · 2) | 2 human + screen-rec |
| Brand film      | ~520 (4 · 4 · 4) | 4–5             |
| Stills          | ~0 on Nano Banana 2 Lite | n/a |

Each video budget is the ceiling — every shot locked at Quality; most can keep their Fast take.

**Prime Directive:** Lite to find out → Fast to tune → **Quality once**. Batch drafts; reuse stills and ingredients; never Quality-render an unproven shot. Omni 360p tests action and timing only — a draft on one model doesn't predict a lock on another.

## 6. Starting-Point Decision

```
SAME face/product/style, Lite/Fast lock? → Ingredients→Video, 8 s  (Phase 5)
SAME face/product, Quality lock?         → Nano Banana still → Frames→Video  (Phase 5 §5)
Have an approved still to animate?       → Frames→Video (start ± end frame)
Brand-new throwaway idea?                → Text→Video
Another angle on the same moment?        → board + Frames→Video · Ingredients on Fast
                                           · timestamped prompt (§3) · Omni edit (⏣40)
Need it longer than 8 s?                 → a cut (default) · still-join · Extend (Lite)
```

Changed in 2026: only Veo 3.1 Lite extends (an extended take is a Lite-quality take), Quality takes no Ingredients, and "Jump To" is in no current Flow Help page. Cut, still-join or Extend: [[10-deep-dive-scene-continuity]] §4.

## 7. Glossary

| Term                | Plain meaning                                                        |
| ------------------- | ------------------------------------------------------------------- |
| **Flow**            | Google's AI filmmaking app (the film set)                           |
| **Veo 3.1**         | Google's video+audio model in Flow (Lite / Fast / Quality) — the course's picture model (the crew) |
| **Gemini Omni Flash 1.1** | Flow's second video model (4–10 s; 360p or 720p) — the second unit: blocking tests, a ⏣40 prompt edit of up to 10 s, saved voices |
| **Nano Banana**     | Flow's image models (Pro, 2, 2 Lite) for every still and board; only 2 Lite is stated free, and it is weakest with several references |
| **Imagen 4**        | Google's legacy image model: not in Flow, shut down on the Gemini API |
| **Whisk**           | Google's image-remix app, closed 2026-04-30; its address redirects to Flow |
| **Ingredients**     | Reference images (character, product, style) a clip reuses — Lite and Fast (8 s) and Omni Flash, **not Quality**; Flow states no maximum (3 is the Veo API's) |
| **Characters**      | Flow's saved cast: `@Name` bundles one or two images with a voice; which models honour it is not fully documented — check live |
| **Frames→Video**    | Give a first (± last) image; the model animates from it — from a Nano Banana still, the only route to a Quality lock with a pinned face |
| **Extend**          | Continue an 8 s Veo clip by describing what happens next; in Flow only Veo 3.1 Lite extends (expect a quality step at the seam from a Fast or Quality base); no Insert / Remove / camera edits after. Flow's credits page lists Extend under all three tiers while its models page says you must use Lite — check the model and cost Flow shows ([[10-deep-dive-scene-continuity]] §2) |
| **Scenebuilder**    | Flow's scene timeline: arrange, reorder, trim heads and tails, preview, download — no transitions or audio. "Jump To" is in no current Flow Help page (§6) |
| **180° rule**       | Keep every camera on one side of the line between your two subjects, so looks and movement stay consistent ([[10-deep-dive-scene-continuity]] §5.4) |
| **30° rule**        | Consecutive shots of one subject differ by ≥ 30° or two shot sizes, or the cut reads as a jump cut |
| **Cut on action**   | Cut *during* a movement so the join hides inside it — the best seam-hider in AI video |
| **J-cut / L-cut**   | Audio leads / lags the picture cut; hides a sound jump at a join (free Resolve; Vids can't split a clip's own sound) |
| **Credits**         | The coins each output costs — on AI Pro about 1,000 a month plus 50 a day, neither rolls over; four takes cost four times, a failed one nothing |
| **SynthID / visible watermark** | Every Flow output carries an invisible SynthID mark; for people living in India a visible watermark is applied automatically. Both stay — never remove or hide them ([[20-colour-finishing-and-delivery]] §2.3, §12) |
| **RAG**             | AI that reads *your* documents before answering (Phase 7)          |
| **Gemini Notebook** (formerly NotebookLM) | Google's tool that turns your docs into a queryable knowledge base; renamed in July 2026, still a standalone product, now also inside the Gemini app |
| **Gem**             | A saved, custom Gemini persona (e.g. the Content Director); on personal accounts Gems become **skills** from November 2026, moved across automatically with their instructions (most built-in Gem tools don't work in skills yet) |
| **PACT**            | Gem-writing frame: Persona · Assignment · Context · Template        |
| **Lyria / MusicFX** | Lyria is Google's music model (3.5 runs Google Flow Music); MusicFX is closed and redirects to Flow Music |
| **Google Flow Music** | Google's music app (Lyria 3.5), included with AI Pro (its Plus plan, on its own credits); Google lists "commercial use rights" for it — read the terms before paid use |
| **Vids**            | Google Vids, a scene-based editor (the editing bench): 9:16, 16:9 or 1:1; splits, transitions, audio tracks across scenes, auto-ducking, captions, unlimited AI voice-over on AI Pro — but no grading, keyframes, speed changes or detaching a clip's own sound |

### 7.1 Director's & Editor's track — terms (files 12–22)

| Term | Plain meaning | Where |
| ---- | ------------- | ----- |
| **Logline** | One sentence: a specific person, what they want, what is in the way, and what changes | 12 §2 |
| **Controlling idea** | The one sentence the whole film argues: the value that changes, and why | 12 §2 |
| **But / therefore test** | Write BUT or THEREFORE between every two beats; an "and then" marks a missing cause | 12 §3 |
| **Beat** | One story moment — one change the audience can see | 12 §3 |
| **Scene turn** | The event that flips a scene's value from + to − or − to +; a scene that does not turn is cut, merged or rewritten | 12 §5 |
| **Set-up / pay-off** | A detail the film makes you notice, and the later moment that gives it meaning | 12 §7 |
| **Bookend** | Opening and closing on the same frame with the opposite charge | 12 §7 |
| **Mood reel** | Beautiful shots with no want behind them — shuffle them and nothing breaks | 12 §1 |
| **Blocking** | Where people stand and move relative to each other, the set and the camera | 13 §4 |
| **Looking room** | Space left on the side a person looks toward | 13 §2 |
| **Contrast ratio** | Key light ÷ fill light: 2:1 gentle, 4:1 shaped, 8:1 low-key | 13 §6 |
| **Practical light** | A light visible in the shot — a lamp, headlights, a phone screen | 13 §6 |
| **Colour script** | One picture per scene mapping colour, light and mood across the film | 13 §7 |
| **Visual rhyme** | Two shots with the same size, angle and composition but different content | 13 §8 |
| **Contrast and affinity** | More difference in a visual component reads as more intensity; more similarity as less (Bruce Block) | 13 §9 |
| **Eye-trace** | Where the viewer's eye is in the frame, and how far it must jump at a cut (Walter Murch) | 13 §10 |
| **Previs** | Planning a film in maps, pictures and timing before generating anything | 14 §1 |
| **Breakdown sheet** | One page per scene listing everything it needs — cast and state, props, light, sounds, risks | 14 §2 |
| **Floor plan** | The location drawn from above with the line, the people, the lights and numbered cameras | 14 §3 |
| **Set-up** | One camera position plus one lighting arrangement; shots that share one are generated together | 14 §3, §8 |
| **Board / key board** | The approved 9:16 still that is a shot's start frame / the first board of a set-up, from which the others are derived | 14 §4 |
| **Animatic** | Boards timed on a timeline with scratch sound, to test runtime, pace and every cut before any video | 14 §6 |
| **Scratch track** | Temporary dialogue and effects recorded only to time the animatic | 14 §6 |
| **Script supervisor** | The person who records everything that must match between shots — in Flow, you | 15 §1 |
| **Continuity bible** | One doc holding identity, state and voice lines, story days, props, Look Sentences and the state table | 15 §6 |
| **State table** | For every shot: where each tracked object is, and its condition, at the first and last used frame | 15 §4 |
| **Identity line / state line** | What never changes in the film / what changes by story day | 15 §3 |
| **Story day** | One day on the story's own calendar (D1, D2, D3); clothes and light change by day, not by scene | 15 §3 |
| **Frozen block** | A bible line whose *body* is pasted unchanged into every prompt (the label stays in the bible) | 15 §5 |
| **Frame pair** | The last used frame of shot A beside the first used frame of shot B, checked at every cut | 15 §8 |
| **Circle take (PRINT / HOLD / NG)** | The take the editor gets first / kept as cover / no good | 15 §7 |
| **Playable direction** | Telling the actor what to *do*, not what to feel; a feeling word gets a stock face | 16 §2 |
| **Shift** | One change of thought inside a shot; one per clip, in the middle | 16 §3 |
| **Intensity ladder** | Every shot scored 1–10 at its first and last used frame, so neighbours meet | 16 §5 |
| **Business** | What the hands do; it gives the model an action and the editor a cut point | 16 §4 |
| **Matched singles** | Two one-person shots built as mirror images so they cut both ways | 16 §8 |
| **Listening shot** | The face of the person not speaking; it carries the line and covers a lip-sync miss | 16 §8 |
| **VOICE line** | A frozen voice description pasted into every line a character speaks | 16 §8 |
| **Dailies** | Raw takes watched as they arrive — once straight through, then with notes | 17 §3 |
| **Selects / string-out** | The chosen take of each shot, marked on its usable window and laid end to end | 17 §5 |
| **Assembly → rough → fine → picture lock** | The four stages of an edit: whole film in order; every cut motivated; every cut frame set; frozen for sound and colour | 17 §5 |
| **Handles** | Unused frames beyond a cut, kept so trims and transitions can move | 17 §4 |
| **Three-point editing** | Set any three of source in / out and timeline in / out; the editor works out the fourth | 17 §6 |
| **Ripple / roll / slip / slide** | The four trims: change a clip's length and shift what follows / move the cut point / change which frames show in a fixed slot / move a clip between its neighbours | 17 §7 |
| **Kuleshov effect** | A shot means what its neighbours make it mean | 17 §9 |
| **Tempo map** | Every shot's length plotted in story order — the film's pace, visible | 18 §2 |
| **Ellipsis** | A cut that leaves out part of an event; the audience fills the gap | 18 §4 |
| **Overlapping action** | Repeating part of an action across a cut so it lasts longer on screen | 18 §4 |
| **Cross-cutting** | Alternating two lines of action that happen at the same time | 18 §6 |
| **Cold open** | Starting mid-story, on a moment strong enough to hook alone | 18 §8 |
| **Pickup** | A shot made after the main shoot to fill a hole the edit found | 18 §12 |
| **Picture lock** | The point after which no shot changes order, length or content | 18 §14 |
| **Room tone** | The recorded "silence" of a room, laid under every gap so the track never goes dead | 19 §4 |
| **Ambience bed** | One continuous sound of a place under a whole scene; it changes off the picture cut, not on it | 19 §5 |
| **Foley** | Body and prop sounds performed to picture | 19 §2, §6 |
| **Spotting** | Deciding, with timecodes, where each music cue starts, changes and stops | 19 §9 |
| **Ducking** | Automatically lowering music or ambience while a line plays | 19 §9 |
| **LUFS / true peak (dBTP)** | Loudness of the whole programme as the ear hears it / the real highest point of the waveform | 19 §10 |
| **Conform** | Pointing the locked timeline at the final files — every shot's locked take, nothing temporary | 20 §2 |
| **Scopes** | Waveform, parade and vectorscope: graphs of brightness and colour that, unlike eyes, do not adapt | 20 §3 |
| **Adjustment clip** | A clip on an upper track whose grade and effects apply to everything beneath it (Resolve's name for an "adjustment layer") | 20 §5–6 |
| **Safe zone (9:16)** | The part of the frame no app interface covers; at 1080 × 1920, x 65–888, y 288–1248 | 20 §9 |
| **Burn-in / sidecar** | Captions printed into the picture / an .srt file that travels beside the video | 20 §8 |
| **SGI** | "Synthetically generated information" — India's legal term for realistic AI audio or video | 20 §12 |
| **Production bible** | One index page listing every document a film runs on, its owner, version and gate | 21 §2 |
| **Day jar / month jar** | Flow's 50 daily credits and AI Pro's 1,000 monthly credits; neither rolls over | 21 §7 |
| **Block key** | A frozen prompt block with a version, such as `LOOK-night@1.0` | 21 §5 |
| **Spike** | A small, time-boxed test of the riskiest shot before anything else is generated | 21 §10 |
| **Gate** | A sign-off point — story, boards, animatic, Lite pass, locks, picture lock, final | 21 §8 |
| **First-pass yield** | The share of shots accepted on their first lock render | 21 §12 |
| **Production sheet** | One row per shot, with the generate, cut and finish columns from every lesson side by side | 22 §3 |
| **Exit test** | The one observable check that lets a stage pass its gate | 22 §2 |
| **Failure clinic** | From what a viewer noticed, a few yes / no checks lead to the continuity that broke, the stage, the file and the price of the fix | 22 §6 |
| **Blank pack** | The templates a new film starts from, each pointing to its filled *Saaf Hisaab* example | 22 §7 |

## 8. Troubleshooting

| Problem                                   | Fix                                                                     |
| ----------------------------------------- | ----------------------------------------------------------------------- |
| Different face every clip                 | **Ingredients** for a Lite / Fast lock, a Nano Banana still → **Frames→Video** for Quality, plus identical character-bible text ([[05-phase-5-character-consistency]]) |
| Unwanted subtitles burned in              | `No subtitles.` (a course habit) + the line in quotation marks after a colon ([[06-phase-6-voice-lipsync-audio]]) |
| Camera is boring / static                 | You forgot to specify movement — always state it ([[04-phase-4-camera-control]]) |
| Clip ignores half my prompt               | Too long / too many actions — cut to 100–150 words, one action          |
| Prompt details contradict → random result | Read it back; delete the fights (bright+moody, etc.)                     |
| Dialogue rushed or cut off                | Line too long — ≤20 words, one breath                                    |
| Blew the monthly budget                   | You Quality-rendered tests or asked for several outputs — draft on Lite with the daily 50, and keep Quality for the hero locks |
| Character drifts over a long clip         | Keep clips short; start from a still with the character in it; hide cuts in the edit |
| Extend "changed" the end of my clip / seam jumps | Every Flow extension is a Veo 3.1 Lite take — expect a quality step after a Fast or Quality base (the last-second / 720p figures are the Gemini API's). End on a hold, delete & re-extend, or cut instead ([[10-deep-dive-scene-continuity]] §2, §4) |
| Clip made from a saved last frame looks soft / different colour | Join on a clean Nano Banana still (last frame of A = first frame of B), same tier & resolution, upscale once ([[10-deep-dive-scene-continuity]] §3.2) |
| Ingredient consistency is weak            | Reference photo is blurry/busy — use sharp, plain-background stills      |
| Ingredient reference blurry / low-res     | Regenerate a clean plain-background still with Nano Banana in Flow (Pro or 2 for several references); sharp refs only |
| Gem writes off-brand / wrong facts        | Add the missing info to the Gemini Notebook brand notebook; re-ground ([[07-phase-7-custom-rag-brand-brain]]) |
| Voice timbre changes between clips        | Veo re-rolls voices: one frozen voice description, takes picked by ear; to hold a voice, test an Omni Flash voice reference or a Character ([[16-directing-performance-and-dialogue-scenes]] §11) |
| Cuts feel jumpy or random                 | Break the 30° rule less, motivate each cut (look / sound / action), cut on action ([[10-deep-dive-scene-continuity]] §5–6) |
| Stitched piece looks like a patchwork (each clip a different look, room, sound) | Freeze one Look Sentence, one still per location (the stills carry the style) + props bible, one camera personality; then hero-clip grade + one music bed, Veo ambience ducked ([[10-deep-dive-scene-continuity]] §7) |
| Transition looks "AI" (dissolve smears the face) | Never dissolve across identity — straight cut on action, or a 6-frame dip ([[10-deep-dive-scene-continuity]] §6.5) |

### 8.1 Director's & Editor's track — problems (files 12–22)

| Problem | Fix | Where |
| ------- | --- | ----- |
| The cut looks beautiful but means nothing | Write the logline; run the shuffle test; cut shots that serve no want | 12 §1–2 |
| Every cut matches, yet the film feels stitched | Write BUT or THEREFORE between every beat; repair each "and then" before generating | 12 §3 |
| The product's arrival feels like an ad break | Plant the question the product answers; the hero makes the decision; show the product late and briefly | 12 §3, §10 |
| Viewers can't follow it without sound | Run the sound-off test on the boards; turn each "told" line into an action | 12 §8 |
| Shots look flat, like stock photos | Build three layers — soft foreground, brightest subject, darker background — and name them in the board prompt | 13 §3 |
| Light jumps sides between shots of one scene | Fix the light sources on the location map; check every board; regenerate, don't grade | 13 §6 |
| A cut feels jumpy though the 180° rule holds | Overlay the two frames; keep the point of interest from jumping across the frame | 13 §10 |
| The bookend reads as "a similar shot", not "the same place" | Make the second board by editing the first; check the edges with an overlay | 13 §8 |
| Boards drift during a long image session | Re-anchor every set-up on the location master and character sheet; one change per edit | 14 §4–5 |
| A vehicle or person travels the wrong way between scenes | Read screen direction off the floor plan before generating | 14 §3 |
| The animatic runs long, or a line doesn't fit its shot | Trim on paper: enter late, leave early; check lines at 2–3 words a second | 14 §6 |
| Coins run out before the hero shots | Generate by set-up, riskiest first; finish the whole Fast pass before any Quality sitting | 14 §8–9, 21 §7 |
| The phone is in the wrong hand, or a prop changes state | Write the hand and the state from the state table; frame-pair on Lite before locking | 15 §4, §8 |
| A long prompt loses details | Cut in order: props not in frame → what the start frame shows → adjectives. Never the frozen blocks, the Out, the hands or the line | 15 §5 |
| A Gem paraphrases the Look Sentence | Search its output for each frozen line's last words, or assemble prompts in a Sheet | 15 §6, 21 §5 |
| Viewers can't tell that time passed | At least two cues per jump — light, wardrobe, prop state, sound | 15 §10 |
| The AI actor over-acts | Replace emotion words with one small physical action plus stillness | 16 §2, §4 |
| The wrong mouth speaks, or faces blend, in a two-person shot | One speaker per generation; two-shots stay silent and short | 16 §8–9 |
| A line is clipped, or lips move at the clip's ends | Keep the line to about 3.5 s of an 8 s clip; mouth closed for the first and last 2 s | 16 §7 |
| One character sounds different between his lines | Frozen VOICE line; cast takes eyes-closed; run the two-line test before choosing the Omni voice route | 16 §11–12 |
| A Hindi word is mispronounced | Non-English speech is "not evaluated" by Google: hear every line on Lite; try one draft respelled | 16 §6 |
| The timeline isn't 24 fps or vertical, and won't change | Set both *before* importing anything; start a new project from a saved preset | 17 §2 |
| A cut on action jumps or stutters | Cut a few frames after the motion starts; test two frames either way; match direction, hand and speed | 17 §8 |
| The locked render doesn't cut like the draft did | A lock is a new generation: replace it on a key frame, then slip or roll | 17 §5, §12 |
| Cuts feel like a metronome | Don't land every cut on the downbeat; cut dialogue to the performance | 18 §3 |
| A hand melts, a face drifts, a prop morphs | Climb the fix ladder — slip, cover with an insert, reframe — and regenerate last | 18 §9, §11 |
| A clip ends a few frames early | Start earlier in the clip; slow it slightly with Optical Flow; hold a static frame briefly | 18 §10–11 |
| A test viewer says "slow" or "confusing" | Treat it as a symptom; find the cause before touching the cut | 18 §13 |
| Every clip sounds like a different room | Disable Veo's audio on non-dialogue clips; one continuous bed plus room tone per place | 19 §3–5 |
| Lines from different clips don't match in level or tone | Normalise, level, then EQ each line against one hero line | 19 §4 |
| Music won't end on the end card | Back-time the last hit to its frame; cut whole bars just before a downbeat | 19 §9 |
| The mix is fine on the Mac and lost on a phone | Music 10–15 dB under dialogue; master near −14 LUFS, peaks ≤ −1 dBTP; check in mono on a phone | 19 §10 |
| Shots in one scene look like different rooms or hours | Balance each to the scene's targets, match skin to the hero shot, then one look over the group | 20 §3–5 |
| Grain won't apply, or a free render is watermarked by Resolve | The ResolveFX Film Grain is Studio-only; use the free route and test-render five seconds | 20 §6 |
| Captions or logo hidden by app buttons | Keep all text inside x 65–888, y 288–1248 at 1080 × 1920 | 20 §9 |
| Unsure whether to label an AI video | Answer every platform's AI question honestly; the law, the policies and the dates are set out side by side | 20 §12 |
| Hero shots made on different days don't match | Make all the Quality locks in one sitting, after a tool check | 21 §3, §6 |
| No record of which prompt or model made a take | Write a small text file beside every downloaded take, and keep a prompt log | 21 §4–5 |
| A "small" Look Sentence fix broke continuity | It is a new block version: find every shot that used the old one and frame-pair each affected cut | 21 §5 |
| A risky shot fails after the money is committed | Test the riskiest shot first, on Lite, before anything else | 21 §10 |
| Something is wrong and you can't tell which fix applies | Start from what the viewer noticed and run that symptom's tree: it names the continuity, the stage, the file and the price | 22 §6 |
| The spare credits meant for room-tone plates are gone by the sound week | Monthly credits don't roll over: check the outtakes on the last generation day and make the plates then | 22 §2, 19 §5 |

## 9. Sources (web-verified 2026-07-15; re-verified 2026-10-01)

Flow Help (Google): [Models & supported features](https://support.google.com/flow/answer/16352836) · [Credits](https://support.google.com/flow/answer/16526234) · [Get started & FAQ](https://support.google.com/flow/answer/16353333) (SynthID, visible watermark; no credits for failed generations) · [Create videos](https://support.google.com/flow/answer/16353334) · [Edit videos & build scenes](https://support.google.com/flow/answer/16935718) · [Projects & characters](https://support.google.com/flow/answer/16935308) · [Flow Music plans](https://support.google.com/flow/answer/17083870)

Models, prompting and Gemini (Google):

- [Veo on the Gemini API](https://ai.google.dev/gemini-api/docs/veo) (API-only Extend figures, 1,024 tokens, languages) · [Gemini Omni on the Gemini API](https://ai.google.dev/gemini-api/docs/omni)
- [Ultimate prompting guide for Veo 3.1 — Google Cloud](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1) · [Veo video prompt guide — Google Cloud](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/video-gen-prompt-guide) (camera and lens words, "arc shot") · [Veo prompt guide — DeepMind](https://deepmind.google/models/veo/prompt-guide/)
- The Keyword: [Veo 3.1 in Flow (2025-10-15)](https://blog.google/innovation-and-ai/products/veo-updates-flow/) · [Lyria 3.5 (2026-07-29)](https://blog.google/innovation-and-ai/models-and-research/google-labs/lyria-3-5/) · [Gemini Notebook, the rename (2026-07-16)](https://blog.google/innovation-and-ai/products/gemini-notebook/notebooklm-gemini-notebook/)
- Closures: [Whisk is moving to Flow](https://workspaceupdates.googleblog.com/2026/03/whisk-is-moving-to-flow-on-april-30-2026.html) · [Imagen on the Gemini API](https://ai.google.dev/gemini-api/docs/imagen) ("now shut down")
- [Gems to skills — Gemini Apps Help](https://support.google.com/gemini/answer/18560919?hl=en) · [Google Vids limits by plan](https://support.google.com/docs/answer/15609411)

Disclosure, ASCI, loudness and delivery: [[20-colour-finishing-and-delivery]] §16.

> **Reminder (vault rule):** credit costs and tier names are the first things Google re-tunes. Where a number touches your budget, confirm it live in Flow (prompt box → **Settings**) before relying on it.

---

**Back to:** [[00_README]] · Start over at [[01-phase-1-the-big-picture]]
