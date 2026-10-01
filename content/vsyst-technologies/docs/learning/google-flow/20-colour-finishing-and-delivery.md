# Colour, Finishing & Delivery — One Look for Thirty-One Clips, Then Out the Door Correctly

> Level: Advanced | Hat: Editor | Time: ~3 hr to read and try; one working day to finish the film | Secures: Perceptual, in the finished picture | Outcome: Saaf Hisaab goes from picture lock to posted: faces matched, three scene looks in one family, free-edition grain, the real app screen in two shots, captions inside the measured 9:16 safe zone, masters that pass a technical QC, and the AI labels that platforms, Indian law and ASCI ask for | Status: written & web-verified **2026-10-01** against DaVinci Resolve 21.1 (free) and its manual, Flow Help, platform help pages, MeitY's 2026 IT Rules amendment and ASCI's 2026 guidelines. Sources in §16.

---

## Explain-it-like-I'm-5

Thirty-one robot crews shot your film, each with its own camera, film stock and idea of "warm". The editor has put the clips in order: picture lock. Now the film goes to the **lab**.

The lab **prints every clip on the same paper with the same chemicals**, so thirty-one rolls look like one. It **adds the title card and subtitles**. It **makes a copy for every cinema**: phones, with buttons painted over the screen's edges and their own rules for the box the film arrives in. Last, it **stamps the box "made with robots"**, because the cinemas, and in India the law, ask for it.

One stamp is already there: for people in India, Google's crew marks every clip it shoots. The lab prints around that mark and never scrapes it off.

## 1. The One Idea — Finishing Is a Fixed Order

**Finishing** is everything done to the picture after picture lock ([[18-editing-2-rhythm-structure-and-rescue]] owns the lock): colour, texture, graphics, captions, checks, export, archive. It secures **perceptual continuity** in the finished picture (look, light and faces matching across every cut) and delivers the film to each platform as you finished it.

Each step assumes the ones before it are frozen, so the order *is* the method:

```
picture lock ─► ① conform ─► ② upscale ─► ③ balance ─► ④ match ─► ⑤ scene look ─► ⑥ texture
                                                                                        │
    ⑪ archive ◄─ ⑩ export ◄─ ⑨ QC ◄─ ⑧ captions ◄─ ⑦ graphics & composites ◄─────────────┘
```

An unbalanced shot can't be matched; a look over a mismatch multiplies it; grain before matching fills the scopes with noise; graphics and captions belong on the final picture; QC runs on the exported file. And **any change upstream re-opens everything downstream**.

## 2. Before Colour — Conform, Upscale, and the Mark That Stays

### 2.1 Conform

To **conform** is to point the timeline at the final files: the locked take of every shot, at final resolution, nothing temporary. (The 1080 × 1920, 24 fps project itself is set up in [[17-editing-1-workflow-and-the-cut]].)

```
1  Duplicate saaf-hisaab_lock_v01 as saaf-hisaab_master_v01. Finish on the copy.
2  Every generated clip ends _F or _Q. An _L file is a Lite draft: it never ships.
3  Count: 31 shots (8 _Q + 23 _F), 2 screen recordings (S3-04, S4-03), the S4-07 card.
4  Each take reads 1080 × 1920 in the Metadata Editor. A 720p file: re-download that take
   at 1080p under the same file name in a new folder, then Media Pool → Relink Selected
   Clips (same take, same frames, so the cut doesn't move).
5  Delete scratch voice, temp music, placeholder grabs. Play every join once.
```

### 2.2 Decide the upscale once

Upscale once, after lock, the same way for every clip ([[10-deep-dive-scene-continuity]] §2.2):

| Route | Verdict |
| ----- | ------- |
| Flow 1080p upscale: **0 credits** on AI Pro, any model. Flow Help: More → Download (270p is the GIF; pick the 1080p size, check live) | ✔ all 31 shots |
| Flow 4K (Ultra only, 50 credits), Resolve Super Scale (Studio), Topaz Video (paid, $399/yr) | ✘ (free Resolve can't encode ≥ 4K anyway) |
| Local ComfyUI, Real-ESRGAN ×4 ([[../comfyui/04-phase-4-video\|ComfyUI Phase 4]] §5): free, slow | only for a shot Flow can no longer upscale; expect a different texture, evened out by the grain (§6) |

Deliver **1080 × 1920**. Meta's Reels-ads guide recommends 1440 × 2560, but stretched pixels add no detail.

### 2.3 The mark that stays

Every Flow output carries an invisible **SynthID** watermark that Flow Help says "should not be tampered with or removed". Flow Help also says **a visible watermark will be applied automatically if you reside in India** (or South Korea or Vietnam). Elsewhere a "Visible watermarking" toggle under the profile picture controls it; for India, Flow Help names no plan that switches it off and gives no reason. (Separately, Indian law since 20 February 2026 makes AI tools label synthetic media and not let users remove the label: §12.)

So the visible mark is in all 31 generated shots, through grade, upscale and export. **It stays. This course does not teach removing, cropping out, blurring, covering, darkening or otherwise hiding it.** Three working rules:

- No scale, crop or reframe may push the mark out of frame. A punch-in is for composition only ([[18-editing-2-rhythm-structure-and-rescue]]); one that would lose the mark has become a way round it, so skip it.
- No caption, logo, graphic, vignette or window may sit over the mark or dim it.
- If a shot doesn't work with the mark where it is, regenerate the shot; never cover the mark.

Note the box the mark occupies in one downloaded take, and add it to your safe-zone guide (§9) as a keep-clear area.

## 3. Scopes for People Who Are Not Colourists

A **scope** draws numbers about the picture instead of the picture. Your eyes adapt to whatever they watch; a scope doesn't (Cullen Kelly, §16). Open **Workspace → Video Scopes → On** (Command-Shift-W), 4-up; in each scope's three-dot menu set **Waveform Scale Style → Percentage** (0 black, 100 white).

| Scope | What it draws | Read this | Saaf Hisaab (example readings) |
| ----- | ------------- | --------- | ------------------------------ |
| **Waveform** | every pixel's brightness, laid out left to right as in the picture | the **floor**, the **skin band**, the **peak** | night hero S1-04: floor 4 %, Ravi's cheek 41 %, desk lamp 93 % |
| **Parade** | the same, split into red, green and blue side by side | do the channels line up where the scene should be neutral? | S3-01's white canopy: equal tops = white; a low blue top = an orange cast |
| **Vectorscope** | colour only: angle = hue, distance from the centre = saturation | the **skin cluster** against the skin-tone line | both men's cheeks on the line in every shot; the teal case a spike of its own |

Tick **Show Skin Tone Indicator** (a line the manual calls "a general guidepost for average skin tone hue") and **Show 2X Zoom**. Healthy skin of every complexion sits on or near that line; people differ in brightness and saturation, not hue (Kelly), so it serves Ravi and Kishan alike.

**The column trick.** The waveform keeps the picture's left-to-right layout; in a 9:16 MCU the face fills the middle columns, so the middle of the waveform *is* the skin.

**Three numbers per scene** (floor, skin, peak) go from each scene's hero into the grade sheet (§13). Matching becomes arithmetic, not taste.

## 4. Balance, Then Match — Skin Is the Anchor

**Balancing** makes one shot right on its own: exposure, black floor, highlight peak, no colour cast the Look Sentence didn't ask for. **Matching** makes it equal to its neighbours. Faces top the ladder of what audiences notice ([[15-continuity-bible-script-supervisor]]): match the faces and they forgive a wall that drifts.

**The heroes** are the three hero-face Quality locks: **S1-04** (night), **S3-05** (dusk), **S4-05** (morning). Kishan's are **S2-02** (night) and **S3-09** (dusk).

**The procedure** (Color page, Node Editor in **Clip** mode; a **node** is one step of a grade, and Option-S adds the next step after the selected one):

```
HERO, once per scene
 1  Node BAL: Lift master → floor to the scene number; Gain master → peak; Gamma master
    → skin. Temp / Tint only to remove a cast the Look Sentence didn't ask for.
 2  Color → Stills → Grab Still (Option-Command-G). Write floor / skin / peak in the sheet.

EVERY OTHER SHOT
 3  Node BAL: the same moves, to the hero's floor and peak.
 4  Node MATCH: play the hero still as a wipe (Command-W, or double-click it in the
    Gallery) and match in this order:
      a. skin level   Gamma master until the cheek reads the hero's % (±3 %)
      b. skin hue     small moves of the Gamma wheel until the cluster sits on the line
                      at the hero's angle
      c. saturation   Sat (50 = unchanged) until the cluster is as long as the hero's
      d. background   lamp warmth, window blue: last, and only if they distract
 5  Judge in the cut, not in the wipe: play the scene through.
```

**Worked: S2-03 → S1-04.** S2-03 arrives at floor 7 %, cheek 46 %, its cluster longer than the hero's and slightly toward yellow. Lift master down to a 4 % floor, Gamma master down to a 41 % cheek, Gamma wheel nudged until the cluster sits on the line, Sat 47. Cut S1-04 → S2-03 and play: one man, one lamp.

**Shot Match, the free shortcut** — it replaces the moves of steps 1, 3 and 4 rather than following them (A overwrites node BAL); keep step 2's still to trim against. The 21 manual says it is built to run after the **A** (Auto Color) button on every clip involved, hero included, with the matched clips otherwise ungraded: press A on node BAL of each clip, Command-click the clips, right-click the hero → **Shot Match to This Clip**. The correction goes invisibly into the selected node, and it makes clips the same, not good. Trim on node MATCH.

Across the three story days Ravi's skin **level** changes by design; its **hue** never leaves the line. A level change reads as different light; a hue drift reads as a different man.

## 5. The Look as a Node Tree

A **node** is one step of a grade; the **node tree** is the chain. Resolve runs four trees in a fixed order, **Group Pre-Clip → Clip → Group Post-Clip → Timeline**; a **group** is a set of clips sharing the group trees, and the manual names Post-Clip as the place for "a creative look to an overall scene":

```
EACH SHOT — Clip mode         EACH SCENE — Group Post-Clip        WHOLE FILM
BAL ─► MATCH (─► FIX)   ─►    LOOK ─► ACCENT ─► VIG         ─►   adjustment clip on V2:
exposure  skin to  a window   scene    keep the   soft edges,     Fusion Film Grain (§6)
          hero     if needed  colour   teal teal  ≤ 5 %
Timeline mode stays empty: it touches every clip, the end card's brand teal included.
```

Select a scene's thumbnails, right-click → **Add Into New Group**: NIGHT_OFFICE = S1-01–S2-08 (14 shots), DUSK_FORECOURT = S3-01–S3-11 (11), MORNING_OFFICE = S4-01–S4-06 (6); S4-07 stays out. Pick **Group Post-Clip** in the Node Editor's mode menu and build each look on its hero.

**One family, three looks**, set by the Look Sentences ([[10-deep-dive-scene-continuity]] §7.3) and the colour script in [[13-visual-language-composition-blocking-light]]. Hold constant in all three: the soft, low-contrast curve with a 3–5 % floor, muted saturation with one teal accent, skin hue on the line, one grain, one vignette. Let change: the key light (tungsten → amber → daylight), the brightness (low-key night → high-key morning), how cool the shadows are, and the sky and window colour.

- **NIGHT:** Lift wheel a touch blue (cool shadows), Gain wheel a touch warm (the lamp), Contrast slightly down, Sat 45.
- **DUSK:** Gain toward amber, neutral-cool shadows, no contrast push in the sky (banding, §7). Dusk turns blue by S3-11, so give S3-08 → S3-11 small, equal Temp steps cooler at clip level; the change only ever goes one way. A planned drift is continuity; a random one is a fault.
- **MORNING:** the cleanest light. Warm-neutral Gain, floor 5 %, Sat 50. Relief, in colour.

**ACCENT** keeps the teal teal: open **Hue vs. Sat**, click the phone case in the viewer (Resolve drops three points on that hue) and lift it until the case reads the same in all three scenes and, later, matches the logo. **VIG:** Window palette → Circular → Invert, raise Soft 1, lower the Gamma master until the corners drop no more than 5 %, never over the watermark: if the mark sits in a corner, move or reshape the window so that corner stays undimmed, or leave the vignette out.

Three checks before you leave colour. **Split Screen → Current Group** (Option-Command-W) should read as one room at one hour. **The dissolve** S3-11 → S4-01: on frame 6 of 12, if the parade goes muddy, start S4-01 a touch cooler. **The bookend:** S1-02 beside S4-06 (Split Screen → Selected Clips) should be one frame in opposite light.

## 6. Texture — Grain, Sharpening, Softening, Vignette in the Free Edition

**Texture** is the picture's fine surface. One grain over every shot makes the finest detail come from the grain rather than from whichever crew made the shot; that is how uniform texture hides mixed sources, like Fast and Quality locks side by side.

| Texture | Free route in 21.1 | Studio-only twin | Saaf Hisaab |
| ------- | ------------------ | ---------------- | ----------- |
| Grain | **Fusion page → Film Grain node** on an adjustment clip | ResolveFX Film Grain, Halation, Film Look Creator | Size 1.0, Strength 0.015, Log Processing on, Monochrome on, Time Lock off |
| Sharpen | **Blur palette → Sharpen**: Radius below 0.50; raise Level until flat skin stops sharpening | ResolveFX Sharpen, Sharpen Edges, Soften & Sharpen, UltraSharpen | only a shot softer than its neighbours, clip level, before the grain |
| Soften | Blur palette → **Mist**: lower Radius and Mix together | Beauty, Lens Blur | none: the Look's softness is baked in |
| Vignette | Window palette, Circular, inverted (§5) | — | ≤ 5 %, never over the mark |
| Noise reduction | Fusion Remove Noise node (documented, untested) | temporal, spatial, UltraNR | not needed on Veo footage |

**Build it once.** Effects Library → Toolbox → Effects → drag an **Adjustment Clip** onto V2, from S1-01 to the end of S4-06. Select it, open the Fusion page, select MediaIn1, press Shift-Space, type "Film Grain", press Return, set the values above. In the manual's example, Strength 0.02 lets a mid-grey pixel wander ±2 %; go lower, because platforms re-encode and heavy grain turns to blocky mush.

**The trap.** On the Edit and Color pages, Shift-Space finds the **ResolveFX** Film Grain (Studio-only, same name); practitioners report that a Studio-only effect stamps a watermark on a free render. The Fusion route is documented, not test-rendered for this course: render 5 seconds and look first.

## 7. AI Artefacts — What Helps, What Hurts, What Can't Be Fixed

| Artefact | Looks like | Helps (free) | Makes it worse | Can't fix → |
| -------- | ---------- | ------------ | -------------- | ----------- |
| **Banding** | steps in the dusk sky, the canopy glow, a plain wall | gentle curves on gradients; the grain, which dithers the steps (8-bit has 256 levels, each ≈ 0.4 %; ±1.5 % grain spans several) | contrast or saturation pushed in the sky; sharpening; a low-bitrate export | Deband is Studio-only → regenerate the board with less empty sky |
| **Crushed / milky blacks** | Ravi's hair melting into the night window / grey haze over everything | Lift or Shadows until the floor reads the scene number | a low-contrast look stacked on an already milky clip | detail crushed in the source is gone |
| **Plastic skin** | waxy, poreless faces | the grain; slightly less skin saturation (Hue vs. Sat); Midtone Detail never below 0 | Mist, negative Midtone Detail, sharpening | regenerate with natural skin texture in the board still ([[14-previs-storyboard-floorplan-animatic]]) |
| **Flicker, shimmer** | brightness pulsing; Kishan's checked gamchha or the register lines boiling | use the stable 2–3 s; keyframe Gain against a slow pulse | sharpening | Deflicker is Studio-only → regenerate |
| **Edge crawl** | the doorframe or the tanker's stripe swimming | cut shorter; a hair of blur in a window | sharpening | regenerate |
| **720p softness** | one shot softer than its neighbours | re-download at 1080p (⏣0), then Blur-palette Sharpen with Level raised | upscaling twice; mixing upscalers | lost detail |

## 8. Graphics, the Real Screen, and Captions

### 8.1 One graphics system

One font, one caption style, one logo, one card. **Mukta** (Ek Type; SIL Open Font License, on Google Fonts) has seven weights and Latin plus Devanagari in one family. The logo is the brand-kit PNG, never generated; colours come from the brand palette (teal and white, [[05-phase-5-character-consistency]] §7). All text sits inside the safe box (§9); none is AI-rendered.

### 8.2 The end card, S4-07 (3 s = 72 frames)

```
V1  Generators → Solid Color, brand white
V2  logo PNG: Inspector → Transform, centred, ≈ 500 px wide, centre near y 760
V3  Text+  "DZZLO OMS — get the app."      Mukta Bold, centred near y 1000
V4  Text+  "Audio/Video created using AI"  Mukta Regular, caption size, near y 1180
```

The last line is ASCI's suggested wording (§12), and it travels into WhatsApp forwards, where no platform label exists.

### 8.3 Compositing the real app screen — S3-04 and S4-03

The app screen is never a Veo render ([[10-deep-dive-scene-continuity]] §6.5). Screen-record the real app on a demo account (no real dealer, driver or vehicle data) as the order arrives with Company ✓ Manager ✓ Driver ✓ Vehicle ✓. Open the plate (S4-03 or S3-04) in the Fusion page and drag the recording from the Media Pool into its Node Editor; it arrives as MediaIn2.

**S4-03, the phone still on the desk.** MediaIn2 → **Corner Positioner** → **Merge** (foreground) over MediaIn1 → MediaOut. Drag the four corners onto the glass, and keyframe the Merge's **Blend** from 0 to 1 over 4–6 frames as the plate's screen lights up.

**S3-04, the phone rising.** Feed MediaIn1 into a **Planar Tracker**'s orange Background input. On a frame showing the whole phone, click **Set**, draw a polygon round the **phone and its teal case** (a blank glowing screen has nothing to track), click **Track Forward**. Then **Operation Mode → Corner Pin**, MediaIn2 into **Corner Pin 1**, corners onto the glass, Merge Mode **FG over BG**, tracker output to MediaOut. Use the settled part of the 4 s; a thumb across the glass means hand-masking every frame, so fix that at the board ([[14-previs-storyboard-floorplan-animatic]]).

**Sit it in the shot:** its white just under the plate's brightest highlight (real screens are never paper-white); a small **Blur** until its edges match the case; a gentle **Soft Glow** for spill; a **Background** gradient merged in Screen mode at 5–10 % for the glass. A screen is its own light, so keep it slightly cooler and cleaner than the dusk, pulling it back with a clip-level window if the scene look turns the UI orange. Then step through S3-07: no fake UI text may be legible under the thumb.

### 8.4 Captions

**Mix for sound-on, caption for sound-off.** A **sidecar** is a caption file (.srt) beside the video that viewers switch on; **burn-in** prints captions into the picture. No sidecar option was found for Instagram organic or WhatsApp, so they get burn-in; YouTube and LinkedIn take an .srt. Hence two masters (§10).

In free Resolve: right-click a track header → **Add Subtitle Track**; Inspector → Captions → **Create Caption** per line; style the track in the **Track** panel (Mukta SemiBold, white, dark **Background** box, centred) and keep it with **Save Track as Preset**. Auto-captions are Studio-only; for six lines, typing wins.

BBC 9:16 guidance: line height **3.9–4.5 % of frame height** (≈ 75–86 px at 1920), up to three lines (use two), breaks at punctuation. Its 25 characters across 90 % of the width become about **21–23** across our 823-px safe width. Bottom edge at or above **y 1248**.

The six lines as written, in Latin-script Hinglish, timed from the line windows in file 19's cue sheet ([[19-sound-edit-design-and-mix]] §12). The rule: each caption comes in on its line's first frame and goes out 6 frames after its last; if a take moves a line, move its caption. The BBC puts a phone voice in single quotes:

```
1
00:00:18,167 --> 00:00:20,917
'Payment ho gaya tha,
Ravi ji!'

2
00:00:21,250 --> 00:00:24,000
Sahab, gaadi khadi hai.
Kab tak?

3
00:00:25,667 --> 00:00:28,917
Kaun si gaadi thi?
Kaun sa driver?

4
00:00:35,500 --> 00:00:37,417
Register mein
nahin hai.

5
00:01:02,417 --> 00:01:03,167
Bas?

6
00:01:04,500 --> 00:01:05,250
Bas.
```

For a Devanagari track, check "रजिस्टर में नहीं है।" at 100 %: a bad text engine breaks the half-letter in स्ट first. If it breaks, ship Latin script.

## 9. The 9:16 Safe Zones — Measured

A **safe zone** is the part of the frame no app button or text covers. Platforms publish different margins; take the strictest for each edge:

| Edge | Meta Reels ads (Instagram, Facebook) | Google / YouTube vertical ads, incl. Shorts | **Use** |
| ---- | ------------------------------------ | ------------------------------------------- | ------- |
| Top | 14 % ≈ 269 px | 288 px | **288 px** |
| Bottom | 35 % = 672 px | 672 px | **672 px** |
| Left | 6 % ≈ 65 px | 48 px | **65 px** |
| Right | 6 % ≈ 65 px | 192 px | **192 px** |

LinkedIn only says to keep the edges clear; organic Shorts and WhatsApp publish nothing. Use the union everywhere:

```
  x: 0  65                                          888       1080
y=0    ┌──────────────────────────────────────────────────────┐
       │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
       │░░░░░░░░░░░░░░ top 288 px — app UI ░░░░░░░░░░░░░░░░░░░│
 288   │░░░┌─────────────────────────────────────────┐░░░░░░░░░░│
       │░░░│                                         │░░░░░░░░░░│
       │░░░│   TEXT & LOGO BOX                       │░ right ░░│
       │░░░│   x 65–888 · y 288–1248                 │░ 192 px ░│
       │░░░│   823 × 960 px                          │░ app UI ░│
       │░░░│                                         │░░░░░░░░░░│
       │░░░│   faces and action may go anywhere;     │░░░░░░░░░░│
       │░░░│   text and logos stay in here           │░░░░░░░░░░│
       │░░░│   captions: bottom of the box           │░░░░░░░░░░│
 1248  │░░░└─────────────────────────────────────────┘░░░░░░░░░░│
       │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
       │░░░░░░░░░░░░░░ bottom 672 px — app UI ░░░░░░░░░░░░░░░░│
       │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│
 1920  └──────────────────────────────────────────────────────┘
```

A guide to lay over the timeline, a transparent PNG with 35 % red bands (tested 2026-10-01 with ffmpeg 7.1):

```sh
ffmpeg -f lavfi -i "color=c=black@0:s=1080x1920,format=rgba" -vf "drawbox=0:0:1080:288:red@0.35:fill:replace=1,drawbox=0:1248:1080:672:red@0.35:fill:replace=1,drawbox=0:288:65:960:red@0.35:fill:replace=1,drawbox=888:288:192:960:red@0.35:fill:replace=1" -frames:v 1 -update 1 safe_916_guide.png
```

Add the watermark's keep-clear area with one more `drawbox=X:Y:W:H:yellow@0.5:fill:replace=1` from your §2.3 measurement. Put the PNG on the top video track; switch that track off before rendering.

## 10. Export — Masters, Platforms, Archive

A **master** is the best file of the film you will ever make; every platform re-encodes from it. Deliver page, one **Single clip** render per master:

```
Format MP4 · Codec H.264 · Resolution 1080 × 1920 (the timeline's) · Frame rate 24
Quality: Restrict to 16,000 Kb/s · Encoding Profile High · Entropy Mode CABAC
Key Frames: every 12, only if shown (the manual lists the field for QuickTime H.264)
Audio: AAC · 48,000 Hz · 320 kb/s · the file 19 mix, untouched by export
Subtitle Settings: Export Subtitle ✓ → Burn into video                  (burnin master)
                                    → As a separate file, Export As SRT  (clean master)
File: Use Custom Filename → saaf-hisaab_master_v01_burnin_render
```

16 Mbps is twice YouTube's 1080p recommendation; grain needs the bits. YouTube also wants the file's index (the "moov") at the front, and the 21 manual offers no setting for it, so finish each MP4 with this tested line:

```sh
ffmpeg -i saaf-hisaab_master_v01_burnin_render.mp4 -c copy -movflags +faststart saaf-hisaab_master_v01_burnin.mp4
```

| Platform | File | Length | Label (§12) |
| -------- | ---- | ------ | ----------- |
| Instagram Reels | `_burnin` | organic: up to 20 min (third-party); ads: 0 s–15 min | AI label in the posting flow |
| YouTube Shorts | `_burnin` (no .srt, or the text doubles) | up to 3 min; as an **ad**, only the first 60 s play in the feed → the 60 s cut ([[18-editing-2-rhythm-structure-and-rescue]]) | AI use: Yes |
| Facebook | `_burnin` | no length limits for Reels (Meta, 2025) | AI label |
| WhatsApp | `_burnin` | Status up to 90 s (third-party): the 90.0 s film sits on the line, so Status gets the 60 s cut; send the full film as a **Document** (reported to skip recompression; 2 GB limit) | none in-app → the end card |
| LinkedIn | `_clean` + `.srt` | 3 s–15 min; ≤ 30 Mbps; ProRes won't process | none found → the end card |

**Archive** (file 21 scales it up): both MP4s and the .srt; a ProRes 422 HQ `.mov` copy, never uploaded; **Export Project Archive** (.dra, project plus media; right-click the project in the Project Manager); stills, prompt and take logs, screen recordings, font licence, music terms, the §13 sheet, the QC record, and screenshots of each AI-label setting.

## 11. Technical QC — the Pass List

This extends [[08-phase-8-pro-workflow-and-playbooks]] §4. Run it on the exported file, not the timeline.

```
PICTURE
[ ] ffmpeg -hide_banner -i FILE → h264 (High), yuv420p, 1080x1920, 24 fps, Duration 00:01:30
    (its last line, "At least one output file must be specified", is expected: it only reads)
[ ] no black frames, except a fade into the card if it goes through black:
    ffmpeg -hide_banner -nostats -i FILE -vf blackdetect=d=0.04:pix_th=0.10 -an -f null -
[ ] every face on the skin line and inside ±3 %; no clipped faces; no hair lost in black
[ ] the watermark present wherever Flow put it: not cropped, covered, blurred, mirrored or dimmed
[ ] real screens stick to the phone; demo data only; no fake UI text anywhere (S3-07)
[ ] no real oil-company logo, pump name or readable number plate in any shot
[ ] watched on a real phone, at full and at half brightness
SOUND (the mix is file 19's; QC only measures)
[ ] ffmpeg -hide_banner -nostats -i FILE -af ebur128=peak=true -f null -
    Summary → I: −14 LUFS (±1) · True peak → Peak: ≤ −1.0
[ ] AAC, 48 kHz, stereo
TEXT
[ ] frames at 19 s, 63 s and 88 s with the guide on top, nothing in a red band:
    ffmpeg -ss 00:00:19 -i FILE -i safe_916_guide.png -filter_complex overlay -frames:v 1 -update 1 qc_19s.png
    ffmpeg -ss 00:01:03 -i FILE -i safe_916_guide.png -filter_complex overlay -frames:v 1 -update 1 qc_63s.png
    ffmpeg -ss 00:01:28 -i FILE -i safe_916_guide.png -filter_complex overlay -frames:v 1 -update 1 qc_88s.png
[ ] the six captions match the script word for word; ≤ 2 lines; CTA reads "DZZLO OMS — get the app."
LEGAL
[ ] product truth only; no "real dealer" or "true story" framing; no real person's likeness or voice
[ ] font licence and music terms filed; disclosure done per §12
```

## 12. AI Disclosure — Platform Policy, Indian Law, Self-Regulation

*This is information, not legal advice. Each row says what kind of rule it is. Before a paid campaign, ask a lawyer.*

| Rule | It is | What it says | Saaf Hisaab → do this |
| ---- | ----- | ------------ | --------------------- |
| **YouTube "AI use"** | Platform policy | Disclose realistic AI, including content that "generates a realistic scene that didn't actually occur"; AI-generated music must be disclosed; colour fixes, captions and upscaling need not. Disclosure "won't limit a video's audience or impact its eligibility to earn money" | Photoreal scenes plus AI music → YouTube Studio, upload → Attributes → **AI use: Yes**. Don't wait for an automatic label |
| **Meta "AI info"** (Instagram, Facebook) | Platform policy | Requires its disclosure tool for "photorealistic video or realistic-sounding audio that was digitally created or altered", and may penalise failure | Turn on the AI label on the final posting screen (third-party guides call it "Add AI label"; Meta's help page could not be read) |
| **Google Ads AI label** | Platform policy | "AI regulations in the European Union, India, and New York require" labels on certain AI ads; the setting "doesn't guarantee your compliance" | If it runs as an ad: the label setting plus the end-card line |
| **IT Rules amendment 2026** (G.S.R. 120(E), notified 10 Feb, **in force 20 Feb 2026**) | **Law** (India) | **Synthetically generated information (SGI)** is AI audio or video that appears real and shows a person or event as indistinguishable from a real one; routine editing, colour adjustment, noise reduction and transcription are excluded. Duties fall on platforms: AI tools must not allow SGI that falsely depicts a real person or event in a way likely to deceive, must label the rest prominently, with permanent metadata, and must not let users remove either (Rule 3(3)); large platforms must take an uploader's declaration, verify it and label, so that nothing synthetic is published without the declaration or label (Rule 4(1A)). No label size is set; the draft's 10 % was dropped | It fits MeitY's own example of SGI: "an AI-generated realistic video clip of a person (virtual human) speaking". When a platform asks whether the upload is AI-generated, answer **Yes**. Never strip a label or metadata; a Resolve render carries no provenance metadata from Flow's files into your master (the 21 manual documents no Content Credentials), which is why you declare and label by hand |
| **MeitY "Second Amendment"** (March 2026) | **Draft**, not in force | About platforms following ministry advisories, not about labels | Nothing changes today; watch it |
| **ASCI guidelines** (signed 17 Sep 2026; effective 3 months after publication, about **end-December 2026**) | **Self-regulation**, not law | A label is mandatory for synthetic ambassadors and for fabricated events or settings that may affect how consumers understand the product. Banned even with a label: AI testimonials passed off as a real person's, exaggerated results, non-existent places shown as real, a likeness used without consent. No label for colour correction, ambient music or subtitles. Suggested wording: "Audio/Video created using AI" | Ravi is a synthetic brand ambassador → the end-card line. Never present him as a real customer |

## 13. The Grade and Delivery Sheet

```
GRADE & DELIVERY SHEET — saaf-hisaab_master_v01 · Resolve 21.1 free · 1080×1920 · 24 fps
GROUP           SHOTS        HERO (Kishan)  FLOOR  SKIN (Ravi)  PEAK    NOTES
NIGHT_OFFICE    S1-01–S2-08  S1-04 (S2-02)  4 %    38–44 %      ≤ 95 %  warm lamp, cool window, teal case
DUSK_FORECOURT  S3-01–S3-11  S3-05 (S3-09)  3 %    42–48 %      ≤ 95 %  amber → blue S3-08→S3-11, one way; sky banding
MORNING_OFFICE  S4-01–S4-06  S4-05          5 %    52–58 %      ≤ 97 %  high key; Sat 50
S4-07 card outside all groups · Timeline mode empty · grain: adjustment clip V2, Film Grain 1.0 / 0.015
CHECK  dissolve mid-frame · bookend S1-02/S4-06 · tanker stripe S2-06/S3-01/S4-04 · screens S3-04, S4-03
SHIP   _burnin.mp4 · _clean.mp4 + .srt · ProRes archive · faststart · QC §11 · labels §12
```

The floor and skin bands are this film's targets, read off its heroes. Set yours the same way.

## 14. What Finishing Cannot Fix

- **Detail that was never generated.** An upscale makes pixels, not pores; 4K is out of reach on AI Pro and in free Resolve.
- **Wrong content.** A drifted face, the phone in the wrong hand, a broken eyeline: no grade moves them. Regenerate ([[15-continuity-bible-script-supervisor]], [[18-editing-2-rhythm-structure-and-rescue]]).
- **Baked-in banding or flicker** in the free edition: Deband and Deflicker are Studio-only.
- **The platform's re-encode.** Your master is the best the film will ever look; the feed will look a little worse.
- **A phone the tracker can't hold.** A fast, half-covered phone needs a shot designed for the composite.
- **The mark and the label.** Both stay, and a label doesn't make a misleading ad acceptable (ASCI).

## 15. Exercises

**15.1 — Read three scopes (0 coins).** Three of your clips with a face; Percentage scale, skin indicator, 2X zoom. Artefact: floor, skin and peak for each, and whether each cluster sits on the line.

**15.2 — Match by hand, then by machine (0 coins).** Two clips of one character from different generations. Duplicate the timeline; match copy A with the §4 procedure and copy B with A + Shot Match to This Clip. Artefact: skin % and angle for both, and the one you keep.

**15.3 — One scene, one tree (0 coins).** Group one scene, build a LOOK in Group Post-Clip, check Split Screen → Current Group, then change the LOOK once and watch every clip follow. Artefact: a Gallery still of the grid.

**15.4 — Grain and the trap (0 coins).** Fusion Film Grain on an adjustment clip at 0.01, 0.015 and 0.03: render 5 s of each, watch on your phone, upload one as an unlisted YouTube video to see what survives, and confirm no Blackmagic watermark. Artefact: your chosen strength.

**15.5 — A screen on a still phone (0 coins).** Record 5 s of the app on a demo account and composite it onto any still phone with a Corner Positioner and the §8.3 moves. Artefact: a 3-second render; ask someone whether the screen is real.

**15.6 — Guide, master, QC (0 coins).** Make the §9 PNG with your watermark's keep-clear area. Export burn-in and clean masters of any finished piece, run faststart, then every §11 check, overlay frames included. Artefact: the guide PNG and the filled QC record.

**15.7 — Fix or regenerate? (~⏣20).** Give your worst artefact shot the §7 free fixes for 15 minutes, then regenerate it once on Fast from the same board still. Artefact: both side by side, and a one-line verdict on which ships.

## 16. Sources (web-verified 2026-10-01)

Primary, Blackmagic Design:

- [DaVinci Resolve 21 Reference Manual (July 2026)](https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_21_Reference_Manual.pdf): all Resolve steps here
- [Resolve 21.1 Studio and iPad Features](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_Studio_21_Features.pdf): the Studio-only list; [Supported Codec List](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_21_Supported_Codec_List.pdf): ≥ 4K encode is Studio

Primary, Google:

- Flow Help: [FAQ](https://support.google.com/flow/answer/16353333) (SynthID, visible watermark); [Download & YouTube](https://support.google.com/flow/answer/16935308); [Credits](https://support.google.com/flow/answer/16526234) (upscaling)
- YouTube Help: [Disclosing GenAI content](https://support.google.com/youtube/answer/14328491); [Upload encoding](https://support.google.com/youtube/answer/1722171); [Shorts length](https://support.google.com/youtube/answer/12779649); [Captions](https://support.google.com/youtube/answer/2734698)
- Google Ads Help: [Shorts ads and AI labels](https://support.google.com/google-ads/answer/16041697); [Vertical safe zone](https://support.google.com/google-ads/answer/9128498)
- [Google Fonts: Mukta](https://fonts.google.com/specimen/Mukta); [ofl/mukta metadata](https://github.com/google/fonts/tree/main/ofl/mukta)

Primary, Meta, LinkedIn, WhatsApp:

- [Instagram Reels ads guide](https://www.facebook.com/business/ads-guide/update/video/instagram-reels); [Reels ads, "Sound On"](https://www.facebook.com/business/ads/facebook-instagram-reels-ads); [AI labels (Feb 2024)](https://about.fb.com/news/2024/02/labeling-ai-generated-images-on-facebook-instagram-and-threads/); ["AI info" (2024)](https://about.fb.com/news/2024/04/metas-approach-to-labeling-ai-generated-content-and-manipulated-media/); [AI in ads (2026 update)](https://about.fb.com/news/2025/02/gen-ai-transparency-metas-ads-products/); [Facebook Reels (2025)](https://about.fb.com/news/2025/06/making-it-easier-create-videos-facebook/)
- [LinkedIn video specs](https://www.linkedin.com/help/linkedin/answer/a548372); [LinkedIn captions](https://www.linkedin.com/help/linkedin/answer/a552177); [WhatsApp 2 GB files](https://blog.whatsapp.com/reactions-2gb-file-sharing-512-groups)

Primary, India:

- MeitY: [IT Rules as amended to 10.02.2026](https://www.meity.gov.in/static/uploads/2026/02/550681ab908f8afb135b0ad42816a1c9.pdf); [FAQ on the 2026 amendment](https://www.meity.gov.in/static/uploads/2025/10/065b6deb585441b5ccdf8be42502a49c.pdf); [Draft Second Amendment](https://www.meity.gov.in/static/uploads/2026/03/30591fc6e322dcbcc9dae84a0f02e9e7.pdf)
- [ASCI guidelines on labelling synthetic content in advertising](https://www.ascionline.in/wp-content/uploads/2026/09/Guidelines-for-Responsible-Labelling-of-Synthetically-Generated-Content-in-Advertising.pdf)

Standards and tools:

- [BBC Subtitle Guidelines](https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/): 9:16 sizes, lines, position, phone voices
- [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html): every command here was run with ffmpeg 7.1 on 2026-10-01
- [Topaz pricing](https://www.topazlabs.com/pricing); [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN)

Secondary and craft:

- [Cullen Kelly, "5 Tips for Getting Perfect Skin Tones in DaVinci Resolve" (Frame.io Insider)](https://blog.frame.io/2020/10/05/skin-tones-in-davinci-resolve/): scopes over eyes; one narrow hue range for all skin
- [MxM India on ASCI (30 Sep 2026)](https://www.mxmindia.com/advertising/asci-issues-guidelines-for-labelling-synthetically-generated-content-in-advertising/); [Khaitan & Co on the 2026 amendment](https://www.khaitanco.com/thought-leadership/MeitY-notifies-the-IT-Amendment-Rules-2026) (10 % label dropped); [Minter.io on Instagram AI labels (2024)](https://minter.io/blog/everything-you-need-to-know-about-ai-labels-on-instagram/)

---

**Previous:** [[19-sound-edit-design-and-mix]] · **Next:** [[21-long-form-multi-scene-production]] · **Track map:** [[11-directors-track-roadmap]] · **Back to:** [[00_README]]
