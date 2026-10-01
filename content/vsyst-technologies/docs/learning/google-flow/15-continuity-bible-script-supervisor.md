# The Continuity Bible — Doing the Script Supervisor's Job for a Crew With Amnesia

> Level: Intermediate | Hat: Continuity | Time: ~2 hr | Secures: perceptual continuity, shot by shot | Outcome: a continuity bible and 32-shot state table, prompts built from frozen blocks within a word budget, a take log, a frame-pair check at every cut, and the judgement to fix, cover or leave each error | Status: written & web-verified **2026-10-01** against Flow Help, Google's Veo 3.1 guides, the Resolve 21 manual and ffmpeg 7.1 (commands test-run today). Sources in §13.

---

## Explain-it-like-I'm-5

On a real film set, one person sits beside the camera with a notebook and never looks away: which hand held the cup, how full it was, which way the actor looked, which takes the director liked. A week later, when the crew films the other half of the conversation, the notebook keeps the cup half full and in the left hand. That person is the **script supervisor**.

Your robot crew has no notebook. Every 8-second crew shoots and forgets ([[00_README]] catch #1), so you hold it. It is called the **continuity bible**, and its busiest page is the **state table**: for every shot, where each object is and what condition it is in, at the first and last frame you will use.

## 1. The One Idea: You Are the Script Supervisor

A **script supervisor** (once the "continuity clerk" or "script girl") records everything that must match between shots — action, dialogue, wardrobe, props, set dressing, hair, make-up, axis and eyelines — and tells the editor which takes were good and why. Films are shot out of order; the record lets them cut together.

In Flow every shot is made out of order *by a stranger* who sees one start frame and your words ([[10-deep-dive-scene-continuity]] §1). So you do both halves of the job: **before generating** (bible, state table, prompts — §2–6), as the director, and **after** (take log, frame-pair check, fixes — §7–10), as the editing director.

```
BIBLE → PROMPTS → TAKES → TAKE LOG → FRAME-PAIR CHECK → FIX ──┐
  ▲                                                          │
  └──────────── a fix that changes a state is written back ◄─┘
```

Of the track's four continuities, this file secures the **perceptual** one, shot by shot. Story is [[12-story-engine-seamless-storytelling]], performance [[16-directing-performance-and-dialogue-scenes]], sound [[19-sound-edit-design-and-mix]].

## 2. The Eight Continuities and the Lever That Locks Each

A **continuity** is anything the audience expects to stay the same across a cut unless the story changed it. Most levers start from a **board** — the storyboard still, made with Nano Banana in Flow, that doubles as the shot's start frame ([[14-previs-storyboard-floorplan-animatic]] §4). "Seen?" is the rank on §9's attention ladder (1 = nearly everyone notices).

| Continuity | Breaks as | Seen? | The lever that locks it |
| ---------- | --------- | ----- | ----------------------- |
| **1 Identity** — face, age, hair | Ravi's stubble differs S2-01 → S2-03 | 1 | Board made from the character sheet → Frames→Video; CHARACTER line verbatim. Quality takes no Ingredients, so identity lives *in the still* |
| **2 Wardrobe, hair** | Sleeves down on D1; the watch on his right wrist | 4 (2 on a hand insert) | The STATE line; one sheet per day (`CHAR_ravi_D1.png`); the board |
| **3 Props and their state** | The chai steams on D1; the phone in his left hand | 3 near hands, 5 in a wide | The state table (§4); in-frame props in bible words |
| **4 Light, time, weather** | The key light flips sides; amber returns after blue | felt as "another day" | The light plan ([[13-visual-language-composition-blocking-light]] §6); Look Sentence verbatim; one location master per time; one model (Veo 3.1); the grade ([[20-colour-finishing-and-delivery]]) |
| **5 Space, direction, eyeline** | Ravi looks camera-*left* at the door | felt as confusion | The AXIS block in every prompt; floor plan and boards (file 14) |
| **6 Action match** — hands, head, gaze | The phone rises in his right hand and reaches his ear in his left | 2 | The ACTION block's Out; first- and last-frame boards; the trim ([[17-editing-1-workflow-and-the-cut]]) |
| **7 Performance intensity** | A calm S2-03 between a tense S2-01 and the peak | felt | The board's expression; file 16's intensity ladder |
| **8 Sound** | The buzz becomes a ring; the idle stops mid-scene | heard as "stitched" | Every shot generated quiet (§5); each sound and bed laid in the edit from one source (file 19) |

The rules are in file 10 §5.4; this record keeps them on shot 27 as well as shot 1.

## 3. Identity, State and the Story Day

An **identity line** holds what never changes *in this film*; a **state line** holds what changes with the story day. Ravi's face is identity, his shirt is state. Kishan's uniform and gamchha sit in his *identity* line because he wears them every day of this story — the split is per film, not per person. Keep two lines because you paste identity everywhere and swap state by day; a merged line gets edited scene by scene, and an edited identity line is a new face ([[05-phase-5-character-consistency|Phase 5]] §4). Pros log wardrobe with its state: "coat, buttoned", not "coat".

The steel watch sits in all three of Ravi's state lines because it crosses every day: on a hand insert (S2-04, S4-01) the watch *is* his identity. A mood word in a STATE line ("alert and guarded", "warm approachable smile") is the day's starting condition: the action sentence and the board decide the moment, and casting rejects a take that plays the mood against the action ([[16-directing-performance-and-dialogue-scenes]] §2).

**Flow lever:** one sheet per state — `CHAR_ravi_D1.png`, `_D2`, `_D3`, plus `CHAR_kishan.png`. Google says a Flow **Character** (`@Name`) keeps "face, clothing, and voice" consistent, so one Ravi Character would drag the D1 shirt into D3: if you use Characters, make one per day, all with the same voice.

A **story day** is one day on the story's own calendar; clothes change when it does. Track by day, not by scene:

| Day | Scenes | Look · master still | Ravi | Motif states |
| --- | ------ | ------------------- | ---- | ------------ |
| D1 | 1–2, continuous, 9 PM | night office · `LOC-A_night_master.png` | STATE D1 | chai full, cold; registers open; harsh buzz |
| D2 | 3, dusk | dusk forecourt · `LOC-B_dusk_master.png` | STATE D2 | phone in hand; soft chime; tanker arrives right-to-left |
| D3 | 4, 7 AM | morning office · `LOC-A_morning_master.png` | STATE D3 | chai steaming, in hand; registers shelved; chime; tanker leaves left-to-right |

Scenes 1 and 2 are one day, so nothing may change between them; scenes 1 and 4 share a room but not a day, so the room needs two masters. Days decide clothes and light; scenes decide what happens.

## 4. The State Table — All 32 Shots

**State** is a tracked thing's condition at one moment: where it is, in whose hand, how full, open or shut, lit or dark. The **state table** records it at each shot's **first and last used frames** — either side of every cut — under three laws:

1. A shot's end state is the next shot's start state, unless a time jump separates them.
2. A change nobody sees must be one the audience would believe happened in the cut: the pen may leave his hand between S1-05 and S1-06; the chai may not get drunk.
3. The start state is what the first-frame board shows, the end state what the last-frame board shows.

`→` changes during the shot · `=` as the row above · `—` not in frame · **R1** = the front register he works in (R2 and R3 lie open either side) · **carry-in** = what a scene inherits from the shot before it.

**Scene 1 · D1 · 9 PM · LOC-A night.** Constant: STATE D1; window camera-right, blue night, canopy lights on. Desk map: R1 in front of him; the lamp at the desk's left end (frame-left, as file 14 places it); calculator at his left (frame-right); phone face-down at his right front corner (frame-left), a hand's width from the chai — full, cold, no steam.

| ID | Ravi: hands · eyes | Phone | Glass · registers · pen | Check first |
| -- | ------------------ | ----- | ----------------------- | ----------- |
| S1-01 | right hand writes → lifts the pen | — | R1: a figure written → the ink smudges | no watch on this hand |
| S1-02 | pen hand lifting → rests; eyes on R1 | face-down, still | glass untouched; three registers open | bookend: log the camera position |
| S1-03 | — | buzzing, teal back up → creeps toward the glass | glass full | no screen, so no composite |
| S1-04 | left hand rubs his eyes → glances down-left at the phone → hand drops to R1 | = | = | watch near his face; a desk glance, not across the line |
| S1-05 | left forefinger runs down a column → stops; the pen (right hand) circles the smudge twice | — | R1, the S1-01 page | watch on the finger hand |
| S1-06 | right hand *empty* → lifts the phone to his right ear | desk → right hand, at his ear | pen lying across R1 | right hand, right ear |

**Scene 2 · D1, continuous · LOC-A night.** Carry-in: phone at his right ear; pen across R1; chai full, cold, no steam. From S2-02 on, the tanker idles outside, heard under every shot.

| ID | Ravi: hands · eyes | Phone | Kishan · tanker · sound | Check first |
| -- | ------------------ | ----- | ----------------------- | ----------- |
| S2-01 | phone at his ear → jaw tightens → eyes camera-right, to the door | right ear | caller off-screen | Ravi's lips closed |
| S2-02 | — | — | Kishan in the doorway, frame-right, looking camera-left; headlights behind; idle starts | gamchha on his left shoulder |
| S2-03 | left hand flips R1's pages → lifts the next; eyes down | = | idle | page hand = left |
| S2-04 | left hand: page lands → forefinger down a column → stops | — | — | watch in frame; no smudge |
| S2-05 | — | — | waits, twisting the gamchha's end in his left hand → shifts his weight → glances back over his left shoulder | gamchha stays on the left shoulder |
| S2-06 | — | — | tanker under the canopy, nose to the office, headlights on, cab **empty**; Kishan out of frame | one stripe; no driver |
| S2-07 | lowers the phone; eyes door → R1 | ear → desk, under his right hand | idle | line to the register, not the phone |
| S2-08 | still; eyes on R1 | face-down under his hand | Kishan turns → exits frame-right; door click; idle carries over | chai still full |

**Scene 3 · D2 · dusk · LOC-B.** Constant: STATE D2; LOC-B's axis line, "Ravi is frame-left, looking right; Kishan is frame-right, looking left."

| ID | Ravi: hands · eyes | Phone | Kishan · tanker · light | Check first |
| -- | ------------------ | ----- | ----------------------- | ----------- |
| S3-01 | small, frame-left by the pump, arms folded | right hand | tanker enters frame-right → stops in the bay; cab door opens; amber sky, canopy lights just on | right-to-left |
| S3-02 | — | — | steps down, a hand on the cab door → frame-right, looking camera-left, wary | looks left |
| S3-03 | arms folded; looks camera-right | right hand, on his left forearm → chimes | — | right hand, even folded |
| S3-04 | raises the phone; glow on his thumb | plain white screen, no text, four corners in view | — | composited later (file 20) |
| S3-05 | eyes on the phone → brows lift → up, camera-right, to Kishan | case back to camera | — | Quality hero face |
| S3-06 | — | — | braced → a small chin-lift | same size as S3-05 |
| S3-07 | right thumb taps the screen | glow | — | right thumb |
| S3-08 | — | — | a gloved hand seats the nozzle in the fill port | white paint; plain work glove |
| S3-09 | — | — | braced → half-smile: *"Bas?"* | gamchha left |
| S3-10 | small smile: *"Bas."* | right hand, low | — | still the right hand |
| S3-11 | frame-left, phone at his side | = | Kishan frame-right; tanker filling; amber → blue dusk | light only darkens |

**Scene 4 · D3 · 7 AM · LOC-A morning.** Carry-in: none (a time jump, §10). Constant: STATE D3; window camera-right, daylight, canopy lights off; registers closed and stacked on the shelf; tidy desk, calculator in its D1 spot; phone face-up in its D1 spot; chai at his left hand, so the inserts show the watch.

| ID | Ravi: hands · eyes | Glass · phone | Set · tanker | Check first |
| -- | ------------------ | ------------- | ------------ | ----------- |
| S4-01 | left hand takes the glass → lifts it | full, steaming → rising | — | steam in words; the watch |
| S4-02 | sips → holds it at chest height | glass in left hand | registers on the shelf behind | polo logo identical |
| S4-03 | glances once (off-screen) | phone lights (plain glow); soft chime; it doesn't move | — | no buzz, no creep |
| S4-04 | — | — | tanker enters frame-left → exits right; Kishan's right hand raised from the cab | left-to-right |
| S4-05 | looks camera-right → lifts the glass in salute → starts to lower it; warm smile | glass in left hand | — | hero face; looks right |
| S4-06 | leans back, glass in his left hand | phone face-up in its spot | tidy desk; registers shelved; daylight | S1-02's camera position |
| S4-07 | end card, not generated | — | — | — |

Three cells are not in the shot list, and without them the model decides, differently every take: the D1 phone lies **face-down** (no screen to garble; the teal case is the accent), the **pen leaves his right hand** before S1-06 (or he answers with a pen in his fist), and the **cab in S2-06 is empty** (its driver is at the door). Finding the decisions nobody made is the whole job.

## 5. The Prompt Skeleton and Its Word Budget

The skeleton is Google's Veo formula — [Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance] — plus **AXIS**, because the model can't see the previous shot (file 10 §5.4), and **AUDIO**, because Veo makes sound. Its **frozen blocks** are written once in the bible, and their bodies are pasted unchanged: CHARACTER, STATE, LOOK, the location's AXIS line (LOC-A's is "Camera on the room side; the door and the window are camera-right.") and, in a speaking shot, the VOICE line from [[16-directing-performance-and-dialogue-scenes]] §8. LOC-B's AXIS line has two halves, one per man ("Ravi is frame-left, looking right" · "Kishan is frame-right, looking left"): a two-shot pastes both; a single pastes only the half naming the man in frame, then "The other man stays off-frame." Props are named in the props bible's exact words. Annotated template, not for pasting:

```
[CAMERA]    size · angle · move — one sentence (Phase 4 words)
[SUBJECT]   CHARACTER line verbatim + the STATE line for this story day
[ACTION]    one action, present tense — and how the shot ENDS (the "Out", file 10 §5.7)
[SCENE]     location + time; only the props that are in frame, in bible words
[AXIS]      side of the line · eyeline direction · which hand
[LOOK]      the Look Sentence, verbatim
[AUDIO]     quiet room tone; the line in the colon format, or the one effect to keep; "No music. No subtitles."
```

Paste one block per line, in that order, without the bracket tags: Veo's documented use of square brackets is timecodes (`[00:00-00:04]`).

**Why paste, never retype.** The model reads words, not intentions: "warm tungsten desk lamp" and "warm desk lamp" are different instructions, and each rewording re-rolls the light. Identical blocks also make any two prompts a clean **diff**: when two clips differ, the cause is in the lines that differ. A frozen block is a constant — import it, never edit a copy — so paste its whole **body**, never its bible label: in a prompt, quotation marks are for speech, square brackets for timestamps. A name leads where needed (`Ravi, a friendly…`, `Ravi has a warm…`).

**The word budget.** Google's hard limit is 1,024 tokens; at Gemini's rule of thumb of about 4 characters a token, Prompt A below is roughly 340. Length isn't the limit — attention is, which is why Phase 2 kept prompts near 150 words. In a speaking Ravi D1 shot the frozen bodies take **101 words** (CHARACTER 12, STATE 17, LOOK 40, the location half of AXIS 12, VOICE 20) before the shot says anything; its own camera, action and timing, props, hands and sound add about 140. A full prompt lands near **240 words**, over the habit by design. Past that, cut in this order: (1) props not in frame; (2) description the start frame already shows; (3) adjectives that don't change what a body does; (4) camera words the LOOK already says. Never cut a frozen block, the Out, a hand, an eyeline, a spoken line or the closing "No music. No subtitles." Still long? The shot is doing two things — split it.

**When a frozen block disagrees with the shot.** Every Look Sentence says "eye-level", yet S1-01, S1-05 and S2-04 are top-down and S1-02 and S4-06 high angle. Don't edit the block: put the exception first in CAMERA ("High-angle wide shot, looking down at the desk") and bake the angle into the board, where a fix costs a still, not a render. The Look's "shot on 35 mm" is a film look; the lens goes in the camera sentence ("35 mm lens").

**The image-led prompt.** Every shot here is a board animated with **Frames→Video** ("+ Add start frame", plus "+ Add end frame" for a moving shot). The still carries the face, clothes, set and light; Flow Help's own step is to "describe the action or transition that should happen between the frames". The rule: **the still carries what *is*; the words carry what *happens*, and whatever the still can't show.**

- **CAMERA — keep**, adding "keep the framing of the start frame": a still has no move.
- **SUBJECT — a naming clause only**: "Ravi is the man in the image." Re-describing a visible face can only disagree with it. Full lines stay for anything that enters after frame one (the tanker in S3-01).
- **ACTION and the Out — keep**: only words say what happens.
- **SCENE — a naming clause** ("The pump office at 9 PM."), plus only what moves or changes (S4-01's steam, S1-03's buzzing phone) and, on a moving shot, where the light comes from (file 13 §11 keeps S2-07's lamp at frame-left).
- **AXIS — keep, always**: the still shows frame one's hand and eyeline; your words set every later frame's.
- **LOOK — keep verbatim**: light, grain and lens re-roll as the shot moves (file 10 §3.1). Google's examples drop style words, so test it (exercise 12.4).
- **AUDIO — keep**: a still is silent. Every shot is generated quiet ([[19-sound-edit-design-and-mix]] §3): a dialogue shot asks for its line and room tone; an insert with a kept hit (the pen in S1-01 and S1-05, the nozzle in S3-08) names that one sound; every other shot asks for quiet room tone only. All end "No music. No subtitles."

**Prompt A — S2-03, full skeleton** (241 words): for a Lite or Fast Ingredients draft before the board exists (ingredients `CHAR_ravi_D1.png` and `LOC-A_night_master.png`), and the record the board is drawn from.

```
Medium close-up, eye level, 35 mm lens, static camera.
Ravi, a friendly Indian man, early 30s, short black hair, light stubble. Crumpled pale-blue cotton shirt, sleeves rolled to the elbow, steel watch on his left wrist, tired eyes.
Ravi sits at his desk. For the first two seconds he is still: the phone pressed to his right ear, eyes on the open register, mouth closed. Then he asks two short questions into the phone, his eyes still searching the page. For the final two seconds his mouth stays closed and his left hand begins to turn a page.
The pump office at 9 PM. In frame: a fat red cloth-bound register, open on the desk; a black phone in a teal case.
Camera on the room side; the door and the window are camera-right. His eyes stay down on the register. The phone is in his right hand at his right ear; his left hand turns the pages.
Shot on 35 mm, shallow depth of field, soft low-contrast film look with fine grain; warm tungsten desk lamp as key light, cool blue night through the window as fill; muted palette with one teal accent; eye-level, tripod-steady camera. 9:16.
Quiet night-office room tone. Ravi has a warm, slightly husky male voice, early 30s, an Indian man speaking natural, colloquial Hindi; medium-low pitch, unhurried. Ravi says, low and clipped, holding his temper: "Kaun si gaadi thi? Kaun sa driver?" No music. No subtitles.
```

**Prompt B — S2-03, image-led** (203 words): Veo 3.1 Quality, Frames→Video, start frame `S2-03_board_v1.png`.

```
Medium close-up, eye level, 35 mm lens, static camera; keep the framing of the start frame.
Ravi is the man in the image.
For the first two seconds he is still: the phone pressed to his right ear, eyes on the open register, mouth closed. Then he asks two short questions into the phone, his eyes still searching the page. For the final two seconds his mouth stays closed and his left hand begins to turn a page.
The pump office at 9 PM.
Camera on the room side; the door and the window are camera-right. His eyes stay down on the register. The phone is in his right hand at his right ear; his left hand turns the pages.
Shot on 35 mm, shallow depth of field, soft low-contrast film look with fine grain; warm tungsten desk lamp as key light, cool blue night through the window as fill; muted palette with one teal accent; eye-level, tripod-steady camera. 9:16.
Quiet night-office room tone. Ravi has a warm, slightly husky male voice, early 30s, an Indian man speaking natural, colloquial Hindi; medium-low pitch, unhurried. Ravi says, low and clipped, holding his temper: "Kaun si gaadi thi? Kaun sa driver?" No music. No subtitles.
```

B is 38 words lighter; past its naming clauses, every word left is an instruction the picture can't give.

## 6. The Continuity Header and a Gem That Pastes

The **continuity header** is one scene's frozen blocks plus its carry-in state — to a scene what [[03-phase-3-context-and-script-planning|Phase 3]]'s context header is to a project. Keep all four in one Google Doc, `saaf-hisaab_continuity-bible`, with §2–4:

```
CONTINUITY HEADER — Scene 2 · D1 · 9 PM, continuous · LOC-A night
SUBJECT   CHARACTER — "Ravi": …  STATE D1 …: …  CHARACTER — "Kishan": …
VOICE     VOICE — Ravi: …  VOICE — Kishan: …
LOOK      LOOK — "DZZLO night office": …
AXIS      Camera on the room side; the door and the window are camera-right.
PROPS     the props bible line, verbatim
CARRY-IN  phone at his right ear; pen across R1; chai full, no steam
```

**A Sheet can't paraphrase:** [[21-long-form-multi-scene-production]] §5 assembles every prompt from a `Blocks` tab with `TEXTJOIN` and `VLOOKUP`, so nobody types one.

**A Gem that pastes and drafts.** Create a Gem, attach the bible Doc and the locked shot list ([[11-directors-track-roadmap]] §6 with [[14-previs-storyboard-floorplan-animatic]] §7) under **Knowledge → Add files**, and instruct it:

```
You are the script supervisor for "Saaf Hisaab". Given a shot ID, write its
Flow prompt as plain sentences, one block per line: camera, subject, action,
scene, axis, look, audio; no square brackets, no bible labels. Copy the body
of every frozen line (CHARACTER, STATE, VOICE, LOOK, AXIS) from the attached
bible character for character, name first ("Ravi, a friendly…", "Ravi has a
warm…"); never shorten or reword one; name props only in the props bible's
words. Take the camera, action and Out from the attached shot list. In a
LOC-B single, AXIS takes only the half that names the man in frame, then
"The other man stays off-frame." Audio: quiet room tone, plus the spoken
line, or the one hit to keep (pen in S1-01 and S1-05, nozzle in S3-08),
ending "No music. No subtitles." Take every hand, eyeline and prop state
from the state table.
"Image-led" means: subject becomes "<name> is the man in the image." and
the scene line keeps only place, time and things that move or change.
After the prompt, list any conflict with the state table.
```

Before pasting, paste each frozen body into Find (⌘F) on the answer: a body not found whole means the Gem paraphrased — or let the Sheet's per-block check do it ([[21-long-form-multi-scene-production]] §11). Google says Gems on personal accounts become **skills** in November 2026 (Workspace from March 2027), carried across with their supported files and called with `/` and the name; these instructions work as either ([[11-directors-track-roadmap]] §8). A skill can't take Drive files or notebooks yet (Google: "in the coming weeks"), so until then upload copies of the two documents and re-upload them after every change.

**The bible outlives the film.** Ravi's STATE D3 carries the Phase 5 spokesperson line, so later DZZLO ads start from D3; LOC-A, Kishan and the tanker can recur. Freeze the bible at picture lock as v1.0; start the next film from a copy.

## 7. The Take Log and the Continuity Report

A **take** is one output of one generation; Flow charges for each. Rename every download to its take name (`S2-03_t02_L.mp4` = shot, take, tier) and log it:

| Take | Seed still | Prompt | Used (s) | Matched | Broke | Verdict | ⏣ |
| ---- | ---------- | ------ | -------- | ------- | ----- | ------- | - |
| S2-03_t01_L | S2-03_board_v1 | p1 | 1.0–5.0 | face, ear, eyes | page turned with the **right** hand at 4.2 s | NG: AXIS too weak | 10 |
| S2-03_t02_L | = | p2: "his left hand turns the pages" | 1.0–5.0 | hands, eyes; line at 1.5–4 s | stubble lighter than the board | HOLD | 10 |
| S2-03_t03_F | = | p2 | 1.0–5.0 | as t02; stubble right | — | HOLD: back-up | 20 |
| S2-03_t04_Q | = | p2 | 1.0–5.0 | as t03, sharper | — | **PRINT ◯** | 100 |

On film, when the director called "Print!", the script supervisor, camera assistant and sound recordist **circled** that take number so the lab printed only those — **circle takes**, a name that stuck. **PRINT** is the take the editor gets first; **HOLD** is good but not flawless, kept as cover; **NG** means "no good", always with the reason, because the reason names the block to fix (t01's reason became p2's AXIS line). Count coins per finished shot: S2-03 cost ⏣140, a draft under [[14-previs-storyboard-floorplan-animatic]] §7's plan, because t02 was good enough to move up.

The **continuity report** is the PRINT rows plus one column, **deviations** — every way the printed take differs from the state table ("t04: phone lower at 5.0 s than S2-04 expects"). The editor cuts from it (file 17).

## 8. The Frame-Pair Check at Every Cut

A **frame pair** is the last used frame of shot A beside the first used frame of shot B — the two pictures either side of a join. The film has 30 joins between generated shots. Check them on the **Lite drafts**: same model as the locks, a free check, and a fault found now costs ⏣10 to fix, not ⏣100. Repeat on the locks.

**Times.** The last used frame is one frame before A's out-point: at 24 fps, 5.0 s becomes **4.958 s**. Resolve timecode converts as seconds + frames ÷ 24, so `00:00:04:23` is 4.958 s.

**One frame** (run it in Terminal, after `brew install ffmpeg` if you don't have it):

```
ffmpeg -ss 4.958 -i S2-03_t02_L.mp4 -frames:v 1 A_out.png
```

**Both frames, side by side**, scaled to one height because the stacking filter needs equal heights — so a 720p draft can sit beside a 1080p lock:

```
ffmpeg -ss 4.958 -i S2-03_t02_L.mp4 -ss 0.5 -i S2-04_t01_L.mp4 -filter_complex "[0:v]scale=-2:960[a];[1:v]scale=-2:960[b];[a][b]hstack=inputs=2" -frames:v 1 PAIR_S2-03_S2-04.png
```

Tested today on 24 fps clips: frame-accurate.

**The checklist**, in the order the eye looks (§9):

```
1 Face      same man, age, stubble, hair
2 Eyes      the side AXIS says; same height
3 Hands     same hand on the same object; the action continues
4 Near      phone (hand, ear, case) · glass (level, steam) · pen
5 Wardrobe  shirt, sleeves, watch LEFT wrist, gamchha LEFT shoulder
6 Sides     who is frame-left / right; direction of travel
7 Light     key side, warmth, window brightness
8 Set       window right, shelf, three registers, canopy lights
9 Sound     play the cut: room tone, buzz, the idle
→ PASS · FIX (which block?) · LEAVE (why? §9)
```

**Worked: S2-03 → S2-04**, a cut on the page flip. A ends on his left hand lifting a page, phone at his right ear; B opens on a left hand and the page landing, so item 3 passes. Item 5 fails on S2-04_t01: no watch. On a hand insert the watch is the only proof the hand is Ravi's, so FIX: add "steel watch on his left wrist, in frame" to S2-04's AXIS line and redraft (⏣10).

**In Resolve (free).** On the Edit page, start rolling a cut: the viewer shows a **two-up display** of the outgoing and incoming frames — the pair, live. For light, on the Color page right-click the viewer on A → **Grab Still**, then on B select the still in the Gallery and click **Image Wipe**. Allow a minute a cut: half an hour for the film.

## 9. What Audiences Notice — and the Fix Ladder

**Change blindness** — failing to notice a change across a cut — is normal. Levin and Simons (1997) put nine deliberate errors into a conversation scene, such as a scarf or plate changing colour. On a first viewing nobody reported anything odd; told to hunt on a second, viewers found about two of nine, mostly those nearest the faces. When the *actor* was swapped across a cut, about two-thirds missed it. Eye-tracking shows why: viewers watch faces and sudden movement and almost ignore the edges of the frame (Smith, 2012). Even viewers told to spot cuts missed a quarter of the cuts inside a scene — a third when the cut fell on a sudden movement (Smith and Henderson, 2008), the evidence behind cutting on action.

| Rank | What | In this film | Rule |
| ---- | ---- | ------------ | ---- |
| 1 | Faces and eyes | Ravi across S2-01 → S2-03 → S2-07 | Always fix |
| 2 | Hands at the cut | the phone hand S1-06 → S2-01; the glass hand S4-01 → S4-02 | Fix on every cut on action |
| 3 | Objects near face and hands | the phone at his ear; the chai's level and steam; the pen | Fix when it sits on a cut |
| 4 | Wardrobe | sleeves, watch wrist, gamchha shoulder, polo logo | Fix at MS or closer |
| 5 | Background | which register lies where in S1-02; the shelf; which cab door Kishan uses in S3-01 | Usually leave |

Two warnings. The research covers changes *hidden by a cut*; an AI fault *on screen* — a face drifting mid-shot, a hand growing a finger — is motion on the thing the eye is watching, so it ranks 1 whatever its size. And **emotion first**: Murch's Rule of Six weights emotion at 51 % and 3-D space at 4 % (file 10 §5.6). If S2-07's best performance ends with the phone lower than S2-08 expects, keep it: every eye goes to Kishan turning to leave.

**The fix ladder** — climb only as high as the fault needs:

| Rung | You do | ⏣ | Won't fix |
| ---- | ------ | - | --------- |
| 1 Trim or re-order | Move the in- or out-point clear of the fault | 0 | A fault in the middle of the used part |
| 2 Cover | Cut to an insert or reaction you have (S2-05 covers a bad second of S2-03) | 0, or ⏣20 for a new Fast insert | A face the story must show |
| 3 Fix the still | Drag the board into Flow's prompt box: "Move the steel watch to his left wrist. Change nothing else." Redraft on Lite, re-lock | still free on Nano Banana 2 Lite (weak at multi-step edits; else check Flow's cost), then ⏣10 + ⏣20 or ⏣100 | A fault in the motion |
| 4 Regenerate | Same board, corrected AXIS or ACTION words | ⏣10, then ⏣20 or ⏣100 | — |
| Rescue | Omni Flash **Edit & refine**: up to 10 s of the locked take, one change | ⏣40 | Voices; and it adds a second model, so frame-pair it against both neighbours |

A horizontal flip ([[18-editing-2-rhythm-structure-and-rescue]] §10) puts the watch on his right wrist and the phone in his left hand, and mirrors the polo logo and Flow's visible mark, so the flip is closed on every marked clip. A punch-in is for composition, never a way round the visible watermark every clip carries.

## 10. Deliberate Discontinuity — Announcing a Time Jump

A **time jump** is a discontinuity you want read as story. Give each **at least two independent cues** so nobody mistakes it for an error — and a continuous scene **none**.

| Join | Transition | Light | Wardrobe | Place, props | Sound | Cues |
| ---- | ---------- | ----- | -------- | ------------ | ----- | ---- |
| S1-06 → S2-01, inside D1 | cut on action | same | same | same | same room | **0** |
| S2-08 → S3-01, D1 → D2 | hard cut on the door click | night → dusk | pale blue → cream | office → forecourt; the registers left behind | the idle bridges | **3**: light, shirt, place |
| S3-11 → S4-01, D2 → D3 | 12-frame dissolve (file 10 §6.3) | dusk → morning | cream → navy polo | forecourt → office; cold chai → steaming; registers open → shelved | buzz → chime | **5**: the dissolve, light, shirt, place, sound |

The idle across S2-08 → S3-01 is a *link*, not a time cue: it says "same tanker" while the light and shirt say "next day". The reverse trap is a **false time cue**: steam on S2-08's chai would read as "a fresh cup, time has passed" in a real-time scene. Hence "no steam" in the D1 constants.

## 11. What Still Can't Be Done

- **Flow can't read your state table**; the bible works only through what you paste.
- **A start frame plus reference images in one Veo generation is probably impossible** — Flow offers separate modes (unverified; check live). Identity must be in the board.
- **Hands and small objects still change mid-shot**, even from perfect inputs. Harvest around it and log where.
- **Text drifts.** Google claims readable text for Omni, not Veo: watch the polo logo, and keep phone screens a plain glow for the composite.
- **Veo re-rolls voices per clip** — see files 16 and 19.
- **Nobody publishes how often Veo honours "left hand".** After twenty takes, your log is that data.

## 12. Exercises

**12.1 — Write the bible (0 coins).** The §6 Doc: identity, state and voice lines, story-day tracker, desk map, props, Look Sentences, axis lines, four headers. Artefact: the Doc.

**12.2 — Find the decisions nobody made (0 coins).** From the shot list alone: where is the pen at S1-06's first frame? What proves S2-04's hand is Ravi's? Who is in S2-06's cab? Is there steam in S2-08? Compare with §4. Artefact: answers, misses marked.

**12.3 — Cut three prompts to image-led (0 coins).** Write full prompts for S1-06, S3-01 and S4-01, then cut each by §5's rules. S1-06 must keep his empty right hand, S3-01 the tanker's full words (it enters after frame one), S4-01 the steam. Artefact: six prompts with word counts.

**12.4 — Test the keep-the-LOOK rule (~⏣20).** Two Lite Frames→Video drafts of S1-04, with and without the LOOK line; frame-pair each against the S1-03 and S1-05 boards. Artefact: four PAIR images and a one-line verdict.

**12.5 — Draft, log, circle (~⏣30).** Three Lite takes of S2-03 from Prompt B; log them with honest NG reasons; circle one. Artefact: three take-log rows.

**12.6 — Frame-pair three cuts (0 coins with existing drafts; ~⏣60 for six Lite drafts).** S1-06 → S2-01, S2-03 → S2-04, S3-03 → S3-04. Artefact: three PAIR images with checklists.

**12.7 — The attention test (0 coins).** Two edits of the S2-03 board on Nano Banana 2 Lite: (a) the watch on his right wrist; (b) one register gone. Show two colleagues the original, then an edit, 3 seconds each; ask what changed. Artefact: a note — does it match §9's ladder?

**12.8 — Time-jump audit (0 coins).** Play the animatic (file 14) muted to someone new; after each scene ask "same day, or a new day?" Artefact: §10's table from their answers; any missed jump gets one more cue.

## 13. Sources (web-verified 2026-10-01)

Google (primary):

- Flow Help — [Create videos](https://support.google.com/flow/answer/16353334) (Frames) · [Edit videos & build scenes](https://support.google.com/flow/answer/16935718) (Omni Edit & refine) · [Models & supported features](https://support.google.com/flow/answer/16352836) · [Credits](https://support.google.com/flow/answer/16526234) · [Images](https://support.google.com/flow/answer/16729550) · [Characters](https://support.google.com/flow/answer/16935308)
- Gemini API — [Veo](https://ai.google.dev/gemini-api/docs/veo) (1,024 tokens, 24 fps) · [Tokens](https://ai.google.dev/gemini-api/docs/tokens)
- [Google Cloud — Ultimate prompting guide for Veo 3.1](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1) (formula; frames workflow; audio labels)
- Gemini Apps Help — [Use Gems](https://support.google.com/gemini/answer/15146780?hl=en&co=GENIE.Platform%3DDesktop) · [Gems to skills](https://support.google.com/gemini/answer/18560919?hl=en)

Tools:

- [FFmpeg filters — hstack](https://ffmpeg.org/ffmpeg-filters.html#hstack); commands test-run with ffmpeg 7.1, 2026-10-01 · [Homebrew ffmpeg](https://formulae.brew.sh/formula/ffmpeg)
- [DaVinci Resolve 21 Reference Manual](https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_21_Reference_Manual.pdf) — ch. 51 (two-up display), ch. 127 (Grab Still, Image Wipe)

Craft and research:

- Wikipedia — [Script supervisor](https://en.wikipedia.org/wiki/Script_supervisor) · [Dailies](https://en.wikipedia.org/wiki/Dailies) (circle takes)
- [NFI — Script supervisor](https://www.nfi.edu/script-supervisor/) (print, hold) · [The four script-supervisor forms](https://scriptsupervisor.com.br/blog/script-supervisor-template/) (wardrobe state) · [EditMentor — abbreviations](https://editmentor.com/blog/decoding-the-language-of-filmmaking-a-guide-to-common-abbreviations/) (NG)
- StudioBinder — [Story days](https://www.studiobinder.com/blog/how-to-mark-story-days/) · [Continuity editing](https://www.studiobinder.com/blog/what-is-continuity-editing-in-film/)
- [Levin & Simons (1997), *Psychonomic Bulletin & Review* 4, 501–506](https://experts.illinois.edu/en/publications/failure-to-detect-changes-to-attended-objects-in-motion-pictures/) · [Levin, Simons, Angelone & Chabris (2002), *British Journal of Psychology* 93](https://www.chabris.com/Levin2002.pdf) (the authors' summary of the actor swap)
- [Smith (2012), "The Attentional Theory of Cinematic Continuity", *Projections* 6(1)](https://ualresearchonline.arts.ac.uk/id/eprint/21187/) · [Smith & Henderson (2008), "Edit Blindness", *Journal of Eye Movement Research* 2(2)](https://bop.unibe.ch/JEMR/article/download/2264/3460)
- Murch's Rule of Six — via [[10-deep-dive-scene-continuity]] §5.6

---

**Previous:** [[14-previs-storyboard-floorplan-animatic]] · **Next:** [[16-directing-performance-and-dialogue-scenes]] · **Track map:** [[11-directors-track-roadmap]] · **Back to:** [[00_README]]
