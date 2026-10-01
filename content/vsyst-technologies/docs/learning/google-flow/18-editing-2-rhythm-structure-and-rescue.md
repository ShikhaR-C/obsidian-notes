# Editing 2 — Rhythm, Structure, Time and the Rescue Kit

> Level: Advanced | Hat: Editor | Time: ~3 hr | Secures: Emotional, across the film | Outcome: you can map a film's pace, move time and information with the cut, re-cut the same shots to 60 and 30 s, rescue a failed AI clip for 0 coins, write a pickup, run a test screening and lock picture | Status: written & web-verified **2026-10-01** against the DaVinci Resolve 21 Reference Manual and Blackmagic's 21.1 Studio list, Flow Help and the craft sources in §17.

---

## Explain-it-like-I'm-5

The robot crews have gone home. On your desk sit 31 boxes of film, each shot by a crew that never met the others. [[17-editing-1-workflow-and-the-cut|File 17]] taught you to join two boxes invisibly. This file teaches the editor's other two jobs.

The **drummer's**: a film has a heartbeat — quick where trouble closes in, slow where relief comes. No crew generated it; the editor plays it, by choosing how long each shot stays on screen.

The **mechanic's**: some boxes come back broken — a hand melts, a face changes halfway, the tanker drives the wrong way. Calling the crew back costs coins, so the mechanic first tries the free tools in order: cut earlier, cover it, zoom a little, slow it a little, hold a frame. Only when all fail does he send the crew a short, exact note asking for **one** new shot.

## 1. The One Idea

**Rhythm** is the pattern of shot lengths across a film and the feeling it makes. **Rescue** is the editor's set of repairs that make a failed clip usable without spending a coin. Both are designed, not found.

This file secures **emotional continuity** — one curve of feeling across all four scenes ([[11-directors-track-roadmap]]) — and rescues **perceptual continuity** when a clip breaks, from rough cut to picture lock. File 17 decided each cut; this file decides the film. Two rules:

1. **Every rung of the fix ladder (§9) except the last costs 0 coins.** A new shot is the last resort.
2. **Each shot's use is fixed** — it came out of the animatic ([[14-previs-storyboard-floorplan-animatic]]). The fine cut may slide a cut by up to **6 frames** (¼ s); a rescue that needs more is a pickup (§12) or a logged change.

## 2. Rhythm Is Designed — the Tempo Map

**Pace** is how long shots last; **average shot length (ASL)** is running time ÷ number of shots. A **tempo map** plots every shot's length in story order, so you *see* the pulse before you feel it. Saaf Hisaab's, from the master list (t = start, in seconds):

```
  t   shot   use  █ = ½ s
  0   S1-01  2   ████       scene 1 · ASL 3.0 s:
  2   S1-02  4   ████████   long and short alternate,
  6   S1-03  2   ████       restless, not yet urgent
  8   S1-04  4   ████████
 12   S1-05  3   ██████
 15   S1-06  3   ██████
 18   S2-01  3   ██████     scene 2a · 3.0 s: the argument
 21   S2-02  3   ██████
 24   S2-03  4   ████████
 28   S2-04  2   ████
 30   S2-05  3   ██████
 33   S2-06  2   ████       scene 2b · 2.3 s ◄ tightens
 35   S2-07  3   ██████     PEAK: the CU push-in · hold
 38   S2-08  2   ████       hard cut
 40   S3-01  3   ██████     scene 3a · 3.25 s: the stand-off
 43   S3-02  3   ██████
 46   S3-03  3   ██████
 49   S3-04  4   ████████   reading time
 53   S3-05  3   ██████     scene 3b · 2.1 s: the quick exchange
 56   S3-06  2   ████
 58   S3-07  2   ████
 60   S3-08  2   ████
 62   S3-09  2   ████
 64   S3-10  2   ████
 66   S3-11  2   ████       12-frame dissolve
 68   S4-01  3   ██████     scene 4 · 3.1 s: breath
 71   S4-02  4   ████████
 75   S4-03  3   ██████
 78   S4-04  3   ██████
 81   S4-05  3   ██████
 84   S4-06  3   ██████     8-frame fade
 87   S4-07  3   ██████     = 90 s
```

Four words to read it with:

- **Contrast.** An even pace goes numb; a *change* of pace is what the audience feels. S2-03 (a line that needs its breath) and S3-04 (a screen that needs reading time) feel long *because* their neighbours are short.
- **The peak.** Scene 2 tightens from 3.0 to 2.3 s a shot, but S2-07 peaks by being the film's **tightest shot** ([[10-deep-dive-scene-continuity]] §5.2) and its quietest — the music drops out ([[19-sound-edit-design-and-mix]]) — not by being fast.
- **The hold.** Staying on a face after its line so it lands. S2-07's 72 frames: ~12 lowering the phone, ~40 for *"Register mein nahin hai."*, ~20 of held silence, then cut on Kishan's movement.
- **Breath.** After the fastest run (S3-06 → S3-11), scene 4 settles to an even 3 s. Fast, then slow, is what relief feels like.

Two kinds of fast: scene 2b is **uneven** (2-3-2) and reads as trouble; scene 3b is **even** (2-2-2-2-2-2), a mechanism clicking shut — the deal is easy now.

**Make your own:** Edit page → **Index** (the Edit Index) → option menu → **Export Edit Index** (.csv); its **Record Duration** column is your shot lengths. Redraw it every version.

## 3. Cutting With and Against Music

A **beat** is one pulse of the music, a **bar** a group of beats (usually four), the **downbeat** beat 1, the strongest. At 24 fps, frames per beat = 1,440 ÷ BPM: 18 at 80 BPM, where a bar is 72 frames — exactly 3 s; 12 at 120 (a 48-frame bar). At 100 BPM (14.4) beats fall between frames. Four placements:

- **On the beat** — impact, arrival: the dissolve into scene 4, centred on 01:08:00 — beat 3 of a bar, not a downbeat.
- **Just ahead of the beat** — a practitioner habit puts a cut 1–2 frames early so it *feels* on the beat; test it on your own cut.
- **Well ahead of the beat** — the picture changes first and the music confirms it: this film's scene-4 cuts sit 12 frames, two-thirds of a beat, before each downbeat (below).
- **Against the beat** — unease, or a moment the music must not own: scene 2's dialogue is cut to the performance.

Every cut on the downbeat looks mechanical: the viewer predicts the cuts and watches the clock, not the faces. Vary lengths; use secondary beats (Larry Jordan, §17). Murch ranks rhythm below emotion and story ([[10-deep-dive-scene-continuity]] §5.6): cut to the performance, lay the bed, then move a *few* cuts onto beats.

**Worked: the film's bed.** [[19-sound-edit-design-and-mix]] §9 scores Saaf Hisaab at 80 BPM and back-times M2 from its final chord at 01:27:12, so downbeats fall every 3 s: …01:09:12, 01:12:12, 01:15:12, 01:18:12, 01:21:12, 01:24:12, 01:27:12. Each 3-s shot can fill one bar, but no scene-4 cut lands on a downbeat. From S4-03 on, the cuts (01:15:00, 01:18:00, 01:21:00, 01:24:00) and the fade to the end card (01:27:00) each sit 12 frames ahead of one: the new picture is already up when the downbeat arrives, and the final chord lands on the logo, not on the cut. The 2-s clicks of S3-06 → S3-11 (48 frames, 2⅔ beats) run against the bar — only every third cut can meet a downbeat. Under a 120-BPM bed all six would.

**Free Resolve:** the **Beat Detector** is **Studio-only**. Instead, deselect all clips, park on each downbeat's waveform peak and press **M**; with snapping on (**N**), cuts snap to the markers.

## 4. Time — Compress, Expand, Jump

Screen time and story time are two clocks; the cut sets the exchange rate. To **compress**:

- **Ellipsis** leaves out part of an event and lets the audience fill the gap: S2-08 → S3-01, almost a day vanishes.
- **Cutaway**: time passes while we look away — the search in S2-04 → S2-06 outlasts its 7 s on screen.
- **Montage sequence**: many moments in seconds, usually on music — a 2–3 min version could show a month of 9 PM nights in four 2-s inserts.

To **expand**:

- **Overlapping action** repeats part of an action across a cut: open S4-02 with ~8 frames of the glass still rising, and the first sip stretches.
- **Cutting between people** spreads one moment over everyone it touches: S3-04 → S3-07 turns a few seconds' decision into 11 s; S4-04 → S4-05 gives the salutes 6 s.

**The two time jumps need no caption** — [[15-continuity-bible-script-supervisor]] §10 counts three cues at the first and five at the second, more than the two it asks for:

- **D1 9 PM → D2 dusk** (S2-08 → S3-01, a hard cut on the door click): light (lamp-lit → amber dusk), place (office → forecourt), wardrobe (pale blue → cream). The same engine across the cut is a link, not a time cue.
- **D2 → D3 7 AM** (S3-11 → S4-01, a 12-frame dissolve): the dissolve itself, light (blue dusk → morning), wardrobe (cream → navy polo), props (the chai cold → steaming, the registers shelved) and sound (the buzz → a chime).

Why a cut, then a dissolve? Scene 2 ends on a loss whose consequence is the next image: the cut keeps the sting, and the engine makes it cause → effect. Scene 3 ends in relief, so the dissolve lets time pass gently ([[10-deep-dive-scene-continuity]] §6.1).

## 5. Montage in Working Terms

**Montage**, in the Soviet sense, is meaning made by putting shots side by side. Sergei Eisenstein named five methods in the 1920s; as working tools:

- **Metric** — cut by count, whatever the content: S3-06 → S3-11, six shots of 48 frames.
- **Rhythmic** — length follows the movement in the frame: S1-06 → S2-01, cut as the phone arrives at his ear.
- **Tonal** — shots chosen and cut for one feeling: scene 4, warm, soft, slow.
- **Overtonal** — all three at once: the dissolve into scene 4, where the pace slows, the glass lifts and blue turns gold.
- **Intellectual** — two images make an idea neither holds alone: in a 15-s ad, S2-04 (a finger finds nothing on paper) cut to S3-04 (an order already verified) says "this replaces that" with no words.

## 6. Scene Joins — Enter Late, Leave Early

**Enter late, leave early** is a screenwriting mantra, often traced to William Goldman (the origin is disputed): start a scene as late as it still makes sense; leave once its turn has happened. The editor applies it inside scenes (cut the hello and goodbye) and at joins: end on a **hook** — a question, sound or unfinished action — and open on the **answer**.

| Join | Leave early → enter late | Hook → answer | Link |
| ---- | ------------------------ | ------------- | ---- |
| 1 → 2 · S1-06 → S2-01 | No "hello": the call is already an argument | Who keeps calling? → *"Payment ho gaya tha, Ravi ji!"* | Cut on action |
| 2 → 3 · S2-08 → S3-01 | No close-up reaction; the tanker already arriving | Has he lost the driver? → the same tanker, next dusk | Hard cut; engine bridge: cause → effect |
| 3 → 4 · S3-11 → S4-01 | No handshake; morning already under way | Will it last? → steam from the chai glass | 12-frame dissolve; the chai motif |

**Cross-cutting** (parallel action) alternates two lines of action happening at the same time, usually converging on one moment; suspense comes from expecting them to meet. In scene 3 it would cut Kishan's tanker on the road against Ravi waiting at the pump. Cost: a new location (a dusk road, its own master still) and about three new shots — moving **right-to-left**, as the tanker arrives in S3-01 — at 2 Lite drafts + 1 Fast lock each: ⏣120, over the ≈ ⏣80 spare, plus 6–8 s the 90 s lacks. And it asks the wrong question: scene 3 is "will they trust each other?", not "will he come?", which S3-01 answers in its first second. Cross-cut when two lines race a clock to one moment.

## 7. Who Knows What — Suspense, Surprise, Reveal Order

**Surprise** is information the audience gets with a character; **suspense**, information it gets *before*. Hitchcock explained it to François Truffaut (interviews 1962; *Hitchcock/Truffaut*, 1966) with a bomb under a table: unknown, the blast buys "fifteen seconds of surprise"; shown in advance, the same small talk buys "fifteen minutes of suspense". Inform the audience whenever you can.

The order of S3-04 → S3-07 decides who knows what:

| Order | Audience knows | S3-06 (Kishan braced) plays as | Verdict |
| ----- | -------------- | ------------------------------ | ------- |
| **A**, the list: S3-04 · 05 · 06 · 07 | At 49 s — 13 s before *"Bas?"* | Gentle suspense: we wait for him to learn there's no fight | **Use.** The film argues that a record ends the argument: we read it, then watch it work |
| **B**: S3-05 · 06 · 04 · 07 | At 54 s, after "what did he see?" | Plain tension | The product becomes a punchline; the screen's reading time comes after the feeling |
| **C**: drop S3-04 | Never | Confusion | Fails product truth |

What you never tell is a choice too. The film never says whether the phone voice in S2-01 was right: the controlling idea is about a record nobody argues about, not who was wrong — so nobody is a villain.

## 8. Restructuring — the Same Shots at 60 and 30 Seconds

**Restructuring** changes the film's architecture in the edit: re-ordering beats, a cold open, dropping a shot you love, giving a line's job to a look. The 90-s list stays fixed; the 60 and the 30 are separate cuts of the same shots, each at its listed use.

**60 s — 23 shots kept, 9 dropped (−30 s):**

| Scene | Kept (use, s) | Dropped | Why it still reads |
| ----- | ------------- | ------- | ------------------ |
| 1 · 8 s | S1-01 (2) · S1-02 (4) · S1-03 (2) | S1-04, 05, 06 | **Ellipsis:** the buzzing phone cuts to the phone at his ear |
| 2 · 15 s | S2-01 (3) · S2-02 (3) · S2-04 (2) · S2-06 (2) · S2-07 (3) · S2-08 (2) | S2-03, 05 | **A line lost to a look:** S2-04's finger asks Ravi's question |
| 3 · 22 s | S3-01 (3) · S3-04 (4) · S3-05 (3) · S3-06 to S3-11 (2 each) | S3-02, 03 | The chime cuts the wide straight to the phone |
| 4 · 15 s | S4-01 (3) · S4-04 to S4-07 (3 each) | S4-02, 03 | Glass → horn → tanker → salute → bookend |

S1-04 and S2-03 are two of the eight Quality locks — ⏣200 on the floor. The coins are spent either way (a **sunk cost**); the only question is whether the film is better without them.

**30 s — 11 shots.** A **cold open** starts mid-story, on a moment strong enough to hook alone:

```
S2-07  3  "Register mein nahin hai."   ← cold open: the hook is a question
S2-08  2  Kishan walks out
S3-01  3  next dusk, the tanker returns
S3-04  4  the verified order — we read it
S3-05  3  Ravi reads, looks up
S3-07  2  he approves (keep the nozzle clunk; S3-08's picture goes)
S3-09  2  "Bas?"
S3-10  2  "Bas."
S3-11  2  release · 12-frame dissolve
S4-02  4  navy polo, registers stacked
S4-07  3  end card                                    = 30 s
```

Scene 1 goes — and S4-06 with it, because a bookend needs both ends — and so does S3-06, which shrinks §7's suspense to a beat.

**In Resolve:** **Edit > Duplicate Timeline**, renamed `saaf-hisaab-60_cut_v01`; select the dropped shots and press **Forward Delete** (fn-Delete on a MacBook) to ripple them out — plain Delete leaves gaps. **Command-Shift-drag** (a **Shuffle Insert**) swaps a clip past its neighbours: that is how S2-07 opens the 30.

## 9. The Fix Ladder — Cheapest First

[[15-continuity-bible-script-supervisor|File 15]] has a ladder for *generation* fixes. This is the **editor's** ladder: climb it in order on a duplicated timeline; stop at the first rung that passes on the phone. Rungs 1–8 cost 0 coins.

| # | Rung | Fixes — and its limit | Free Resolve: where |
| - | ---- | --------------------- | ------------------- |
| 1 | **Trim / slip** | A fault at the head or tail; a slip moves the use onto clean frames (file 17). Not a fault inside the frames you need | The trims |
| 2 | **Re-order** | A cut that fights its neighbour; a misplaced reveal. Cause, axis and eyelines must still hold | Shuffle Insert |
| 3 | **Cover** | A bad stretch inside a needed shot: an insert or reaction over it, its sound playing on. Too many read as patches | **Place On Top** (F12) → V2 |
| 4 | **Punch in / reframe** | A fault at the frame edge; a tighter frame. 110–120 % at most (§10); never a new shot size | Inspector › **Transform** › Zoom, Position; Resize Filter **Sharper** (the manual's pick for scaling up). Smart Reframe: Studio |
| 5 | **Retime** | A clip a few frames short; a speed mismatch at a cut on action. Never while someone speaks | **Change Clip Speed**; **Retime Controls** (Command-R); **Fit to Fill** (Shift-F11) stretches a source range to fill a timeline gap; Retime Process **Optical Flow**, Motion estimation **Enhanced Better**. Speed Warp: Studio |
| 6 | **Hold a frame** | An action a few frames short; a morph at the end. A frozen frame is dead (§10) | Retime Controls › **Freeze Frame**; **Clip › Freeze Frame** (Shift-R) freezes a whole clip |
| 7 | **Flip** | A reversed eyeline or direction. Mirrors text, hands, light and Flow's mark | Inspector › Transform › **Flip Image** |
| 8 | **Smooth Cut** | A small jump inside one static shot. Runs on "AI powered Speed Warp processing" (manual) | Treat as **Studio** (check live) |
| 9 | **One new shot** (⏣10–120) | Everything above failed; it must match both neighbours | Flow: Frames→Video from the board, same model and tier (§12). Background fix: Omni Flash **Edit & refine** (⏣40, ≤ 10 s) — draft first; it re-renders in another model's look |

Google Vids documents no speed, freeze or keyframe tools (check live): this is a Resolve ladder.

> **Flow's visible mark stays exactly as Flow made it.** Flow applies a visible watermark automatically for creators living in India (Flow Help). Punch-in, reframe and flip are composition and rescue tools — **never a way round the mark**. If a rescue would crop, cover, blur or mirror it, that rung is closed for that shot. Disclosure: [[20-colour-finishing-and-delivery]].

## 10. Limits in Numbers

These are the course's **working limits**; exercise 16.4 replaces them with yours.

**Punch-in.** AI Pro's biggest Flow file is the free **1080p** upscale — your timeline's exact size, and already an upscale. Resolve's Transform works from the clip's source pixels (manual, *Image Sizing*), so every percent above 100 enlarges:

```
zoom    real pixels shown   share of frame   limit
110 %   982 × 1745          83 %             faces stop here
120 %   900 × 1600          69 %             clean inserts and wides stop here
150 %   720 × 1280          44 %             never
```

Editors cutting HD treat 110 % as safe and 120 % as the edge for clean footage (§17). A punch-in trims edges but never makes a new shot: the 30° rule wants two sizes, the subject at least doubling ([[10-deep-dive-scene-continuity]] §5.4). No **Dynamic Zoom** creeps either: the film's four push-ins are designed ([[13-visual-language-composition-blocking-light]]); a fifth dilutes them.

**Retime.** At 24 fps a clip at S % shows 24 × S/100 real frames a second; Optical Flow invents the rest. The manual: smooth on linear motion, artefacts where moving elements cross or the camera moves unpredictably; practitioners add hands passing the lens.

```
speed   real / invented frames a second   limit
90 %    21.6 / 2.4                        almost anything silent
75 %    18 / 6                            the floor for hands and inserts
50 %    12 / 12                           linear motion only: steam, a tanker
                                          on a locked camera
```

Never retime while someone speaks: slowed speech sounds wrong, and normal-speed sound stops matching the lips. Speed points in Retime Controls **mute the clip's own audio** (manual), so lay the bed under it. Arithmetic: 2 s of action at 80 % lasts 2.5 s; a 12-frame hold makes it 3.

**Hold.** ≤ 6 frames on a silent face; ≤ 12 on a static insert or wide where nothing moves; never on steam, smoke, a moving vehicle or speech.

**Flip.** A flip mirrors text (register figures, the polo's logo, tanker lettering), hands (phone hand, watch wrist, Kishan's gamchha shoulder), sides (LOC-A's window is camera-right), light, screen direction (the tanker arrives right-to-left, leaves left-to-right) — and Flow's mark. Of the 31 generated shots, three pass the craft tests on paper: S1-03, S2-06 and S3-08, if no lettering shows. With the mark on every clip, your answer today is **0 of 31**. Flips are for unmarked footage: a real-camera cutaway, or the local second unit ([[../comfyui/09-google-flow-parity]]), whose realistic shots still carry the disclosure duties of [[20-colour-finishing-and-delivery]] §12.

## 11. The AI Rescue Kit — Fault by Fault

Each row climbs §9 for one fault. "Regenerate" means the fault sits in frames the story needs and no rung fixes it within ±6 frames — then write a pickup (§12).

| Fault | Symptom (where) | Editorial fix (rungs) | Regenerate when… |
| ----- | --------------- | --------------------- | ---------------- |
| **Face drifts** | Jaw or eyes change as the push-in lands (S3-05) | Slip to the frames before it (1); cut to the listener at the drift (3) | The drift is inside the action you need |
| **Hands melt** | Fingers merge on the page flip (S2-03) | Cut before the hand moves; the clean insert carries it (1, 3); crop an edge melt, ≤ 120 % (4) | The hand *is* the shot (S2-04, S3-07): ⏣20 at Fast |
| **Morphing prop** | The chai glass reshapes; the tanker grows a stripe | Trim to the stable stretch (1); cover (3); background props are noticed last (file 15) | A motif at its pay-off (S4-01); a background object may earn one Omni edit (⏣40) |
| **Dead eyes** | No blink, no focus (S2-05) | Use the frames where the eyes move (1); ≤ 2 s; a motivated look before it reads as thought (Kuleshov, file 17) | The eyes are the shot (S2-07): write in "blinks once, eyes drop to the register" |
| **Lip-sync miss** | The mouth slips on "…driver?" (S2-03) | Cut to the listener or insert on the bad syllables; the line runs under (3; file 10 §6.5) | The speaker must be seen (S2-07). Omni can't edit voices |
| **Extend seam wobble** | A shift at the join (not in this film) | Trim ~10 frames (file 10 §2.2); cover (3); bury its audio under a J-cut | Two re-extends fail: cut, or still-join (file 10 §3.2). Flow Help says only Lite extends; check the model and cost Flow shows |
| **Light jump** | Exposure or colour pops; one shot warmer | Trim around it (1); match in the grade (file 20); a 6-frame dissolve across light, never across a face | The pulse is in frames you need |
| **Soft clip** | One shot softer than its neighbours | Never punch in; keep it short; put it after movement; one texture in the grade (file 20) | A hero face: re-render on its neighbours' tier |
| **Action won't match** | Phone height or speed differs, S1-06 → S2-01 | Another frame (file 17); retime the faster clip 90–110 % (5); cut on a look; a cutaway (3) | Wrong hand or side — the flip is closed |
| **Ends too early** | The tanker stops 2 s into S3-01's 3 s | Start earlier (1); Fit to Fill or ≥ 80 % (5); hold ≤ 12 frames (6); pre-lap the next sound (file 19) | The action is unfinished: write the hold in (file 10 §9) |

## 12. The Pickup List

A **pickup** is a shot made after the main shoot to fill a hole the edit found. The editor writes it; the director makes it — Frames→Video from the board still, same model and tier as the shot it replaces ([[10-deep-dive-scene-continuity]] §3.2 fix 4). It names **the shot**, **the failed frames**, **what the take must do** and **what it must match**:

```
PICKUP LIST · saaf-hisaab_cut_v06 · editor → director · edit-week daily credits

P1  S3-07 · Insert ECU · static · use 2 s · 00:00:58:00–00:01:00:00
Fault  right thumb melts into the glass on the tap, 00:00:58:14–58:20
Tried  slip (every take melts) · punch-in (melt is mid-frame) ·
       cover (needs more than 6 frames of S3-06)
Need   one clean tap and lift; phone still; nothing else moves; 4 s clip (14 §7)
Match  PU1_S3-06_out.png · PU1_S3-08_in.png · right thumb · teal case ·
       screen glow on the thumb (state table, file 15)
Make   Frames→Video from S3-07_board_v1 · 2 Lite drafts → 1 Fast lock
Coins  ⏣40
```

Export the match frames with **File > Export > Current Frame as Still**, parked on the last used frame before the shot and the first after. If an action's *timing* is the doubt, rehearse it on Omni Flash at 360p first (⏣4–7) — timing only, never the look.

Price the list before you send it:

```
P1  S3-07  thumb melts on the product's own moment       Lite ×2 → Fast      ⏣40
P2  S4-04  FAULT: the take drives right-to-left, so      Lite ×2 → Fast      ⏣40
           it reads as arriving. NEED: the tanker
           leaving left-to-right. The flip is closed
P3  S3-05  face drifts in the 4 frames left after        Lite ×2 → Quality   ⏣120
           the allowed trim
TOTAL ⏣200 · not the spare: P1 + P2 from daily credits, P3 from monthly
```

Rank story errors first, then what audiences notice (faces, then hands — file 15). P2 breaks the story and P1 is the product's moment, so they go first. **Pickups are not paid from the ⏣80 spare**, which [[14-previs-storyboard-floorplan-animatic]] §9 allocates: they are made in the edit weeks, after the twenty generation days, from those days' 50 daily credits — P1 + P2 take about two days. P3 is a Quality pickup and needs monthly credits (the next cycle's), or the decision to keep S3-05's Fast render. It waits for the screening: if nobody notices four frames, drop it; if anyone does, it leads next month's plan ([[21-long-form-multi-scene-production]] §7).

## 13. Test Screenings

A **test screening** shows an unfinished cut to fresh eyes, to learn what it does to a stranger. You can't screen for yourself: you know too much.

- **Three to five viewers, one at a time:** one from the audience (a pump dealer, or the colleague who sells to dealers), one who has never heard of DZZLO, nobody who saw the boards.
- **On a phone, full screen, sound on** (Meta: Reels default to sound on), then once muted. Say only: "It's ninety seconds; I'll ask questions after."
- **Watch the viewer, not the film.** Note the timecode where eyes leave the phone, or a frown or laugh arrives; mark it later (**M**; **Command-M** adds a note). Edit Index → **Show Markers** → **Export Edit Index** makes the notes a .csv.

Ask in order — never "did you like it?": (1) "What happened?" — listen for *because*; a string of "and then"s means the causal chain broke ([[12-story-engine-seamless-storytelling]]). (2) "Who was it about, and what did he want?" (3) "What did the phone do?" (4) "Where did you get lost, or bored?" (5) "Which picture do you remember?" (6) "What would you do next?"

**A note names a symptom, rarely the cause.** Neil Gaiman's advice to writers fits editors: when people say something is wrong, they are almost always right; when they say how to fix it, they are almost always wrong (paraphrased).

- *"The start is slow."* — no question in the first 3 s, and the first line comes at 18 s. Look at S1-01's hook and the 60-s cut's scene 1.
- *"Why did the driver leave?"* — his deadline isn't heard. Look at S2-02's mix (file 19).
- *"What did the app do?"* — the screen is unreadable, or comes after the feeling. Look at S3-04's composite (file 20) and the §7 order.
- *"Was that the next day?"* — one cue too few at D1 → D2. Look at S3-01's dusk light and Ravi's new shirt (§4).

One viewer is a possibility; two is a fact. Fix the cause, then screen again with new eyes.

## 14. Picture Lock and Turnover

**Picture lock** is the point after which no shot changes order, length or content: 00:01:30:00, 2,160 frames at 24 fps, every cut on a known frame. **Turnover** hands the locked film to sound and colour, and both need the lock. **Sound** (file 19) places every effect, room-tone fill, split edit and music cut to the frame — a 4-frame trim at 20 s moves everything after it. **Colour** (file 20) matches each shot to its neighbours — a re-order changes the neighbours, a pickup arrives ungraded, a punch-in changes softness.

Alone, turnover is you handing the film to yourself — exactly when discipline slips. [[21-long-form-multi-scene-production]] owns the gates; this is the editor's list:

```
[ ] Screening notes closed, or parked by name; pickups cut in or dropped
[ ] 00:01:30:00 · 32 shots · 2 visible transitions
[ ] Edit > Duplicate Timeline → saaf-hisaab_lock_v01 · Lock Track on video tracks
[ ] Rescue audit: Edit Index → Show Clips With Speed Effects / Transform
    Effects / Stills and Freeze Frames → Export Edit Index → to colour
[ ] Handles ≥ 24 frames (Source In − Source Start, Source End − Source Out)
    wherever a dissolve or a split edit sits
[ ] Reference movie: Workspace > Data Burn-In (timecode + clip name, clear
    of Flow's mark) → render 1080 × 1920 H.264
[ ] Timeline exported (Shift-Command-O, .drt) · Export Project Archive
[ ] Change log: what changed since the last cut, in frames
```

## 15. What Still Can't Be Fixed

- **No rescue creates frames that were never generated** — a missing look, a dead performance, an unsaid line.
- **A lip-sync miss on a face you must see.** Free Resolve has no lip-sync repair; Google says Omni can't edit voices.
- **No punch-in headroom on AI Pro.** 1080p is the ceiling.
- **Studio-only rescues:** Speed Warp, Smooth Cut (treat as Studio: it runs on Speed Warp; check live), Frame Replace, Deflicker, Motion Deblur, Smart Reframe, SuperScale and the Beat Detector.
- **The mark** closes some rungs on some shots.
- **Restructuring can't invent a cause.** If viewers can't say why Kishan comes back, that is a story fix ([[12-story-engine-seamless-storytelling]]), not a re-order.

## 16. Exercises

**16.1 — Your tempo map (0 coins).** Draw the §2 map from your cut's exported Edit Index; mark the peak, the hold and the breath. Artefact: `tempo-map_cut_vNN.txt`.

**16.2 — The 60 and the 30 (0 coins).** Do §8 on paper, then on duplicated timelines; watch both beside the 90. Artefact: two timelines and a "what we lost" list.

**16.3 — Suspense or surprise (0 coins).** Cut S3-04 → S3-07 in orders A and B; show each to a different person; ask only "What did the phone do?" Artefact: two answers, your verdict.

**16.4 — Your limits (0 coins).** Punch a face to 105–120 % and an insert to 130 %; retime a hand shot to 90, 75 and 50 % (Optical Flow, Enhanced Better); judge on the phone at arm's length. Artefact: your own §10 tables.

**16.5 — Climb the ladder (0 coins).** Climb §9 with your three worst clips on a duplicated timeline, stopping at the first rung that passes. Artefact: a rescue log — clip, fault, rung, minutes.

**16.6 — One pickup (0 coins to write; ⏣40–120 to make).** For the fault the ladder couldn't fix: the §12 template, the frame pair, the price against your month. Artefact: `pickups_cut_vNN.md` and two stills.

**16.7 — Screen it, then lock it (0 coins).** Three viewers, six questions, symptom → cause, then the §14 checklist. Artefact: `saaf-hisaab_lock_v01`, the burn-in reference and the rescue-audit .csv.

## 17. Sources (web-verified 2026-10-01)

Primary — tools:

- [DaVinci Resolve 21 Reference Manual — Blackmagic, July 2026](https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_21_Reference_Manual.pdf) — speed effects, Inspector, Edit Index, Smooth Cut, image sizing, Data Burn-In
- [Resolve 21.1 Studio and iPad Features — Blackmagic](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_Studio_21_Features.pdf) — the Studio-only list
- Flow Help: [Credits](https://support.google.com/flow/answer/16526234) · [Edit & build scenes](https://support.google.com/flow/answer/16935718) · [Models & features](https://support.google.com/flow/answer/16352836) · [Get started / FAQ](https://support.google.com/flow/answer/16353333) (visible watermark)
- [Introducing Gemini Omni — The Keyword](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-omni/) · [Gemini API — Omni](https://ai.google.dev/gemini-api/docs/omni) (no voice editing)
- [Reels ads — Meta](https://www.facebook.com/business/ads/facebook-instagram-reels-ads) (sound on by default)

Craft:

- [Hitchcock/Truffaut — Wikipedia](https://en.wikipedia.org/wiki/Hitchcock/Truffaut) · [The bomb under the table — Alec Nevala-Lee](https://nevalalee.wordpress.com/2011/10/26/the-bomb-under-the-table/)
- [Soviet montage theory — Wikipedia](https://en.wikipedia.org/wiki/Soviet_montage_theory) · [Glossary of Film Terms — University of West Georgia](https://www.westga.edu/academics/university-college/writing/glossary_of_film_terms.php)
- [Ellipsis (narrative device) — Wikipedia](https://en.wikipedia.org/wiki/Ellipsis_(narrative_device)) · [Cross-cutting — Wikipedia](https://en.wikipedia.org/wiki/Cross-cutting)
- [Enter late, exit early — Go Into The Story](https://gointothestory.blcklst.com/screenwriting-mantra-enter-late-exit-early-5b06e1e70bf3) · [Start late, leave early — No Film School](https://nofilmschool.com/start-late-leave-early)
- [Larry Jordan on montage to music — No Film School](https://nofilmschool.com/2014/09/larry-jordan-teaches-us-how-create-video-montage-set-music) · [Beat-sync editing — Bitcut](https://bitcut.app/blog/beat-sync-video-editing) · [BPM and picture — Tools for Film](https://www.toolsforfilm.com/blog/bpm-and-picture-editors-guide)
- [Zoom limits — Creative COW](https://creativecow.net/forums/thread/how-much-can-you-zoom-in-on-4k-footage-in-a-1080p/) · [DVXuser](https://www.dvxuser.com/threads/a7s-ii-how-far-can-i-zoom-in-with-4k-on-1080p-time-line.348946/)
- [Repairing bad optical-flow retimes — ProVideo Coalition](https://www.provideocoalition.com/slow-mo-blues-fixing-bad-optical-flow-retimes/)
- [Picture lock — Wikipedia](https://en.wikipedia.org/wiki/Picture_lock) · [Feature Turnover Guide — Evan Schiff, ACE](https://www.evanschiff.com/articles/feature-turnover-guide-part-1/)
- [Neil Gaiman's rules of writing — The Marginalian](https://www.themarginalian.org/2012/09/28/neil-gaiman-8-rules-of-writing/)

---

**Previous:** [[17-editing-1-workflow-and-the-cut]] · **Next:** [[19-sound-edit-design-and-mix]] · **Track map:** [[11-directors-track-roadmap]] · **Back to:** [[00_README]]
