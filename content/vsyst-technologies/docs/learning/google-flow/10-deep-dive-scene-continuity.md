# Deep Dive — Scene Continuity Past 8 Seconds: What Extend Really Does, Why the Last-Frame Trick Goes Soft, and the Fixes

> Level: Intermediate → Advanced | Time: ~2.5 hr | Outcome: you know *exactly* what Flow does at the join between two clips, you stop being surprised when Extend "changes" your clip, and you have three working recipes for a continuous shot longer than 8 seconds that doesn't drop in quality at the seam — plus a director's method for breaking a scene into shots and choosing the transition between them (§5–6), and the cohesion stack that makes a ten-clip cut look like one film (§7). | Status: written & web-verified **2026-09-25** against the Veo 3.1 API docs, Flow Help, and the Keyword post on Flow's Veo 3.1 tools. Sources in §12.

---

## Explain-it-like-I'm-5

Remember: every 8-second clip is shot by a **fresh robot crew that never met the last one** ([[00_README]] catch #1). So how do you make a 24-second shot? Only two ways, and both are hand-overs between crews:

- **Extend** — the new crew is allowed to watch the **last one second** of the old crew's film. They **re-shoot that second** so their footage lines up, then keep filming. They hand you back **one film** (old + new) — and the whole thing comes back in the **small format** (720p), whatever format the old film was in.
- **Last-frame → Frames to Video** — you take a **photocopy of the last picture** of the old film and tell a brand-new crew "start from this." A photocopy of a movie frame is blurry. The new crew starts from a blurry picture, has never seen the old film's lighting, lens, or colours, and guesses the rest.

That's the whole explanation of both problems you've hit. Everything below is the fix.

## 1. The Two Problems, One Cause

| You see                                                           | What is actually happening                                                                                                                                                     | Fix family (§)      |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- |
| "I extended my clip and the **previous part changed too**"        | Extend **re-generates the final second** (24 frames) as its seed, re-rolls the audio across the join, and returns **one merged file at 720p** — so the "old" part is softer if you were looking at a 1080p/4K upscale | §2                  |
| "I used the **end frame as a start image** and the new clip's **quality / look doesn't match**" | The frame is a **compressed video frame** (soft, mid-motion), and the new generation re-rolls lens, light, colour, grain and everything not visible in that one picture          | §3                  |

The cause is the same: **a clip carries no memory forward except 24 frames (Extend) or 1 frame (Frames→Video).** Lighting, lens, colour grade, grain, audio bed, and every detail hidden from that seed are re-invented by the next generation. Continuity is therefore something you *engineer at the join*, not something the tool promises.

## 2. Problem A — "Extend changed my previous clip"

### 2.1 What Extend really does (facts, not vibes)

From Google's own docs (Gemini API for Veo 3.1, read 2026-09-25) and the Keyword post announcing the Flow tools:

| Fact                                                                                                | Consequence for you                                                                                       |
| --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| "Extend **finalizes the final second (24 frames)** of your video and continues the action"          | The last second of your clip is **re-generated** — motion, light, and sound in that second can shift      |
| "Each video is generated based on the **final second** of your previous clip"                        | Nothing before that second is seen by the new generation — identity comes from those 24 frames only       |
| Output is "a **single video combining** the user input video and the generated extended video"      | What you see in Scenebuilder is a **new merged file**, not your original with a bit added                 |
| Extension output is **"720p only"**                                                                 | If your base clip was upscaled to 1080p/4K, the merged file drops the *whole* thing back to 720p          |
| Adds **7 s** per extension (Flow / Vids UI says "8 s"); up to **20** extensions, max **148 s**      | Long takes are possible; drift and softness compound with each hop                                         |
| Input must be **Veo-generated**; works on **Veo 3.1 and 3.1 Fast only — not Lite**                  | You can't draft an extend chain on the 10-coin tier; budget Fast (~⏣20) or Quality (~⏣100) per hop        |
| Cannot combine with **Ingredients** or **first/last frame** in the same call                        | Identity during an extension comes from the last second, not from your reference photos                   |
| "Voice is not able to be effectively extended **if it's not present in the last 1 second**"          | Dialogue must either **finish clearly before** the last second or **still be running through** it         |
| Flow Help: you can't apply **Insert / Remove / Camera** edits to extended clips; Scenebuilder can **trim** the start/end of a clip | Do your object edits *before* extending; trimming is your seam scalpel                    |
| Flow Help: the original clip in your library is **not modified**                                    | Your 8-second original is safe — the "changed" clip is the merged output on the timeline                  |

So the three things that "changed" are exactly: **(1)** the seam second was re-shot, **(2)** the merged output is 720p, **(3)** the audio bed across the join was re-generated. None of it is a bug. It's the hand-over.

### 2.2 The fixes, in order of effect

**1. Work the whole chain at 720p, upscale once at the end.** Never upscale the base clip and then extend it — you're paying for pixels the merge throws away. Base at 720p → extend → extend → *then* upscale the finished clip (Flow's **Upscale** on the clip: 1080p on AI Pro, 4K on Ultra), or upscale the whole assembled scene in the editor. One upscale, applied to everything, means one look.

**2. Design the last second as a hand-over, not a climax.** The 24 frames the next crew sees must be *easy to continue*:

- End on a **hold**: weight balanced, face readable, hands visible and still, no limb crossing the frame edge.
- **No camera move in the last second** — finish the push-in or dolly at ~7 s and let it settle.
- **No expression change, turn, or pick-up** in the last second.
- **Dialogue:** end the line by ~6.5 s ("…chai in hand." *beat*), or if the line must carry over, make sure the voice is *audibly running* through the final second.
- Write this into the prompt: *"…she holds the pose, looking at the phone, for the final second."*

**3. Prompt the extension as a continuation, not a new idea.** Flow pre-fills the extension prompt with your original — **keep ~80% of it verbatim** (the lighting, lens, palette, and camera sentences especially) and add **one micro-change**: *"she now begins to smile"*, *"the tanker rolls forward slowly"*. Never introduce a new character, a new location, a new camera move, or a new light source through Extend — that's a new shot, and forcing it is how you get stretched limbs and a different face.

**4. Same tier both sides of the join.** Base on Fast, extend on Fast; base on Quality, extend on Quality. Tier changes are look changes.

**5. When the seam jumps, delete the extension — not the base — and re-extend.** Two or three attempts for a clean seam is normal. Regenerate only the failing part; never regenerate the base to fix an extension.

**6. Trim the fight.** If the re-shot second visibly disagrees with what came before, trim the last few frames of the original *or* the first few of the extension in Scenebuilder. A cut 10 frames earlier is invisible; a wobble is not.

**7. Know when *not* to extend.** Extend is for **same action + same angle + same place** where the last second "contains enough continuity evidence." Anything else — new angle, new location, a time jump, a different body position — is a **cut** (§4), and a cut is *cheaper and better*.

### 2.3 The seam review (do this every time)

Watch the join **three ways**: at normal speed, **muted** (sound hides picture faults), and **frame-by-frame** around the seam. Check, in this order:

```
silhouette · facial age · accessory position (glasses, logo, watch) ·
shadow direction · camera speed · colour temperature · grain/softness · audio bed
```

If one of those breaks, the fix is almost always in §2.2 step 2 or 3 — the hand-over second wasn't quiet enough, or the prompt drifted.

## 3. Problem B — "The clip made from my last frame looks worse / different"

### 3.1 Why it happens

- **The frame is a decoded H.264 frame from a 720p stream.** It carries compression softness and, if anything was moving, motion blur. Frames→Video treats it as ground truth, so the new clip either **inherits the softness** or "corrects" it to a cleaner look — *either way it doesn't match.*
- **A frame has no memory of lens, light, grade, grain, or sound.** Those are re-rolled from your prompt words. If the words differ even slightly, the look differs.
- **Anything not visible in the frame is re-invented.** (A filmmaker's example: a mascot whose mouth is closed in the saved frame came back with different teeth.)
- **Different tier or different prompt skeleton = different image statistics.** A Lite follow-on to a Quality base will never match.

### 3.2 The fixes, in order of effect

**1. Make the join a *still*, not a video frame. (The big one.)** Don't hand the next crew a photocopy — hand both crews the *same clean photograph*:

```
① Imagen / Nano Banana → one clean, sharp, high-res "join still"
     (same ingredients, same framing, same light as the shot — see Phase 5)
② Clip A = Frames→Video with the join still as the LAST frame
③ Clip B = Frames→Video with the join still as the FIRST frame
```

Both clips now *arrive at* and *depart from* the same crisp picture. Nothing soft ever enters the pipeline, and identity is baked into the still by the ingredients you used to make it. This is also how you build a **bridge**: first frame = a still from the end of A, last frame = a still for the start of B, and Flow generates the transition.

**2. If you must use a real frame, harvest it properly.**

- Take it from the **upscaled download** (1080p/4K), not the 720p preview.
- Pick the **sharpest, stillest frame in the last second** — usually *not* the very last one, which is often mid-motion.
- **Clean it**: upscale/de-blur in Nano Banana, Topaz, or the local ComfyUI stack (see [[../comfyui/09-google-flow-parity]]), keep the exact aspect ratio, and colour-match it to a mid-clip frame of A.
- Make sure every detail that must persist is **visible** in it (open mouth, logo, the phone screen).

**3. Put identity in the still, not the mode.** Frames→Video and Ingredients→Video are separate modes in Flow — you can't feed both a start frame and reference photos in one generation. So bake the face/product into the join still *when you make it* (Imagen with the same character sheet — Phase 5 layer 1), and let Frames→Video lock the framing.

**4. Same prompt skeleton, same tier, same resolution — then upscale both identically.** Copy the lighting, lens, palette, and style sentences verbatim from clip A's prompt. Render B on the same tier as A. Upscale A and B with the same tool at the same setting.

**5. Hide the join editorially.** A straight continuation *exposes* a mismatch; a **cut** *hides* it. Cut **on action** (the hand reaches for the phone in A → the phone is lifted in B), change the **shot size or angle** across the cut, or drop a 1-second **B-roll insert** between them. Never use a dissolve to paper over a change of face, age, or accessory — it advertises the fault.

**6. Match in post.** In DaVinci Resolve, **colour-match** B to A (Vids can't); add the same light grain to both so 720p softness reads as "film", not "AI". This step rescues most near-misses.

## 4. Decision: Extend, Still-Join, or Cut?

```
Same action, same angle, same place, and the last second is a quiet hold?
      → EXTEND (720p chain, upscale at the end)                           §2

Continuous moment but you need control over what the join looks like,
or the shot must survive at 1080p/4K?
      → STILL-JOIN (Imagen still = last frame of A = first frame of B)    §3.2 ①

New angle / new location / time jump / different body position?
      → CUT (two clips, cut on action; Vids or Resolve)                   §3.2 ⑤

Need identity locked across the join more than motion continuity?
      → Ingredients→Video for both clips + cut on action                  Phase 5
```

Rule of thumb from real films: an average shot lasts **3–5 seconds**. Audiences don't want 24-second continuous takes; they want a story cut well. Most "I need a longer clip" problems are actually "I need three shots" problems. §5 is how a director breaks those three shots; §6 is what goes between them.

## 5. Break the Scene Like a Director

### 5.1 The one idea

A scene is not a long shot. A scene is **a sequence of decisions about where the audience's eyes are**, one shot at a time, with a reason for every change. A director "breaks" a scene (the French word is *découpage* — literally "cutting up") *before* anyone shoots, by answering a short list of questions and writing a shot list in which **every shot has one job and every cut has a motive.** That habit is worth more in Flow than anywhere else, because in Flow every shot is a fresh crew: the plan is the only thing holding the scene together.

[[03-phase-3-context-and-script-planning|Phase 3]] turned a brief into *beats* (hook → value → proof → CTA; problem → agitate → solve → payoff). [[04-phase-4-camera-control|Phase 4]] gave you the camera *vocabulary* (sizes, angles, moves, lenses). This section is the missing middle: **how a beat becomes two or three shots, and in what order.**

### 5.2 Seven questions before you break a scene (ask them in this order)

| #  | Question                   | Why it matters                                                                                       | DZZLO "9 PM Register" beat                                              |
| -- | -------------------------- | ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 1  | **What changes?**          | A scene has one turn: before → after. If nothing changes, it's B-roll, not a scene.                  | Before: "just another late night." After: "this is costing me."         |
| 2  | **Whose scene is it?**     | The point-of-view character gets the closest shot and the reaction shots.                            | The dealer. Not the registers.                                          |
| 3  | **Where is the line?**     | The axis of action runs between the two things that matter; every camera stays on one side (§5.4).   | Dealer ↔ the buzzing phone / the window to the pump.                    |
| 4  | **What's the geography?**  | Establish the space once, wide and early. After that you may go as close as you like.                | One high wide of the office: desk, registers, window, pump lights out.  |
| 5  | **What must be seen close?** | The proof. That's an insert, and it's the shot the audience remembers.                             | Ink smudging on a fat register; later, the phone's verified ticks.      |
| 6  | **Where's the peak?**      | The emotional high point gets the tightest shot. Move in as intensity rises, out as it resolves.     | The half-argument on the phone: *"Kaun si gaadi thi?"*                  |
| 7  | **How do we leave?**       | The exit — a look, a move out of frame, a sound — *decides the transition* into the next beat (§6).  | The phone rings again → smash cut to "The Dispute".                     |

Answer these in the brief doc (Phase 3) before touching Flow. Five minutes here saves fifty coins later.

### 5.3 The shot-size ladder — order, not vocabulary

Sizes are an emotional dial (Phase 4). *Sequencing* them is the craft:

| Pattern                 | Order                                                                    | Use for                                                                          |
| ----------------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| **Classic**             | WS establish → MS engage → CU / insert detail → CU reaction → MS/WS release | Tutorials, brand films, anything that needs to breathe                        |
| **Cold open** (social)  | CU or insert **hook** → WS establish → MS → CU → CTA card               | Reels / Shorts: the wide is the *least* interesting frame, so don't open on it   |
| **Intensify**           | MS → MCU → CU → ECU, each cut tighter                                    | The *Agitate* beat — the problem closing in                                       |
| **Release**             | ECU → CU → MS → WS, each cut looser                                      | The *Payoff* beat — relief, air, the "after"                                      |

Two rules that come with the ladder: **one size step per cut feels natural, two steps feels punchy, three feels like a mistake** (unless it's a deliberate smash cut, §6.3). And **the closest shot of the scene must land on the line or the detail that matters most** — if your CU sits on a nothing moment, re-order.

### 5.4 The three continuity rules that make cuts invisible

**The 180° rule (the line).** Draw a line between the two things that matter (dealer ↔ tanker). Keep every camera on **one side** of it. Then the dealer always looks camera-*right* at the tanker, and the tanker always enters from camera-*left* — and the audience's mental map holds. Cross the line and they feel the world flip, even if they can't say why. In Flow you *state the side in every prompt*:

```
Camera on the dealer's left side, eye level. He looks off-frame RIGHT toward
the pump. (Every shot in this scene keeps the pump to the right.)
```

To cross the line legitimately: use a *neutral* shot on the line (straight at his face, or straight down the pump lane), or show the camera crossing it inside one shot.

**The 30° rule.** Two consecutive shots of the same subject must differ by **at least 30° of angle** *or* by **two shot sizes** (WS → CU). Anything less reads as a **jump cut** — the picture "hops." If a Jump To or a reaction shot looks like a glitch, this is usually why.

**Screen direction & eyelines.** Exit frame-left → enter frame-right (or he appears to walk back). The phone stays in the same hand. Eye-level in shot A means eye-level in shot B of the same conversation (a high angle "answering" an eye-level shot reads as a power shift — use it only on purpose). Flow cannot see your previous shot, so *you* are the script supervisor: write the side, the hand, and the eyeline height into every prompt of the scene, verbatim.

### 5.5 Coverage — give the editor choices (and hide AI faults)

A film crew never shoots one shot per moment; they shoot a **master** plus **coverage** (the same moment from two or three angles) so the editor can cut around anything. In AI video this is your single best defence: **a moment you have from two angles always has a clean cut available.**

In Flow, coverage comes three ways:

| Coverage tool                                   | What it does                                                                                                                                                    | Use for                                                       |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Jump To** (Scenebuilder)                      | "Explain what should happen next and the footage will transition to a new shot but preserve the context from the last frame" — Flow's own *cut to a new angle* in the same scene, character and setting carried over | The reaction shot; the reverse angle; the CU after the MS |
| **Same join still, different prompt** (§3.2 ①) | The same clean still as first frame, prompted at a different size / angle                                                                                       | Matched-lighting coverage where identity is critical          |
| **Ingredients→Video, size changed**             | Same character sheet, new prompt: "close-up, same office, same light"                                                                                           | Cheap CU / reaction inserts drafted on Lite                   |

**Harvest, don't use.** An 8-second clip is a *source*, not a shot. A pro cut uses **2–5 s of it** and keeps the rest as handles for the edit. Plan on: **one clip → one or two shots; a 30-second promo → 8–12 shots → 6–8 clips.** Phase 3's "30 s = 4 shots" is four *beats*; each beat gets two or three shots when it's cut like a pro.

**Coverage on a budget (the Prime Directive still rules):** lock only the **face** shots at Quality; inserts, hands and cutaways at **Fast**; product B-roll from **Image→Video** off an Imagen still; the app UI is a **real screen recording** composited in the edit — never a Veo render. Two Quality locks plus four Fast inserts cost about what Phase 1 budgeted per beat, and cut ten times better.

### 5.6 Motivate every cut

Walter Murch's **Rule of Six** for when a cut is right, in order of weight: **emotion (51 %)**, **story (23 %)**, **rhythm (10 %)**, **eye-trace (7 %)**, **2-D screen plane (5 %)**, **3-D space (4 %)**. The order is the lesson: an audience forgives a broken line if the cut serves the emotion; they never forgive a geometrically perfect cut that lands on nothing.

Practical translation — cut when the viewer's eye *wants* the next picture:

- **A look** → cut to what they look at.
- **A sound** → cut to its source.
- **An action** → cut *during* it, never before or after (§6.2, cut on action).
- **New information** → cut the moment the current frame has none left. A shot is as long as its information, not as long as the clip.

### 5.7 Design the join *before* the shot

This is the pro habit AI rewards most. **Decide the transition first, then write the outgoing frame of A and the incoming frame of B to serve it.**

| You want…        | So clip A must end with…                                              | And clip B must start with…                                          |
| ---------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Cut on action    | The action **starting** in the last 2 s ("he begins to lift the phone") | The **same action mid-way** ("the phone already rising to his ear") |
| Cut on a look    | "He looks off-frame right and holds"                                  | The thing he sees, from his side of the line                         |
| Match cut        | A composition you can repeat (centre-framed ledger, top-down)         | The same composition, new subject (the app ledger, top-down)         |
| Sound bridge     | A named sound ("the phone starts buzzing on the desk")                | The same sound continuing ("the buzz resolves into the chime")       |
| Masked cut       | An object filling the frame ("the tanker passes, blacking the lens")  | The same cover clearing                                              |

A shot list without an **"Out →"** column is a wish list. Add the column (§5.8) and every prompt's last sentence writes itself.

### 5.8 The director's shot list (template + worked example)

Columns: **# · Beat · Shot (size · angle · move — Phase 4 words) · What happens (one action) · Use (s) · Out → next · Flow method (tier) · Audio.**

Beats 1–2 of the [[01-phase-1-the-big-picture|Phase 1]] promo — "The 9 PM Register" and "The Dispute" — broken like a director (≈ 16 s, 6 shots, 6 clips):

| # | Beat    | Shot                                                  | What happens (one action)                                                    | Use | Out → next                                    | Flow method (tier)                                           |
| - | ------- | ----------------------------------------------------- | ---------------------------------------------------------------------------- | --- | --------------------------------------------- | ------------------------------------------------------------ |
| 1 | Problem | ECU · top-down · static, macro                        | A pen scratches a number into a fat paper register; the ink smudges          | 2 s | **Cut on action** — the hand lifts            | Image→Video from an Imagen still (Fast)                      |
| 2 | Problem | WS · high angle · static (Phase 4 "problem" recipe)   | Night office. Dealer hunched over three registers; a phone buzzes on the desk | 3 s | **J-cut** — the buzz continues under #3       | Ingredients→Video, dealer sheet + office still (**Quality**) |
| 3 | Problem | MCU · eye level · slow push-in                        | He rubs his eyes and glances at the phone                                    | 3 s | **Smash cut** on the ring →                   | **Jump To** from #2 (Fast)                                   |
| 4 | Agitate | CU · slightly low · handheld                          | On the phone: *"Payment ho gaya tha!"*                                       | 3 s | **Cut on a look** — he looks down             | Ingredients→Video (**Quality**, the dialogue shot)           |
| 5 | Agitate | Insert ECU · top-down · static                        | A finger flips register pages; the totals don't match                        | 2 s | **Cutaway on sound** — a truck horn           | Fast, hands only                                             |
| 6 | Agitate | WS · eye level · static, through the office window    | An unfamiliar tanker and driver waiting at the pump                          | 3 s | **Dip to white**, 6 frames → beat 3 (relief)  | Jump To from #4, or Text→Video (Fast)                        |

Read the "Out" column top to bottom and you can *hear* the edit before a coin is spent. Note the line: the pump is camera-right in #2, #3 and #6; the phone is in his right hand in #3 and #4; every prompt says so.

## 6. Transitions — What Each One Says, and When to Use It

### 6.1 The one idea

A transition is a **sentence the audience reads without knowing it.** A cut says "same time, keep watching." A dissolve says "time passed." A fade says "the end." Use the wrong one and the viewer reads a wrong sentence — subtly confused, and they blame the ad. Use the right one and the join disappears.

The ratio in a professionally cut 30-second ad: **about 90 % straight cuts** (mostly on action or on a look), **one** smash cut at the turn, *maybe* one dissolve or dip, and a fade only at the very end. **If you're using more than two visible transitions, you're decorating, not editing.**

### 6.2 The invisible ones — cuts (use these 90 % of the time)

| Transition                        | What it tells the audience                                   | Use when                                                                                   | Don't use when                                              | How to make it                                                                                           |
| --------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| **Straight cut**                  | "Same time, same place — keep watching"                      | The default for everything inside a scene                                                  | —                                                           | Butt the clips in Scenebuilder / Vids                                                                    |
| **Cut on action**                 | "Nothing happened between these"                             | Every movement-based join; **the best seam-hider in AI video**                             | There's no action to cut on (use a look instead)            | A: the action starts in the last 2 s; B: starts mid-action; trim so the movement continues               |
| **Cut on a look** (eyeline match) | "Here's what they see"                                       | Reveals: the phone, the tanker, the product                                                | Eyelines aren't consistent (breaks the 180° rule)           | A: "looks off-frame right, holds"; B: the object, from his side of the line                              |
| **Reaction shot**                 | "Here's how it lands"                                        | After a line or a reveal; **hides lip-sync misses and lets you shorten dialogue**          | It stalls the pace                                          | Jump To (same scene, new angle) or an Ingredients→Video CU                                               |
| **Cutaway / insert**              | "Meanwhile, this detail"                                     | Compress time; hide a bad join; show the UI (composite the real screenshot)                | As a crutch for *every* join — it starts reading like a patch | Fast or Image→Video, 1–2 s                                                                             |
| **Match cut** (graphic)           | "These two things are the same idea"                         | Problem → solution: paper ledger → app ledger, calculator → phone, in the same framing     | Realism continuity (it's an *idea* cut)                     | Same composition in A's last frame and B's first frame (§3.2 ①), or a Frames→Video bridge                |
| **J-cut / L-cut** (split edit)    | "The next moment is already arriving" / "the last one lingers" | Dialogue; any scene change you want to feel fluid; **burying Extend's re-generated seam audio** | The audio itself is the fault                        | Resolve: unlink audio, slide it 10–20 frames. Vids: run a VO or music bed over the cut instead           |
| **Sound bridge**                  | "The sound carries us over"                                  | Scene changes with a motif: kettle whistle → notification chime; horn → engine             | —                                                           | Name A's ending sound and B's opening sound in the prompts; overlap them in the edit                     |
| **Masked / invisible cut**        | "There was no cut"                                           | Faking a continuous take: pass behind a hand, a tanker, a doorframe, darkness              | Nothing in the scene can cover the frame                    | A ends with an object filling the frame; B starts from the same cover; cut inside the black / blur       |
| **Jump cut**                      | "Time skipped — and I'm telling you so"                      | Tutorials, vlogs, comedy, "hours later" on the *same* framing                              | Narrative continuity — it's the failure mode of the 30° rule | Same framing, trim the middle; a 2-frame dip if it's harsh                                              |

### 6.3 The visible ones — transitions (sparingly, on purpose)

| Transition                                       | What it tells the audience                    | Use when                                                                                              | Don't use when                                                                        | How to make it                                                                         |
| ------------------------------------------------ | --------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Smash cut**                                    | "Shock — everything changed"                  | The ad's turning point: night chaos → morning calm; problem → solution                                | Twice in one ad                                                                       | Hard cut from A's loudest frame to B's quietest; kill the music for one beat           |
| **Dissolve** (cross-dissolve)                    | "Time passes / softens"                       | Montage, memory, mood, "later that day"; a **6–12-frame micro-dissolve** to blend a small light shift | To hide a face, age or accessory change — it *advertises* the fault; inside one action | Vids: Dissolve. Keep it under 1 s except in montage                                  |
| **Dip to black / white**                         | "Breathe" (white = relief, clean, the "after") | Between distinct beats — Agitate → Solution; tutorial chapters                                        | More than once or twice per piece                                                     | 4–8 frames; Vids Fade or Resolve                                                       |
| **Fade in / fade out**                           | "Begin" / "The end"                           | Opening and closing; chapter breaks in long tutorials                                                 | Inside a 30-s ad (kills momentum)                                                     | Vids: Fade                                                                             |
| **Wipe / slide**                                 | "Playful, retro, step-by-step"                | UI walkthroughs, tutorial steps, listicles                                                             | Premium brand films (reads as a slideshow)                                            | Vids: Slide                                                                            |
| **Whip pan**                                     | "Energy — same world, new spot"               | Social hype; a quick relocation (office → pump)                                                        | Anything calm; identity-critical joins                                                | A ends on a fast pan right (motion blur); B opens on the same pan settling; cut in the blur |
| **Generative bridge** (Frames→Video, first + last) | "Transformation"                            | Stylised morphs: the paper ledger *becomes* the app ledger; night *becomes* morning                    | Realism — it drifts                                                                   | Flow Frames→Video with both frames, 4–8 s, Fast                                        |
| **Speed ramp**                                   | "Hit"                                         | Beat drops; the product reveal                                                                         | Dialogue                                                                              | Resolve; needs clean motion in the source clip                                         |
| **Cross-cutting** (parallel)                     | "Meanwhile, elsewhere"                        | Tension: dealer's office ↔ tanker on the road; tutorial "you ↔ the app"                                | Single-location micro-ads                                                             | Two clip chains, cut alternately, each cut shorter than the last                       |
| **Montage**                                      | "A lot happened"                              | Day-in-the-life; feature runs on music; **the safest AI structure — no shot needs to be long**         | One moment needs to breathe                                                           | 1–2 s shots on the music beat; all Lite / Fast                                         |
| **Title / graphics card**                        | "New chapter"                                 | Tutorials (Step 1 → Step 2); the CTA                                                                   | Inside emotional beats                                                                | Vids text scenes                                                                       |

### 6.4 Pacing, in numbers

| Rule                             | Number                                                    |
| -------------------------------- | --------------------------------------------------------- |
| First cut (the hook)             | within **1–3 s**                                          |
| Average shot, social ad          | **2–4 s**                                                 |
| Dialogue / proof shot            | **5–8 s** (the only long ones)                            |
| Visible transitions per 30 s     | **2 at most**                                             |
| Last shot (CTA) hold             | **2–3 s**                                                 |
| Where the cut lands              | **on the music beat** — drop the music in first, cut to it |

### 6.5 Transition rules that are specific to AI footage

1. **Cuts hide AI faults; continuations expose them.** When in doubt, cut.
2. **Dissolve across light, never across identity.** A 6-frame dissolve blends a colour-temperature shift; a 1-second dissolve across a changed face is a confession.
3. **Bury Extend's seam under a J-cut.** Start the next shot's audio (or the music bed) before the picture cut and the re-generated second of audio disappears.
4. **Static-to-static, or matched motion.** A moving shot cut to a static one feels like a stumble unless the cut is on action. If A ends on a push-in, let it settle (§2.2 step 2) or cut inside the motion to a shot with the *same* motion.
5. **The UI is never a Veo render.** Insert shots of the app are real screen recordings composited in the edit (Phase 1 §7). That insert is also your most reliable cutaway.
6. **A reaction shot forgives a bad line.** If the lip-sync misses on a Quality clip, cut to the listener on the bad syllables instead of re-rendering — 0 coins.

### 6.6 Which tool makes which transition

| Tool                                     | Makes                                                                                                                        |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **Flow — Extend**                        | The same shot continuing (no cut) — §2                                                                                       |
| **Flow — Jump To**                       | A cut to a new shot in the same scene, character and context preserved from the last frame — coverage, reactions, reverse angles |
| **Flow — Frames→Video (first + last)**   | A generative bridge / morph between two stills                                                                               |
| **Flow — Scenebuilder**                  | Order, trim (start / end), preview, download                                                                                 |
| **Google Vids**                          | Straight cuts; the transition icon between scenes: **fade, dissolve, slide**; text cards; music bed                          |
| **DaVinci Resolve (free)**               | Split edits (J / L), dips, speed ramps, colour match, grain — everything Vids can't                                          |

## 7. Making a Stitched Piece Look Like *One* Film

### 7.1 The one idea

"Consistency" is not one thing. It is **six things the viewer adds up without noticing**: the **look** (colour, contrast, grain), the **light**, the **lens & camera behaviour**, the **set & props**, the **sound**, and the **rhythm**. A cut of ten AI clips looks like a patchwork because every clip re-rolls all six — even when the face is right. The viewer reads a warmth shift between two shots as *a different room*; a room-tone jump as *a different day*; a drone shot after a handheld shot as *stock footage*.

Nobody can fix six variables at the end. Pros **lock four before generating** (look, light, camera, set) and **unify the last two after** (sound, rhythm — plus a grade that mops up whatever leaked). The recipe in one line:

```
decide the look once → generate STILLS, not clips → animate the stills →
grade and score the whole timeline as one thing
```

### 7.2 Diagnose first — which of the six is drifting?

| You see                                                                   | What's drifting          | Fix in          |
| ------------------------------------------------------------------------- | ------------------------ | --------------- |
| Every clip is a different warmth / brightness / contrast                  | Look & light             | §7.3, §7.6      |
| Same character, different room each time (desk, registers, window move)   | Set & props              | §7.4            |
| One shot handheld, the next a drone, the next an orbit                    | Camera personality       | §7.5            |
| Some clips soft, some sharp                                               | Resolution pipeline      | §2.2 step 1, §7.6 |
| Each clip *sounds* different; music restarts; room tone jumps             | Sound                    | §7.7            |
| Everything matches and it *still* feels random                            | Rhythm & structure       | §7.8, §6.4      |

### 7.3 Lock the look at the source — the Look Sentence

One sentence, about 30 words, pasted **verbatim** into every prompt of the piece, plus the **same style-reference image as ingredient #3** in every clip (Phase 5 §7). Template:

```
LOOK — "DZZLO night office": shot on 35 mm, shallow depth of field, soft
low-contrast film look with fine grain; warm tungsten desk lamp as key light,
cool blue night through the window as fill; muted palette with one teal
accent; eye-level, tripod-steady camera. 9:16.
```

Rules: same **time of day** across the scene (never "night" in one prompt and "evening" in the next), same weather, same named light sources, same lens words, same palette words, same aspect ratio, same tier, same resolution. Phase 3's brand-feel line and Phase 5's style ingredient *are* this — the usual failure is that the sentence **changed** between prompts: Gemini paraphrased it, or a human "improved" it. Freeze it. A Gem that pastes it for you (Phase 7) exists for exactly this reason.

### 7.4 Lock the set — one still per location, and a props bible

Generate each location **once** as a clean still (Imagen, or Nano Banana Pro inside Flow): the office at 9 PM; the pump lane at dawn. Every shot in that location either **starts from that still** (Frames→Video) or **carries it as an ingredient** (Ingredients→Video: "the office from image 2"). Keep a **props bible** — the five to eight objects that must persist and what they look like — and paste the relevant lines into every prompt:

```
PROPS — three fat red cloth-bound registers; a black phone in a teal case;
a steel chai glass; a Casio calculator; the window showing the pump's white
canopy lights.
```

Objects you don't name get re-invented — registers thin out, the phone case changes colour, the window moves.

**The stronger version — storyboard the whole piece as one consistent still set before any video.** In one image session, derive every frame from the previous one: *"same office, same light — now from a high wide"* → *"now a top-down of the register"* → *"now a close-up of his face lit by the phone."* Image models hold a look across a set far better than video models hold it across generations, and stills are nearly free. Then animate each still with Frames→Video and the Look Sentence. The video model only adds motion; the consistency was decided in the pictures. This is [[03-phase-3-context-and-script-planning|Phase 3]] §5 taken to its conclusion, and it is the single biggest upgrade a patchwork cut can get.

### 7.5 Lock the camera personality

Pick **one** camera style for the whole piece and never leave it:

| Personality               | Words in every prompt                                              | Fits                                   |
| ------------------------- | ------------------------------------------------------------------ | -------------------------------------- |
| **Tripod & push-ins**     | static or slow push-in, eye level, 35 mm, tripod-steady            | Spokesperson, product, trust           |
| **Documentary handheld**  | gentle handheld, natural light, medium-wide, 24–35 mm              | UGC, lifestyle, testimonials           |
| **Cinematic glide**       | slow dolly or orbit, low angle, shallow DoF, 50–85 mm              | Brand films, hero product              |

One movement *speed* too — all "slow", or all "energetic". Phase 4 §7's recipes by content type are these columns; the mistake is taking one shot from each. An aerial opener, an orbiting product shot and a handheld testimonial in the same 30 seconds is three different films.

### 7.6 Fix the rest in the grade — the hero-clip method

1. **Pick the hero clip** — the one that looks most like the Look Sentence.
2. **Match every other clip to it.** DaVinci Resolve (free): Color page → Shot Match to the hero; or by hand in this order — white balance, exposure, contrast, saturation.
3. **One adjustment layer over the whole timeline**: one LUT / film look, one fine grain layer (2–4 %), one soft vignette, one sharpen-or-soften pass. Every pixel now goes through the same texture, and **uniform texture is what the eye reads as "one film."** It also hides the 720p-versus-upscaled softness gap from §2.2.
4. **When the sources are far apart, use an anchor grade**: teal-and-orange, high-contrast noir, or black-and-white with the teal accent. Mismatches vanish inside a strong grade.
5. Vids can't do any of this. Resolve can; CapCut can do a basic version. It's an hour to learn and it pays back on every piece.

### 7.7 Sound is half the consistency

The ear stitches what the eye can't. Under every clip run **one continuous music bed** (Lyria / MusicFX, [[06-phase-6-voice-lipsync-audio|Phase 6]]) and **one continuous ambience** (room tone, street). **Mute or duck Veo's per-clip ambience** — each clip's room sounds different, and that alone is a large share of "it feels stitched." Use **one VO voice**, generated once and cut over the picture, instead of per-clip dialogue wherever a line doesn't need to be on-camera. One SFX per object — the same notification chime every time. **J-cut every scene change** (§6.2) so sound arrives before picture.

### 7.8 Rhythm and structure — make the variety look intentional

- **Cut to the beat**, and keep shot lengths inside a band (2–4 s) so no clip sticks out.
- **Bookends**: open and close on the same frame or location.
- **A recurring motif** every ~8 seconds: the phone insert, the teal accent, the chai glass.
- **Connective tissue**: 1-second establishing or detail shots from the location still between beats.
- **One graphic system**: one font, one lower-third, one caption style, one logo bug, one overlay colour.
- **Cast the takes.** Generate two or three candidates per shot and choose the ones that **match the hero**, not the best individually. A pro editor cuts the take that fits, not the take that shines.
- **If it still won't hold**: fewer locations, fewer characters, more montage. Variety on music reads as design; variety inside a dialogue scene reads as a mistake.

### 7.9 The cohesion checklist (run it before you export)

```
[ ] Look Sentence identical in every prompt; style ingredient in every clip
[ ] One still per location; props bible pasted
[ ] One camera personality; one movement speed
[ ] Same tier, same resolution; upscaled once, at the end
[ ] Hero clip chosen; every clip matched to it; one adjustment layer over all
[ ] One music bed, one ambience, one VO voice; Veo's ambience ducked
[ ] Shot lengths in a band; cuts on the beat; at most 2 visible transitions
[ ] Bookends; a motif; one graphic system
```

## 8. Recipe — A 24-Second Continuous DZZLO Beat (worked example)

Goal: the dealer at the pump office, phone in hand, order arrives, tanker fills — one continuous feel, no visible seam, deliverable at 1080p.

| Step | Action                                                                                                              | Tier    | Coins   |
| ---- | ------------------------------------------------------------------------------------------------------------------- | ------- | ------- |
| 1    | Imagen: **two join stills** with the Ravi character sheet — (J1) dealer looking at phone, (J2) dealer glancing up at tanker | —       | 0 (image) |
| 2    | Clip A: Frames→Video, **last frame = J1**, 720p. Prompt ends "…holds the phone still for the final second."          | Lite ×2 | 20      |
| 3    | Clip B: Frames→Video, **first frame = J1, last frame = J2**, 720p, same prompt skeleton                              | Lite ×2 | 20      |
| 4    | Clip C: Frames→Video, **first frame = J2**, tanker fills, 720p                                                      | Lite ×2 | 20      |
| 5    | Seam review (§2.3) on the Lite drafts; fix stills/prompts, not clips                                                 | —       | 0       |
| 6    | Lock A, B, C at Quality (same prompt skeletons)                                                                     | Quality | 300     |
| 7    | Assemble in Scenebuilder/Vids; colour-match in Resolve if needed; **upscale once** to 1080p                         | —       | 0       |
| **Total** |                                                                                                                |         | **360** |

Compare: "extend, extend, extend, regenerate the whole chain when hop 2 drifts" routinely costs more *and* ends at 720p. The still-join recipe spends coins only on shots you already know are right ([[01-phase-1-the-big-picture]] Prime Directive) and ends at 1080p.

## 9. Prompt Patterns for the Join

**End-of-clip hold (put at the end of every clip you intend to continue):**

```
…For the final second the camera settles and she holds the pose, eyes on
the phone, hands still, expression unchanged. No new action.
```

**Extension micro-prompt (Flow pre-fills the original; keep it, add one line):**

```
[original prompt kept verbatim]
Continue the same shot from the exact same camera position. She now
begins to smile as the order confirmation appears. Same warm morning
light, same 35 mm framing, same ambient street sound. No cut, no new
camera move.
```

**Frames→Video from a join still:**

```
Start exactly from the provided image — same framing, same lighting
(warm morning window light from camera-left), same 35 mm look, same
colour palette (DZZLO teal and white). The dealer lifts his eyes from
the phone toward the tanker outside. Slow, subtle. No subtitles.
```

Note the same three sentences of *look* language across all three. That repetition is what "continuity" is made of.

## 10. What Still Can't Be Fixed (honesty, vault rule)

- **Extend is 720p, full stop** (as of the API docs on 2026-09-25). If the deliverable must be 4K and the shot must be one unbroken take longer than 8 s, upscale after the chain and accept upscaler texture — or use the still-join.
- **Drift compounds.** Hop 3 of an extend chain has seen hop 2's re-shot second, not your original. Beyond two hops, expect to re-anchor with a still-join or a cut.
- **The re-shot second is not optional.** You can trim it, you can make it quiet, but you cannot tell Extend to leave it alone.
- **Google re-tunes this constantly** — Extend was Veo 2-only and silent not long ago; audio and Veo 3.1 arrived later. Re-check the API page in §12 before relying on a limit.

## 11. Exercises

**11.1 — See the re-shot second (~⏣40).** Render an 8 s Fast clip with a deliberate motion in the last second (a head turn). Extend it. Frame-step the join: watch the turn get re-shot. Now render the same clip ending on a hold and extend again. Compare the seams.

**11.2 — Prove the photocopy problem (~⏣30).** Take the last frame of a Lite clip from the 720p preview → Frames→Video. Then take the same frame from the upscaled download, clean it in Nano Banana → Frames→Video. Side by side.

**11.3 — Still-join (~⏣40).** Make one Imagen join still with your Ravi sheet. Clip A with it as *last* frame, clip B with it as *first* frame, both Lite. Butt them together in Scenebuilder. This should be your cleanest join yet.

**11.4 — Cut instead (~⏣20).** Same beat as 11.3 but as two different shot sizes cut on action. Notice it's cheaper, faster, and nobody sees a "join" because there isn't one.

**11.5 — Break a beat (0 coins).** Take beat 3 of the promo, "The Verified Order," and answer the seven questions (§5.2). Then write it as three shots in the §5.8 table with an **Out →** for each. If you can't name the Out, the shot isn't designed yet.

**11.6 — Cut it three ways (0 coins, existing clips).** In Vids, join any two of your clips (a) as a straight cut on action, (b) with a 1-second dissolve, (c) as a smash cut with the music dropped for a beat. Watch each one muted. Only one feels like an ad; the dissolve is the one that looks like AI.

**11.7 — Coverage for free (~⏣30).** From an existing MS clip, generate the reaction CU two ways: **Jump To** in Scenebuilder, and **Ingredients→Video** with "close-up, same office, same light." Cut each against the MS with the 30° rule in mind. Keep whichever holds identity; note which you'd reach for next time.

**11.8 — Hero-clip grade (0 coins).** Take your last stitched piece into Resolve. Pick the hero clip, shot-match the rest to it, add one grain + LUT adjustment layer, lay a continuous music bed and mute Veo's ambience. Export and play it next to the original. That is usually the "nice" that was missing — and it cost nothing.

**11.9 — Storyboard set first (~⏣60).** In one image session make six stills of one location, each derived from the previous ("same office, same light, now…"). Animate three of them on Lite with Frames→Video and the Look Sentence. Cut them together. Now cut three Text→Video clips of the same beats. The difference is §7.4.

## 12. Sources (web-verified 2026-09-25)

Primary (Google):

- [Veo on the Gemini API — Extend (last second / 720p / 148 s / 20 hops), first & last frame, reference images, resolutions](https://ai.google.dev/gemini-api/docs/veo)
- [Bringing new Veo 3.1 updates into Flow — The Keyword ("generated based on the final second of your previous clip")](https://blog.google/innovation-and-ai/products/veo-updates-flow/)
- [Edit videos & build scenes in Flow — Flow Help (Extend, trim, Veo-only inputs, no Insert/Remove/Camera on extended clips)](https://support.google.com/flow/answer/16935718)
- [Create videos in Flow — Flow Help (Frames to Video, Ingredients)](https://support.google.com/flow/answer/16353334)
- [Create longer Veo videos in Google Vids — Workspace Updates (Extend, +8 s)](https://workspaceupdates.googleblog.com/2026/06/create-longer-veo-videos-and-generate-multiple-at-once-in-Google-Vids.html)

Secondary (practitioner write-ups — treat as indicative):

- [How to extend AI video scenes naturally in Google Flow — FourFeetz (hold the pose, when to cut instead)](https://fourfeetz.com/insights/extend-ai-video-scenes-google-flow)
- [Flow Scenebuilder Extend shots — DigiWebInsight (pre-filled prompt, micro-prompts, delete-and-re-extend)](https://digiwebinsight.com/flow-scenebuilder-extend-shots/)
- [How to extend Veo 3.1 videos beyond 8 seconds — AI Free API (720p-only extensions, match resolution)](https://www.aifreeapi.com/en/posts/veo-3-extend-video-length)
- [Veo 3.1 video extend guide — Apiyi (the "80 % rule" for extension prompts)](https://help.apiyi.com/en/veo-3-1-video-extend-guide-en.html)
- [I have a Flow video — how can I fix it? — Whisk AI Labs (Upscale button; Lite is lower quality)](https://whiskailabs.net/i-have-a-flow-video-how-can-i-fix-it-2026/)
- [Testing the limits of AI video with Veo 3.1 — The AI Filmmaker (details not visible in the saved frame get re-invented)](https://theaifilmmaker.substack.com/p/testing-the-limits-of-ai-video-with)

Film grammar, and the tools' own cut / transition features (§5–6):

- [Introducing Flow — The Keyword (Jump To: "explain what should happen next…")](https://blog.google/technology/ai/google-flow-veo-ai-filmmaking-tool/)
- [5 tips for using Flow — The Keyword](https://blog.google/innovation-and-ai/products/flow-video-tips/)
- [How to use Google Flow — Tom's Guide (Extend continues the shot; Jump To cuts to a new one)](https://www.tomsguide.com/ai/google-gemini/how-to-use-google-flow-the-new-ai-video-generator-meant-for-filmmakers)
- [Adding visual enhancements in Google Vids — DataCamp (fade, dissolve, slide between scenes)](https://campus.datacamp.com/courses/create-engaging-video-with-google-vids/create-engaging-video-with-google-vids?ex=7)
- [180-degree rule — Wikipedia](https://en.wikipedia.org/wiki/180-degree_rule)
- [30-degree rule — Wikipedia](https://en.wikipedia.org/wiki/30-degree_rule)
- [Cut (transition) — Wikipedia](https://en.wikipedia.org/wiki/Cut_(transition))
- [Dissolve (filmmaking) — Wikipedia](https://en.wikipedia.org/wiki/Dissolve_(filmmaking))
- [Walter Murch — Wikipedia (*In the Blink of an Eye*, the Rule of Six)](https://en.wikipedia.org/wiki/Walter_Murch)
- [Video transitions in film, with examples — Backstage](https://www.backstage.com/magazine/article/video-transitions-75727/)
- [The hidden meaning behind popular video transitions — PremiumBeat](https://www.premiumbeat.com/blog/the-hidden-meaning-behind-popular-video-transitions/)

Look, prompting and grading consistency (§7):

- [How to create effective prompts with Veo — DeepMind prompt guide (style, lighting, lens keywords)](https://deepmind.google/models/veo/prompt-guide/)
- [Ultimate prompting guide for Veo 3.1 — Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1)
- [DaVinci Resolve — Blackmagic Design (free edition: shot match, adjustment layers, grain)](https://www.blackmagicdesign.com/products/davinciresolve)

---

**Back to:** [[00_README]] · Beats → shot lists: [[03-phase-3-context-and-script-planning]] · Consistency layers: [[05-phase-5-character-consistency]] · Voice & music bed: [[06-phase-6-voice-lipsync-audio]] · Camera language for the hold: [[04-phase-4-camera-control]] · Assembly: [[08-phase-8-pro-workflow-and-playbooks]] · Cheat-sheets: [[09-reference]]
