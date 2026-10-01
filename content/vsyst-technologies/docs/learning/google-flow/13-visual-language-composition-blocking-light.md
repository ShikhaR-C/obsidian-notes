# Visual Language — Composition, Blocking, Light and the Colour Script

> Level: Beginner → Intermediate | Hat: Director | Time: ~2.5 hr | Secures: **perceptual continuity, by design, before generation** | Outcome: you plan every 9:16 frame so the pictures belong together — frame, blocking, light, colour, and where the eye lands at each cut — and you know the words that make Nano Banana and Veo draw it | Status: written & web-verified **2026-10-01** against Google's Veo and Nano Banana prompt guides, Flow Help and the sources in §14.

---

## Explain-it-like-I'm-5

The robot crew ([[00_README]]) has no art director, and no lighting crew that remembers. For each clip a fresh crew walks into an empty room and decides where the lamp goes, where the actor stands and what colour the night is. Ten clips, ten rooms.

So you hand every crew one **map**: where each person stands and why, which wall the light comes through, what colour each scene is, where the eye should be when the picture changes. Draw it once, on paper and in stills, and every crew paints from it. That map is **visual language**.

## 1. The one idea — plan the pictures to belong together

The eye decides "this is one film" before the brain does: light from the same side, one colour world, people where they stood, the eye landing where it expects at every cut. That is **perceptual continuity**, one of the track's four (causal, perceptual, emotional, sonic), and a director secures it before generating — here, **in the board stills**. Every generated Saaf Hisaab shot is a board still animated with Frames→Video, so frame, blocking, light and colour are decided in a cheap still; Veo only adds motion.

One habit runs through the file: **fix things to the map, not to the screen.** The window is on the east wall; the sun sets behind the pump. Every frame is a view of one world, so no two can disagree.

Neighbours: shot and move names, [[04-phase-4-camera-control|Phase 4]]; the 180°, 30° and screen-direction rules, [[10-deep-dive-scene-continuity]] §5.4; boards, [[14-previs-storyboard-floorplan-animatic]]; shot-by-shot tracking, [[15-continuity-bible-script-supervisor]]; the grade, [[20-colour-finishing-and-delivery]].

The stills come from Flow's image models, **Nano Banana Pro, 2 and 2 Lite** ([[11-directors-track-roadmap]] §8). Only NB 2 Lite is stated free, so this file's word tests use it — check the cost Flow shows before a long session on the others.

## 2. Composition in a 9:16 frame

**Composition** is where things sit in the frame, and so where the eye goes first. A 9:16 frame is 1,080 px wide and 1,920 tall: no room sideways, plenty top to bottom. So you **stack** the story: context on top, the person and the action in the middle, nothing that matters at the bottom.

Platform buttons and text cover parts of the frame; keep text and logos inside **x 65–888, y 288–1,248** ([[20-colour-finishing-and-delivery]] §9 owns the measurements). For a director that box is a map — here with S1-02, the bookend, stacked into it:

```
 y       x: 0         360        720    888  1080
    0  ┌──────────────────────────────────┬─────┐
       │ TOP STRIP (platform bar)         │     │
  288  ├──────────────────────────────────┤     │
       │ dark wall,        ┌──────────┐   │ BUT-│
       │ bare shelf        │ window,  │   │ TONS│
       │ ● lamp            │ canopy   │   │     │
       │                   └──────────┘   │     │
  640  │═══ EYE LINE: Ravi's head ════════│     │
       │ hunched over 3 open red          │     │
       │ registers, the full chai glass   │     │
 1070  │┄┄┄ caption band ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄│     │
 1248  ├──────────────────────────────────┤     │
       │ DEAD ZONE (platform UI):         │     │
       │ the desk's front edge, soft      │     │
 1920  └──────────────────────────────────┴─────┘
```

| Rule | What it is | Saaf Hisaab |
| ---- | ---------- | ----------- |
| **Eye line** | the eyes sit on the upper-third line, y ≈ 640 | every **single** (a shot of one person), from S1-04 on |
| **Headroom** — the gap above the head | too much and the person sinks; in a CU crop the forehead, never the chin | S2-07: mouth above y ≈ 1,000, the caption under the chin |
| **Looking room** — space on the side a person looks toward | nudge the face ≈ 100 px off centre, away from its look | Ravi looks right: face at x ≈ 440; Kishan looks left: x ≈ 640 |
| **Thirds vs centre** | thirds for a person looking somewhere; centre for an object that *is* the world | the register inserts S1-01, S1-05, S2-04, dead centre |
| **Balance, negative space** — empty area that belongs to the picture | imbalance is tension; emptiness is absence | S2-08: big Ravi low-left, small Kishan high-right, then an empty doorway |
| **Frame within a frame** | a doorway or window boxing the subject — already vertical | Kishan in the doorway (S2-02); the tanker through the window (S4-04) |
| **Leading lines** | lines that carry the eye | the column leads to the circled figure (S1-05); the tanker's stripe runs diagonally into the bay (S3-01) |

Three 9:16 habits:

- **Leave the bottom third empty.** Below y 1,248 is platform UI: the desk edge or the floor goes there, never the chai glass or a hand.
- **Keep the right edge free.** Past x 888 are the buttons, so Kishan's face — always frame-right — stays near x 640.
- **Plan for the watermark.** Flow puts a visible watermark on every output for people living in India (Flow Help; [[11-directors-track-roadmap]] §8). Compose with it in the frame. Nothing here crops, blurs or covers it: a reframe is for composition, never a way round the mark.

## 3. Depth — three layers, not one

**Depth** is the sense that a frame has a near, a middle and a far. Left alone, the models drift toward the stock-photo frame — one evenly lit subject against an equally bright backdrop, what Bruce Block calls **flat space**. It looks cheap and makes cuts look like collage. Build three **layers** into every board:

| Layer | How it reads | S2-08, as Kishan leaves |
| ----- | ------------ | ----------------------- |
| Foreground | close to the lens, soft, at an edge: it puts the viewer in the room | the desk edge and the cold chai glass |
| Subject | sharpest, brightest skin, warm | Ravi at the desk, left of centre, big |
| Background | smaller, softer, darker or cooler | the lit doorway, upper right; Kishan small, walking out |

Write the cues: **overlap** (the near thing hides part of the far one), **size**, **focus** (shallow depth of field is already in the Look Sentence), **tone** (a background darker than the face) and **colour** (warm comes forward, cool recedes, as Block notes). The night office gets depth free: warm face, cool window. §9 turns depth into a story progression across the four scenes.

## 4. Blocking — where people stand is what they mean

**Blocking** is where the actors stand and move relative to each other, the set and the camera; **staging** is arranging it so the arrangement tells the story (Katz's *Film Directing Shot by Shot* is the classic text). In Flow, positions you don't fix get reinvented in every clip.

Four dials do the telling: **distance** (Edward T. Hall's **proxemics**, the study of personal space, has zones: personal 0.46–1.2 m, social 1.2–3.7 m, public beyond), **level** (sitting or standing), **nearness to the lens** (whoever the film belongs to keeps the foreground) and **what stands between them** (a desk, a threshold, folded arms, glass — or nothing). Two maps fix every position (R = Ravi, K = Kishan):

```
LOC-A · the pump office from above

                     back wall, shelf
       ┌───────────────────────────────────────┐
       │                                       ║ window
 white │   ● lamp ┌──────────┐                 ║ (east)
 wall  │          │ R   desk │·······axis······K▯ door → forecourt
       │          └──────────┘                 │
       │   ROOM SIDE: every camera stays here  │
       │   [1]      [7]         [5]       [2]  │
       └───────────────────────────────────────┘
 [1] high, in the corner ........ S1-02, S4-06 (the bookend)
 [7] eye level, near the desk ... S2-08: R near the lens, K small in the doorway
 [2] near the door, facing R .... S1-04, S1-06, S2-03, S2-07, S4-02, S4-05 (S2-01: 2′, 30°+ round)
 [5] near the desk, facing door . S2-02, S2-05 (S2-06: 6 inside the door; S4-04: 8 inside the window)
 Inserts: 3 looks down at the desk; 4 sits at desk level. Numbers and set-up codes: file 14 §3.
```

```
LOC-B · the forecourt at dusk from above, camera side at the bottom

  ✸ low sun, setting behind the cabin: a rim on both men, never a face light
  ┌───────────── office cabin: background of every wide ─────────────┐
  ═════════════════════ canopy, cool white lights ═════════════════════
          ◄═════ tanker lane: rolls in right to left (S3-01) ═════
       ▣ pump
       R··················axis··················K     S3-02/03: ≈ 3–4 m
       R K                                           S3-11: ≈ 1 m
  ──────────────────────────── CAMERA SIDE ───────────────────────────
  [1] wides ...... S3-01, S3-11 (in S3-01 Ravi waits, small, frame-left)
  [2] facing R ... S3-03, S3-05, S3-10
  [5] facing K ... S3-02, S3-06, S3-09
```

Across scenes 2 → 3 → 4, the blocking tells the story without a word:

|              | Scene 2 | Scene 3 opens | Scene 3 closes (S3-11) | Scene 4 |
| ------------ | ------- | ------------- | ---------------------- | ------- |
| Distance     | ≈ 3 m, social | ≈ 3–4 m, social to public | ≈ 1 m, personal | a forecourt's width |
| Between them | the desk; the threshold Kishan never crosses | open air, folded arms, the phone | nothing — side by side, watching the nozzle | glass: they see each other |
| Level        | Ravi sits, Kishan stands — the standing man can leave, and does | both standing | both standing, same height | Ravi leans back; Kishan high in the cab |
| Reads as     | a hearing with no evidence | a stand-off | partners | trust that needs no closeness |

Three working rules:

1. **Level sets the eyeline.** Seated Ravi looks camera-right *and slightly up*; standing Kishan looks camera-left *and slightly down*. Write the height into the prompt's [AXIS] block (§11), not just the side.
2. **Move only with a motive on screen.** Kishan comes to the door because his tanker waits, and leaves because the register can't answer. Ravi's arc is in his posture: hunched → arms folded → leaning back.
3. **In 9:16, show distance in depth, not width.** A 1,080 px frame can't hold two people 3 m apart side by side without shrinking them. So scene 2 is built from singles, S2-08 stages the distance near–far (Ravi near the lens, Kishan shrinking into the doorway), and the one side-by-side two-shot, S3-11, comes when they stand an arm's length apart. Long things go diagonal: the tanker in S3-01 rolls into the bay at an angle, into the depth.

Test blocking for ⏣6: an 8 s Omni Flash 1.1 draft at 360p, prompted "single continuous shot, no scene cuts" (Omni cuts between shots unless told not to). Judge positions and timing only — never the look, which a draft on another model can't predict.

## 5. Lens, height and the four push-ins

### 5.1 Lens and height are attitude

A face can fill the frame from near with a wide lens (≈ 24 mm, an arm's length away) or from far with a long one (≈ 85–135 mm, the classic portrait range). Perspective comes from **camera distance**, not the lens: near and wide enlarges the features and keeps the room, so the viewer is inside the person's space; far and long flattens the face against a soft background, so the viewer watches from outside.

**The film's constant is 35 mm at eye level.** By convention 50 mm is "normal" and 35 mm or shorter is wide-angle, so 35 mm is a mild wide: close enough to stand in the room with Ravi, wide enough to keep his trap, the office, in every close-up. Eye level makes the camera his equal, so there is no low angle: Phase 4's "solution = low-angle push-in" suits an ad whose hero is the product; here the app is a tool ([[12-story-engine-seamless-storytelling]]).

Two angles break the constant on purpose. The **top-down inserts** (S1-01, S1-05, S2-04) are the register's own view: the record. The **high angle** of S1-02 is Phase 4's "problem" angle, a man buried in paper; at S4-06 the rhyme (§8) **earns** it again, and it reads as the book closing. The Look Sentence still ends "eye-level" and is never edited: on these five shots the camera sentence comes first, states the angle, and the board carries it ([[15-continuity-bible-script-supervisor]] §5).

Put the lens in the **board** prompt ("35 mm lens"; Google's image guide uses "85mm portrait lens"): Veo's guides name only "wide-angle lens" and "macro lens", and treat "shot on 35mm" as a film *style* — as the Look Sentence's phrase reads.

### 5.2 The four push-ins — the camera moves when Ravi's mind moves

A camera move needs a motive: it **follows** something, **reveals** something, or mirrors a change of **thought**. This film never follows (tripod) and reveals only by cutting, so its four moves are thought moves, slow push-ins on Ravi as his thinking turns:

| Shot (s) | The thought | Why here | Settles |
| -------- | ----------- | -------- | ------- |
| S1-04 (8–12), MCU | he chooses to ignore the phone | the first time the film leans in | before his hand moves (static S1-05 next) |
| S2-07 (35–38), CU | "my own record can't answer" | the peak; the only move in scene 2, after six static shots | holds; cut on Kishan's movement |
| S3-05 (53–56), MCU | suspicion turns to belief as he reads | the turn of the film | as he looks up — the look motivates the cut |
| S4-05 (81–84), MCU | gratitude: he salutes | rhymes with S1-04 — then he ignored a call, now he answers a horn | before the glass lowers (static S4-06 next) |

**Slow** means about one shot size over the 8 s clip, so the 3–4 s you use move half a size: felt, not seen (course heuristic; check on Lite). **Settle 1 s before** a cut to a static shot ([[10-deep-dive-scene-continuity]] §6.5 rule 4); **never two moves in a row**; **pin the end** with a tighter board from the same camera position as the end frame (Frames→Video, **+ Add end frame**).

## 6. Light as story

### 6.1 The working words

| Term | What it is |
| ---- | ---------- |
| **Key** / **fill** | the main light, which makes the shadows / a weaker light that lifts them |
| **Direction** | front = flat, nothing hidden; side = shape, drama; back = an outline, the **rim** |
| **Hard / soft** | a small source (bulb, sun) gives crisp shadows; a large one (window, bounce) wraps softly |
| **Contrast ratio** | key ÷ fill: 2:1 is one stop (a stop = double the light; gentle), 4:1 two (shaped), 8:1 three — **low-key**, the drama and noir end |
| **Colour temperature** | light's colour in kelvin, and *lower is warmer*: sunset ≈ 1,850 K, household bulb ≈ 2,400 K, studio tungsten 3,200 K, overcast daylight ≈ 6,500 K |
| **Practical** / **motivated** | a light you can see in the shot / light that seems to come from a believable source |

Stops, ratios and kelvins are for reading a board and setting the grade, not prompt words (§12): in a prompt, name the source, its side and what falls into shadow (§11).

In the Look Sentences, "soft low-contrast film look" is the **stock**, the same in every scene; the **ratio** belongs to the scene, so an 8:1 night stays moody with milky, not crushed, blacks.

### 6.2 The three Look Sentences, read as a lighting plan

| Look | Key | Fill | Practicals | What the light means |
| ---- | --- | ---- | ---------- | -------------------- |
| Night office (scenes 1–2) | warm lamp on the desk, frame-left, hard | cool night through the window, frame-right | lamp, canopy in the window, phone, headlights behind Kishan | a small pool of warmth in a big cold dark: alone with paper |
| Dusk forecourt (scene 3) | last amber sun, low behind the pump — a rim on both men | cool white canopy overhead | canopy, the phone's glow | one light on both men, as equals; the phone's glow lights Ravi's face (S3-04 → S3-05) |
| Morning office (scene 4) | soft warm daylight through the window, frame-right | pale bounce off the white wall, frame-left | the lamp is **off** | the window that was cold is now the warm side |

**Time of day is story.** Night is work without end; dusk, when day and night swap, is where suspicion turns to trust; morning is the clean start. Light is also the audience's clock: each new story day arrives in a new light ([[15-continuity-bible-script-supervisor]] §10 adds the other cues).

### 6.3 Fix the source on the map, and the direction holds

Place light in the world ("the window is on the east wall"), not per shot ("light from the left"), and every shot inherits its direction from the §4 maps:

- **LOC-A.** The window is camera-right in Ravi's coverage, straight ahead in shots toward the door, **never camera-left**; the lamp sits at the desk's frame-left end. The window faces east, so the morning sun enters there too.
- **LOC-B.** The cameras face west, so the setting sun sits behind the cabin and pump in every shot: a rim behind both men, never a sun on a face.

Check every board before animating it — night warm left, cool right (except the top-down inserts, where the lamp lands frame-right: file 14 §3); dusk bright behind; morning bright on the window side — and regenerate a wrong one. The grade can't fix it: free Resolve's power windows nudge brightness but move no shadow, and Relight is Studio-only (Blackmagic's 21.1 Studio list, §14).

## 7. The colour script

A **colour script** is a strip of small pictures, one per scene or beat, mapping colour, light and mood across a film so its emotional arc shows at a glance. Pixar art director Ralph Eggleston brought the practice to the studio, painting the first in pastel for *Toy Story* (per Amid Amidi, author of a book of Pixar's colour scripts). The grade follows it later.

| Scene | Dominant | Accent | Contrast · temperature | Should feel |
| ----- | -------- | ------ | ---------------------- | ----------- |
| 1 · The 9 PM Register (D1) | amber lamp pool on red registers, in blue-black dark | teal phone case | ≈ 8:1 · warm left, cool right | late, alone, boxed in |
| 2 · The Dispute (D1) | the same, plus white headlights; bluer as Ravi turns to the door | teal phone at his ear | highest at S2-07 · the split at its widest | pressure → defeat |
| 3 · The Verified Order (D2, dusk) | amber sky behind the pump, white canopy, deepening blue | teal phone, its glow on his thumb | ≈ 4:1 · warm behind, cool in front → all blue by S3-11 | wary → trust |
| 4 · Morning Chai (D3, 7 AM) | cream, wood, pale walls, the navy polo | small teal phone → teal logo (S4-07) | ≈ 2:1 · warm, from the window | air, relief, the books closed |

**The arc in one line:** warmth starts trapped in a lamp and ends filling the room. The wardrobe walks it too: faded pale blue (D1) → cream (D2) → navy polo (D3).

**One accent, one meaning.** Teal is the record you can trust. It lives only on the phone — S1-03, S1-06, S2-01, S2-03, S2-07, S3-03, S3-04, S3-07, S4-03 — and finally the logo. Nothing else is teal: off-white walls, Kishan's khaki, the tanker's stripe a deeper, darker blue (regenerate any board that turns it teal). **Red** is the dispute: registers sprawling in scene 1's foreground end closed and small on the shelf in scene 4.

**Build it in ten minutes.** Put each shot's current board in one folder, named by its ID, and run (tested on ffmpeg 7.1; write `'*.jpg'` if your boards are JPEGs):

```
ffmpeg -reinit_filter 0 -pattern_type glob -i '*.png' \
  -vf "scale=135:240,tile=8x4" -frames:v 1 colour_script.png
ffmpeg -i colour_script.png -vf "gblur=sigma=12" colour_script_squint.png
```

The first lays all 31 boards on one 8 × 4 sheet in story order (the IDs sort that way; `-reinit_filter 0` accepts mixed sizes). The second blurs it — the **squint test**: you should still see four families and one teal dot moving through them. Two scenes in one blurred patch mean a flat arc; regenerate a board from "another film" now, while it's free.

## 8. Rhymes — two frames, one form

A **visual motif** is an image that returns and gathers meaning ([[12-story-engine-seamless-storytelling]] owns plant and pay-off). A **rhyme** is the mechanism: two shots with the same *form* — size, angle, lens, camera position, composition — and different *content*. The audience feels the link without noticing it.

| Pair | Same form | What changes | What it says |
| ---- | --------- | ------------ | ------------ |
| **S1-02 / S4-06** | WS, high angle, camera 1 | night → morning; lamp off; registers open on the desk → stacked on the shelf; hunched → leaning back, chai in hand | same man, same room, a different life |
| **S1-03 / S4-03** | insert CU, the phone on the same spot of the desk | a harsh buzz creeping toward the glass → one soft chime, one glance | the device that brought trouble now brings none |
| **S1-05 / S2-04** | top-down ECU, same register, same column centred | finds a wrong figure → finds nothing | the search is failing, so S2-04 must be *more*: faster, more pages |

Smaller rhymes: S1-04 / S4-05 (the push-ins), S2-06 / S4-04 (the tanker framed by door, then window), S2-08 / S3-11 (apart, then together).

**Make one in Flow.** Hover the locked first board → **More → Add to Prompt**, and add `CHAR_ravi_D3.png` the same way. NB 2 Lite is weak with several references, so use Nano Banana Pro or 2 and check the cost Flow shows. Prompt only the change:

```
Same camera position, framing, lens and composition as the office image.
Change only: it is 7 AM; soft warm morning daylight comes through the
window at frame-right; the desk lamp is off; the three red registers are
closed and stacked on the shelf on the back wall; the desk is tidy; the man,
now in the navy polo from the character image, leans back in his chair
holding a steaming steel chai glass. Keep everything else exactly the same,
preserving the original composition.
```

The last sentence is adapted from Google's own wording for an edit that keeps its composition. Then ghost-overlay the pair (§10): desk edge, shelf and window frame should coincide. Off by more than a register's width, it reads as "a similar shot", not "the same place" — regenerate.

## 9. Contrast and affinity — visual intensity follows the story

Bruce Block (*The Visual Story*, 3rd edition, 2021) breaks every picture into seven **basic visual components** — space, line, shape, tone, colour, movement, rhythm — under one principle: the more **contrast** (difference) in a component, the more visual intensity; the more **affinity** (similarity), the less. His method: draw the **story structure graph** — conflict intensity 0–100 through exposition, conflict, climax and resolution — then one graph per component beneath it, giving each a job: a **constant**, a **progression**, or **contrast and affinity** that spikes where the story spikes. The climax gets the most contrast; affinity drains the resolution.

Saaf Hisaab's story graph follows the emotional curve of [[12-story-engine-seamless-storytelling]] §6 on Block's 0–100 scale — the same peak, S2-07, and the same release, from S3-11 into scene 4; [[16-directing-performance-and-dialogue-scenes]] §5 scores it shot by shot:

```
            Block's 0–100 scale, one ▇ = 5
S1-01–02    ▇▇▇                     15   exposition
S1-03–06    ▇▇▇▇▇▇                  30
S2-01–03    ▇▇▇▇▇▇▇▇▇▇▇             55
S2-04–06    ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇         75
S2-07       ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇  100   the peak, 35–38 s
S2-08       ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇        80
S3-01–03    ▇▇▇▇▇▇▇▇▇▇              50
S3-04–07    ▇▇▇▇▇▇▇▇▇▇▇▇▇▇          70   the turn
S3-08–10    ▇▇▇▇▇▇▇▇▇               45
S3-11       ▇▇▇▇▇                   25   release
S4-01–07    ▇▇                      10   resolution
```

| Component | Job | Plan |
| --------- | --- | ---- |
| Movement | constant, four spikes | static, except the four push-ins; height and lens never change |
| Space | progression, one spike | close office → deep forecourt (canopy, bay, road, sky) → office with a bright window; the biggest size jump is S2-06 → S2-07, a small tanker in the doorway → the tightest face |
| Tone | progression | dark, ≈ 8:1 → ≈ 4:1 → bright, ≈ 2:1 |
| Colour | progression, one spike | the warm/cool split widest at S2-07; one warm family in scene 4 |

**At the peak, four components contrast at once.** S2-07 has space (wide → the tightest CU), tone (half the face in shadow, the page brightest), colour (warm lamp side against blue window side) and movement (scene 2's only move) — while the point of interest stays near the eye line, so the jolt is size, not search. **The resolution is affinity everywhere:** scene 4 keeps sizes close, one warm family, low contrast, one gentle move. A hard shadow, a cold patch or a big size jump on a scene 4 board fights the ending. Rhythm is the editor's component ([[18-editing-2-rhythm-structure-and-rescue]]).

## 10. Eye-trace across the cut

Walter Murch counts **eye-trace** — the location and movement of the audience's focus of interest within the frame — fourth of his six criteria for a cut, at 7 % ([[10-deep-dive-scene-continuity]] §5.6). In 9:16 it bites: a cut that drops the eye in the wrong place makes the viewer search, and a 2–3 s shot can't afford it. The eye lands on a face, then the brightest area, then movement — a working order, not a law.

**The ghost overlay** lays the last used frame of A over the first used frame of B, with the thirds grid and the safe box on top (tested on ffmpeg 7.1):

```
ffmpeg -i S2-04_board_v2.png -i S2-05_board_v1.png -filter_complex \
 "[0]scale=1080:1920,format=rgb24[a];[1]scale=1080:1920,format=rgb24[b];\
[a][b]blend=all_mode=average,drawgrid=w=iw/3:h=ih/3:t=2:c=white@0.6,\
drawbox=x=65:y=288:w=823:h=960:c=red@0.8:t=4" J_S2-04_S2-05_ghost.png
```

On boards it costs nothing; on clips, pull the frames at your cut points first ([[15-continuity-bible-script-supervisor]] §8). **Rule of thumb** (a course heuristic, not a published number): for an invisible cut, keep the jump between the two points of interest under a third of the frame height, **≈ 640 px**. Break it once per film, on purpose — the size jump into S2-07 (§9).

| Cut | Eye leaves A at (x, y) | B's subject at | Travel | Design note |
| --- | ---------------------- | -------------- | ------ | ----------- |
| **S2-01 → S2-02**, on a look | Ravi's eyes ≈ (450, 620), turning right | Kishan's face ≈ (640, 620) | ≈ 190 px, the way he looked | put B's subject where A's look points; keep the headlights low and soft so Kishan's face is the brightest thing |
| **S2-04 → S2-05**, insert to face | the finger stops ≈ (540, 900) | Kishan's eyes ≈ (620, 640) | ≈ 270 px | frame the column to run y ≈ 350–900; a finger ending at y ≈ 1,450 sits under the platform UI *and* forces an 800 px climb |
| **S3-11 → S4-01**, 12-frame dissolve | the two heads, y ≈ 700, centred | the steam over the glass ≈ (540, 650–900) | ≈ 0 | both pictures share the screen for half a second; in one zone, one picture becomes another — the men dissolve into the steam |

## 11. The word lists

Every shot has a **board** prompt (Nano Banana: composition, light, colour) and a **Veo** prompt (Frames→Video: motion, sound, the frozen blocks). "Google" marks wording from Google's own guides; the rest is course wording — test it free on NB 2 Lite. Google's principle: *describe the scene, don't just list keywords*.

| Tool | Board prompt | Veo prompt | Does nothing alone → write instead |
| ---- | ------------ | ---------- | ---------------------------------- |
| Placement | Google: "A 9:16 vertical poster"; course: "his eyes on the upper third of the frame", "at frame-right" | course: "keeps his eyes on the upper third" | "rule of thirds", "well composed" → name the place |
| Depth | Google: "shallow depth of field (f/1.8)", "soft, blurred background (bokeh)"; course: "in the foreground, out of focus, …" | Google: "shallow focus", "deep focus" | "3D", "immersive" → name the three layers |
| Lens, height | Google: "85mm portrait lens", "low angle shot"; course: "35 mm lens", "at eye level" | Google: "eye-level", "top-down shot", "wide-angle lens", "macro lens" | a focal length in the Veo prompt alone → put it in the board |
| Light | Google: "Golden hour backlighting creating long shadows" | Google: "warm sunlight, long shadows", "harsh fluorescent overhead lights", "spotlight in one area" | "cinematic lighting", "dramatic lighting", "4:1", "3200K" → the source, its side, what falls into shadow |
| Colour | Google: "Cinematic color grading with muted teal tones" | Google: "cool blue tones", "warm tones", "night" | "vibrant"; "no teal" → describe the absence as a presence, as Google advises: "plain off-white walls" |
| Blocking | course: "stands in the doorway and does not enter", "side by side, an arm's length apart" | course: "looks camera-right and slightly up" | "they interact naturally"; "facing each other" in a vertical two-shot |

The S1-02 board words, to slot into file 14 §4.4's board prompt:

```
A photorealistic high-angle wide shot, 9:16 vertical, 35 mm lens, shallow
depth of field. Top of the frame: the dark back wall; at frame-right, the
window with the pump's white canopy lights. His head is level with the upper
third, hunched over three open red registers beside a full steel chai glass.
The bottom of the frame is only the dark front edge of the desk. A single
warm desk lamp at frame-left lights the pages and his face from the side;
cool blue night from the window at frame-right; the corners fall into shadow.
```

The camera, scene and axis sentences of S2-07's Veo prompt (Frames→Video from its two boards, locked on Quality), word for word from [[16-directing-performance-and-dialogue-scenes]] §8, which owns the prompt; as pasted: one block per line, plain sentences, no tags. [[15-continuity-bible-script-supervisor]] §5 owns the skeleton and what an image-led prompt keeps.

```
Start exactly from the provided first frame and end on the provided last frame. Close-up, eye level, a very slow push-in that settles by the sixth second, 35 mm lens.
The pump office at 9 PM; the desk lamp at frame-left.
Camera on the room side; the door and the window are camera-right. Face just left of centre; phone in his right hand; his eyes go from the doorway, off-frame right and slightly up, down to the register.
```

## 12. What still can't be done

- **Placement words are requests, not coordinates.** Neither model promises a pixel. The board is the firm control; Frames→Video pins the start (and the end, with an end frame), never the middle.
- **Lens numbers are style hints.** Veo's guides document no focal lengths; whether "35 mm" changes Veo's perspective is untested.
- **Light can flip between generations, and no grade moves a shadow.** Check direction on every board and every Lite draft.
- **Ratios and kelvins are not prompt words.** Google's guides use neither; translate them into sources and shadows, and set exact contrast and colour in the grade.
- **A colour script survives generation only roughly.** The grade pulls shots back into the family; it can't turn night into morning.
- **Omni 360p drafts test blocking and timing, never the look.**
- **The watermark is in every frame** for creators in India; no composition here relies on hiding it.
- **Eye-trace is only 7 %.** Emotion comes first (Murch): never wreck a performance to save 200 px.

## 13. Exercises

**13.1 — Map the three relationships (0 coins).** Draw scenes 2, 3 and 4 from above: both men, the distance in metres, what stands between them, who is nearer the lens. *Artefact:* three maps with a one-line reading each.

**13.2 — Named light against an adjective (0 coins).** The same night-office prompt twice on NB 2 Lite: once ending "dramatic cinematic lighting", once with the light sentences of the §11 board words. Which puts warm on the left and cool on the right? *Artefact:* two stills and a verdict.

**13.3 — Colour script and squint (0 coins).** One NB 2 Lite board per scene, then the §7 commands. Four families, one teal dot? *Artefact:* the sheet and its squint.

**13.4 — The bookend rhyme (0 video coins; check the Nano Banana Pro cost Flow shows).** Make S4-06 from S1-02 with the §8 edit, then ghost-overlay the pair. *Artefact:* two boards and a ghost with the desk edges aligned.

**13.5 — Eye-trace three cuts (0 coins).** Ghost the boards for S2-01 → S2-02, S2-04 → S2-05 and S3-11 → S4-01; mark each point of interest, measure the travel, note anything in the dead zone or under the buttons, and fix the worst board. *Artefact:* three ghosts and a three-row table.

**13.6 — Graph your own film (0 coins).** For a 30-second DZZLO ad, draw Block's story graph and, beneath it, space, tone, colour and movement, each marked constant, progression or contrast. Fix one place where a component fights the story. *Artefact:* the graphs.

**13.7 — Block S2-08 on Omni (~⏣12).** Two 8 s Omni Flash 1.1 drafts at 360p (⏣6 each), "single continuous shot, no scene cuts": (a) Ravi near the lens, Kishan deep in the doorway; (b) both side by side across the frame. Watch muted: which says "left alone"? *Artefact:* two drafts and the verdict.

**13.8 — Push or hold (~⏣20).** S1-04 from its board on Veo 3.1 Lite twice (⏣10 each): static, then a slow push-in that settles by 7 s. Cut each between the S1-03 and S1-05 boards. *Artefact:* two clips and a note on which one makes you lean in.

## 14. Sources (web-verified 2026-10-01)

Primary — Google:

- [Ultimate prompting guide for Veo 3.1 — Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)
- [Veo prompt guide — Google DeepMind](https://deepmind.google/models/veo/prompt-guide/)
- [Generate videos with Veo — Gemini API](https://ai.google.dev/gemini-api/docs/veo)
- [7 tips to get the most out of Nano Banana Pro — The Keyword, 2025-11-20](https://blog.google/products-and-platforms/products/gemini/prompting-tips-nano-banana-pro/)
- [How to prompt Gemini 2.5 Flash Image Generation — Google Developers Blog, 2025-08-28](https://developers.googleblog.com/how-to-prompt-gemini-2-5-flash-image-generation-for-the-best-results/)
- [Image generation — Gemini API](https://ai.google.dev/gemini-api/docs/image-generation)
- Flow Help: [Images](https://support.google.com/flow/answer/16729550) · [Create videos](https://support.google.com/flow/answer/16353334) · [Credits](https://support.google.com/flow/answer/16526234) · [Get started / FAQ](https://support.google.com/flow/answer/16353333)

Tools:

- [DaVinci Resolve 21.1 Studio features](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_Studio_21_Features.pdf)
- [FFmpeg filters documentation](https://ffmpeg.org/ffmpeg-filters.html); every command here was run on ffmpeg 7.1

Craft:

- [Bruce Block, *The Visual Story*, 3rd ed. — Routledge](https://www.routledge.com/The-Visual-Story-Creating-the-Visual-Structure-of-Film-TV-and-Digital-Media/Block/p/book/9781138014152) and its [Chapter 9 sample](https://www.routledge.com/rsc/downloads/Chapter_9_from_The_Visual_Story_3e_9781315794839.pdf)
- [Film Book Notes on *The Visual Story*](https://filmbooknotes.blogspot.com/2013/05/the-visual-story-by-bruce-block.html)
- [Amid Amidi on Pixar's colour scripts — Animated Views](https://animatedviews.com/2011/the-art-of-pixar-the-complete-color-scripts-and-select-art-from-25-years-of-animation-an-interview-with-author-amid-amidi/)
- [Murch's Rule of Six — PremiumBeat](https://www.premiumbeat.com/blog/when-and-where-to-make-the-cut-inspired-by-walter-murchs-in-the-blink-of-an-eye/)
- [Practical lighting — StudioBinder](https://www.studiobinder.com/blog/what-is-practical-lighting-in-film/)
- Wikipedia: [Proxemics](https://en.wikipedia.org/wiki/Proxemics) · [Perspective distortion](https://en.wikipedia.org/wiki/Perspective_distortion) · [Normal lens](https://en.wikipedia.org/wiki/Normal_lens) · [Wide-angle lens](https://en.wikipedia.org/wiki/Wide-angle_lens) · [Headroom](https://en.wikipedia.org/wiki/Headroom_%28photographic_framing%29) · [Lead room](https://en.wikipedia.org/wiki/Lead_room) · [Rule of thirds](https://en.wikipedia.org/wiki/Rule_of_thirds) · [Composition](https://en.wikipedia.org/wiki/Composition_%28visual_arts%29) · [Lighting ratio](https://en.wikipedia.org/wiki/Lighting_ratio) · [Low-key lighting](https://en.wikipedia.org/wiki/Low-key_lighting) · [Soft light](https://en.wikipedia.org/wiki/Soft_light) · [Color temperature](https://en.wikipedia.org/wiki/Color_temperature)
- Further reading: [Katz, *Film Directing Shot by Shot*](https://mwp.com/product/film-directing-shot-shot-25th-anniversary-edition-visualizing-concept-screen/)

---

**Previous:** [[12-story-engine-seamless-storytelling]] · **Next:** [[14-previs-storyboard-floorplan-animatic]] · **Track map:** [[11-directors-track-roadmap]] · **Back to:** [[00_README]]
