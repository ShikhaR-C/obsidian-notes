# Sound — Edit, Design and Mix: One Sound World for 31 Clips

> Level: Intermediate → Advanced | Hat: Editor | Time: ~3 hr, plus one mixing session | Secures: Sonic | Outcome: you give Saaf Hisaab's locked picture one sound world — a clean dialogue edit, continuous beds, effects on the cut frame, three split edits, two spotted music cues — and deliver a mix at −14 LUFS / −1 dBTP that still reads on a phone speaker | Status: written & web-verified **2026-10-01** against the DaVinci Resolve 21 manual and Blackmagic's 21.1 Studio list (every Resolve tool here is in the free edition unless marked Studio), Flow, Flow Music and Vids Help, and the sound-craft sources in §15.

---

## Explain-it-like-I'm-5

Every robot crew that shot one of your clips also brought its own microphone — and each recorded a different room: a different hum, a different street outside, sometimes music nobody asked for. Lay 31 clips in a row and you hear 31 rooms. That is why a stitched AI film *feels* stitched even when every face matches.

The sound editor is the crew member who shoots nothing. He throws the 31 rooms away and builds **one** world: one office that hums the same all night, one street outside, one buzz that is always the same buzz, one piece of music that knows when to keep quiet. Ears are lazy in a useful way: **if the sound keeps going, the brain decides the picture kept going too.**

## 1. The One Idea: Sound Is the Glue

Of the track's four continuities — causal, perceptual, emotional, sonic — this file secures the fourth, **after picture lock** ([[18-editing-2-rhythm-structure-and-rescue]]). [[10-deep-dive-scene-continuity]] §7.7 is the summary; this is the craft.

The film-sound theorist Michel Chion (*Audio-Vision*) named the two effects that make the ear forgive the eye:

- **Synchresis** — a sound and a picture at the same instant weld into one event. A door click on the exact cut frame turns two clips made by strangers into one door closing.
- **Added value** — what the sound tells us, the audience credits to the picture. A night ambience unbroken across a cut says "same room, same minute", and the brain believes it.

So every cut is also a sound decision:

| At the cut, the sound… | The audience reads |
| ---------------------- | ------------------ |
| continues unchanged | same place, same time — the cut disappears |
| lands a sync hit on the cut frame | one event, seen twice |
| arrives before the picture (**J**) | the next moment is already here |
| lingers after the picture (**L**) | the last moment still matters |
| changes completely | somewhere else, or later — only on purpose |

**Murch's density budget.** In a 2005 essay, Walter Murch observed that an audience can follow about **two and a half** layers of the *same* kind of sound; spread the layers from speech ("encoded") through effects to music ("embodied") and about **five** stay clear. So: at most five layers at any moment, never three of one kind. Scene 2 sits at five — dialogue, room, engine, Foley, music — which is why its music is a pulse with no melody.

## 2. The Layers and the Track Layout

- **Dialogue** — spoken lines; on-camera lines are **sync** (the lips were made with them).
- **Room tone** — the "silence" of a room when nobody speaks. Digital silence sounds like a fault, not a pause.
- **Ambience bed** — a place's continuous sound: canopy hum, crickets, distant trucks.
- **Hard effects** — sync sounds of one visible event: the buzz, the door click, the horn.
- **Foley** — body and prop sounds performed to picture (pen, pages, glass), named after Universal's Jack Foley.
- **Music** — the score; nobody in the film hears it.

One track per job, so each layer moves as one decision:

| Track | Name | Holds | Processing |
| ----- | ---- | ----- | ---------- |
| A1 | DIA | Veo clip audio, linked to V1 — only the 5 lines and 3 kept hits on (§3) | Dialogue Leveler; high-pass 80–100 Hz |
| A2 | PHONE (mono) | the off-screen voice, S2-01 | phone chain (§4.4) |
| A3 | ROOM | RT-A, the cabin's room tone | — |
| A4 | AMB | outside beds EXT-N, AMB-B, EXT-M (§5) | Ducker 2 dB, source DIA + PHONE |
| A5 | ENGINE | Kishan's tanker, all three days | pan and EQ for perspective |
| A6 | FX | buzz, chimes, door, brakes, nozzle, horn | — |
| A7 | FOLEY | pen, pages, cloth, steps, glass, thumb tap | — |
| A8 | MUSIC | M1, M2 (§9) | Ducker 3 dB, source DIA + PHONE |
| Bus 1 | main mix | everything | Limiter, Ceiling −1.0 dB |

In Resolve, right-click an audio track header to add tracks (Mono for PHONE, Stereo for the rest); click the default "Audio 1" name, type the new one, press Return. On the Fairlight page the **Dialogue Leveler** sits in each channel strip's Track FX section; reveal the **Ducker** from the Mixer's three-dot menu → **Visible Track FX**. The main bus is **Bus 1** (some manual pages call it Main 1).

```
FREE      Dialogue Leveler · Ducker · EQ · Limiter (true peak) · Reverb ·
          Distortion · audio Noise Reduction · Stereo Fixer · Elastic Wave ·
          Loudness meters · Normalize Audio Levels · Sound Library · Record Voiceover
STUDIO    Voice Isolation · Dialogue Separator · Dialogue Matcher · Music Remixer ·
          Music Editor · Beat Detector · Voice Convert · subtitles from audio
```

**The Vids route.** Vids audio tracks span scenes, with **Format → Sound** for volume and fades, **Narrative** / **Background** ducking and at most 50 audio objects. Vids Help documents no way to detach a clip's own sound, so the beds, effects and music below work there; the dialogue L-cut (§8) does not.

## 3. Veo's Native Audio, Clip by Clip: Keep, Duck or Replace

Veo hands you one fused track per clip: the voice, that clip's room, and whatever else it invented. There are no stems, and the free edition cannot pull a voice out (Voice Isolation and Dialogue Separator are Studio). Decide per clip:

| Veo gave you… | Decision | Why |
| ------------- | -------- | --- |
| a lip-synced line | **K — keep** the line; duck its own room out around it (§4.1) | the lips were made with it |
| the clip's ambience | **R — replace** with the bed | 31 clips = 31 rooms |
| music | **R — always** | it restarts every clip, fused under lines |
| a good hit, in sync | **F — keep the hit** only; layer if thin | it is already on the frame |
| a motif sound (buzz, chime) | **R** — one sample, every time | one sound per object (file 10 §7.7) |

Saaf Hisaab: **K** = S2-02, S2-03, S2-07, S3-09, S3-10 · **F** = S1-01 (pen), S1-05 (pen circles), S3-08 (nozzle) · **R** = the other 23.

**Ask the director for edit-friendly audio.** [[06-phase-6-voice-lipsync-audio|Phase 6]] teaches sound in prompts; this is the editor's request for the `[AUDIO]` block (the letters and tags are labels; paste only the words after them; K is S2-07's line exactly as [[16-directing-performance-and-dialogue-scenes]] §8 builds it):

```
K  [AUDIO] Very quiet room tone. Ravi has a warm, slightly husky male voice,
           early 30s, an Indian man speaking natural, colloquial Hindi;
           medium-low pitch, unhurried. Ravi says, almost a whisper, flat, to
           himself: "Register mein nahin hai." No music. No subtitles.
F  [AUDIO] The nozzle clunks into the fill port. No music. No subtitles.
R  [AUDIO] Quiet room tone only. No music. No subtitles.
```

For K shots this beats naming the idle or the pages in the prompt: an idle fused under a line can't be removed, and ENGINE carries it anyway. Leave Flow's **Return silent videos** off — even a clip you will replace is a free sync guide.

**In Resolve**, each clip's audio lands on A1 with its picture. Option-click the audio of each R clip (sound without picture) and press **D** to disable it — it stays in place as a guide. On the three F clips, drag the Audio Fade handles inward until only the hit remains.

## 4. The Dialogue Edit

### 4.1 Tops, tails and fades

The **top** is where a line's audio starts, the **tail** where it ends. Option-click the audio's edge and drag it in — the picture stays — so each kept line starts **2–4 frames** before the first syllable and ends **6–8 frames** after the last, keeping the breath and the room's decay. Then fade each end with the Audio Fade handles: 2–4 frames if the clip's room matches the bed, **5–10 frames** (200–400 ms, Larry Jordan's figure) if it doesn't. Fairlight's automatic 1.5 ms crossfade between adjacent clips (**Project Settings → Fairlight → Enable Soft Fades**) stops clicks, not a change of room.

### 4.2 Room-tone fill

Find the quietest 2–3 s in the night-office outtakes — no speech, no movement — and lay copies end to end on ROOM from 00:00 to 00:40, crossfaded as in §5; the same **RT-A** returns under scene 4 from 01:07:00. Crews record 30–60 s of room tone on set for this job; you harvest it. Levels add, as Larry Jordan points out — a line brings its own room, so the room is louder under a line than in the gaps. The 5–10-frame fades and the 2 dB Ducker on AMB keep the floor even.

### 4.3 Make separately generated lines sound like one scene

1. Select the six dialogue clips (DIA and PHONE) → right-click → **Normalize Audio Levels** → Normalization Mode: a loudness standard (not Sample Peak) → target **−16** → Set Level: **Independent**, so each clip is matched on its own.
2. Switch on the **Dialogue Leveler** for DIA (Track FX on the Fairlight page; the Inspector on the Edit page): default preset *Allow wider dynamics*, **Lift Soft Dialogue** on, a little **Background Reduction** (Blackmagic's advice: normalise first, as in step 1).
3. **Hero-line EQ.** One reference per voice: Ravi = S2-07 (the peak), Kishan = S2-02. Drag the Fairlight EQ onto each other line: high-pass at 80–100 Hz on all; boomier than the hero → cut 2–3 dB near 250 Hz; duller → add about 2 dB near 3 kHz (speech presence lives around 2–5 kHz). Flip the plug-in's **A/B** buttons against the hero; stop when they sound like one room, not when they sound "good".
4. **Perspective — a little.** Kishan at the doorway (S2-02, MS) sits 1–2 dB under Ravi's close lines, with a touch of small-room **Reverb** (Dry/Wet under 10%); Ravi's close lines stay dry. Mixers change reverb only *slightly* between shot sizes — intelligibility wins.

### 4.4 The off-screen phone voice (S2-01)

No lips to match, so any clean read works; [[16-directing-performance-and-dialogue-scenes]] picks the source (its default: record a colleague on a phone). On PHONE, insert the **Fairlight EQ** with Band 1 **Hi-Pass** at 300 Hz and Band 6 **Lo-Pass** at 3,400 Hz — the telephone voice band — then **Distortion** (Blackmagic's own description names "old telephones") at a low amount, Dry/Wet 20–30%. Sit it 2–4 dB under Ravi's lines, centred. Save both plug-ins with **Add Preset** as `PHONE-earpiece`.

### 4.5 When a line must be re-done

| Option | Cost | Limit |
| ------ | ---- | ----- |
| Lift the line from another take of the same shot; fit its timing with **Elastic Wave** (Fairlight) | 0 | only if the voice matches — Veo re-rolls voices per clip |
| Cover the bad words with the listener or an insert (an L-cut, §8; file 10 §6.5 rule 6) | 0 | the start of the line must be good |
| Regenerate from the board still | ⏣20 Fast / ⏣100 Quality | the new voice may differ from the other lines |
| Off-screen only (S2-01): a teammate on a phone or Resolve's **Record Voiceover** tool · a Veo Lite clip's voice · Vids AI voice-over (Hindi; unlimited on AI Pro) | 0 · ⏣10 · 0 | Vids media: read its terms first; a realistic synthetic voice may need a label (file 20) |

A voice that holds across clips — an Omni voice reference (with Ingredients) or a Character — is decided before generating, in file 16. Not available: Omni's 40-credit edit cannot change voices; Dialogue Matcher and Voice Convert need Studio; Flow documents no cloning of an uploaded voice.

## 5. Ambience Beds: One Continuous World per Place and Time

A **bed** runs under a whole scene and changes **12–24 frames off a picture cut** (as a J or an L), never on it — unless you want the audience to feel a hard break.

| Bed | Under | Layers (three at most) | Changes |
| --- | ----- | ---------------------- | ------- |
| RT-A — cabin room tone | scenes 1, 2 and 4 | the glass cabin's quiet air | never — same room, every day |
| EXT-N — night outside | S1-01 → S2-08 | canopy-light hum · crickets · a far highway truck every 12–20 s | out on the hard cut, 00:40:00 |
| AMB-B — dusk forecourt | S3-01 → S3-11 | canopy hum (lights just on) · birds settling · far traffic | out through the dissolve |
| EXT-M — morning outside | S4-01 → S4-07 | birds · a two-wheeler now and then · far traffic | pre-laps from 01:07:00 (J2) |

The lesson is the first row: scene 4 is the same office on another day, so the room tone stays and only the outside changes — "same office, new morning", the sound half of the D1 → D3 change [[15-continuity-bible-script-supervisor]] tracks in picture.

| Source | Cost | Rights |
| ------ | ---- | ------ |
| The quietest stretch of outtakes from the same set-up | 0 | Flow's terms: Google "won't claim ownership", but states no commercial licence — read them |
| A room-tone plate: Frames→Video on Lite from `LOC-A_night_master.png` (or the dusk and morning masters), 8 s, the audio line `Only the quiet hum of the empty office at night, no voices. No music. No subtitles.` | ⏣10 each; ⏣30 for three — the spare's room-tone draw ([[14-previs-storyboard-floorplan-animatic]] §9) | as above |
| The Fairlight sound library, downloaded from the **Sound Library** panel (over 500 professionally recorded Foley sounds) | 0 | Blackmagic calls it royalty-free |
| Voice Memos recorded at a real pump, 2 minutes per place (Resolve on a Mac imports them) | 0 | yours — ask the dealer; record nobody's conversation |

Also possible: a Flow Tool such as *Mondo Sónico* (ambience and Foley with stems; credits shown in Flow) or the local second unit ([[../comfyui/09-google-flow-parity]]).

**Build a bed.** Pick 6–8 s with no distinctive event and lay copies end to end. Select each join, press **Shift-T** (**Timeline → Add Audio Only Transition**), double-click the crossfade, set Duration 24–48 frames and style **+3 dB**: two *different* stretches of sound crossfaded on a linear curve dip about 3 dB in the middle; the boosted curve holds the level. Then place the distinctive events — a truck passing — by hand, at uneven gaps: an event repeating at a fixed interval gives the loop away.

## 6. Hard Effects and Foley That Sell a Cut

Put the hit on the frame where the action **completes** — contact, not approach — and synchresis does the rest: cut and sound become one event.

**Sync tolerance, in numbers.** ITU-R BT.1359 found viewers detect sound **leading** picture at about 45 ms but sound **lagging** only at about 125 ms. At 24 fps a frame is 41.7 ms: one frame early is already at the edge of notice; one or two frames late is safe. When unsure, slip a hit later, never earlier.

| Sound | Where (film time) | What it sells |
| ----- | ----------------- | ------------- |
| Pen scratch (F) | stops on the hand-lift, 00:01:18 | the cut on action into the wide |
| Page flip (Foley) | the slap on 00:28:00, the cut frame | one flip, seen from two distances |
| Door click | 00:39:23, one frame before the cut | the end of scene 2 — the engine carries on alone |
| Cab-door latch | 00:43:01, one frame after the cut | the cut on action at the cab |
| Thumb tick → nozzle clunk (F, layered) | 00:58:12 → 01:00:02 | cause and effect across two shots: his tap *makes* the clunk |
| The steel glass | rattling on the desk as the phone creeps (S1-03); lifted, 01:10:16 | the chai motif in sound: untouched and cold → in his hand |

To **layer** a thin Veo hit with a library hit, zoom into the waveforms and line up the two attacks exactly.

**Heavy sounds vanish on phones.** Most phone speakers struggle below 200 Hz and roll off completely by 100 Hz. Kishan's idling engine is mostly low rumble, so give it energy around 250–700 Hz — a rattle or exhaust-tick layer, or an EQ lift — or the phone audience never hears it.

## 7. Motifs and Bridges: The Story in Sound

- **The phone** tells the story: a harsh buzz on wood (S1-02 → S1-06, the problem calling) becomes a soft chime (S3-03, S4-02, the answer arriving). One buzz file, one chime file, the same each time — so the change of sound *is* the change of story.
- **The tanker** speaks for Kishan: idling and waiting under scene 2 (*"gaadi khadi hai"*), rolling in and switching off in scene 3 (he is staying), passing with one horn tap in scene 4 (thanks). One engine family, all three days.
- **Screen direction in sound.** The tanker arrives right-to-left (S3-01): pan its engine right → left. It leaves left-to-right (S4-04): pan left → right. Keyframe the clip's **Pan** in the Inspector.

**The engine bridge, D1 → D2.** The idle enters faint under S2-02 (headlights behind Kishan), rises 6 dB in S2-06 (we see it), then drops 6 dB and loses its top under S2-07 and S2-08: split the clip at 00:35:00 (Command-\\) and give that piece a Fairlight EQ Band 6 **Lo-Pass** near 1 kHz — the sound designer's signal for "behind something". The world recedes for the peak. It runs through the door click and crossfades over 24 frames into the dusk arrival at 00:40:00. The picture says "next day" with light and a new shirt; the sound says "same tanker, same problem". Build: two clips on ENGINE, edit at 00:40:00, **Shift-T**, Duration 24, Alignment **Begin on Edit**, style +3 dB.

**The music bridge.** M2 plays straight across the dissolve, so the morning arrives as the answer to the evening. Pre-lapping the morning is J2 below.

## 8. Split Edits, Step by Step

A **split edit** puts the sound cut and the picture cut on different frames; J and L are named for their shapes on the timeline:

```
J-cut: B's sound arrives early         L-cut: A's sound lingers
V1  |--- shot A ---|--- shot B ---     V1  |--- shot A ---|--- shot B ---
A1  |--- A ---|------- B ---------     A1  |------- A -------|--- B -----
             ↑ 12 frames early                              ↑ 16 frames late
```

**Roll the audio edit; never drag the audio clip.** A roll moves the join and keeps every word on its lips. A drag slides the sound off its picture, and Resolve flags it with red out-of-sync numbers on the clip — undo (Command-Z). This is the roll [[10-deep-dive-scene-continuity]] §6.2 asks for in its J-cut / L-cut row.

On the Edit page:

1. Check the handles — clips cut to 2–4 s out of 4, 6 or 8 have seconds to spare.
2. Select the sound side only: **Option-click** the audio half of the edit point on A1, or press V, then **Option-U** until only the audio is selected (the keys [[17-editing-1-workflow-and-the-cut]] uses) — as if **Linked Selection** (Shift-Command-L) were off.
3. Type **−12** and Return to roll it 12 frames earlier (a J), or **+16** for 16 frames later (an L). Comma and Period nudge one frame; Shift-Comma and Shift-Period nudge five.
4. Press **Shift-T**, then double-click the crossfade and set its Duration to 2–4 frames (Shift-T uses the one-second standard duration).
5. Play from three seconds before: does the sound arrive or linger *for a reason*?

The film's three split edits:

1. **J1 — S1-02 → S1-03, the buzz.** The buzz starts at 00:05:06, 18 frames before the cut to the phone: the sound asks "what's that?", the next picture answers. It lives on FX, so you place it — no roll. The two chimes (S3-03 → S3-04, S4-02 → S4-03) and the horn (S4-03 → S4-04) repeat this shape at 12 frames.
2. **L1 — S2-03 → S2-04, the line over the empty column.** Slip S2-03 until *"Kaun sa driver?"* ends at 00:28:16, then roll the DIA edit +16. The question plays over the finger finding nothing — the picture answers it — and its last words need no lip-sync. The page flip on FOLEY marks the cut.
3. **J2 — S3-11 → S4-01, pre-lapping the morning.** RT-A and EXT-M start at 01:07:00 and fade up over 24 frames under the dusk wide; AMB-B and the fuel flow fade out 01:07:12–01:08:06, through the 12-frame dissolve. The audience hears morning before seeing it, so the time jump lands as relief, not a reset.

## 9. Music: Spotting, Temp, Generating, Cutting, Ducking

**Spotting** is deciding, with timecodes, where each music cue starts, changes and stops (on a feature, director and composer do it together). File 10 §7.7's "one continuous music bed" is the promo version; in a story film *one* means **one musical family**, spotted in and out.

```
0s           13             35                  54.5             87.5  90
|............|==============|...................|================|~~~~|
  sound only   M1 pulse       SILENCE             M2 trust theme   button
               (pen circles)  (S2-07 → S3-05)     (eyebrows lift)  (logo)
```

| Cue | In | Out | Why |
| --- | -- | --- | --- |
| M1 *pressure* — low drone, slow pulse, no melody | 00:13:00, the pen's first circle | 00:35:00, hard out on the cut to S2-07 | marks "this is costing me"; a melody would fight four lines |
| Silence | 00:35:00 | 00:54:12 | the peak and the wary standoff play on room, engine and one quiet line |
| M2 *trust* — same key and tempo, warm melody | 00:54:12, Ravi's eyebrows lift (S3-05) | final chord 01:27:12, rings out to 01:30:00 | enters on the man, not the phone — the product makes the change possible, he makes it ([[12-story-engine-seamless-storytelling]]); swells 3 dB on the release, 01:06:00 |

**Silence at S2-07** is not digital zero: music and effects out, room tone and the muffled idle stay, and *"Register mein nahin hai."* is spoken into that. The drop *is* the peak.

**Temp versus final.** The animatic and rough cut ([[14-previs-storyboard-floorplan-animatic]]) run on a **temp** — a quick Flow Music draft or a library track. Directors have grown so attached to temp music that they rejected the real score; don't. Generate the final cues after picture lock, to the locked timings.

**Generate.** **Google Flow Music** runs Lyria 3.5, which Google says lets you "control the tempo and duration"; AI Pro includes its Plus plan (10,000 Flow Music credits a month, separate from Flow's video credits). The Gemini app (tracks up to 3 minutes on Pro) and Vids (50 thirty-second clips and 20 songs a month on Pro) also work. Prompt for a cue that is easy to cut:

```
M2: Instrumental film-score cue, 80 BPM, one key throughout, no vocals.
Soft santoor melody and warm piano over a low tanpura drone. Starts
sparse, builds gently, clear phrase breaks every 8 bars. Ends on one
decisive final chord that rings out, no fade-out. 45 seconds.

M1: Same key and tempo. Low tanpura drone and a slow, soft frame-drum
pulse; no melody; uneasy and restrained. 30 seconds.
```

Why 80 BPM: at 24 fps one beat is **18 frames** and a bar of four is **72 frames = 3 s** — the film's commonest shot length — so every musical edit lands on a whole frame. With the final chord at 01:27:12, M2's downbeats fall every 3 s back to its entry at 00:54:12, and from S4-03 on each cut lands 12 frames before a downbeat — with the music, never on it; [[18-editing-2-rhythm-structure-and-rescue]] leaves that choice of tempo to this file.

**Cut M2 to length:**

1. **Back-time it** — place it from its Out, not its In: the final chord at 01:27:12, on the logo. If the chord sits 42 s into the file, the cue now starts at 00:45:12 — 9 s early.
2. **Find the bars.** Play the cue, press **M** on each downbeat, then drag each marker onto the attack in the waveform. (Studio's Detect Music Beats does this; free does not.)
3. **Cut whole bars, landing where a phrase begins** (the prompt asked for a break every 8 bars). Blade (**Command-\\**) just before the downbeat that opens bar 9 — an edit right before a strong attack is hidden by it (pre-masking) — and again 3 bars (216 frames) earlier, at bar 6. Delete bars 6–8 and close the gap by sliding the first part later, so the chord stays at 01:27:12: the cue now starts at 00:54:12, on the eyebrow lift.
4. **Crossfade** 2–4 frames across a beat, about half a second (12 frames) on a sustained pad, style +3 dB — never a long fade on rhythmic music.
5. **A few frames out?** Elastic Wave can stretch one short passage; stretching a whole track adds artefacts.
6. **End on a button**: a clear, decisive ending, not a fade — the final chord on the logo, ringing out under the end card.

M1 needs no ending: it is cut dead at 00:35:00, and the interruption is the point.

**Ducking.** Music sits 10–15 dB under dialogue; the **Ducker** on MUSIC (Source: DIA, Command-click PHONE) dips another 3 dB while a line plays — Blackmagic says 2.0–5.0 dB works best. Keep its defaults (Lookahead 15 ms, Rise Time 10 ms, Hold 150 ms, Recovery Time 750 ms), lengthening Recovery if the music jumps back too fast after *"Bas."*

## 10. The Mix

Order: **relationships, then loudness, then checks.**

**Three words first.** **LUFS** measures loudness the way ears hear it, not just how high the waveform reaches. **Integrated** loudness is that measure averaged over the whole film, near-silent gaps left out: one number for the film. **True peak** (dBTP) is the loudest instant once the file is turned back into sound, which can sit above its highest sample; holding it at −1 leaves room for a platform's re-encode, which pushes peaks higher.

| Layer | Where it sits (practitioner recipe; judge on a phone) |
| ----- | ------------------------------------------------------------ |
| Dialogue | each line normalised to −16 LUFS (§4.3) — the recipe's −16 to −14 window |
| Phone voice | 2–4 dB under the on-camera lines |
| Music under lines | 10–15 dB under dialogue, Ducker 2–5 dB on top |
| Music in the clear (S3-11, scene 4, end card) | lifted in the gaps, never above the lines |
| Room tone | about 20 dB under dialogue, continuous |
| Beds and engine | between room tone and music; up where nobody speaks (S2-06, S3-01, S4-04) |
| Hard effects | short; buzz and horn may touch dialogue level for a moment |
| Bus 1 | **Limiter**, Ceiling −1.0 dB — Fairlight's Limiter is a true-peak limiter |

| Who | Number | Status |
| --- | ------ | ------ |
| EBU R 128 (broadcast) | −23 LUFS, ≤ −1 dBTP | official standard |
| AES TD1008 (streaming) | speech −18, mixed −17, music −16 LUFS; ≤ −1 dBTP | official recommendation |
| YouTube | turns loud videos down to ≈ −14 LUFS, never turns quiet ones up | engineers' measurements; no published number (Blackmagic's manual calls −14 "the YouTube target") |
| Meta, WhatsApp | none published | — |
| **Our master** | **−14 LUFS integrated, ≤ −1 dBTP** (≤ −2 dBTP for WhatsApp-bound files) | social-media convention |

Why −14: YouTube never lifts a quiet video, so a −17 mix plays quieter than its neighbours; anything louder is turned down anyway.

1. **Project Settings → Fairlight → Audio Metering → Target Loudness level: −14** (default −23).
2. On the Loudness meter at the right of the Fairlight meters, click **Reset**, play the whole film from 00:00:00, read **Integrated**. Move the Bus 1 fader by the difference; repeat. (On a bounced mix: right-click → **Analyze Audio Level**.)
3. Export and measure the file itself with the free tool ffmpeg — read **I** (integrated) and the true peak. Leave the Deliver page's **Audio Normalization** off when you mixed to target, so the file is what you heard.

```
ffmpeg -hide_banner -nostats -i saaf-hisaab_master_v01.mp4 -af ebur128=peak=true -f null -
```

**Mono check.** Insert **Stereo Fixer** on Bus 1, Format **Mono**, and play the film: anything that vanishes or turns hollow (usually wide music or a bed) needs fixing. Bypass it before export.

**Phone check — the one that counts.** AirDrop the export to your phone and play it on the speaker at half volume, at arm's length, then on earphones:

```
[ ] every line understood without captions — S2-01's phone voice especially
[ ] the buzz and the chime are clearly different sounds
[ ] the engine is audible in S2-06 and S3-01 (its mid-range layer is there)
[ ] the music never covers "Bas?" / "Bas."
[ ] nothing crackles at the loudest moments (buzz, horn, final chord)
[ ] the silence at S2-07 feels chosen, not broken
```

## 11. The Muted Film

Meta says Reels "default to Sound On", so mix for sound-on and caption for sound-off. Some viewers still watch muted — on a bus, in a meeting — so every story point carried by sound needs a silent backup:

| Sound cue | Muted, they get it from |
| --------- | ----------------------- |
| The buzz | S1-03: the phone creeping toward the glass |
| *"Payment ho gaya tha, Ravi ji!"* (S2-01) | **only a caption** — the one line with no lips |
| *"Sahab, gaadi khadi hai. Kab tak?"* | caption + Kishan glancing back at his waiting tanker (S2-05, S2-06) |
| *"Kaun sa driver?"* · *"Register mein nahin hai."* | captions + the empty column (S2-04) + the tightest shot (S2-07) |
| The engine bridge, D1 → D2 | the picture: night → dusk light, a new shirt |
| The chime | S3-04: the phone's glow and the composited verified order |
| *"Bas?"* · *"Bas."* | captions + two smiles + the nozzle going in |
| The horn tap | S4-04: the hand raised from the cab |

**Hand-off.** The Dialogue column of the cue sheet is the caption list — six lines with in and out times. [[20-colour-finishing-and-delivery]] styles them, places them in the safe zone and burns them in.

## 12. The Cue Sheet — 90 Seconds, Every Sound

Film time `mm:ss:ff` at 24 fps (if your timeline starts at 01:00:00:00, add the hour). Line times are planned; slip a few frames to fit the takes. Beds run unless a row says otherwise: scenes 1–2 RT-A + EXT-N, scene 3 AMB-B, scene 4 RT-A + EXT-M. **Bold** = a split edit or a sync point.

| TC in | Shot | Dialogue | Ambience and engine | Effects / Foley | Music |
| ----- | ---- | -------- | ------------------- | --------------- | ----- |
| 00:00:00 | S1-01 | — | beds fade up 12 fr | pen scratch, stops on the lift, 00:01:18 | — |
| 00:02:00 | S1-02 | — | — | page rustle; **buzz in 00:05:06 (J1)** | — |
| 00:06:00 | S1-03 | — | — | buzz on wood; the glass rattles as the phone creeps | — |
| 00:08:00 | S1-04 | — | — | buzz stops 00:10:12, after his glance — ignored | — |
| 00:12:00 | S1-05 | — | a far truck | pen circles ×2; **buzz in 00:14:12** | **M1 in 00:13:00** |
| 00:15:00 | S1-06 | — | — | an exhale; buzz stops on the pick-up, 00:16:08 | M1 |
| 00:18:00 | S2-01 | PHONE 00:18:04–00:20:16 *"Payment ho gaya tha, Ravi ji!"* | — | — | M1, ducked |
| 00:21:00 | S2-02 | Kishan 00:21:06–00:23:18 *"Sahab, gaadi khadi hai. Kab tak?"* | engine idle in, faint | — | M1, ducked |
| 00:24:00 | S2-03 | Ravi 00:25:16–00:28:16 *"Kaun si gaadi thi? Kaun sa driver?"* | idle low | pages under his hand | M1, ducked |
| 00:28:00 | S2-04 | **L1: the line's last 16 fr** | idle low | **page flip on the cut** | M1 |
| 00:30:00 | S2-05 | — | idle | weight shift (cloth, sandal) | M1 +2 dB |
| 00:33:00 | S2-06 | — | **idle +6 dB** | — | M1 |
| 00:35:00 | S2-07 | Ravi 00:35:12–00:37:04 *"Register mein nahin hai."* | RT-A only; idle −6 dB, Lo-Pass ~1 kHz | phone lowered | **M1 hard out — silence** |
| 00:38:00 | S2-08 | — | idle muffled | footsteps out; **door click 00:39:23** | — |
| 00:40:00 | S3-01 | — | night beds out on the cut; AMB-B up 12 fr; **idle → dusk arrival, 24-fr crossfade**, pan R→L | brakes hiss 00:42:12; engine off 00:42:20 | — |
| 00:43:00 | S3-02 | — | — | **cab-door latch 00:43:01**; boots on concrete | — |
| 00:46:00 | S3-03 | — | — | arms fold; **chime 00:48:12** | — |
| 00:49:00 | S3-04 | — | — | chime rings out; phone handling | — |
| 00:53:00 | S3-05 | — | — | — | **M2 in 00:54:12** |
| 00:56:00 | S3-06 | — | — | — | M2 |
| 00:58:00 | S3-07 | — | — | thumb tick 00:58:12 | M2 |
| 01:00:00 | S3-08 | — | — | **nozzle clunk 01:00:02** + a library layer; fuel flow in 01:01:08 | M2 |
| 01:02:00 | S3-09 | Kishan 01:02:10–01:02:22 *"Bas?"* | flow continues | — | M2, ducked |
| 01:04:00 | S3-10 | Ravi 01:04:12–01:05:00 *"Bas."* | flow | — | M2, ducked |
| 01:06:00 | S3-11 | — | AMB-B up; **RT-A + EXT-M in 01:07:00 (J2)**; AMB-B and flow out 01:07:12–01:08:06 | — | M2 +3 dB |
| 01:08:00 | S4-01 | — | across the 12-fr dissolve | steel glass lifted 01:10:16 | M2, across the dissolve |
| 01:11:00 | S4-02 | — | — | a sip; **chime 01:14:12** | M2 |
| 01:15:00 | S4-03 | — | — | **horn tap 01:17:12** | M2 |
| 01:18:00 | S4-04 | — | engine passes, pan L→R, Lo-Pass (through glass) | — | M2 |
| 01:21:00 | S4-05 | — | engine fading right | cloth as the glass rises | M2 |
| 01:24:00 | S4-06 | — | — | chair creak 01:24:02 | M2 |
| 01:27:00 | S4-07 | — | beds out by 01:28:00, under the 8-fr fade | — | **M2 final chord 01:27:12**, rings out to 01:30:00 |

## 13. What Sound Can't Fix

- **No stems.** A line and its clip's room arrive fused; the free edition cannot separate them. Prompt for quiet rooms, trim tight, fill with room tone.
- **A different voice stays a different voice.** EQ makes two takes sound like one room, not one man; Dialogue Matcher needs Studio and Omni's edit cannot touch voices. Regenerate, or plan the voice before generating (file 16).
- **No automatic music fitting in free.** Music Editor and the Beat Detector are Studio; you cut by ear and markers.
- **Lips can't be re-timed.** Slip a line a frame or two, or cover it with the listener; you cannot move a mouth.
- **Rights are only partly stated.** Google One Help lists "commercial use rights" among AI Pro's Flow Music benefits; no Google page read states a commercial licence for Flow or Veo *video* output, or for music made in the Gemini app or Vids. Read the terms before paid use, file them with the track, and disclose AI music where the platform asks (file 20) — rights are not disclosure.
- **Loudness targets are partly convention.** Meta and WhatsApp publish none; −14 LUFS is practice, not law. The phone in your hand is the final judge.

## 14. Exercises

**14.1 — Spot it (0 coins).** Watch your locked cut with sound, then muted; write its spotting table — each cue's in, out and why. Artefact: `saaf-hisaab_spotting_v01`.

**14.2 — The template (0 coins).** Build A1–A8 and Bus 1 with the Limiter; name the tracks; disable every R clip's audio. Artefact: timeline `saaf-hisaab_sound_v01`.

**14.3 — Room tone from nothing (0 coins).** Harvest RT-A from three rejected night takes, loop it to 40 s with +3 dB crossfades, play scenes 1–2 over it with only the lines on. Artefact: `RT-A_night_40s.wav`.

**14.4 — Three split edits (0 coins).** Build J1, L1 and J2 at the §8 frames, each with a named marker. Then build L1 wrongly — drag the audio — and find the red numbers. Artefact: `saaf-hisaab_sound_v02`.

**14.5 — The phone voice (0 coins).** Record a teammate reading S2-01 into Voice Memos; build the §4.4 chain; A/B it against the dry read. Artefact: the `PHONE-earpiece` presets.

**14.6 — Cut M2 to length (0 coins; Flow Music credits only).** Generate M2 from the §9 prompt, back-time the final chord to 01:27:12, cut whole bars until the entry lands at 00:54:12. Artefact: `M2_cut_v01`.

**14.7 — Mix to target (0 coins).** Target −14, Limiter at −1.0 on Bus 1; play the whole film; export; measure with ffmpeg. Artefact: a mix log — integrated LUFS, true peak, what you changed.

**14.8 — Mono, phone, muted (0 coins).** Run the §10 mono and phone checks and the §11 muted audit; fix one thing from each; re-export. Artefact: `saaf-hisaab_master_v01` plus three notes.

**14.9 — Room-tone plates (~⏣30).** If no outtake holds a clean stretch, make one 8 s Lite plate per location with the §5 prompt and rebuild the beds. Artefact: three `.wav` beds.

## 15. Sources (web-verified 2026-10-01)

Primary — tools and standards:

- Blackmagic Design: [DaVinci Resolve 21 Reference Manual](https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_21_Reference_Manual.pdf) (audio on the Edit and Fairlight pages, Fairlight FX, loudness, Deliver) · [Resolve 21.1 Studio and iPad Features](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_Studio_21_Features.pdf)
- Flow Help: [Projects and download ("Return silent videos")](https://support.google.com/flow/answer/16935308) · [Get started / FAQ (terms, ownership)](https://support.google.com/flow/answer/16353333) · [Credits](https://support.google.com/flow/answer/16526234) · [Tools](https://support.google.com/flow/answer/17104535) · [Six new Flow Tools — The Keyword](https://blog.google/innovation-and-ai/models-and-research/google-labs/six-new-tools-built-by-creatives/) · [Introducing Gemini Omni — The Keyword](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-omni/)
- Music: [Lyria 3.5 — The Keyword, 2026-07-29](https://blog.google/innovation-and-ai/models-and-research/google-labs/lyria-3-5/) · [Google Flow Music plans](https://support.google.com/flow/answer/17083870) · [Use Google AI Pro benefits — Google One Help](https://support.google.com/googleone/answer/14534406) · [Music in the Gemini app](https://gemini.google/overview/music-generation/)
- Vids Help: [Audio tracks](https://support.google.com/docs/answer/14999865) · [Feature limits](https://support.google.com/docs/answer/15609411) · [AI video clips](https://support.google.com/docs/answer/16143507)
- Platforms: [YouTube — disclosing altered or synthetic content](https://support.google.com/youtube/answer/14328491) · [Meta — Reels ads ("default to Sound On")](https://www.facebook.com/business/ads/facebook-instagram-reels-ads) · [Production Advice — YouTube loudness measurements](https://productionadvice.co.uk/stats-for-nerds/)
- Standards: [EBU R 128](https://tech.ebu.ch/docs/r/r128.pdf) · [AES TD1008](https://aes.org/wp-content/uploads/2024/01/20210924_TD1008_v3.13.pdf) · [ITU-R BT.1359](https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.1359-0-199802-S!!PDF-E.pdf) · [FFmpeg filters (ebur128)](https://ffmpeg.org/ffmpeg-filters.html)

Craft:

- [Walter Murch, "Dense Clarity – Clear Density" — Transom, 2005](https://transom.org/2005/walter-murch/) · [Michel Chion, *Audio-Vision* — Columbia University Press](https://cup.columbia.edu/book/audio-vision-sound-on-screen/9780231185899/) · [review defining synchresis — filmsound.org](http://www.filmsound.org/philips.htm)
- Wikipedia: [Split edit](https://en.wikipedia.org/wiki/Split_edit) · [Room tone](https://en.wikipedia.org/wiki/Room_tone) · [Foley](https://en.wikipedia.org/wiki/Foley_(filmmaking)) · [Film score — spotting, temp tracks](https://en.wikipedia.org/wiki/Film_score) · [Voice frequency](https://en.wikipedia.org/wiki/Voice_frequency)
- Dialogue: [Larry Jordan — dialogue and room tone](https://larryjordan.com/articles/mix-dialog-room-tone-faster-in-adobe-premiere-pro/) · [Production Expert — dialogue editing](https://www.production-expert.com/production-expert-1/5-techniques-for-dialogue-editing-in-film-and-tv) · [Production Expert — reverb for dialogue](https://www.production-expert.com/production-expert-1/when-to-use-mono-stereo-or-surround-reverbs-for-dialogue) · [John Purcell — Waves](https://www.waves.com/john-purcell-dialogue-editing-for-motion-picture) · [Audiokids — room tone](https://audiokids.it/what-is-room-tone/)
- Design and editing: [Karen Collins — auditory perspective](https://designingsound.org/2013/08/21/auditory-perspective-putting-the-audience-in-the-scene-2/) · [Mike Senior — hiding the edit, Sound On Sound](https://www.soundonsound.com/techniques/reaper-best-ways-hiding-edit) · [Fink, Holters & Zölzer — cross-fading, DAFx-16](https://www.hsu-hh.de/ant/wp-content/uploads/sites/699/2017/10/Fink-Holters-Z%C3%B6lzer-2016-Signal-matched-power-complementary-cross-fading-and-dry-wet-mixing.pdf) · [LANDR — bass on phone speakers](https://blog.landr.com/make-bass-audible-phone-speakers/)
- Music editing: [Larry Jordan — the back-time edit](https://larryjordan.com/articles/fcpx-backtime-edit/) · [Film Editing Pro — cutting music](https://www.filmeditingpro.com/quick-tips-for-cutting-music-cues/) · [SonicScoop — timing edits](https://sonicscoop.com/music-sync-skills-7-tips-for-creating-timing-edits-for-tv-film-and-video/) · [Michael Musco — button endings](https://www.michaelmusco.com/2026/02/structural-language-music-supervisors-expect.html)

---

**Previous:** [[18-editing-2-rhythm-structure-and-rescue]] · **Next:** [[20-colour-finishing-and-delivery]] · **Track map:** [[11-directors-track-roadmap]] · **Back to:** [[00_README]]
