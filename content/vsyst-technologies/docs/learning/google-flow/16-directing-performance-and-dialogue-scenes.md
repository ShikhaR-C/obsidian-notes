# Directing Performance and Dialogue Scenes — One Believable Man, Made by Strangers

> Level: Intermediate → Advanced | Hat: Director | Time: ~2.5 hr | Secures: emotional continuity | Outcome: you direct an AI actor with a verb, a still and a number; time a Hinglish line inside 8 seconds; cover a two-person scene in matched singles; and choose, by one cheap test, how voices hold across clips | Status: written & web-verified **2026-10-01** against Flow Help, the Gemini API Veo and Omni pages and Google's Veo 3.1 prompting guide. Sources in §15.

---

## Explain-it-like-I'm-5

Every clip is shot by a fresh robot crew ([[00_README]] catch #1), and that includes the **actor**. The Ravi in S2-03 has never met the Ravi in S2-07. He hasn't read the script and can't hear you say "again, smaller". He gets two things: a **card** (the prompt) and a **photo of where to start** (the board still).

Write a feeling on the card ("sad") and he pulls the most obvious sad face in his box. Write a job ("lower the phone slowly and keep looking at the page") and he looks like a man thinking. Even his **voice** is new on every card, unless you give the crew a saved voice (§11).

Scene 2 is eight clips by eight strangers. Make the audience believe it was one man having one long, bad evening.

## 1. The One Idea — the Note Is the Prompt and the First Frame

On a set, a director shapes a performance *between* takes: "slower", "not yet", "less". Flow has no between: each generation is a first take by an actor with no memory. **All directing happens before you press Generate**, through five levers:

| Lever | On a set | In Flow |
| ----- | -------- | ------- |
| What he does | the note before the take | `[ACTION]`, in playable verbs (§2) |
| Where the face starts and ends | rehearsal, marks | first- and last-frame boards (§3) |
| How much | "more" or "less" between takes | an intensity score, turned into size words (§5) |
| The voice | one actor all day | a frozen VOICE line, or a saved voice (§11) |
| Which take | the circled take | casting takes against the ladder (§12) |

This file secures **emotional continuity**, the third of the track's four continuities ([[11-directors-track-roadmap]]): one man, one feeling, one curve, across clips made by strangers. You secure it before generating; [[18-editing-2-rhythm-structure-and-rescue]] protects it in the cut. Audio prompt basics stay in [[06-phase-6-voice-lipsync-audio|Phase 6]], cutting dialogue in [[17-editing-1-workflow-and-the-cut]], cleaning and mixing in [[19-sound-edit-design-and-mix]].

## 2. Playable Verbs — Direct the Doing, Never the Feeling

An adjective tells an actor the *result* you want. Judith Weston (*Directing Actors*) calls that **result direction** and calls it inaccurate: nobody can decide to feel, only to do. Her fix is "playing the objective rather than the result". A video model is the extreme case: write "sad" and it plays the label, a stock face; write what a sad man in this room *does* and you get behaviour, which the audience reads as feeling.

A **playable direction** = a verb + its object + one physical detail + how the shot ends. Give each actor one per clip; two only when the second is the shift (§3).

| Shot | Weak (a result) | Playable (a job) |
| ---- | --------------- | ---------------- |
| S1-04 | exhausted | presses thumb and finger into his closed eyes, glances at the buzzing phone, goes back to the column |
| S2-05 | impatient | twists the end of his gamchha, shifts his weight, glances back toward his tanker |
| S2-07 | devastated | lowers the phone and says the line to the register, not to Kishan |
| S3-05 | surprised | his eyebrows lift a little as he reads; he looks up from the phone to Kishan |

Two habits help:

- **An objective per man per scene.** The **objective** is what he wants, as a verb; it lives on the scene card ([[12-story-engine-seamless-storytelling]]), not in the prompt. Scene 2: Ravi wants *to settle the claim from his own record*; Kishan, *to get his tanker filled and go*. Scene 3: Ravi wants *to fill the tanker without being burned again*; Kishan, *to be filled without another argument*. Only its verbs go in the prompt.
- **No frozen line may argue with the performance.** Flow Help says the prompt "should complement, not contradict, your visual inputs". STATE D2's "alert and guarded" is false by S3-10, so the board shows the smile, `[ACTION]` states it, and casting rejects any take that stays guarded.

## 3. One Shift per Clip — and the Two Frames That Hold It

A **shift** is one change of thought: the doubt lands, the smile arrives, the hope goes. An 8-second clip holds **one**; two shifts is a scene pretending to be a shot. Put the shift **in the middle**, so the editor's 2–4 s ([[10-deep-dive-scene-continuity|file 10]] §6.4) has a still face before it and the new state after it:

```
0 s          2 s                          6 s              8 s
├── BEFORE ───┼──────── THE SHIFT ──────────┼──── AFTER ──────┤
 still, mouth    eyes move, a breath,          new state held,
 closed          the line or the gesture       mouth closed
 ▲ first-frame board = IN state                ▲ last-frame board = OUT state
            └────── the editor's 2–4 s "Use" comes from in here ─────┘
```

Both ends are **pictures**: the boards of [[14-previs-storyboard-floorplan-animatic]] §4.

- **The first-frame board is the opening expression.** Veo starts from it. If it shows Ravi calm while the prompt says furious, the clip spends its first second fighting the picture, so describe the board exactly in the first sentence of `[ACTION]`.
- **The last-frame board pins the OUT** where the next cut depends on it (model name → **Video → Frames** → *Add start frame*, *Add end frame*). S2-07 must end eyes on the register, mouth closed.
- **Keep the two boards one shift apart**: same pose and light, one change. Flow invents every frame between them, and a big gap is where faces drift ([[10-deep-dive-scene-continuity|file 10]] §6.3).
- **Change an expression in the still, not the prompt**: *"Same image. Only change: his mouth is closed and his jaw is slightly tighter."* Nano Banana 2 Lite is free, but Google says it is not optimised for multi-turn editing; for a chain of edits use Nano Banana Pro or 2 (check the cost Flow shows).

## 4. Business, Eyelines, Stillness and the Pause

**Business** is what the hands do: an action for the model instead of a mood, and a cut point for the editor ([[10-deep-dive-scene-continuity|file 10]] §5.7). Use one piece per shot, tracked in the state table of [[15-continuity-bible-script-supervisor]] §4. Ravi: the pen and registers; the phone always at his **right** ear or in his **right** hand; the chai glass in his **left** hand, watch showing. Kishan: the end of his gamchha, twisted in his left hand while he waits (scene 2); a hand on the cab door (scene 3); a hand raised from the cab (scene 4). Business never covers the mouth on a line.

**Eyelines** have a direction and a height. Direction comes from the axis: Ravi looks camera-right, Kishan camera-left ([[10-deep-dive-scene-continuity|file 10]] §5.4). Height comes from the blocking. In scene 2 Ravi sits and Kishan stands, so Ravi looks **slightly up** and Kishan **slightly down**; in scene 3 both stand and look **level**. Write both into `[AXIS]`; a target (*"eyes on the doorway, off-frame right"*) keeps the eyes off the lens.

**Stillness** is a direction. Michael Caine's film-acting advice: the closer the camera, the less you do — "less … and less … and less". On a close-up, movement reads as noise; thought shows in the eyes. **The pause** is where the audience watches him think. Practitioners leave silence before and after a generated line so the character doesn't start mid-breath; it becomes the editor's handle (§7).

**Under-play on purpose.** The tells of AI acting: eyebrows climbing on every word, a wide-open mouth, the head bobbing with speech, a gesture on every line, a smile that switches fully on, eyes flicking to the lens. Don't list don'ts ([[02-phase-2-prompting-basics|Phase 2]] §4); describe the small version, as Google's examples do (*"A slight, mysterious smile plays on her lips"*): not "angry" but *"only his jaw tightens; his head stays still"*.

## 5. The Intensity Ladder

Score every shot twice, 1–10, for the pressure of the feeling: at its first used frame (**IN**) and its last (**OUT**). 1 = at rest, 5 = pressed, 8 = cornered, 10 = breaking.

> Inside a scene, shot A's OUT and shot B's IN differ by **one step at most**, unless something on screen causes the jump: a line, a sound, a reveal. A scene change may reset the level.

Saaf Hisaab, every generated shot:

```
SC1 D1 night    S1-01 3→3  S1-02 3→3  S1-03 3→4  S1-04 4→4  S1-05 4→5  S1-06 5→5
SC2 D1 night    S2-01 5→6  S2-02 6→6  S2-03 6→7  S2-04 7→7  S2-05 7→7  S2-06 7→7
                S2-07 8→9  S2-08 9→8     ◄ the peak: tightest shot, quietest line
                ── hard cut, next day: the level resets ──
SC3 D2 dusk     S3-01 5→5  S3-02 5→6  S3-03 6→6  S3-04 6→6  S3-05 6→5  S3-06 6→6
                S3-07 5→4  S3-08 4→4  S3-09 4→3  S3-10 3→2  S3-11 2→2
                ── 12-frame dissolve ──
SC4 D3 morning  S4-01 2→2  S4-02 2→1  S4-03 1→1  S4-04 1→2  S4-05 2→3  S4-06 2→2
                                                       ◄ S4-05: the salute
```

The ladder scores the emotional curve of [[12-story-engine-seamless-storytelling]] §6 shot by shot, on its own scale: the same peak (S2-07) and release (S3-11 into scene 4) as [[13-visual-language-composition-blocking-light]] §9's graph.

**1. The peak is the smallest performance.** S2-07 scores 9 and is played at almost nothing: eyes, a breath, a near-whisper. Score up, size of play down, frame tighter ([[10-deep-dive-scene-continuity|file 10]] §5.3):

| Score | Size | Play | Words for `[ACTION]` |
| ----- | ---- | ---- | -------------------- |
| 1–3 | WS / MS | natural, unhurried | "relaxed", "takes his time" |
| 4–6 | MS / MCU | one small gesture | "a small…", "once" |
| 7–8 | MCU / CU | eyes and breath | "holds still", "only his eyes move" |
| 9–10 | CU | almost nothing | "barely moving his lips", "one slow breath" |

**2. The best take alone can be wrong in the cut.** An S2-03 take where Ravi slaps the register shut and barks the questions scores 9, the liveliest of the day. Cut in, it makes S2-05's waiting Kishan look deaf and S2-07's whispered 9 a step *down*. Print the 6→7 take: Weston tells directors to cast relationships, not performances.

**3. Each man keeps his own level; resets need visible causes.** At S3-05 Ravi softens to 5 while Kishan, who hasn't seen the screen, stays braced at 6. The drop to 5 at S3-01 works because the hard cut, new light and new shirt say *next day*, while the engine sound says *same tanker* ([[15-continuity-bible-script-supervisor]] §10).

## 6. Lines Worth Speaking

Saaf Hisaab has **six** spoken moments in 90 seconds, two of them one word. That is design: every on-camera line is a lip-sync risk and a ⏣100 Quality lock, the story must play with the sound off ([[12-story-engine-seamless-storytelling]]), and fewer lines leave less voice drift to hide (§11).

1. **One breath, one thought.** Phase 6's ≤ 20 words is the ceiling; ours run 1–7.
2. **Spoken, not written:** Hinglish as said at a pump (*sahab*, *gaadi*, *kab tak?*), spelled the way you'd text it.
3. **Subtext over statement.** **Subtext** is what a line means under its words. Kishan never says "you're calling me a cheat"; *"Kab tak?"* carries it.
4. **If a look can carry it, cut the line.** Ravi's apology is the look up from the phone in S3-05. Kishan's anger is a walk-out and a door click. Scene 4's thanks are a raised hand and a lifted glass: the film's warmest exchange has no words.

| Shot | Line | Words · ≈ s at 2–3 words/s | What it really says |
| ---- | ---- | -------------------------- | ------------------- |
| S2-01 | *"Payment ho gaya tha, Ravi ji!"* | 6 · 2.5 | Your books are wrong, not mine. |
| S2-02 | *"Sahab, gaadi khadi hai. Kab tak?"* | 6 · 2.5 | My time costs money too. |
| S2-03 | *"Kaun si gaadi thi? Kaun sa driver?"* | 7 · 3 | I can't prove anything. |
| S2-07 | *"Register mein nahin hai."* | 4 · 1.7 (quiet) | My own system failed us both. |
| S3-09 | *"Bas?"* | 1 · 0.5 | No argument this time? |
| S3-10 | *"Bas."* | 1 · 0.5 | It's settled. I trust you. |

Each line's final window is set by the cue sheet in [[19-sound-edit-design-and-mix]] §12.

**The language caveat.** Google's API pages for Veo and Omni both say English is fully supported and other languages "have not been evaluated": they may work, and results can vary. Hear every Hinglish line on a Lite draft before any lock. If a word comes out wrong, spend one Lite draft respelling it as it sounds, and log what worked.

## 7. Timing a Line Inside 8 Seconds

At 2–3 words a second ([[06-phase-6-voice-lipsync-audio|Phase 6]] §2), even S2-03's seven words take about 3 s. Spend the rest on silence: **mouth closed for the first two seconds and the last two.** The editor trims both ends of a generated clip ([[17-editing-1-workflow-and-the-cut]] explains why), and closed mouths let the line be slid, J-cut or L-cut ([[19-sound-edit-design-and-mix]]) without lips moving over silence. Set **Generation length** to 8 s for every dialogue shot. If drafts keep ending mid-word, give the shot a closed-mouth last board.

Write the timing in plain words. Google documents **timestamp prompting** (`[00:00-00:02] …`) as a way to put *several shots* in one clip, so a one-shot prompt uses time words (a template: fill the ‹ › slots):

```
For the first two seconds he is still and silent, mouth closed, ‹the IN state›.
Then ‹the shift›, and he says, ‹delivery›: "‹line›"
For the final two seconds he holds ‹the OUT state›, mouth closed. No new action.
```

Use Phase 6's colon format (speaker, colon, then the line in quotation marks; quotes are Google's documented rule for speech) and end with `No music. No subtitles.` Music is laid in the mix ([[19-sound-edit-design-and-mix]] §3); "No subtitles" is community advice, not Google's rule, kept as a course habit because it costs nothing.

## 8. Covering a Two-Person Scene — Matched Singles

**Coverage** is the set of shots a scene can be cut from ([[10-deep-dive-scene-continuity|file 10]] §5.5). For two people talking:

| Shot | In Flow | In Saaf Hisaab |
| ---- | ------- | -------------- |
| **Master** (two-shot): both men, wider | safe when silent, risky when talking (§9) | S2-08, S3-11, both silent |
| **Over-the-shoulder**: one face, past the other man's shoulder | two people in one prompt (§9) | not used |
| **Single**: one man, either **clean** (no one else in frame) or **dirty** (a sliver of the other man) | one speaker per generation; clean is safest | every line |
| **Matched singles**: two singles built as mirror images | `[CAMERA]` pasted identically into both | S2-03↔S2-05, S3-02↔S3-03, S3-05↔S3-06, S3-09↔S3-10 |
| **Listening shot**: the face of the man *not* speaking | no lip-sync to fail | S2-05, S3-06 |
| **Insert**: an object, close | cheap; cuts anywhere | S2-04, S3-04, S3-07, S3-08 |

**Why scene 2 is all singles.** Story: a desk and a doorway stand between the men; they share a picture only once, in S2-08, as Kishan leaves. Tool: one speaker per generation reliably puts the right line in the right mouth (§9). Edit: the editor chooses whose face carries each line, often the listener's, since a neutral face takes its meaning from the line laid over it (the Kuleshov effect, [[17-editing-1-workflow-and-the-cut]]).

**What "matched" means.** A **shot-reverse-shot** is a pair of shots of two people from opposite sides, cut back and forth. The cinematographer Neil Oseman's conventions for it: same size, same lens, eyelines at matching heights, looking room in front of each face, faces on opposite sides of the frame. In prompts: `[CAMERA]` identical, `[AXIS]` mirrored, both boards made in one image session. Scene 2 breaks the match twice, on purpose: S2-02 (MS, Kishan still at the door) and S2-07 (CU, the peak). Where a push-in cuts to a static single (S3-05 → S3-06), it must settle at the static shot's exact size; draw that into S3-05's last-frame board.

**The prompts** are Frames→Video on Veo 3.1 from each board, in the track skeleton ([[15-continuity-bible-script-supervisor]] §5 owns its word budget and which blocks a board-led shot may drop). Two frozen **VOICE lines** join the bible to fix *who* each man sounds like; only the per-shot **delivery**, how this line is said, changes:

```
VOICE — Ravi: a warm, slightly husky male voice, early 30s, an Indian man
speaking natural, colloquial Hindi; medium-low pitch, unhurried.

VOICE — Kishan: a dry, gravelly male voice, late 40s, an Indian man
speaking natural, colloquial Hindi; low pitch, clipped.
```

**S2-03** (Ravi, MCU; start frame `S2-03_board_v1.png`; draft on Lite, check on Fast, lock on Quality). Its block bodies are [[15-continuity-bible-script-supervisor]] §5's Prompt B, word for word. Like the two below, it is an annotated template, not for pasting: paste each block's body on its own line, in this order, without its tag:

```
[CAMERA]  Medium close-up, eye level, 35 mm lens, static camera; keep the
          framing of the start frame.
[SUBJECT] Ravi is the man in the image.
[ACTION]  For the first two seconds he is still: the phone pressed to his
          right ear, eyes on the open register, mouth closed. Then he asks two
          short questions into the phone, his eyes still searching the page.
          For the final two seconds his mouth stays closed and his left hand
          begins to turn a page.
[SCENE]   The pump office at 9 PM.
[AXIS]    Camera on the room side; the door and the window are camera-right.
          His eyes stay down on the register. The phone is in his right hand
          at his right ear; his left hand turns the pages.
[LOOK]    Shot on 35 mm, shallow depth of field, soft low-contrast film look
          with fine grain; warm tungsten desk lamp as key light, cool blue
          night through the window as fill; muted palette with one teal
          accent; eye-level, tripod-steady camera. 9:16.
[AUDIO]   Quiet night-office room tone. Ravi has a warm, slightly husky male
          voice, early 30s, an Indian man speaking natural, colloquial Hindi;
          medium-low pitch, unhurried. Ravi says, low and clipped, holding his
          temper: "Kaun si gaadi thi? Kaun sa driver?" No music. No subtitles.
```

In the templates below, each ‹…› slot takes a frozen body verbatim; every body is printed together in [[22-capstone-saaf-hisaab-workbook]] §4.1.

**S2-07**, the peak: start frame `S2-07_board_v1.png`, end frame `S2-07_board_v1_last.png`, framed tighter so the push-in lives in the difference:

```
[CAMERA]  Start exactly from the provided first frame and end on the
          provided last frame. Close-up, eye level, a very slow push-in that
          settles by the sixth second, 35 mm lens.
[SUBJECT] Ravi is the man in the image.
[ACTION]  For the first two seconds he is still, phone at his right ear, eyes
          up toward the doorway, mouth closed. Then his eyes drop to the
          register and he slowly lowers the phone out of frame. He says the
          line to the register, very quietly, barely moving his lips. For the
          final two seconds he stays still, eyes on the page, mouth closed.
[SCENE]   The pump office at 9 PM; the desk lamp at frame-left.
[AXIS]    Camera on the room side; the door and the window are camera-right.
          Face just left of centre; phone in his right hand; his eyes go from
          the doorway, off-frame right and slightly up, down to the register.
[LOOK]    ‹the night-office LOOK body, as in S2-03›
[AUDIO]   Very quiet room tone. ‹Ravi's VOICE body, as in S2-03›. Ravi says,
          almost a whisper, flat, to himself: "Register mein nahin hai."
          No music. No subtitles.
```

**S3-09 and S3-10**, the matched pair: `[CAMERA]` identical, character for character, and `[AXIS]` mirrored, each with only its own man's half of LOC-B's AXIS line ([[15-continuity-bible-script-supervisor]] §5):

```
S3-09 · Kishan · start frame S3-09_board_v1.png
[CAMERA]  Medium close-up, eye level, 35 mm lens, static camera; keep the
          framing of the start frame.
[SUBJECT] Kishan is the man in the image.
[ACTION]  For the first two seconds he is still and braced, eyes on the man
          off-frame left, mouth closed. Then the corner of his mouth lifts in
          a small, unsure half-smile and he asks one word, softly. For the
          final two seconds he holds the half-smile, mouth closed.
[SCENE]   The fuel forecourt at dusk.
[AXIS]    Kishan is frame-right, looking left. The other man stays
          off-frame. He stands just right of centre and looks camera-LEFT,
          level.
[LOOK]    ‹the dusk-forecourt LOOK body, verbatim›
[AUDIO]   Only quiet room tone. ‹Kishan's VOICE body›.
          Kishan says, soft and half-laughing: "Bas?" No music. No subtitles.

S3-10 · Ravi · start frame S3-10_board_v1.png
[CAMERA]  Medium close-up, eye level, 35 mm lens, static camera; keep the
          framing of the start frame.
[SUBJECT] Ravi is the man in the image.
[ACTION]  For the first two seconds he is still, eyes on the man off-frame
          right, mouth closed. Then he gives one small nod and answers with
          one word, warmly. For the final two seconds a small smile stays,
          mouth closed.
[SCENE]   The fuel forecourt at dusk.
[AXIS]    Ravi is frame-left, looking right. The other man stays off-frame.
          He stands just left of centre and looks camera-RIGHT, level; the
          phone lowered in his RIGHT hand.
[LOOK]    ‹the dusk-forecourt LOOK body, verbatim›
[AUDIO]   Only quiet room tone. ‹Ravi's VOICE body›.
          Ravi says, quiet and final: "Bas." No music. No subtitles.
```

Cut the pair both ways: the eyelines should meet and the faces sit at the same height.

## 9. Two People in One Frame

Google says Veo 3.1 handles "multi-person conversations". Practitioners report what happens when it must decide who says what: the line lands in the **wrong mouth**, **both mouths move**, or the faces **blend**. Replicate's Veo 3 guide says the model sometimes "mixes up who says what", and consistency guides name "multi-character identity bleed". For a line that must land, that risk isn't worth ⏣100.

**The single-shot workaround:** one speaker per generation, with the other man off-screen as an eyeline (§4). It is Google's own pattern: in its Veo 3.1 dialogue example, the detective's line and the woman's reply are separate shots made from the same reference images.

**A two-shot is safe when nobody speaks and the bodies are plainly different**, as in S2-08 and S3-11. `[ACTION]` says *"Neither man speaks"*, and `[AUDIO]` reads *"Quiet room tone. No music. No subtitles."*; effects go in the mix ([[19-sound-edit-design-and-mix]] §3). The board comes from both character sheets in one image (Nano Banana Pro's API takes five character references). And each shot runs 2 s, too short for a blend to show.

## 10. The Off-Screen Phone Voice (S2-01)

The caller is never seen, so his line needs no lip-sync. Generating it inside S2-01 risks Ravi's lips moving to the caller's words, in a voice that sounds like it's in the room, not in a phone.

| Route | For | Against |
| ----- | --- | ------- |
| Generate it in S2-01 | one render | wrong-mouth risk; a new stranger each re-roll; room sound, not phone sound |
| **Record it**: a colleague, a phone voice memo | free; a real performance; exact timing | needs a quiet room |
| Vids **Voiceover** (Hindi included; unlimited on AI Pro) | free; steerable with `[` audio tags | narrator presets, not actors; Vids Help limits generated video to Vids and is silent on voice-over, so read the terms |

**Default: record it.** Generate S2-01 with Ravi silent (*"He listens, the phone at his right ear, mouth closed; his jaw tightens once"*) and the audio *"Quiet room tone. No music. No subtitles."* Making the line sound like a phone is the job of [[19-sound-edit-design-and-mix]] §4.4.

## 11. One Voice Across Clips — Two Routes, One Test, One Default

### 11.1 What Flow does today

- **Veo 3.1** builds the voice from your words, fresh every generation. Google says consistent speech "remains an area of active development".
- **Omni Flash 1.1 voice reference.** Model name → **Omni Flash** → **Video → Ingredients** → **Add → Voices**; pick a preset or **Create New Voice** (Base Voice, Name, Voice Performance, optional Sample Dialogue, then Sync and **Save New Voice**). Call it as `@Voice: Ravi`. It works **only with Ingredients** (anything else gives an error) and is single-speaker.
- **Characters** bundle 1–2 images with a saved voice; Flow Help claims face, clothing and voice "remain strictly consistent". Clothing is bundled, so Ravi needs one Character per story day, all sharing one voice. Help documents voices only with Omni, so treat Characters as the Omni route until you see a Veo clip use one.
- **Avatar** (`@me`) is your own face and voice, not a cast member. AI Studio's voice replication isn't available in India.

### 11.2 The two routes

| | **A: Veo 3.1 Frames→Video + VOICE line** | **B: Omni Flash Ingredients + saved voice** |
| - | ---- | ---- |
| Picture | Veo, like the other 26 generated shots | a second model in the five most-watched shots; no source says the looks match |
| Framing, eyeline, expression | pinned by the board | from reference images and words (start frame plus Ingredients: unverified in Flow; the Omni API allows it) |
| Voice | re-invented every clip | one saved voice; "strictly consistent" is Google's claim |
| Hinglish | "not evaluated" | "not evaluated" |
| One 8 s line | ⏣10 Lite · ⏣20 Fast · ⏣100 Quality | ⏣6 at 360p · ⏣12 at 720p |

Omni also cuts between shots unless you write "single continuous shot, no scene cuts", and its edit tool can't change a voice.

### 11.3 The two-line voice test

Ravi's two D1 lines, S2-03 and S2-07, are where a voice change would show most: same night, same shirt, seven seconds apart.

1. **Route A.** Render both shots on Veo 3.1 Lite, Frames→Video from their boards, 8 s, the VOICE line in each: ⏣20, drafts you'd make anyway.
2. **Route B.** **Create New Voice** "Ravi", with the VOICE line as its Voice Performance (check the cost Flow shows). Render both shots on Omni Flash with Ingredients = `CHAR_ravi_D1.png` + `LOC-A_night_master.png`. Use each shot's full no-board prompt (like [[15-continuity-bible-script-supervisor]] §5's Prompt A), with `@Voice: Ravi` in place of the VOICE body and "single continuous shot, no scene cuts" added; 8 s, 720p: ⏣24, the voice test's draw on the ⏣80 spare ([[14-previs-storyboard-floorplan-animatic]] §9).
3. **Score each route's pair from 1 to 5.** *Eyes closed:* one man, or two? *Hinglish:* every word clear? *Lips:* does the mouth match, frame by frame? *Cut, muted:* between its neighbours' boards or drafts in Resolve (S2-02/S2-04, S2-06/S2-08), do the face, light and grain belong?
4. **Too close to call?** Render one more take of each (+⏣44, from daily credits, not the spare).

**Decision rule:** Route B takes the dialogue only if it wins **eyes-closed by 2 or more**, scores **4 or more on cut-muted**, and is no worse on Hinglish and lips. Otherwise, use Route A.

### 11.4 The default

**For Saaf Hisaab, use Route A.** The track budget's five dialogue locks ([[11-directors-track-roadmap]] §7) already assume it:

1. The dialogue singles are faces, which audiences check first ([[15-continuity-bible-script-supervisor]] §9); a second picture model there risks the mismatch people notice most.
2. Matched singles need the board as first frame, and only Route A pins framing, eyeline and expression with a picture.
3. Route A's weakness has cheap covers: the frozen VOICE line, casting takes by ear (§12), the listening shot ([[10-deep-dive-scene-continuity|file 10]] §6.5 rule 6), and the day break between Ravi's D1 lines and his one D2 word.

**Switch to Route B** when the test says so, or when one character carries many lines and the voice *is* the brand: a spokesperson series, or [[08-phase-8-pro-workflow-and-playbooks|Phase 8]] §3.4's "DZZLO teacher". Then make the whole piece in Omni: one film, one model again.

**Last resorts**, cheapest first: give the line to a look (§6); play the best-matching take's audio over the listener; a recorded voice-over, only for lines whose mouth isn't on screen. For a hero spokesperson, the local second unit can lock one synthetic voice and re-sync lips (the vault's ComfyUI course, file 09: Chatterbox TTS, Wav2Lip); untested here, and never with a real person's voice without consent.

## 12. Casting Takes

You can't direct a take, but you can cast one. Draft each dialogue shot on Lite with **Number of outputs** set to 2 (each output is charged: ⏣20), the one deliberate exception to the default of 1 ([[21-long-form-multi-scene-production]] §7): the two outputs are two of the three Lite drafts [[14-previs-storyboard-floorplan-animatic]] §7 plans for a dialogue shot, not extra spend. Then judge every take in this order:

1. **Muted: the face.** Does the shift land in the middle? Eyes off the lens? Any tell from §4? Phone in his right hand, watch on his left wrist?
2. **Eyes closed: the voice.** Right words, natural Hinglish, the VOICE line's man, the same man as in his other lines?
3. **In the cut: the neighbours.** Do IN and OUT sit within one step of the ladder?

A take must pass all three. When two pass, print the one that fits the neighbours, not the one that shines alone ([[10-deep-dive-scene-continuity|file 10]] §7.8); log print, hold or no good in the take log of [[15-continuity-bible-script-supervisor]] §7. Judge the Fast and Quality renders the same way: the voice you keep is the one in *that* clip.

## 13. What Still Can't Be Done

- **No note between takes.** A re-roll is a new actor. Budget takes, not perfection.
- **No locked voice on Veo.** Omni's consistency is Google's claim until your own test confirms it.
- **Hinglish is unevaluated** by Google on both models.
- **Two speakers in one frame** is still unreliable, and cloning an uploaded voice isn't documented.
- **Omni's voice route can't pin your board** as a first frame, as far as Flow Help documents. No Flow tool edits a voice after generation.
- **Lip-sync is least forgiving in a tight close-up**, exactly where the peak line lives; the listener is your cover.
- **The visible watermark** (added automatically for creators in India) is on every performance shot. Compose with it; never hide or crop it.

## 14. Exercises

**14.1 — The verb pass (0 coins).** Rewrite the `[ACTION]` of every shot with a face as verb + object + physical detail + how it ends. Add a "performance" column to your shot list: objective, business, shift, timing.

**14.2 — Score your ladder (0 coins).** Score IN and OUT for every shot of your own film, or re-score Saaf Hisaab. Circle each cut that breaks the one-step rule; name its on-screen cause, or fix it.

**14.3 — Board the shift (0 coins on Nano Banana 2 Lite; check the cost on Pro or 2).** Make S2-07's two boards: phone at his ear, eyes on the doorway; then phone gone, eyes on the register. Mouth closed in both; the last framed tighter.

**14.4 — Matched pair on Lite (~⏣40).** Render S3-09 and S3-10 from their boards, two outputs each: two of each shot's three planned Lite drafts (14 §7). Cut them both ways in Resolve. Do the eyelines meet? Note what broke the match.

**14.5 — The two-line voice test (~⏣44: the spare's ⏣24 draw plus ⏣20 of planned drafts; a second round from daily credits).** Run §11.3. Write each route's four scores and a one-line decision in your production bible.

**14.6 — Break it on purpose (~⏣10).** Make one Lite clip of the "Bas?" / "Bas." exchange as a two-shot, both lines in one prompt. Whose mouth said what? Log it "no good", with the reason.

**14.7 — Record the caller (0 coins).** Record *"Payment ho gaya tha, Ravi ji!"* three ways on your phone: insisting, wounded, angry. Lay each under the S2-01 board in Resolve; keep the one that best explains Ravi's tightening jaw.

## 15. Sources (web-verified 2026-10-01)

Primary (Google):

- [Create videos in Flow — Flow Help](https://support.google.com/flow/answer/16353334)
- [Projects & characters — Flow Help](https://support.google.com/flow/answer/16935308)
- [Models & supported features — Flow Help](https://support.google.com/flow/answer/16352836)
- [Manage your Flow credits — Flow Help](https://support.google.com/flow/answer/16526234)
- [Veo on the Gemini API](https://ai.google.dev/gemini-api/docs/veo)
- [Gemini Omni Flash on the Gemini API](https://ai.google.dev/gemini-api/docs/omni)
- [Ultimate prompting guide for Veo 3.1 — Google Cloud](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)
- [Veo — Google DeepMind](https://deepmind.google/models/veo/)
- [Create voiceovers with AI in Google Vids — Docs Editors Help](https://support.google.com/docs/answer/15070345)
- [AI video clips in Google Vids — Docs Editors Help](https://support.google.com/docs/answer/16143507)

Practitioners (indicative):

- [How to prompt Veo 3 — Replicate, 2025-06-10](https://replicate.com/blog/using-and-prompting-veo-3)
- [Dialogue prompting in Veo 3.1 — Prompt Architects, 2026-08-26](https://prompt-architects.com/blog/101-veo-dialogue-prompts)
- [AI video character consistency guide — PixMind, 2026-07-18](https://www.pixmind.io/posts/ai-video-character-consistency-guide)

Craft:

- [Judith Weston, "Directing the Actor" (MovieMaker reprint)](https://actioncutprint.com/files/DirectingActor-JudithWeston.pdf)
- [Peter D. Marshall, "3 Judith Weston action verb quotes", 2025-09-10](https://filmdirectingcoach.substack.com/p/3-judith-weston-quotes)
- [Sheila O'Malley on Michael Caine's *Acting in Film*](https://www.sheilaomalley.com/?p=44298)
- [Neil Oseman, "Composing a Shot-Reverse", 2017-04-16](https://neiloseman.com/composing-a-shot-reverse/)
- [StudioBinder — types of camera shots](https://www.studiobinder.com/blog/ultimate-guide-to-camera-shots/)
- [StudioBinder — shot reverse shot, reaction shots and coverage](https://www.studiobinder.com/blog/shot-reverse-shot-cutaways-coverage/)
- [Kuleshov effect — Wikipedia](https://en.wikipedia.org/wiki/Kuleshov_effect)

---

**Previous:** [[15-continuity-bible-script-supervisor]] · **Next:** [[17-editing-1-workflow-and-the-cut]] · **Track map:** [[11-directors-track-roadmap]] · **Back to:** [[00_README]]
