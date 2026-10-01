# Editing 1 — Workflow and the Cut: Turning Ninety Clips into One Film

> Level: Beginner → Intermediate | Hat: Editor | Time: ~3 hr, plus one night's distance | Secures: Perceptual + emotional, at each cut | Outcome: you set up DaVinci Resolve (free) for 9:16 at 24 fps, log a Flow shoot, take a scene from selects to picture lock with three-point edits and the four trims, find the cut frame, cut first dialogue and review like an editor — worked frame by frame on scene 1 of *Saaf Hisaab*. | Status: written & web-verified **2026-10-01** against the DaVinci Resolve 21 Reference Manual (21.1 is current), Blackmagic's Studio and codec lists, Flow and Vids Help, and the BBC subtitle guidelines. Sources in §16.

---

## Explain-it-like-I'm-5

The robot crew has finished shooting. On your desk sit about ninety little boxes of film, each four to eight seconds long. In every box the good part is in the middle: in the first second the crew is still getting into position; in the last they hold still, waiting for someone to shout "cut". No crew ever saw any box but its own.

You are the first person who will watch them all. Your job is to open every box, keep the two to four seconds that matter, and glue them together so nobody can see the glue — until thirty-one strangers' work looks like one camera, one night, one man's bad evening turning into a good morning. That is editing: the last rewrite of the film, done by its first audience.

## 1. The One Idea — The Footage Is Not the Film

**Editing** is deciding which frames the audience sees, in what order, for how long. The editor wears two hats: the **last writer** (shot order and length are the story's final draft) and the **first audience** (the first person to feel it play). One asks "what does this cut say?"; the other, "did I feel anything?"

The footage is not the film. *Saaf Hisaab* leaves about 90 clips on disk — ~50 Lite drafts, 31 Fast renders, 8 Quality locks — for 87 seconds of generated picture. Even of the 31 chosen takes, more than half is never seen (87 s used of 190 s). That is not waste; it is the cut's raw material ([[10-deep-dive-scene-continuity]] §5.5, "harvest, don't use").

In Flow you are also the only one who has seen every clip. Of the track's four continuities ([[11-directors-track-roadmap]]), this file secures two **at each cut** — **perceptual** (nobody sees the join) and **emotional** (the feeling runs across it) — after generation, before sound ([[19-sound-edit-design-and-mix]]) and colour ([[20-colour-finishing-and-delivery]]). Re-ordering the story is [[18-editing-2-rhythm-structure-and-rescue]].

```
Lite pass ──► DAILIES ──► SELECTS ──► ASSEMBLY ──► ROUGH CUT
 (drafts)        §3          §5          §5           §5
                                                       │
        locks rendered for the shots the rough cut kept ◄┘ (Fast / Quality)
                              │
                              ▼
           FINE CUT ──► PICTURE LOCK ──► sound (19) · colour & delivery (20)
           §5, §7–§11       §5
```

## 2. Set Up Once — Resolve (Free) for 9:16 at 24 fps, and the Vids Route

### 2.1 The project

DaVinci Resolve 21.1 (September 2026) is current; its free edition does everything here. Create a project named `saaf-hisaab` and set these rows **before importing anything**: once files are in the **Media Pool** (Resolve's clip library), the manual says the timeline frame rate "cannot be changed".

| Where | Setting | Value | Why |
| --- | --- | --- | --- |
| Project Settings (gear button, bottom right; Shift-9) → Master Settings | Timeline resolution | `1920 x 1080 HD`, then tick **Use vertical resolution** → 1080 × 1920 | The delivery size; encoding ≥ 4K needs Studio (Blackmagic's codec list, §16) |
| same | Timeline frame rate · Playback frame rate | **24** · 24 | Veo renders at 24 fps — not 23.976 |
| Image Scaling → Input Scaling | Mismatched resolution files | `Scale entire image to fit` (default) | A 720 × 1280 download still fills the frame |
| Color Management | Color science | `DaVinci YRGB` (default) — leave it | Grading is [[20-colour-finishing-and-delivery]]'s |
| Preferences (Command-Comma) → System → General | Use Mac Display Color Profile for viewers | On | The viewer matches your Mac's screen |
| Preferences → User → Editing | Pre-roll time · Post-roll time | 2 s · 2 s (our choice) | **/** then plays every cut in context |
| macOS System Settings → Keyboard → Keyboard Shortcuts → Function Keys | Use F1, F2, etc. keys as standard function keys | On (or hold **Fn**) | Resolve's edit keys are F9–F12, which a Mac otherwise uses for system jobs |

Save it once: Project Settings → option menu (three dots, top right) → **Save Current Settings as Preset** → `DZZLO 9:16 24p`, then pick it → **Set As Default Preset**. If Resolve offers to change the frame rate on your first import, something is not 24 fps (often a phone screen recording — file 20's): choose **Don't Change** and find it.

Cut on the **Edit page**: the **Source Viewer** (left) plays a clip, the **Timeline Viewer** (right) plays the edit. Make timelines with **File → New Timeline** (Command-N) after selecting your `00_timelines` bin (§3.1); new timelines land in the selected bin.

### 2.2 The Vids route, and where it stops

Google Vids is a scene-based editor: 9:16, trim handles, Split scene at playhead, transitions with a duration slider, audio tracks that span scenes, automatic ducking, unlimited Hindi voice-over on AI Pro ([[11-directors-track-roadmap]] §8).

**Use Vids** for a 15–30 s cut-down of up to eight clips, straight cuts, music or voice-over: video size 9:16, one clip per scene, drag the blue handles to trim, music and voice-over on audio tracks across scenes, a **Transition** between scenes (it overlaps them), **Download as MP4**. **It stops** where this film starts: Google documents no way to detach a clip's own sound (no true J/L cut of dialogue — run voice-over or music across), and no speed, keyframes or grade ([[11-directors-track-roadmap]] §8); trims are per clip, by handles or start/end times, with no documented roll or slide. *Saaf Hisaab* is a Resolve job. Flow's **Scenebuilder** (arrange, trim heads and tails, preview, download) is for watching drafts in order, not cutting.

## 3. Ingest, Organise, and Watch Dailies

### 3.1 Ingest — names first, then bins

Resolve links to your files where they sit; they "are not moved, copied, or otherwise transcoded". So rename and file every download **before** import, in the track's naming (shot + take number + tier letter):

```
DZZLO-films/saaf-hisaab/      (file 21 §4)
  04_stills/boards/   S1-01_board_v1.png …            (file 14)
  05_takes/
    S1/         S1-01_t01_L.mp4  S1-01_t02_F.mp4 … S1-04_t04_Q.mp4
    S2/  S3/  S4/
  06_real/      (file 20: app recordings)    07_audio/   (file 19)
  08_edit/      saaf-hisaab_cut_v04_review.mp4 …
```

Import the takes as bins: **Media** page → Media Storage → right-click `05_takes` → **Add Folder and SubFolders into Media Pool (Create Bins)**. Bins S1–S4 appear, one per scene, inside a `05_takes` bin. Right-click the bin list → **Add Bin** for `00_timelines`, `01_boards`, `03_sound`, `04_graphics` (bin numbers only set Resolve's sort order; they don't mirror the disk folders).

Log every take in **Inspector → File**: **Scene**, **Shot**, **Take**; tick **Good Take** (Resolve: "a good or circled take" — your *print*); **Clip Color** Orange for *hold*, Chocolate for *no good* (the 16 colours run Orange to Chocolate); one line of **Comments** saying why. **Auto Select Next Unsorted Clip** loads the next clip when you press Return. These mirror the take log in [[15-continuity-bible-script-supervisor]].

### 3.2 Dailies — twice, differently

**Dailies** (in India, *rushes*) are the raw takes, watched as they arrive so faults are caught while a re-shoot is still cheap — in Flow, before the next session's coins go.

**Pass 1 — once through, no stopping.** Workspace → Viewer Mode → **Cinema Viewer** (Command-F); play each take once, no rewinding, and write your first reaction — even a nonsense word. Walter Murch notes anything that will help him recognise a shot months later ("banana" is his example): there is only one first time, and it is the closest you get to the audience's feeling (Hullfish, *Art of the Cut*, 2020).

**Pass 2 — with the tools.** In the Source Viewer, **J K L** play reverse / stop / forward; **K** + tap **J** or **L** (or the arrow keys) moves one frame. **M** marks a fault (Command-M, or M twice, pauses for a note, then plays on). **I** and **O** mark the usable window (§4); Resolve saves each clip's In and Out, so your selects build themselves later. Murch also warns that a bare "good" or "no good" is useless: a shot's value changes as the story does. Write *why*.

Times are `s:ff` — seconds and frames at 24 fps, so `1:12` is frame 36.

```
DAILIES — saaf-hisaab — LOC-A night — Lite pass
take         | pass-1 reaction       | window    | action / line frames    | verdict | why
S1-04_t01_L  | rubs like a cartoon   | —         | —                       | NG      | over-acts; rubs twice
S1-04_t02_L  | tired, real ("ash")   | 1:10–5:20 | glance 3:02; hand 5:05  | PRINT   | watch reads; push settles 6:12
S1-05_t01_L  | finger melts at 4:18  | 1:00–4:17 | 2nd circle closes 4:10  | HOLD    | clean before 4:18
```

The **action / line frames** column is the one beginners skip and editors live on: where each shot's **Out** ([[10-deep-dive-scene-continuity]] §5.7) begins, where each line starts and ends, where a blink falls. Continuity faults go to file 15's continuity report.

## 4. The Usable Window — Why a Clip Is Cut From Its Middle

Ask Flow for the length [[14-previs-storyboard-floorplan-animatic]] §7 plans: 4, 6 or 8 s. Veo's price per output is the same at all three (Omni prices by length — [[11-directors-track-roadmap]] §8), so a single-board shot loses nothing by going long; a two-board shot (first + last frame) must not, because its motion is spread over the whole clip. The seconds beyond the cut are free **handles** — frames kept so the cut can still move.

```
8-second Veo clip = 192 frames (0–191) at 24 fps
0:00        1:00                                        7:00        7:23
 |----------|-------------- usable window --------------|-----------|
 board still  the one action, the line, the Out           the hold,
 waking up    — every cut point lives here                the landing
 = head handle                                            = tail handle
```

| Why the ends are weak | What it means for the cut |
| --- | --- |
| A Frames→Video clip starts **on** its board still: frame 0 is a photograph, moving at zero speed | No cutting into motion on frame 0; for a cut on action, B's In comes once its movement is up to speed (§8.1) |
| The prompt ends the shot on its Out, then **holds** ([[10-deep-dive-scene-continuity]] §5.7, §9) | The hold is a handle, not a shot |
| The model fills the whole clip; with too short a line, practitioners report awkward silence or invented words (Replicate, on Veo 3) | Keep the line and its reaction; leave the filler outside ([[16-directing-performance-and-dialogue-scenes]] times a line inside 8 s) |
| Trims and transitions eat handles: Resolve's default handle is one second, and a transition needs "overlapping handles" on both clips | The 12-frame dissolve S3-11 → S4-01, centred, needs 6 unused frames past the cut in each clip. If Resolve offers **Trim Clips** when you add it, the handles are short: **Cancel**, then slip A earlier or B later (§7) |

Plan every shot's use inside its window, the clip minus its first and last second: **1:00–7:00** in 8 s, 1:00–5:00 in 6 s, 1:00–3:00 in 4 s. Check it on your clips (exercise 15.3).

## 5. Selects → Assembly → Rough → Fine → Picture Lock

**Selects** are the circled takes with In and Out marked on their usable windows. A **string-out** (Resolve: *stringout*) is all of them end to end in shot order, to watch in one go. Then come four stages. Each forbids the next stage's work, because polishing a shot you may drop wastes hours — and in Flow, coins.

| Stage | Built from | Decide here | Forbidden here | Timeline |
| --- | --- | --- | --- | --- |
| **String-out** | circled Lite takes | Which take per shot; what is missing (→ a re-shoot note) | Judging pace; trimming | `saaf-hisaab_selects_v01` |
| **Assembly** | selects, trimmed toward planned lengths | Does the whole film exist, in order, without gaps? Runtime against 90 s | Frame trims, music, colour, effects, captions | `saaf-hisaab_cut_v01` |
| **Rough cut** | the assembly | A motive for every cut; order (with file 18); which shots stay; lengths to ±12 frames; listener or speaker per line; which locks to render | A lock for a shot that may go; colour; the mix | `_cut_v02`, `_cut_v03` |
| **Fine cut** | the rough, locks swapped in | The exact frame of every cut and hold (§7–§8); where sound leads (file 19) | Restructuring; new shots without a pickup decision (file 18) | `_cut_v04` … |
| **Picture lock** | the fine cut | Nothing — order and length are frozen | Any change of duration: sound and colour are built on it | `_lock_v01` |

Lock discipline and the turnover checklist are file 18's.

**String-out in Resolve.** In the S1 bin, switch the Media Pool to List view and sort by Clip Name. Select the circled takes → right-click → **Create Timeline Using Selected Clips** → tick **Use Selected Mark In/Out** → name it. Each clip arrives cut to its dailies window.

**Assembly.** Duplicate the string-out and ripple each head and tail (§7) toward the shot list's "Use" length. Or duplicate your animatic ([[14-previs-storyboard-floorplan-animatic]]) and swap each board for its select with a **Replace** edit (§6), which keeps the replaced clip's length — the assembly inherits the planned timing.

**Draft → lock.** A Fast or Quality lock is a new generation; its action won't land on the draft's frame. The rough cut tells you which locks are worth their coins — where the schedule allows, render locks only for shots it kept ([[21-long-form-multi-scene-production]] sets the gates). To swap one in, park the timeline on a key frame of the draft (S1-04: his eyes opening after the rub), park the Source Viewer on the same moment in the lock, press **F11** (Replace): the lock drops in at the draft's length, aligned on that frame.

## 6. Three-Point Editing — the Source/Timeline Habit

**Three-point editing** puts part of a source clip at a chosen place in the timeline: set any three of source In, source Out, timeline In and timeline Out, and Resolve works out the fourth. The habit: **the source says *what*, the timeline says *where*, the key says *how*.** Mark the source, press **Q** to switch to the timeline, mark it, then edit.

| You know… | Mark these three | Then | Example |
| --- | --- | --- | --- |
| Where the shot starts and ends, and where it goes | Source In + Out; the timeline playhead acts as In | **F10** Overwrite | S1-02 at film time 2:00 |
| The exact **last** frame (the Out action) and the slot | Source Out + timeline In + Out | **F10** — Resolve *backtimes* the clip so its Out lands on the timeline Out | S1-01, below |
| One moment must land on another | both playheads, no marks | **F11** Replace | draft → lock, §5 |
| A gap to fill from a chosen first frame | Source In + timeline In + Out | **F10** | any 2 s insert |

**F9** inserts and pushes everything after it along; **F10** overwrites; **Shift-F12** appends; **Option-X** clears In and Out. Every edit also has a toolbar button and a drag-on overlay in the Timeline Viewer.

**Backtiming S1-01.** A cut on action is defined by its Out, so mark that first: in the source, park on 2:23, five frames after the hand starts to lift, and press **O**. In the timeline, mark In on the film's first frame and Out on frame 47 (a 2 s slot). F10: Resolve counts back 48 frames and uses 1:00–2:23, the 4 s clip's whole window, so the lift lands exactly on the cut.

## 7. The Four Trims — Ripple, Roll, Slip, Slide

A **trim** changes an existing edit — half the job of editing, says the Resolve manual. Four trims move four different things:

```
                 A        |        B        |        C
RIPPLE   A's end moves; B, C and everything after shift     → film length CHANGES
ROLL     the cut between A and B moves; A + B stays the same → length same
SLIP     B stays put; which frames show inside B change      → length same
SLIDE    B moves; A and C give or take frames                → length same
```

| Trim | Fixes, on AI clips | Scene 1 example | Resolve (Edit page) |
| --- | --- | --- | --- |
| **Ripple** | Length: a board still waking up at the head, a slack pause after a line, a gesture that never ends | In the string-out S1-04 runs its whole 6 s window; ripple head and tail toward its 4 s, and everything after moves up | **T** (Trim mode); **V** selects the nearest edit; **U** picks its outgoing or incoming side; **,** / **.** one frame — or drag one side of the edit |
| **Roll** | The cut lands a few frames early or late in an action or a look | S1-05 → S1-06: roll 3 frames later so the second circle closes before the cut | **V** (centre of the edit), **,** / **.** — or drag the edit, in Selection mode (**A**) too |
| **Slip** | The slot is right but shows the wrong 2 seconds: a melting finger, the action late in the take | S1-05: slip 10 frames later so both pen circles show | **Shift-V** selects the clip; **S** toggles Slip / Slide; **,** / **.** — or drag the clip's top middle in Trim mode |
| **Slide** | An insert lands early or late against its sound or line | S1-03: slide 6 frames later so the phone appears 18 frames after its buzz begins (file 19's J-cut: the sound arrives before its picture) | **Shift-V**, **S** to Slide, **,** / **.** — or drag the clip's bottom name bar in Trim mode |

**Worked run — the S1-05 | S1-06 roll (§12, step 5).** Park the playhead near that cut and press **V**: the whole edit is selected, so it rolls. Tap **.** three times, watching the 2-up, then press **/** to play around it. Command-Z undoes it.

Three habits:

- **Watch the frame pair.** **Shift-,** / **Shift-.** nudge 5 frames. While you trim, Resolve shows a 2-up (ripple, roll) or 4-up (slip, slide) of the frames either side of the cut — a live [[15-continuity-bible-script-supervisor]] frame-pair check. Double-click an edit for the larger **Precision Trim Editor**.
- **Trim in a loop.** Select the edit (**V**), turn on looping (**Command-/**), press **/** to play around it, and tap **,** or **.** as it plays; each nudge replays the loop. This is how editors find a frame by feel.
- **Ripple early, roll late.** The manual warns that ripple can alter sync across a timeline. Ripple freely in the assembly and rough; once music and sound are laid (file 19), use roll, slip and slide, which leave the rest in place. **Option-U** trims an edit's picture or sound alone — the start of the J- and L-cuts [[19-sound-edit-design-and-mix]] builds.

## 8. Finding the Cut Frame

A cut hides best where attention is busy elsewhere. In an eye-tracking study, viewers told to *look for* cuts still missed a third of those that coincided with "a sudden onset of motion" (32.4 %), a quarter of other cuts inside a scene (25.1 %), and under a tenth of cuts between scenes (9.4 %) (Smith & Henderson, 2008).

### 8.1 Cut on action

1. **How far in.** Let the movement start in A and run **3–6 frames** — enough for the eye to catch the onset — then cut (a starting point, not a law). S1-01: the lift starts at 2:18; the cut is at 2:23.
2. **Overlap or drop.** B's first frame should continue A's last; the movement is the bridge the eye follows across the cut. Loop three versions: exact; B **two frames later** (drops a sliver of action); B **two frames earlier** (repeats a sliver). If the move jumps ahead, overlap a frame or two; if it stutters, drop. Keep the version where you cannot find the cut.
3. **Match direction, hand and speed — not pixels.** Two separately generated clips never match exactly. Keep the direction (both rising), the hand (the phone lives in his right) and the **speed**: step both moves with the arrow keys and count frames over the same distance. A Frames→Video clip begins at rest, so set B's In where its movement has reached A's speed: 6–12 frames into the movement, never before 1:00. A board drawn mid-move (S1-02's rising hand) is up to speed by then; a move that starts later needs its 6–12 frames inside the window.

S1-06 → S2-01 is the film's hardest test. [[14-previs-storyboard-floorplan-animatic]] §4.5 boards it as one instant from two set-ups — S1-06 ends as the phone reaches his right ear, S2-01 opens there from camera 2′ — so the cut lands on A's arrival frame. B starts on its board, at rest, so A's phone must be slowing into the ear, not still flying; if it isn't, take A's Out a frame or two later.

### 8.2 Cut on a look

Hold A until the look has **landed** — the eyes stop, then 4–8 frames more as a starting point — and cut to what is seen, from his side of the line ([[10-deep-dive-scene-continuity]] §5.4). A cut made while the eyes still travel arrives before the audience knows where to look. S2-05 → S2-06: Kishan glances back, his eyes settle, and the cut finds his tanker idling under the canopy. The same study warns: look-cuts were missed about as rarely as scene changes (10.9 %). A look tells the story; it will not hide a seam — for that, cut on action.

### 8.3 Cut at the end of a thought

Cutting *The Conversation*, Walter Murch noticed that the frames he chose to cut on kept coinciding with Gene Hackman's blinks. His reading: a blink marks the end of a thought, or the turn to a new one, and a cut is the film's blink (Radiolab, "Blink"; Lahr, *LRB*, 2025). Find the frame where the face finishes thinking — a blink, the eyes dropping, a breath out — and cut on it or just before. A Veo blink inside the usable window is a ready-made cut point; one mid-line is not. S2-07 → S2-08: after *"Register mein nahin hai."* hold until his eyes drop to the register, then cut on Kishan's turn. When the emotional cut and the tidy cut disagree, take the emotional one ([[10-deep-dive-scene-continuity]] §5.6).

## 9. Meaning From Juxtaposition — the Kuleshov Effect

In the 1910s and 1920s Lev Kuleshov is said to have intercut one expressionless close-up of the actor Ivan Mozzhukhin with a bowl of soup, a girl in a coffin and a woman on a divan; audiences saw hunger, grief and desire in a face that never changed. No copy is known to survive. A 1992 recreation did not find the effect; an fMRI study (2006) and a 2016 study found neutral faces read in the direction of their context. That is the **Kuleshov effect**: a shot means what the shots around it make it mean.

What it fixes for free:

- **A take that plays too big** ([[16-directing-performance-and-dialogue-scenes]]). Pick the calmer take and let the neighbour carry the feeling. S1-03 → S1-04: after the buzzing phone creeps toward the cold chai, Ravi's tired, neutral face reads as dread — no take where he *acts* dread needed.
- **A blank listening single.** S2-05 → S2-06: Kishan's waiting face, then his tanker idling — the audience supplies "my load, my time". Log every neutral second in dailies; it is the most reusable frame you own.

It also adds meanings you didn't ask for: Ravi's small smile cut straight after the empty register reads as smug. Judge every face against its neighbours, never alone.

## 10. Shot Length Is Reading Time

A shot ends when the audience has read it. Film teachers call the time a shot takes to register its **content curve**: a child's smile reads almost at once; a frame with several planes and text takes far longer (Sharman, *Moving Pictures*). [[10-deep-dive-scene-continuity]] §6.4 gives the pacing bands; this table places a shot inside them.

| The viewer must take in… | Starting length | In *Saaf Hisaab* |
| --- | --- | --- |
| A new place, first time: where, who, what's wrong | 3–4 s | S1-02 4 s · S3-01 3 s |
| A place seen before | 2–3 s | S2-08 2 s · S4-06 3 s (the ending earns its third second) |
| A face making one change of thought | 2–4 s — as long as the thought | S1-04 4 s · S3-06 2 s |
| A face speaking | the line + about half a second | S2-03 4 s · S3-09 2 s |
| An object, one fact | about 2 s | S1-01 · S1-03 · S2-04 · S3-07 · S3-08 |
| Words to read | words ÷ 3 a second, + 1 s to find them | S3-04 4 s: the four ticks need ~2.5 s; the turn of the film earns the rest |

Three words a second is the BBC's subtitle pace of 160–180 words a minute (BBC subtitle guidelines, §16). **Hold a beat** — in this course, at least 12 frames — where the audience must feel rather than read: after the peak line at S2-07, after *"Bas."* at S3-10. **Leave** when the information is used up ([[10-deep-dive-scene-continuity]] §5.6), before the shot goes stale — with AI clips, every extra second is another chance to drift.

## 11. First Rules for Cutting Dialogue

Six spoken moments; the full dialogue edit is files 18 and 19's. The first rules:

1. **Picture and sound are two cuts.** A line can run on over the listener (L-cut), or the next line can arrive before its face (J-cut). **Option-U** trims one without the other; [[19-sound-edit-design-and-mix]] builds both.
2. **Prefer the listener when a line's weight is in how it lands.** As Videomaker's Sean Berry puts it, a line's true impact is sometimes in the person hearing it. S2-01 is built this way: *"Payment ho gaya tha, Ravi ji!"* is an off-screen voice, and the shot is Ravi's jaw tightening.
3. **Show the speaker when the line reveals the speaker.** *"Register mein nahin hai."* is Ravi's own admission, so it plays on his face, in the film's tightest shot (S2-07).
4. **Never cut on a silence with no thought in it.** The pause before S2-07's line — he lowers the phone, looks at the register — is a thought; keep it. The half-second after a Veo line where the face goes slack is not; cut it.
5. **Cut the model's filler.** A one-word line like *"Bas?"* (S3-09) leaves the model 8 seconds to fill. Take the word and its reaction; if filler runs into the line's end, cut to the listener.
6. **Cut between words, never inside one — and check sync on p, b and m**, the **bilabial** sounds, made with both lips closed. On *"Bas."* the lips must be shut on the frame where the *b* starts, or the one before. If a word misses, cover it with the listener ([[10-deep-dive-scene-continuity]] §6.5, rule 6).

## 12. Worked Example — Scene 1, Step by Step

Scene 1: six shots, 18 s, 432 frames, no dialogue. Source times are inside each take, at its 14 §7 length; film time counts from the film's first frame.

| # | Shot | Take | Source in → out | Frames | Film time | Cut into next | Why |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | S1-01 ECU pen | `S1-01_t02_F` | 1:00 → 2:23 | 48 | 0:00–1:23 | On action: the hand lifts | Backtimed (§6); smudge reads by 1:14; lift starts 2:18, cut 5 frames in |
| 2 | S1-02 WS, bookend | `S1-02_t02_F` | 1:00 → 4:23 | 96 | 2:00–5:23 | J-cut: the buzz leads (file 19) | In with his arm already rising, continuing A; out once he settles |
| 3 | S1-03 insert, phone | `S1-03_t03_F` | 1:00 → 2:23 | 48 | 6:00–7:23 | On a look: to his eyes | Its whole window; out at its closest creep to the glass |
| 4 | S1-04 MCU push-in | `S1-04_t04_Q` | 1:20 → 5:19 | 96 | 8:00–11:23 | On action: hand to the register | In mid-rub; glance (3:12) and look-away inside; hand moves 5:15, out 4 frames later |
| 5 | S1-05 insert, column | `S1-05_t03_F` | 1:16 → 4:15 | 72 | 12:00–14:23 | On sound: the buzz again | In with the finger already moving; out the frame after the second circle closes |
| 6 | S1-06 MCU, phone | `S1-06_t02_F` | 2:00 → 4:23 | 72 | 15:00–17:23 | On action: as the phone arrives at his ear → S2-01 | In on the exhale; out the frame the phone reaches his ear — S2-01's first board (file 14) |

Every In is at or after 1:00 and every Out a second or more before its clip ends. The 4 s and 6 s clips keep one second of tail (S1-05 keeps 1:08); only the 8 s S1-04 keeps more than 2 s (2:04).

1. **String-out — `saaf-hisaab_selects_v01`.** One circled Lite take per shot (Create Timeline Using Selected Clips); scene 1's part runs about 20 s.
2. **Assembly — `_cut_v01`.** Duplicate it; ripple each head and tail toward the Use length. Watch once: do a night, a tired man and an unanswered phone read?
3. **Rough — `_cut_v02`.** Watch muted, then on the phone, checking each cut against the shot list's Out column. Each lock reuses its draft's board, prompt and length ([[14-previs-storyboard-floorplan-animatic]] §7, rule 4) but is a new generation: its timings move (step 5). A rough cut sits within ±12 frames of plan (§5); this one leaves two edits early: S1-03 starts 6 frames early, so the phone appears only 12 frames after its buzz, and the S1-05 | S1-06 cut sits 3 frames early, before the second circle closes.
4. **Locks in — `_cut_v03`.** Duplicate; Replace each draft with its lock, aligned on a key frame (S1-04: his eyes opening). Durations don't change, so step 3's drift is still there.
5. **Fine — `_cut_v04`.** S1-04's lock plays 10 frames slower than its draft (glance 3:12 against the draft's 3:02, hand 5:15 against 5:05 — §3), so its hand now moves after the cut: slip S1-04 10 frames later. Roll S1-05 | S1-06 3 frames later and slide S1-03 6 frames later, which returns step 3's drift; slip S1-05 10 frames later. Loop every cut. Then open the **Edit Index** (Resolve's list of every edit): its Source In/Out, Record In/Out and duration columns should read as the table above — your decision table, kept by Resolve.

## 13. Versions, Review, and the Closing Checklist

### 13.1 Versions

- **Before every pass**, select the timeline → **Edit → Duplicate Timeline** (it arrives with "copy" in its name) → rename it to the next version → work only on the copy; the old version stays exactly as it was.
- Right-click old versions → **Disable Timeline**: they stay in the Media Pool but no longer load.
- Safety net: Preferences → User → Project Save and Load → **Timeline Backups** on, plus **File → Create Timeline Backup** (Option-Command-S) before a risky change.
- What changed? With the new version open, right-click the old one → **Compare With Current Timeline**. **View → Show Duplicate Frames** marks any frames used twice.

### 13.2 The four viewings

Export a review copy (**File → Quick Export**, pick a preset, save as `08_edit/saaf-hisaab_cut_v04_review.mp4`; masters are file 20's) and watch it four ways:

| Viewing | Catches | Fix lives in |
| --- | --- | --- |
| On the phone, full screen, once, no stopping | Boredom, confusion, a jolt — at the size it will be seen | here, or file 18 |
| Muted | Cuts with no visual motive; seams the sound was hiding; whether the story reads without words (file 12's sound-off test) | §7–§8 |
| Eyes closed | Sound bumps at picture cuts; lines that crowd each other | file 19 |
| Next day, cold | What familiarity hid — you are an audience again | wherever the note points |

Write notes as `time · what I felt`, not the fix: "bored at 0:13" is a note; "trim S1-05" is a guess. Tracing a note to its cause is file 18's skill.

### 13.3 The closing checklist — Dmytryk's rules

Edward Dmytryk, a film editor before he directed, set out his rules of cutting in *On Film Editing* (Focal Press, 1984). Paraphrased:

```
[ ] Every cut has a positive reason — the "Why" column is never blank.
[ ] Unsure between two frames? Cut long; tighten in the fine cut.
[ ] Cut in movement whenever you can (§8.1).
[ ] Fresh beats stale — leave before the information runs out (§10).
[ ] Scenes begin and end on continuing action — S1-01 opens mid-scratch;
    scene 2 ends as Kishan walks out.
[ ] Cut for the moment's value, not a perfect match — the best
    performance beats a matching hand (file 10 §5.6).
[ ] Substance first, then form — no grade, mix or captions before lock.
```

## 14. What Still Can't Be Done

- **Draft frames don't transfer.** A lock is a new generation; the draft's cut frame does not exist in it. Structure carries over; frames are found again.
- **No frames beyond the clip.** If the action ends at 7:20 you have 4 frames of handle, and no editing tool makes more: regenerate or redesign ([[18-editing-2-rhythm-structure-and-rescue]] has the fix ladder).
- **Kuleshov has limits.** It tilts a neutral face; it won't turn a grin into grief, and one recreation found nothing at all.
- **One angle per moment.** A live shoot covers each moment from several angles; this film generates one shot per moment, so the cut has fewer choices. Missing coverage needs a pickup — a new shot asked for after the shoot (file 18).
- **No AI crutches in free Resolve.** Transcription, text-based editing and timeline scene-cut detection are Studio (Blackmagic's Studio list and manual, §16); everything in this file is free.
- **The watermark stays.** In India every Flow clip carries a visible watermark ([[11-directors-track-roadmap]] §8). Editing never removes it, and no framing is chosen to hide it; disclosure is file 20's.

## 15. Exercises

**15.1 — Set up once (0 coins).** Build the project with every §2.1 row, save the `DZZLO 9:16 24p` preset, import a folder as bins. Artefact: the preset and the bin list.

**15.2 — Two-pass dailies (0 coins).** Six clips you already have: pass 1 in Cinema Viewer, pass 2 with markers, windows and verdicts. Artefact: a filled §3.2 dailies sheet.

**15.3 — Map the weak seconds (0 coins).** On five clips, frame-step the first and last 24 frames; note where motion really starts and where it settles or drifts. Artefact: a five-row table — does the window, a second in from each end, hold?

**15.4 — Three marks, four edits (0 coins).** Make each row of the §6 table once, including a backtimed overwrite. Artefact: four clips, each labelled with its edit type.

**15.5 — Trim drill (0 coins).** On four clips, do one ripple, roll, slip and slide, noting the timeline length before and after each. Artefact: four lines; only the ripple changes the length.

**15.6 — One cut, five versions (0 coins).** Loop one cut on action exact, with B ±2 and with B ±4 frames. Artefact: the version you kept, its frame numbers, and the worst one.

**15.7 — Kuleshov on your own footage (0 coins).** Cut one neutral face after three different inserts; ask three people what he feels in each. Artefact: nine answers.

**15.8 — Cut scene 1 (0 coins with drafts in hand; ~⏣60 for six Lite drafts).** Run §12 from string-out to `_cut_v04`. Artefact: your edit decision table, checked against the Edit Index.

**15.9 — The four viewings (0 coins).** Review `_cut_v04` four ways (§13.2), a night between viewings three and four. Artefact: your `time · what I felt` notes.

## 16. Sources (web-verified 2026-10-01)

Primary — tools:

- [DaVinci Resolve 21 Reference Manual — Blackmagic Design, 2026-07-09](https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_21_Reference_Manual.pdf) (ch. 4, 6, 17, 18, 39, 41, 42, 43, 46, 48, 51, 55) · [Resolve 21.1 Studio and iPad Features, Sept 2026](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_Studio_21_Features.pdf)
- Flow Help — [Edit & build scenes](https://support.google.com/flow/answer/16935718) · [Models & features](https://support.google.com/flow/answer/16352836) · [Credits](https://support.google.com/flow/answer/16526234) · [Projects & downloads](https://support.google.com/flow/answer/16935308)
- Google Vids Help — [Object tracks](https://support.google.com/docs/answer/14960797) · [Transitions](https://support.google.com/docs/answer/14916386) · [Audio tracks](https://support.google.com/docs/answer/14999865) · [Video size](https://support.google.com/docs/answer/16545758)
- [How to use the function keys on your Mac — Apple Support](https://support.apple.com/en-us/102439)
- [Flow Help — Get started / FAQ](https://support.google.com/flow/answer/16353333) (visible watermark) · [DaVinci Resolve 21 Supported Codec List](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_21_Supported_Codec_List.pdf) (≥ 4K encode is Studio) · [BBC Subtitle Guidelines](https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/) (160–180 words a minute)

Craft:

- [Smith & Henderson, "Edit Blindness", *Journal of Eye Movement Research* 2(2), 2008](https://bop.unibe.ch/JEMR/article/download/2264/3460)
- Murch on blinks — [Radiolab, "Blink" (transcript)](https://radiolab.org/podcast/91925-blink/transcript) · [John Lahr, "Every Blink", *LRB* 47(19), 23 Oct 2025](https://www.lrb.co.uk/the-paper/v47/n19/john-lahr/every-blink) · [No Film School, 2016](https://nofilmschool.com/2016/05/not-sure-where-cut-editor-walter-murch-says-answer-may-be-eyes)
- Murch on dailies — [Steve Hullfish, "Art of the Cut: Walter Murch", ProVideo Coalition, 2020-02-10](https://www.provideocoalition.com/aotc-murch-books/)
- Dmytryk — [Matthew Jeppsen, ProVideo Coalition, 2008](https://www.provideocoalition.com/seven_rules_for_film_and_video_editors/) · [NYFA](https://www.nyfa.edu/student-resources/what-you-can-learn-from-edward-dmytryks-7-rules-of-cutting/) · [Edward Dmytryk — Wikipedia](https://en.wikipedia.org/wiki/Edward_Dmytryk) · [*On Film Editing* — Routledge](https://www.routledge.com/On-Film-Editing-An-Introduction-to-the-Art-of-Film-Construction/Dmytryk/p/book/9781138584327)
- [Kuleshov effect — Wikipedia](https://en.wikipedia.org/wiki/Kuleshov_effect)
- [Russell Leigh Sharman, *Moving Pictures*, "Editing" (CC BY-NC-SA) — the content curve](https://uark.pressbooks.pub/movingpictures/chapter/editing/)
- Wikipedia — [Film editing](https://en.wikipedia.org/wiki/Film_editing) · [Picture lock](https://en.wikipedia.org/wiki/Picture_lock) · [Dailies](https://en.wikipedia.org/wiki/Dailies) · [Cutting on action](https://en.wikipedia.org/wiki/Cutting_on_action) · [Bilabial consonant](https://en.wikipedia.org/wiki/Bilabial_consonant)
- Videomaker — [Stages of editing](https://www.videomaker.com/article/c3/17887-stages-of-editing/) · [Sean Berry, tips to edit dialogue, 2019](https://www.videomaker.com/how-to/editing/editing-technique/important-tips-to-help-you-edit-dialogue-correctly/)
- [How to prompt Veo 3 for the best results — Replicate, 2025-06-10](https://replicate.com/blog/using-and-prompting-veo-3)

---

**Previous:** [[16-directing-performance-and-dialogue-scenes]] · **Next:** [[18-editing-2-rhythm-structure-and-rescue]] · **Track map:** [[11-directors-track-roadmap]] · **Back to:** [[00_README]]
