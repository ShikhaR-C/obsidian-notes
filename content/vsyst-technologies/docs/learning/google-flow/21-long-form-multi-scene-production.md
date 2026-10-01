# Long-Form & Multi-Scene Production — Running a Film or a Series Like a Producer-Director

> Level: Pro | Hat: Producer-director | Time: ~3 hr, plus ~2 hr setting up | Secures: All four, at scale | Outcome: you can run Saaf Hisaab — 31 generated shots, ≈ ⏣2,000, twenty working days — and later a longer film or a series as a production: one bible, a library that loses nothing, prompts kept like source code, one model per film, a two-jar coin calendar, seven gates, risks tested first, and numbers that prove it worked | Status: written & web-verified **2026-10-01** against Flow Help, Google One, Docs and Drive Help, the Resolve 21 manual and Google's product announcements. Sources in §15.

---

## Explain-it-like-I'm-5

A 30-second promo is one afternoon with the robot crew ([[00_README]]). A long film is **forty afternoons with forty crews who never meet** — and every few weeks the agency that supplies the robots quietly retrains them. Nobody on set remembers yesterday. The film's only memory is **your filing cabinet**; its only money is **two coin jars** — a big one refilled monthly, and a small one that refills each day you shoot and empties overnight.

The **producer** keeps the cabinet, the jars and the calendar so that forty crews make one film. Files 12–20 taught the tricks; this is the system that makes them hold for a month.

## 1. The One Idea — a Long Film Is a System, Not a Run of Good Afternoons

At 30 seconds the film fits in your head. At 90 seconds — Saaf Hisaab's 31 generated shots, 89 planned renders and about 75 stills over four weeks — it doesn't. **Production** is the system that remembers: documents with owners, assets with names, prompts with versions, coins on a calendar, gates where someone signs. It keeps the four continuities ([[11-directors-track-roadmap]]) true across sessions, months and people — **causal** through the story bible and gate 1, **perceptual** through stills, the block registry and one model, **emotional** by keeping each set-up, and all eight Quality locks, inside one sitting, **sonic** by reusing one ambience bed, one score and one ident.

Saaf Hisaab cuts to a new shot every 2.8 s (87 s of generated picture ÷ 31), and its envelope spends ≈ ⏣65 per generated shot (⏣2,000 ÷ 31), so cost follows shots, not runtime:

| The film | Shots | Coins · months | What breaks first | Fix |
| --- | --- | --- | --- | --- |
| 90 s, Saaf Hisaab | 31 | ≈ 2,000 · 1 | which board, take, hand; coins gone before the locks | §4, §5, §7 |
| 3 min | ≈ 64 | ≈ 4,100 · 2 | look drift between sessions; jars reset mid-film | §3, §5, §7 |
| 5 min, or 4 × 90 s series | ≈ 107–124 | ≈ 6,900–8,000 · 3½–4 | the tool changes; the bible forks; people change | §6, §9, §11 |

## 2. The Production Bible — One Index, One Owner per Document

A **production bible** is an **index**, not one big document: a page listing every document the film runs on, its owner, its version and the gate (G1–G7, §8) that locked it — what television's **series bible** does for writers, done for robot crews. Make a Doc `saaf-hisaab_BIBLE_INDEX` in `00_bible/` (§4):

| # | Document (made in file) | Owner | Locked at | "Locked" means |
| - | --- | --- | --- | --- |
| 1 | Story bible: logline, controlling idea, product truth, beat sheet, scene cards (12) | Director | G1 | no beat or turn changes |
| 2 | Look bible: Look Sentences, colour script, camera personality (13; 10 §7) | Director | G2 | LOOK blocks frozen at a version |
| 3 | Still set: masters, sheets, boards (14; §4) | Director | G2 | no still overwritten |
| 4 | Previs: floor plans, animatic, locked shot list, per-shot plan (14) | Director | G3 | IDs, durations, methods, tiers fixed |
| 5 | Continuity bible: identity, state and voice lines, day tracker, state table, take log (15) | Continuity | G3 (take log open to G5) | every state at every cut decided |
| 6 | Performance notes: intensity ladder, line sheet (16) | Director | G3 | six lines and their intensities fixed |
| 7 | Edit record: cut versions, pickup list, screening notes (17, 18) | Editor | G6 | no frame moves |
| 8 | Sound sheets: track layout, cue sheet (19) | Sound | G7 | mix printed |
| 9 | Colour and delivery sheets: grade, QC, delivery (20) | Colour | G7 | master passed QC |
| 10 | Production sheets: registry, prompt log, change log, ledger, calendar, risk register, tool checks, post-mortem (21) | Producer | live | — |

The files: [[12-story-engine-seamless-storytelling]] · [[13-visual-language-composition-blocking-light]] · [[14-previs-storyboard-floorplan-animatic]] · [[15-continuity-bible-script-supervisor]] · [[16-directing-performance-and-dialogue-scenes]] · [[17-editing-1-workflow-and-the-cut]] · [[18-editing-2-rhythm-structure-and-rescue]] · [[19-sound-edit-design-and-mix]] · [[20-colour-finishing-and-delivery]].

Two rules: **one owner per document**, the only person who changes it; and **a locked document changes only through the change log** (§5), signed by its gate's signer (§8). Freeze each at its gate as a named version — **Last edit** (top right) → pick the version → **More** → **Name this version** → `G2 — board lock`. Docs allows 40 named versions, Sheets 15: name gates, not edits.

## 3. The Hierarchy — and Shooting Out of Order

| Level | Saaf Hisaab | Count | The unit of… |
| --- | --- | --- | --- |
| Film | Saaf Hisaab | 1 | budget, model, bible |
| **Sequence** — scenes forming one narrative unit | A Night (scenes 1–2) · B Dusk (3) · C Morning (4) | 3 | a look, a master still, a character state |
| Scene | The 9 PM Register … Morning Chai | 4 | one turn (file 12) |
| Set-up | one camera position + one light (file 14) | 18 | one sitting per pass |
| Shot | S1-01 … S4-07 | 32 (31 generated) | one board, one prompt, one lock |
| Take | `S2-07_t05_Q.mp4` — S2-07's fifth render | 89 planned | one charged output |

Real productions shoot **out of story order**, grouping scenes that share a location and cast to "shoot out" the location. In Flow, scenes share a master still, a Look Sentence and a character state — so you shoot out the **sequence**:

| Sequence | Scenes · day · place | Master · LOOK block | Shots | Quality locks |
| --- | --- | --- | --- | --- |
| A Night | 1–2 · D1 9 PM · LOC-A | `LOC-A_night_master.png` · LOOK-night | 14 | S1-04, S2-02, S2-03, S2-07 |
| B Dusk | 3 · D2 dusk · LOC-B | `LOC-B_dusk_master.png` · LOOK-dusk | 11 | S3-05, S3-09, S3-10 |
| C Morning | 4 · D3 7 AM · LOC-A | `LOC-A_morning_master.png` · LOOK-morning | 6 | S4-05 |

File 14 groups the 31 shots into 18 set-ups and runs them in three passes — all Lite, all Fast, then the eight Quality locks — riskiest set-up first, faces before inserts, one tier and one set-up per sitting. Across the month, three rules hold:

1. **No set-up straddles a model change.** If a tool check (§6) finds one mid-set-up, finish or restart that set-up; never mix.
2. **Every pass ends in a cut.** Pass 1 → the Lite cut (§7, gate 4); Pass 2 → a complete Fast cut, your insurance if coins run out (file 14); Pass 3 → the lock cut (gate 5).
3. **The eight Quality locks are one sitting on one day** — ⏣800 at once, only after that morning's tool check, so every hero face shares one model state.

## 4. Stills First, at Scale — and an Asset Library That Loses Nothing

Track canon makes every shot a board still turned into video by Frames→Video, so the stills are the film's **source**: a model change leaves them standing; a changed still voids every take made from it. All are approved at gate 2, before any video coin:

| Still set | Files | Count |
| --- | --- | --- |
| Location masters, one per location × time | the three in §3's table | 3 |
| Character sheets, one per story-day state | `CHAR_ravi_D1.png`, `_D2`, `_D3`, `CHAR_kishan.png` | 4 |
| Angle and expression sheets | `CHAR_ravi_D1_angles.png` … | 4 |
| Props sheet | `PROPS_sheet_v1.png` | 1 |
| Boards — 31 first frames, 17 last frames (file 14) | `S2-07_board_v1.png`, `S2-07_board_v1_last.png` | 48 |
| Join stills | none — the 31 joins are 29 cuts, a dissolve and a fade (file 14) | 0 |

File 14 counts about 75 stills in all, made set-up by set-up. Only Nano Banana 2 Lite is stated free: check the cost Flow shows for file 14's image model; if it charges, stills get their own ledger line outside the film's ≈ ⏣2,000 coin envelope, paid from weekend day jars or a top-up pack (§7).

**The Drive tree** — one root per film, numbered so folders sort in working order:

```
DZZLO-films/saaf-hisaab/
├── 00_bible/       BIBLE_INDEX · prompt-log Sheet (Blocks · Prompts · Changes) ·
│                   ledger · risk register · TOOLCHECK_<date>
├── 01_story/  02_look/  03_previs/
├── 04_stills/      masters/ · cast/ (sheets, PROPS) · boards/
├── 05_takes/S1 … S4/     S2-07_t05_Q.mp4 + S2-07_t05_Q.txt   (take + sidecar)
├── 06_real/        screen recordings, real footage, signed releases
├── 07_audio/       VO, effects, music + the terms it came with
├── 08_edit/        Resolve .drp / .dra, saaf-hisaab_cut_v03, _lock_v01
├── 09_masters/     saaf-hisaab_master_v01 + delivery files
└── 10_postmortem/
```

**Names** follow the track's ID table; a fix is a new `_v` file, never an overwrite. **Every take gets a sidecar** — a same-named text file written at download (not file 20's caption sidecar), because Flow Help's create and project pages describe no way to read back a clip's model, prompt or settings:

```
take     S2-07_t05_Q.mp4          day D20 · <date>
prompt   S2-07_p02                model Veo 3.1 - Quality (as the picker names it)
mode     Frames → Video · start S2-07_board_v1.png · end S2-07_board_v1_last.png
outputs  1 · coins 100
blocks   NAME-ravi@1.0 · AXIS-A@1.0 · LOOK-night@1.0 · VOICE-ravi@1.0
text     <the assembled prompt, exactly as sent>
```

**In Flow**, keep one project per film and one **collection** per sequence (**Add** → **Create Collection**). Flow Help's FAQ and projects pages state no retention period, so treat Flow as a workspace, not an archive: download on the day.

**Never delete** a still any take used, a take in any cut version, a lock, a sidecar, the Sheet, a recording with its release, or music with its terms; "no good" takes may go after gate 7, log rows kept. Drive deletes Trash "forever after 30 days" and may drop an older version of an uploaded file after 30 days unless marked **Keep forever** (**More** → **Manage versions**), so never "upload new version" over a still.

## 5. Prompts as Source Code

You run a software company, so treat prompts like code: **frozen blocks** are constants, keyed and versioned (`LOOK-night@1.0`); the **prompt log** is the commit log, one row per prompt version (`S2-07_p02`); a formula is the build, so nobody types a prompt; the **change log** is the changelog; the **frame-pair check** (file 15) is the regression test.

One Sheet, three tabs. `Blocks` holds each frozen block once — key in A, its body in B, as file 15 §5 pastes it (no label, no tag):

```
A  key                B  body (no label)
-                     (empty: "no block")
CHAR-ravi@1.0         Ravi, a friendly Indian man, early 30s, short black hair, light stubble.
NAME-ravi@1.0         Ravi is the man in the image.
STATE-ravi-D1@1.0     Crumpled pale-blue cotton shirt … tired eyes.
AXIS-A@1.0            Camera on the room side; the door and the window are camera-right.
AXIS-B@1.0            Ravi is frame-left, looking right; Kishan is frame-right, looking left.
AXIS-B-ravi@1.0       Ravi is frame-left, looking right. The other man stays off-frame.
AXIS-B-kishan@1.0     Kishan is frame-right, looking left. The other man stays off-frame.
LOOK-night@1.0        Shot on 35 mm … 9:16.
VOICE-ravi@1.0        Ravi has a warm, slightly husky male voice … unhurried.
                      (each … stands for the rest of the line — paste every block whole)
```

`Prompts` holds one row per prompt version in the skeleton's order — key columns are fetched, the rest typed per shot: A ID · B shot · C mode and frames · D CAMERA · E CHAR key · F STATE key · G second-character key · H ACTION · I SCENE · J AXIS key · K eyeline and hands · L LOOK key · M SOUND · N VOICE key · O the delivery and the line (*Ravi says, low and clipped, holding his temper:* then the quoted words), ending "No music. No subtitles." · P assembled prompt · Q status · R why changed. In P2, filled down:

```
=TEXTJOIN(CHAR(10), TRUE, D2, TEXTJOIN(" ", TRUE, VLOOKUP(E2,Blocks!A:B,2,FALSE), VLOOKUP(F2,Blocks!A:B,2,FALSE), VLOOKUP(G2,Blocks!A:B,2,FALSE)), H2, I2, TEXTJOIN(" ", TRUE, VLOOKUP(J2,Blocks!A:B,2,FALSE), K2), VLOOKUP(L2,Blocks!A:B,2,FALSE), TEXTJOIN(" ", TRUE, M2, VLOOKUP(N2,Blocks!A:B,2,FALSE), O2))
```

`CHAR(10)` is a line break, so P holds one block per line, as file 15 §5 pastes them; the inner `TEXTJOIN(" ", …)`s keep SUBJECT, AXIS and AUDIO each on one line; empty cells are skipped. `VLOOKUP(…, FALSE)` fetches a block by exact key. A `-` means no such block (no character in an insert, say); a mistyped key shows `#N/A` rather than silently dropping a block. A board-led row shrinks SUBJECT and SCENE to naming clauses: E holds `NAME-ravi@1.0`, F holds `-`, and I is typed "The pump office at 9 PM." plus only what moves or changes. In LOC-B, J holds `AXIS-B` for a two-shot and the man's own half-key for a single ([[15-continuity-bible-script-supervisor]] §5). Copy P from inside the cell (double-click it, select all) so Sheets adds no quotation marks of its own, paste it into Flow, and check the first paste: the only quotation marks should be the spoken line's.

**The change rule:** a changed block is a **new key**, never an edit, and every shot that used the old key is re-checked. Say Pass 2's dailies find the night clips too warm, and the director wants "soft warm desk lamp" in LOOK-night:

1. **Can the grade fix it?** Warmth is colour, which file 20 fixes for 0 coins. Change blocks for content, not tint.
2. If not, add `LOOK-night@1.1` and filter `Prompts` by L = `LOOK-night@1.0`: 14 shots, all of sequence A.
3. Shots not yet rendered at Fast switch to `@1.1`; column P rebuilds them.
4. Shots already rendered get the frame-pair check on every cut now joining 1.0 to 1.1. A failed Fast lock is retaken (⏣20), as is any rehearsal whose Quality lock is still to come. The spare pays; gate 2 is reopened (§8).
5. Log it in `Changes`: date · LOOK-night 1.0 → 1.1 · why · shots touched · cuts failed · coins · signed.

## 6. One Film, One Model Version

Google re-tunes this stack constantly. Between April and September 2026 Whisk closed, Omni Flash reached Flow (19 May) and moved to 1.1 (27 August), Lyria 3.5 took over Flow Music, and Vids moved to Omni 1.1. Flow's FAQ: "Model costs are evolving fast." The models page lists one version per model and no older ones; the create page offers no seed. You can't pin the model — you **finish inside it**:

1. **A tool check** before Day 1 and before Pass 3, saved as `TOOLCHECK_<date>`; if anything changed, re-plan first.
2. **Model, tier and date in every sidecar.**
3. **One sitting for the eight Quality locks** (Pass 3, D20), after that morning's tool check.
4. **No mixed versions inside a sequence:** re-making one shot after a change means pricing its neighbours too.

```
TOOL CHECK — saaf-hisaab — <date>
Picker names:   Veo 3.1 - Lite · Veo 3.1 - Fast · Veo 3.1 - Quality · Gemini Omni Flash 1.1
Costs shown:    Lite 10 · Fast 20 · Quality 100 · Omni edit 40 · 1080p upscale 0
Modes:          Frames→Video on all three Veo tiers? Ingredients still Lite/Fast only?
Outputs: 1      Board image model + cost: ____
Credits: ____   billing date ____ · spent first: daily / monthly / not stated
Changed since the last check?   no / yes → change log
```

| When this changes mid-film | Do this | What survives |
| --- | --- | --- |
| A price | re-run the ledger; cut drafts before locks | everything |
| The model — a new name, or Fast takes unlike the Lite drafts of the same boards | stop; re-render one Fast-locked shot's board and frame-pair it against its neighbour. Pass → carry on; fail → redo the rest of that sequence as a set | stills, registry, cut, sound |
| A feature disappears (as Jump To did) or arrives | re-plan only the shots it touches; adopt new features next film, or mid-film only to rescue a failing shot | everything else |

The stills are the insurance: a model change makes renders costly to redo, never the design obsolete.

## 7. Coins Across the Month — the Two-Jar Plan

On AI Pro, Flow's credits page describes two kinds of credit. Call them jars:

| | Month jar | Day jar |
| --- | --- | --- |
| Size | 1,000 | 50 |
| Refills | at the start of your billing cycle | daily; the refresh "is triggered by your first generation" |
| Unspent | gone — "do not roll over to the next month" | gone — "don't roll over" |

Canon gives the month jar the locks and Fast renders, the day jar the drafts. One refinement is forced: locks plus Fast renders cost ⏣1,420, more than the month jar holds, so in Pass 2 each day's 50 carries most of three or four Fast renders and the month jar tops up the rest; on the Quality day the day jar pays 50 of the 800. Keep the ⏣80 spare in the month jar — day coins can't be pooled across days, so a ⏣40 rescue must come from the month. Each Quality shot's Fast render is its **rehearsal** (file 14) and its fallback. Keep **Number of outputs** at 1: Flow charges per output, and failed generations are free. The one exception, casting a dialogue take ([[16-directing-performance-and-dialogue-scenes]] §12), asks for two outputs at once: two of that shot's planned Lite drafts ([[14-previs-storyboard-floorplan-animatic]] §7), not extra spend.

**Which jar goes first?** Flow Help doesn't say; it only puts your remaining credits under your profile picture (top right). A third-party report quotes Flow's own on-screen text on one account (13 September): "daily credits used first". Read the wording on yours and note it in the tool check. The calendar assumes daily-first; if yours differs — or you want slack — run it over **two relaxed months**: Passes 1–2 in month 1, Pass 3 and pickups in month 2, after re-checking one pair (§6).

**The calendar.** Day 1 is the first working day of a billing cycle; gate 1 is signed before it.

| Days | Work · gate | Renders | Day jar | Month jar | Month left |
| --- | --- | --- | --- | --- | --- |
| D1–D5 | masters, sheets, boards set-up by set-up; **Pass 1 opens** with file 14's rows 1–4 as their boards land — the **spikes** (§10); **G2** D4; animatic, **G3** D5 | 25 L | 250 | 0 | 1,000 |
| D6–D10 | **Pass 1**, rows 5–17; frame-pair checks; the Lite cut; **G4** D10 | 25 L | 250 | 0 | 1,000 |
| D11–D19 | **Pass 2**: 31 Fast renders, rows 1–18, three or four a day; a complete Fast cut | 31 F | 450 | 170 | 830 |
| D20 | tool check, then **Pass 3**: the 8 Quality locks in one sitting (rows 1–5); **G5** | 8 Q | 50 | 750 | 80 |
| **Total** | | **50 L · 31 F · 8 Q** | **1,000** | **920** | **80 = the spare** |

The **Lite cut** is the animatic with each still swapped for its approved Lite draft; the **lock cut** swaps in the locks. Gates 6–7 cost hours, plus any pickups' daily credits (18 §12). File 20's free 1080p upscale comes after picture lock, so keep the Flow project intact until then.

**The spare is one pot**, allocated once in [[14-previs-storyboard-floorplan-animatic]] §9; R3's blocking test (§10) is one of its draws. A skipped draw frees its coins for a rescue, such as §9's ⏣20 Fast retake; pickups are not paid from it ([[18-editing-2-rhythm-structure-and-rescue]] §12). Price each rescue first: Lite re-draft ⏣10 · Omni blocking draft ⏣4–7 · Fast retake ⏣20 · Omni edit ⏣40 · Quality re-render ⏣100 — outside the envelope, so fall back to the rehearsal. What the spare can't buy leads next month's plan; whatever is left on the cycle's last day expires, so spend it on the next film's riskiest set-up.

Weekend days you generate add uncounted day jars. Beyond that, AI Pro can buy **AI credits** in packs of 2,500, 5,000 or 20,000 (Google One, or inside Flow), which "may expire after a certain period, as set out when you acquire them" — buy against a named risk, never to keep drafting. On Ultra, Flow's table halves Lite and Fast (5, 10) and adds a free lower-priority Lite; Quality stays 100.

**The second units.** On a real film the **second unit** shoots inserts and cutaways in the director's style. Canon gives Omni Flash 1.1 three such jobs: 360p blocking drafts, the ⏣40 rescue edit, and the voice route file 16 weighs. The local ComfyUI stack ([[../comfyui/09-google-flow-parity]]) costs minutes, not coins, under **one film, one model**: a shot goes local only as a *test* — WAN 2.2 TI2V 5B runs on the parity file's Mac and can show whether the tanker reads right-to-left in S3-01 before a Lite draft is spent — never as picture in a Veo film (its 14B model's fp8 files crash on that Mac's GPU; the parity file's durable fix is GGUF). A whole faceless film, such as an internal explainer, may go local; local is then its one model, and any realistic local shot carries the same disclosure duties ([[20-colour-finishing-and-delivery]] §12).

## 8. Gates — Seven Signatures Between Idea and Upload

A **gate** is a point where named artefacts must exist and someone signs that they pass. Behind a gate, the work is locked:

| Gate · when | Must exist | Pass test | Signs | Reopening later costs |
| --- | --- | --- | --- | --- |
| G1 Story · before D1 | story bible (12) | but/therefore chain; four turns; fits 32 shots and ⏣2,000 | Director + Producer | boards and animatic redone |
| G2 Boards · D4 | look bible, masters, sheets, all 48 boards (13–15) | file 14's board review; no brand mark or plate; each board logged with its blocks | Director + Continuity | Lite drafts from changed boards (⏣10 each) |
| G3 Animatic · D5 | 90 s animatic; shot list locked with method and tier (14) | runs 90 s; sound-off test; every cut motivated | Director + Editor | re-drafts and re-locks |
| G4 Lite pass · D10 | file 14's 50 Lite drafts judged; the Lite cut; frame pairs on the 30 joins between generated shots (15 §8) | no unexplained jump; every risk closed or accepted (§10) | Director + Continuity + Editor | ⏣20–100 per shot re-locked |
| G5 Locks · D20 | 31 locks (8 Q, 23 F) with sidecars; the lock cut | frame pairs re-checked; first-pass yield logged | Director + Continuity | coins, plus that shot's sound and colour |
| G6 Picture lock · week 5 | `saaf-hisaab_lock_v01`; screening notes (17, 18) | file 18's turnover checklist | Director + Editor | re-mix, re-grade, re-export, re-QC |
| G7 Final · week 6 | master, QC sheet, deliverables, archive (19, 20) | technical QC; disclosure decided (20) | Producer | a public correction |

**No gate is passed backwards for free.** Reopening one is a decision, not a drift: a line in `Changes` with what, why, coins, hours and that gate signer's initials — in a team of one, your initials and the date in the bible index. It feels silly to sign; it stops "one small tweak" from eating the month jar. One exception is planned: the spikes — Pass 1's first set-ups — run before gates 2 and 3 on purpose.

## 9. Roles, Hand-overs and Dailies

| Hat | Team of 1 | Team of 2 | Team of 3 |
| --- | --- | --- | --- |
| Producer — coins, calendar, risk, gates | you | A | A |
| Director — story, look, boards, performance | you | A | A |
| Continuity and operator — Sheet, take log, frame pairs, the Flow keyboard | you | A | B |
| Editor — selects, cuts, pickup list | you, never on a day you generated | B | C |
| Sound, colour, delivery | you | B | C |

Two people split **shoot** and **post**: the editor is the first audience (file 17) and shouldn't have made the shots. Only the operator pastes into Flow; only the producer spends the month jar; alone, a night's distance stands in for the second person.

**Hand-overs** are named packages, not conversations:

1. Director → operator, at G3: locked shot list, boards, registry at `@1.0`, generation plan.
2. Operator ⇄ editor, daily: takes, sidecars and the take log (file 15) one way; the pickup list (file 18) back.
3. Editor → sound and colour, at G6: file 18's **turnover**, the hand-over of the locked cut — the timeline duplicated as `saaf-hisaab_lock_v01`, plus the project. In Resolve free, **File → Export Project** writes a `.drp` (no media); Project Manager → right-click the project → **Export Project Archive** (the manual also calls it **Archive**) writes a `.dra` folder with all the media — use that between two Macs.
4. Finishing → producer, at G7: master, QC sheet, archive (file 20).

**Dailies**, on a film set, are the day's raw footage watched at day's end. Here they close each generation day in 20 minutes: watch the takes as file 17 teaches, mark the take log, pick tomorrow's re-drafts, copy the balance into the ledger, update the risks, and log three lines:

```
D12 dailies · approved: S1-06_t02_F, S2-02_t04_F · retake: S2-05 — Kishan's eyeline sits
higher than Ravi's in S2-03; fix the board tonight, Fast retake from the spare (⏣20)
· month jar 940 · R2 open
```

## 10. Risk First — the Spike and the Register

Software teams answer the riskiest question first with a **spike**: the smallest possible experiment, time-boxed. Saaf Hisaab's hardest shot is **S2-07** — the peak and tightest shot: a push-in, a Hinglish line, a hand lowering a phone, a performance that must meet S2-06 and S2-08. If it can't be made, the plan changes before anything else is drafted. So D1 opens Pass 1 with file 14's row 1, S2-07 first: three Lite drafts from its board, before any other shot.

A spike has one question ("can Veo deliver S2-07's line, push-in and hand from this board?"), a box (one day jar), a verdict (pass, fix and re-spike, or fall back) and a register line. It costs nothing extra: the drafts were planned anyway, just moved forward. The **risk register** scores each risk likelihood × impact (1–3 each) and names a test, a fallback and an owner:

| ID · owner | Risk | Shots | L × I | Lite test (file 14 row · drafts) | Fallback within the fixed shot list |
| --- | --- | --- | --- | --- | --- |
| R1 · Director | the peak doesn't land: over-acting, a mispronounced line, a melting hand | S2-07 | 9 | row 1, D1 · 3 L | re-board with his eyes down on the register; the line half-hidden, laid in the edit (16, 19) |
| R2 · Continuity | matched singles don't match: face, eyeline height, light side | S2-03/05, S3-02/03, S3-05/06, S3-09/10 | 6 | rows 1–4, D1–D5 · 15 L | re-derive each pair's boards in one image session (14); judge pairs side by side before Pass 2 |
| R3 · Director | two men in one frame blend or swap faces | S2-08, S3-11 | 6 | Omni 360p blocking of S2-08 (⏣6, spare); rows 7, 9 · 5 L | Kishan's back to camera as he leaves; both men small in S3-11 (16) |
| R4 · Director | the bookends don't rhyme | S1-02 ↔ S4-06 | 6 | boards side by side at G2; rows 16–17, back to back · 2 L | derive S4-06's board from S1-02's |
| R5 · Editor | the phone shots won't take a clean composite | S3-04, S4-03 | 4 | rows 12, 15 · 2 L | a dark, blank screen; the real recording goes in at the edit (20) |
| R6 · Producer | an oil-company logo or a legible plate appears | masters, S2-06, S3-01, S4-04 | 4 | G2 review, every dailies | re-board the master clean; never publish a real mark |
| R7 · Continuity | hands at the cut: pen, page, thumb, gloved hand on nozzle | S1-01, S2-04, S3-07, S3-08 | 3 | rows 11–13 · 4 L | use the clean second; the hard effect sells the cut (19) |
| R8 · Producer | the tool changes mid-month | all | 3 | tool checks | §6 |

Week 1's 25 drafts are file 14's rows 1–4 — the four dialogue set-ups, 15 drafts on matched singles and 3 on S2-07 — plus one of row 5. Every risk is tested on Lite before Pass 2 spends a Fast coin: gate 4 waits until each row is closed, accepted or has its fallback written.

## 11. Series, Campaigns and Hybrid Films

**A series is one bible and many films.** Start each episode from a copy of the bible file 15 freezes at picture lock as v1.0. Carried over: identity lines and character sheets, the three masters, the Look Sentences at their versions, the props bible, the camera personality, the music bed, the ident, the Drive tree and the Sheet. New per episode: STATE lines (story days keep counting — episode 2 starts on D4), new masters and props, the shot list, the calendar. A wording fix is `@1.1` for **new** episodes only; a look change is `@2.0`, held for a new season. The **ident** — a 2-second branded sting after the hook — and the end card are graphics made once (file 20), so they never drift.

**The Gem.** File 15 §6 already builds a script-supervisor Gem that pastes the frozen blocks (on personal accounts Gems become skills from November 2026, and its instructions carry over — [[11-directors-track-roadmap]] §8; a skill can't take Drive files or notebooks yet — Google says "in the coming weeks" — so until then give it an uploaded copy of the bible and re-upload it after every change); for a series, give it the series bible. It stays a helper, not the source (Phase 7 §6: grounding reduces errors without abolishing them), and it writes its own action lines, so check each frozen block it pastes. With its prompt in S2, `=ISNUMBER(FIND(VLOOKUP(L2,Blocks!A:B,2,FALSE), S2))` in T2 is TRUE only if the LOOK body appears character for character. Add a column per other key the row uses (E2, F2, G2, J2 or N2 for L2; skip a `-`). The checks follow the row's keys, so a board-led row is never searched for a body it leaves out. A FALSE names the reworded block; the Sheet's version goes to Flow.

**A hybrid film** mixes generated clips with real recordings — Saaf Hisaab's app screens in S3-04 and S4-03 are real recordings composited in the edit. Match before recording, not in the grade. Record the app on a demo account with invented names and numbers, product-truth screens only, one action per take with 3–4 s of handle each side. Shoot real footage (a forecourt plate; a real dealer in a later episode) at 9:16 and 24 fps on a tripod, at the Look Sentence's time of day and key-light side, with written consent from every recognisable person and the location owner, and no oil-company branding. Omni Flash's ⏣40 edit can relight up to 10 s of an uploaded real clip, but the result is altered real footage — a disclosure case on YouTube — and never for a real person without consent. Keep real and generated people in separate shots; proof in a series comes from a real dealer, never an AI character.

**Rights and honesty, in one paragraph.** Ravi and Kishan are invented: never prompt a real person's face or voice, and never let a frame or caption suggest Saaf Hisaab is a real dealer's story. ASCI's guidelines (self-regulation, not law, from about end-December 2026) ban AI testimonials passed off as real customers even with a label, and require a label on "synthetically generated influencers and ambassadors" — which Ravi becomes in the DZZLO polo. Google lists "commercial use rights" among AI Pro's Flow Music benefits; it states none for Gemini-app or Vids music: read the terms and save them beside the file. Claims come only from the product truth. Every clip keeps its SynthID and, in India, its visible watermark — plan graphics around it; never hide it. Platform labels and India's IT Rules (law since 2026-02-20) belong to [[20-colour-finishing-and-delivery]]; the producer budgets the label into the graphics at gate 2.

## 12. Measure It, Then Post-Mortem It

Fill the planned column before D1 and the actual column after gate 7:

| Measure | How | Saaf Hisaab planned | Alarm |
| --- | --- | --- | --- |
| Cost per finished second | coins ÷ seconds of final film | ⏣1,920–2,000 ÷ 90 ≈ ⏣21–22 | over ⏣22: past the envelope |
| **First-pass yield** | shots accepted on their first lock render ÷ 31 | 100% — the envelope buys one lock render per shot | under 90%: the Lite pass approves too easily |
| Drafts per lock | Lite drafts ÷ 31 locked shots | 50 ÷ 31 ≈ 1.6 | over 2.5: the boards aren't working |
| Hours per finished minute | hours logged ÷ minutes of film | ≈ 75 h ÷ 1.5 ≈ 50 h | your first actual becomes the next plan |

The 75 hours are an estimate to replace with yours: story and bible 6 · stills, boards, spikes 15 · animatic and Lite pass 12 · Fast, locks, dailies 18 · edit to lock 10 · sound, colour, captions, QC, delivery 12 · post-mortem 2.

**The post-mortem** comes within a week of gate 7: two hours, written. Borrow Google's SRE rule — it is **blameless**, hunting contributing causes, not a culprit: write "the Sheet let me paste an old LOOK block", not "I was careless". Only the first can be fixed.

```
POST-MORTEM — saaf-hisaab — <date>
1. Planned vs actual: coins by jar · days · hours · renders by tier
2. The four measures
3. What broke, by continuity (causal · perceptual · emotional · sonic), each with its cause
4. Risks: which fired, which spikes caught them, which surprised us
5. Tool changes noticed, with dates
6. Keep · change · try — three each, at most
7. Winners to file: prompt IDs, take IDs, block keys, model and date
```

**Feed the brand brain** ([[07-phase-7-custom-rag-brand-brain|Phase 7]] §6): add the `Blocks` tab, the winning prompts with model and date — a prompt that worked on Veo 3.1 Quality in October 2026 may behave differently on its successor — and item 6 as rules. The next film starts with a tool check, a copy of this Sheet, and every block at its version.

## 13. What Still Can't Be Done (honesty, vault rule)

- **Pin a model or a seed.** The picker lists current versions only and Flow offers no seed, so no take can be re-made exactly — the take file is the asset. A silent re-tune can't be proved either, only noticed as drift; hence the eight locks share one sitting.
- **Read a clip's recipe back from Flow.** No Flow Help page checked describes it; the sidecar is your record.
- **Bank coins.** Both jars expire, top-ups may expire, and the spending order is undocumented.
- **Automate end to end** on this plan: prompts reach Flow by copy and paste, and Resolve's scripting API is Studio-only. The system is a Sheet, a folder tree and habits.
- **Make the local unit look like Veo**, or a series cheaper per shot — reuse saves hours, not coins.
- **Remove or hide the watermark.** Never. Plan around it.

## 14. Exercises

**14.1 — The index (0 coins).** Create `saaf-hisaab_BIBLE_INDEX` with §2's ten documents, an owner and a gate each. Name the version `G0 — index created`.

**14.2 — The registry and the formula (0 coins).** Build `Blocks` with seventeen keys — CHAR ×2, NAME ×2, STATE ×3, AXIS-A, AXIS-B and its two half-keys, LOOK ×3, VOICE ×2 from file 15, and `-` — and `Prompts` with the §5 formula. Assemble S2-07's prompt; add `LOOK-night@1.1`, filter by `@1.0`, and confirm it touches 14 shots.

**14.3 — The jars (0 coins).** Record your billing date and the credits wording under your profile picture in a tool check. Copy §7's calendar into a ledger with real dates.

**14.4 — The first spike (~⏣30).** Board S2-07 and make its three Lite drafts (file 14) as Pass 1's first renders. Write the verdict into a risk register holding all eight rows of §10.

**14.5 — The Gem check (0 coins).** Ask file 15's Gem for three prompts and run §11's block check on each. Count the FALSEs, and note which blocks they name.

**14.6 — Scale it on paper (0 coins).** Plan a three-minute Saaf Hisaab or a four-episode series: a shot every 2.8 s, ⏣65 a shot, ⏣2,000 a month, the stills that carry over, and the sessions where a model update would hurt most.

**14.7 — Post-mortem your last piece (0 coins).** Run the §12 template, blameless, on your last video. Rename its clips to the take form and write their sidecars from memory — what you can't recall is why sidecars are written at download. File three winners into the brand brain with model and date.

## 15. Sources (web-verified 2026-10-01)

Primary — Google:

- Flow Help: [Credits](https://support.google.com/flow/answer/16526234) (jars, refresh, rollover, costs, balance, top-ups) · [Create videos](https://support.google.com/flow/answer/16353334) (settings; no seed) · [Models](https://support.google.com/flow/answer/16352836) · [Projects](https://support.google.com/flow/answer/16935308) (collections) · [FAQ](https://support.google.com/flow/answer/16353333) (failed generations free; watermarks; "Model costs are evolving fast")
- Google One Help: [Purchase AI credits](https://support.google.com/googleone/answer/17103110) · [Manage AI credits](https://support.google.com/googleone/answer/16287445)
- Docs Editors Help: [Version history](https://support.google.com/docs/answer/190843) · [TEXTJOIN](https://support.google.com/docs/answer/7013992) · [VLOOKUP](https://support.google.com/docs/answer/3093318) · [CHAR](https://support.google.com/docs/answer/3094120) · [FIND](https://support.google.com/docs/answer/3094126) · [ISNUMBER](https://support.google.com/docs/answer/3093296). Drive Help: [File versions](https://support.google.com/drive/answer/2409045) · [Trash](https://support.google.com/drive/answer/2375102)
- Google announcements: [Introducing Gemini Omni](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-omni/) · [New creative controls in Flow](https://blog.google/innovation-and-ai/models-and-research/google-labs/new-creative-controls-google-flow/) · [Lyria 3.5](https://blog.google/innovation-and-ai/models-and-research/google-labs/lyria-3-5/) · [Whisk moving to Flow](https://workspaceupdates.googleblog.com/2026/03/whisk-is-moving-to-flow-on-april-30-2026.html) · [Omni 1.1 in Vids](https://workspaceupdates.googleblog.com/2026/09/gemini-omni-11-flash-now-in-vids-with-improved-extension-quality-1080p-and-duration-control.html)

Primary — other:

- Blackmagic: [Resolve 21 Reference Manual](https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_21_Reference_Manual.pdf) (Export Project; Export Project Archive / Archive) · [21.1 Studio features](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_Studio_21_Features.pdf) (archive and collaboration not Studio-marked) · [DaVinci Resolve](https://www.blackmagicdesign.com/products/davinciresolve)
- [ASCI labelling guidelines for synthetically generated content](https://www.ascionline.in/wp-content/uploads/2026/09/Guidelines-for-Responsible-Labelling-of-Synthetically-Generated-Content-in-Advertising.pdf) · [Postmortem Culture — Google SRE book](https://sre.google/sre-book/postmortem-culture/)

Secondary: [Entitlement Is Not Balance — DEV Community, 2026-09-19](https://dev.to/hexisteme/entitlement-is-not-balance-dont-authorize-google-flow-spend-with-arithmetic-3022) ("daily credits used first", one account).

Craft and production — Wikipedia: [Dailies](https://en.wikipedia.org/wiki/Dailies) · [Second unit](https://en.wikipedia.org/wiki/Second_unit) · [Production board](https://en.wikipedia.org/wiki/Production_board) · [Sequence](https://en.wikipedia.org/wiki/Sequence_(filmmaking)) · [Series bible](https://en.wikipedia.org/wiki/Series_bible) · [First pass yield](https://en.wikipedia.org/wiki/First_pass_yield) · [Risk register](https://en.wikipedia.org/wiki/Risk_register) · [Spike](https://en.wikipedia.org/wiki/Spike_(software_development)). In the vault: [[../comfyui/09-google-flow-parity]] (measured 2026-08-01) · [[10-deep-dive-scene-continuity]].

---

**Previous:** [[20-colour-finishing-and-delivery]] · **Next:** [[22-capstone-saaf-hisaab-workbook]] · **Track map:** [[11-directors-track-roadmap]] · **Back to:** [[00_README]]
