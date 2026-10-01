# Deep Dive — Scene Continuity Past 8 Seconds: What Extend Really Does, Why the Last-Frame Trick Goes Soft, and the Fixes

> Level: Intermediate → Advanced | Time: ~2.5 hr | Outcome: you know what Flow does at the join between two clips (and which of its numbers only Google's API page states), you stop being surprised when Extend "changes" your clip, and you have three working recipes for a continuous shot longer than 8 seconds that doesn't drop in quality at the seam — plus a director's method for breaking a scene into shots and choosing the transition between them (§5–6), and the cohesion stack that makes a ten-clip cut look like one film (§7). | Status: written & web-verified 2026-09-25; **tool facts re-verified and corrected 2026-10-01** against Flow Help, the Gemini API docs, Google Vids Help and the DaVinci Resolve 21 manual. Sources in §12.

---

## Explain-it-like-I'm-5

Remember: every 8-second clip is shot by a **fresh robot crew that never met the last one** ([[00_README]] catch #1). So how do you make a 24-second shot? Only two ways, and both are hand-overs between crews:

- **Extend** — the new crew is allowed to watch the **last one second** of the old crew's film. Google's developer guide says they **re-shoot that second** so their footage lines up, then keep filming. They hand you back **one film** (old + new). In Flow the new crew is always the **cheapest crew** (Veo 3.1 Lite), whoever shot the old film — so if the best crew shot it, you can see where the cheap one took over. (Google's developer version of the same crew hands the whole thing back in the **small format**, 720p; Flow doesn't say what size it returns.)
- **Last-frame → Frames to Video** — you take a **photocopy of the last picture** of the old film and tell a brand-new crew "start from this." A photocopy of a movie frame is blurry. The new crew starts from a blurry picture, has never seen the old film's lighting, lens, or colours, and guesses the rest.

That's the whole explanation of both problems you've hit. Everything below is the fix.

## 1. The Two Problems, One Cause

| You see                                                           | What is actually happening                                                                                                                                                     | Fix family (§)      |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- |
| "I extended my clip and the **previous part changed too**"        | Extend **re-generates the final second** as its seed (as the Gemini API describes it; Google's Flow post says only "based on the final second"), re-rolls the audio across the join, and returns **one merged file** whose new part Flow makes with **Veo 3.1 Lite** (and which, if Flow works like the Gemini API, is **720p**) — so it can look plainer or softer than the Fast / Quality original or the 1080p upscale you were looking at | §2                  |
| "I used the **end frame as a start image** and the new clip's **quality / look doesn't match**" | The frame is a **compressed video frame** (soft, mid-motion), and the new generation re-rolls lens, light, colour, grain and everything not visible in that one picture          | §3                  |

The cause is the same: **a Veo clip carries no memory forward except its last second (Extend — "24 frames", in the API's words) or 1 frame (Frames→Video).** (Omni Flash 1.1's own extension reads the last 10 s — in the API, the Gemini app and Vids; in Flow it is still "coming soon".) Lighting, lens, colour grade, grain, audio bed, and every detail hidden from that seed are re-invented by the next generation. Continuity is therefore something you *engineer at the join*, not something the tool promises.

## 2. Problem A — "Extend changed my previous clip"

### 2.1 What Extend really does (facts, not vibes)

Flow Help says little about Extend. Google's **Gemini API page describes the same Veo 3.1 extension in detail** — but for the API, which extends with Veo 3.1 and 3.1 Fast, "not Veo 3.1 Lite": the opposite of Flow. So each row names its source (all re-read 2026-10-01). Read the API rows as the best description of what the model does, not as Flow's promises:

| Fact                                                                                                | Source                              | Consequence for you                                                                                       |
| --------------------------------------------------------------------------------------------------- | ----------------------------------- | --------------------------------------------------------------------------------------------------------- |
| "In the prompt box, describe how the action should continue"                                        | Flow Help                           | It continues the shot; it doesn't start a new one (§2.2 fix 3)                                            |
| "You can currently only extend Veo generated videos"; "All Veo 3.1 8s videos can be extended, but you must use **Veo 3.1 Lite** to extend them" | Flow Help | Every extension is a **Lite take** (⏣10), whatever tier made the 8 s base — expect a quality step at the seam over a Fast or Quality base (§2.2 fix 4). Flow's credits page still lists Extend under all three tiers: Google's pages disagree, so check the model and cost Flow shows before you click |
| "You can't apply other edit modes such as insert, remove, and camera to extended video clips"; Scenebuilder can "trim the beginning and end of each clip with the handles" | Flow Help | Do your object edits *before* extending; trimming is your seam scalpel |
| "When you edit a video in Google Flow, you don't lose the original video"                            | Flow Help                           | Your 8-second original is safe — the "changed" clip is the merged output                                  |
| How long an extension is, its resolution, how many times you can chain it                           | **Not stated** in Flow Help         | Check live; don't plan a long take on the API's numbers below                                             |
| "Each video is generated based on the **final second** of your previous clip"                        | The Keyword, on Flow's Extend (Oct 2025) | Nothing before that second is seen by the new generation — identity comes from that second only      |
| "Extend **finalizes the final second or 24 frames** of your video and continues the action"         | Gemini API                          | The last second of your clip is **re-generated** — motion, light, and sound in that second can shift      |
| "a **single video combining** the user input video and the generated extended video"                 | Gemini API                          | What you get back is a **new merged file**, not your original with a bit added                            |
| "**720p only** for extension"; **7 s** per extension, "up to 20 times", **148 s** in all            | Gemini API                          | If Flow matches, an upscaled base drops back to 720p, and drift and softness compound with each hop       |
| "Voice is not able to be effectively extended **if it's not present in the last 1 second**"          | Gemini API                          | Dialogue must either **finish clearly before** the last second or **still be running through** it         |
| Ingredients or first / last frames in the same call as an extension                                 | Stated nowhere today (unverified)   | Assume identity during an extension comes from the last second, not from your reference photos            |

So the things that "changed" are: **(1)** the seam second was re-shot, **(2)** the new part was made by the cheapest tier — and, if Flow works like the API, the merged file is 720p — and **(3)** the audio bed across the join was re-generated. None of it is a bug. It's the hand-over.

### 2.2 The fixes, in order of effect

**1. Work the whole chain at the generated resolution, upscale once at the end.** Never upscale the base clip and then extend it — the API returns extensions at 720p only and Flow states no resolution, so assume the merge throws those pixels away. Base → extend → extend → *then* upscale the finished clip (1080p is free on AI Pro; 4K is Ultra-only — [[20-colour-finishing-and-delivery]] §2.2), or upscale the whole assembled scene in the editor. One upscale, applied to everything, means one look.

**2. Design the last second as a hand-over, not a climax.** The 24 frames the next crew sees must be *easy to continue*:

- End on a **hold**: weight balanced, face readable, hands visible and still, no limb crossing the frame edge.
- **No camera move in the last second** — finish the push-in or dolly at ~7 s and let it settle.
- **No expression change, turn, or pick-up** in the last second.
- **Dialogue:** end the line by ~6.5 s ("…chai in hand." *beat*), or if the line must carry over, make sure the voice is *audibly running* through the final second.
- Write this into the prompt: *"…she holds the pose, looking at the phone, for the final second."*

**3. Prompt the extension as a continuation, not a new idea.** Flow Help asks only that you "describe how the action should continue" — so, whatever the box shows when it opens, **re-paste your original prompt and change one thing**: keep ~80 % of it verbatim (the lighting, lens, palette, and camera sentences especially) and add **one micro-change**: *"she now begins to smile"*, *"the tanker rolls forward slowly"*. Never introduce a new character, a new location, a new camera move, or a new light source through Extend — that's a new shot, and forcing it is how you get stretched limbs and a different face.

**4. Expect a quality step at the join — and choose what you extend.** Tier changes are look changes, and in Flow every extension is a Lite take. (*Changed in 2026:* "base on Fast, extend on Fast" is no longer possible.) A Lite base extends with no tier change; over a Fast or Quality base, expect a step at the seam. So extend only a base whose continuation you'd accept at Lite quality — never a Quality lock — or don't extend: cut (§4).

**5. When the seam jumps, delete the extension — not the base — and re-extend.** Two or three attempts (⏣10 each) for a clean seam is normal. Regenerate only the failing part; never regenerate the base to fix an extension.

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
① Nano Banana (in Flow) → one clean, sharp, high-res "join still"
     (same references, same framing, same light as the shot — see Phase 5)
② Clip A = Frames→Video, first + last: A's own opening still FIRST,
     the join still LAST (Flow offers first, or first + last — never last alone)
③ Clip B = Frames→Video with the join still as the FIRST frame
```

Both clips now *arrive at* and *depart from* the same crisp picture. Nothing soft ever enters the pipeline, and identity is baked into the still by the references you used to make it. Frames→Video works on every Veo tier, so this route also reaches a Quality lock. This is also how you build a **bridge**: first frame = a still from the end of A, last frame = a still for the start of B, and Flow generates the transition.

**2. If you must use a real frame, harvest it properly.**

- Take it from the **upscaled 1080p download** (free on AI Pro), not the 720p preview. Flow's **Save frame** (pause, hover, Save frame) is quicker and keeps the frame for reuse "as an ingredient, start frame, or end frame", but its resolution isn't stated — compare it with a frame from the download (the ffmpeg line in [[15-continuity-bible-script-supervisor]] §8 grabs an exact one).
- Pick the **sharpest, stillest frame in the last second** — usually *not* the very last one, which is often mid-motion.
- **Clean it**: upscale/de-blur in Nano Banana, Topaz (paid), or the local ComfyUI stack (see [[../comfyui/09-google-flow-parity]]), keep the exact aspect ratio, and colour-match it to a mid-clip frame of A.
- Make sure every detail that must persist is **visible** in it (open mouth, logo, the phone screen).
- Leave Flow's marks alone: every output carries an invisible SynthID watermark, and for people living in India a visible one is applied automatically. Cleaning a frame never means removing, cropping, blurring or painting out the mark ([[20-colour-finishing-and-delivery]] §2.3).

**3. Put identity in the still, not the mode.** Frames→Video and Ingredients→Video are separate modes in Flow, so a start frame plus reference photos in one Veo generation is probably impossible (Flow Help doesn't say; check live). So bake the face/product into the join still *when you make it* (Nano Banana with the same character sheet as its reference — Phase 5 §3; Flow's **Characters**, `@Name`, also bundle a face with a voice, but which models honour them isn't fully documented — check live), and let Frames→Video lock the framing. It is also the only route to a Quality lock with a pinned face: Quality takes no Ingredients.

**4. Same prompt skeleton, same tier, same resolution — then upscale both identically.** Copy the lighting, lens, palette, and style sentences verbatim from clip A's prompt. Render B on the same tier as A. Upscale A and B with the same tool at the same setting.

**5. Hide the join editorially.** A straight continuation *exposes* a mismatch; a **cut** *hides* it. Cut **on action** (the hand reaches for the phone in A → the phone is lifted in B), change the **shot size or angle** across the cut, or drop a 1-second **B-roll insert** between them. Never use a dissolve to paper over a change of face, age, or accessory — it advertises the fault.

**6. Match in post.** In DaVinci Resolve (free edition), **Shot Match** B to A ([[20-colour-finishing-and-delivery]] §4) — Vids has no grade tool; then lay one even grain over both so 720p softness reads as "film", not "AI" (grain is Studio-only as an effect; the free route is [[20-colour-finishing-and-delivery]] §6). This step rescues most near-misses.

## 4. Decision: Extend, Still-Join, or Cut?

```
Same action, same angle, same place, the last second is a quiet hold —
and a Lite-quality continuation is good enough to finish on?
      → EXTEND (every extension is a Lite take; upscale at the end)       §2

Continuous moment but you need control over what the join looks like,
or the shot must lock at Fast or Quality?
      → STILL-JOIN (Nano Banana still = last frame of A = first frame of B)  §3.2 ①

New angle / new location / time jump / different body position?
      → CUT (two clips, cut on action; Vids or Resolve)                   §3.2 ⑤

Need identity locked across the join more than motion continuity?
      → a board still for each clip → Frames→Video (any tier, the only
        way to Quality with a pinned face) + cut on action;
        or Ingredients→Video for both clips (Lite / Fast only)           Phase 5
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

**The 30° rule.** Two consecutive shots of the same subject must differ by **at least 30° of angle** *or* by **two shot sizes** (WS → CU). Anything less reads as a **jump cut** — the picture "hops." If a re-angled shot or a reaction shot looks like a glitch, this is usually why.

**Screen direction & eyelines.** Exit frame-left → enter frame-right (or he appears to walk back). The phone stays in the same hand. Eye-level in shot A means eye-level in shot B of the same conversation (a high angle "answering" an eye-level shot reads as a power shift — use it only on purpose). Flow cannot see your previous shot, so *you* are the script supervisor: write the side, the hand, and the eyeline height into every prompt of the scene, verbatim.

### 5.5 Coverage — give the editor choices (and hide AI faults)

A film crew never shoots one shot per moment; they shoot a **master** plus **coverage** (the same moment from two or three angles) so the editor can cut around anything. In AI video this is your single best defence: **a moment you have from two angles always has a clean cut available.**

In Flow, coverage comes four ways (*changed in 2026:* the old **Jump To** button, which cut to a new angle with the context carried over, is in no current Flow Help page):

| Coverage tool                                   | What it does                                                                                                                                                    | Use for                                                       |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **A derived board still → Frames→Video** (§3.2 ①, §7.4) | Edit the scene's clean still in Nano Banana to the new size or angle ("same office, same light — now a close-up of his face"), then animate it at any tier | Matched-lighting coverage where identity is critical; the reaction, the reverse, the CU after the MS — and the only route to Quality |
| **Ingredients→Video, size changed** (Lite / Fast) | Same character sheet, new prompt: "close-up, same office, same light"                                                                                         | Cheap CU / reaction inserts drafted on Lite, locked at Fast   |
| **A timestamped multi-shot prompt** (Veo 3.1)   | Two set-ups in one generation: `[00:00-00:04] medium shot … [00:04-00:08] close-up reaction …`                                                                 | A quick shot-and-reaction pair; check that both halves hold the face |
| **An Omni Flash re-angle edit** (⏣40)           | Re-prompts up to 10 s of a clip you already have: "change the camera angle to over his shoulder"                                                                | A new angle on a take you love — in another model's look, so frame-pair it ([[15-continuity-bible-script-supervisor]] §8) |

**Harvest, don't use.** An 8-second clip is a *source*, not a shot. A pro cut uses **2–5 s of it** and keeps the rest as handles for the edit. Plan on: **one clip → one or two shots; a 30-second promo → 8–12 shots → 6–8 clips.** Phase 3's "30 s = 4 shots" is four *beats*; each beat gets two or three shots when it's cut like a pro.

**Coverage on a budget (the Prime Directive still rules):** lock only the **face** shots at Quality — from a board still via Frames→Video, since Quality takes no Ingredients; inserts, hands and cutaways at **Fast**; product B-roll from **Frames→Video** off a Nano Banana still; the app UI is a **real screen recording** composited in the edit — never a Veo render. Two Quality locks plus four Fast inserts (⏣280) cost about what Phase 1 budgeted for two beats (⏣300), and cut ten times better.

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
| 1 | Problem | ECU · top-down · static, macro                        | A pen scratches a number into a fat paper register; the ink smudges          | 2 s | **Cut on action** — the hand lifts            | Frames→Video from a Nano Banana still (Fast)                 |
| 2 | Problem | WS · high angle · static (Phase 4 §6 "problem" recipe) | Night office. Dealer hunched over three registers; a phone buzzes on the desk | 3 s | **J-cut** — the buzz continues under #3       | Frames→Video from a board still made with the dealer sheet + office still (**Quality**) |
| 3 | Problem | MCU · eye level · slow push-in                        | He rubs his eyes and glances at the phone                                    | 3 s | **Smash cut** on the ring →                   | Frames→Video from a closer board derived from #2's still (Fast) |
| 4 | Agitate | CU · slightly low · handheld                          | On the phone: *"Payment ho gaya tha!"*                                       | 3 s | **Cut on a look** — he looks down             | Frames→Video from a board still (**Quality**, the dialogue shot) |
| 5 | Agitate | Insert ECU · top-down · static                        | A finger flips register pages; the totals don't match                        | 2 s | **Cutaway on sound** — a truck horn           | Fast, hands only                                             |
| 6 | Agitate | WS · eye level · static, through the office window    | An unfamiliar tanker and driver waiting at the pump                          | 3 s | **Dip to white**, 6 frames → beat 3 (relief)  | Frames→Video from a window board derived from the office still, or Text→Video (Fast) |

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
| **Reaction shot**                 | "Here's how it lands"                                        | After a line or a reveal; **hides lip-sync misses and lets you shorten dialogue**          | It stalls the pace                                          | A board still at the new angle → Frames→Video (§5.5), or an Ingredients→Video CU (Lite / Fast)           |
| **Cutaway / insert**              | "Meanwhile, this detail"                                     | Compress time; hide a bad join; show the UI (composite the real screenshot)                | As a crutch for *every* join — it starts reading like a patch | Fast, or Frames→Video from a still, 1–2 s                                                              |
| **Match cut** (graphic)           | "These two things are the same idea"                         | Problem → solution: paper ledger → app ledger, calculator → phone, in the same framing     | Realism continuity (it's an *idea* cut)                     | Same composition in A's last frame and B's first frame (§3.2 ①), or a Frames→Video bridge                |
| **J-cut / L-cut** (split edit)    | "The next moment is already arriving" / "the last one lingers" | Dialogue; any scene change you want to feel fluid; **burying Extend's re-generated seam audio** | The audio itself is the fault                        | Resolve: roll the audio edit point 10–20 frames — never slide the audio, which breaks lip-sync ([[19-sound-edit-design-and-mix]] §8). Vids can't detach a clip's own sound: run a VO or music bed over the cut instead |
| **Sound bridge**                  | "The sound carries us over"                                  | Scene changes with a motif: kettle whistle → notification chime; horn → engine             | —                                                           | Name A's ending sound and B's opening sound in the prompts; overlap them in the edit                     |
| **Masked / invisible cut**        | "There was no cut"                                           | Faking a continuous take: pass behind a hand, a tanker, a doorframe, darkness              | Nothing in the scene can cover the frame                    | A ends with an object filling the frame; B starts from the same cover; cut inside the black / blur       |
| **Jump cut**                      | "Time skipped — and I'm telling you so"                      | Tutorials, vlogs, comedy, "hours later" on the *same* framing                              | Narrative continuity — it's the failure mode of the 30° rule | Same framing, trim the middle; a 2-frame dip if it's harsh                                              |

### 6.3 The visible ones — transitions (sparingly, on purpose)

| Transition                                       | What it tells the audience                    | Use when                                                                                              | Don't use when                                                                        | How to make it                                                                         |
| ------------------------------------------------ | --------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Smash cut**                                    | "Shock — everything changed"                  | The ad's turning point: night chaos → morning calm; problem → solution                                | Twice in one ad                                                                       | Hard cut from A's loudest frame to B's quietest; kill the music for one beat           |
| **Dissolve** (cross-dissolve)                    | "Time passes / softens"                       | Montage, memory, mood, "later that day"; a **6–12-frame micro-dissolve** to blend a small light shift | To hide a face, age or accessory change — it *advertises* the fault; inside one action | Resolve: Cross Dissolve, or a Vids transition (§6.6). Keep it under 1 s except in montage |
| **Dip to black / white**                         | "Breathe" (white = relief, clean, the "after") | Between distinct beats — Agitate → Solution; tutorial chapters                                        | More than once or twice per piece                                                     | 4–8 frames; Resolve: Dip to Color Dissolve, or a Vids transition                       |
| **Fade in / fade out**                           | "Begin" / "The end"                           | Opening and closing; chapter breaks in long tutorials                                                 | Inside a 30-s ad (kills momentum)                                                     | Resolve: the clip's fade handles, or a Vids transition                                 |
| **Wipe / slide**                                 | "Playful, retro, step-by-step"                | UI walkthroughs, tutorial steps, listicles                                                             | Premium brand films (reads as a slideshow)                                            | Resolve: a Wipe, or Motion → Slide; or a Vids transition                               |
| **Whip pan**                                     | "Energy — same world, new spot"               | Social hype; a quick relocation (office → pump)                                                        | Anything calm; identity-critical joins                                                | A ends on a fast pan right (motion blur); B opens on the same pan settling; cut in the blur |
| **Generative bridge** (Frames→Video, first + last) | "Transformation"                            | Stylised morphs: the paper ledger *becomes* the app ledger; night *becomes* morning                    | Realism — it drifts                                                                   | Flow Frames→Video with both frames, 4–8 s, Fast                                        |
| **Speed ramp**                                   | "Hit"                                         | Beat drops; the product reveal                                                                         | Dialogue                                                                              | Resolve (free edition): retime with **Optical Flow** (Speed Warp is Studio-only); needs clean motion in the source clip. Vids can't change speed |
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
| **Flow — Extend**                        | The same shot continuing (no cut) — a Lite take, on 8 s Veo clips only — §2                                                  |
| **Flow — a timestamped prompt** (Veo 3.1) | A cut *inside* one generation: `[00:00-00:04] … [00:04-00:08] …` — coverage in one clip (§5.5). Omni Flash cuts between shots by default unless told "single continuous shot, no scene cuts" |
| **Flow — Frames→Video (first + last)**   | A generative bridge / morph between two stills — on every Veo tier, and on Omni Flash 1.1 on the web                         |
| **Flow — Omni Flash Edit & refine** (⏣40) | A new angle, light or background on up to 10 s of an existing clip, by prompt — coverage or a rescue, in another model's look; it can't change voices |
| **Flow — Scenebuilder**                  | Order, trim (start / end), preview, download — no transitions, no audio tools                                                |
| **Google Vids**                          | Straight cuts; split a scene at the playhead; the transition types Vids offers between scenes, with a duration slider (Google doesn't name them; a third-party course lists fade, dissolve and slide); text cards; music and voice-over on audio tracks that run across scenes, with automatic ducking. It can't detach a clip's own sound (no true J / L cut of sync audio), grade, keyframe or change speed |
| **DaVinci Resolve (free edition)**       | Split edits (J / L), dips, speed ramps with Optical Flow, Shot Match, adjustment clips — everything Vids can't. Studio-only: Speed Warp, Film Grain, Film Look Creator (the free grain route: [[20-colour-finishing-and-delivery]] §6) |

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

One sentence, about 30 words, pasted **verbatim** into every prompt of the piece, plus the **same style-reference image** behind every still you make — and as an ingredient on any Lite or Fast Ingredients shot (Phase 5 §7). Template:

```
LOOK — "DZZLO night office": shot on 35 mm, shallow depth of field, soft
low-contrast film look with fine grain; warm tungsten desk lamp as key light,
cool blue night through the window as fill; muted palette with one teal
accent; eye-level, tripod-steady camera. 9:16.
```

Rules: same **time of day** across the scene (never "night" in one prompt and "evening" in the next), same weather, same named light sources, same lens words, same palette words, same aspect ratio, one model (Veo 3.1), the same tier where you can, same resolution. Phase 3's brand-feel line and Phase 5's style ingredient *are* this — the usual failure is that the sentence **changed** between prompts: Gemini paraphrased it, or a human "improved" it. Freeze it. A Gem that pastes it for you (Phase 7) exists for exactly this reason — on personal accounts Gems become skills from November 2026, and the instructions carry over.

### 7.4 Lock the set — one still per location, and a props bible

Generate each location **once** as a clean still (Nano Banana Pro or Nano Banana 2, inside Flow): the office at 9 PM; the pump lane at dawn. Every shot in that location either **starts from that still** (Frames→Video, any tier) or **carries it as an ingredient** (Ingredients→Video on Lite or Fast: "the office from image 2"). Keep a **props bible** — the five to eight objects that must persist and what they look like — and paste the relevant lines into every prompt:

```
PROPS — three fat red cloth-bound registers; a black phone in a teal case;
a steel chai glass; a Casio calculator; the window showing the pump's white
canopy lights.
```

Objects you don't name get re-invented — registers thin out, the phone case changes colour, the window moves.

**The stronger version — storyboard the whole piece as one consistent still set before any video.** In one image session, derive every frame from the previous one: *"same office, same light — now from a high wide"* → *"now a top-down of the register"* → *"now a close-up of his face lit by the phone."* Image models hold a look across a set far better than video models hold it across generations, and stills are cheap — Nano Banana 2 Lite is free; check the cost Flow shows for the other image models (for a chain of derived frames use Nano Banana Pro or 2: Google says 2 Lite isn't built for multi-turn editing). Then animate each still with Frames→Video and the Look Sentence ([[14-previs-storyboard-floorplan-animatic]] §4 is the full method). The video model only adds motion; the consistency was decided in the pictures. This is [[03-phase-3-context-and-script-planning|Phase 3]] §5 taken to its conclusion, and it is the single biggest upgrade a patchwork cut can get.

### 7.5 Lock the camera personality

Pick **one** camera style for the whole piece and never leave it:

| Personality               | Words in every prompt                                              | Fits                                   |
| ------------------------- | ------------------------------------------------------------------ | -------------------------------------- |
| **Tripod & push-ins**     | static or slow push-in, eye level, 35 mm, tripod-steady            | Spokesperson, product, trust           |
| **Documentary handheld**  | gentle handheld, natural light, medium-wide, 24–35 mm              | UGC, lifestyle, testimonials           |
| **Cinematic glide**       | slow dolly or orbit, low angle, shallow DoF, 50–85 mm              | Brand films, hero product              |

One movement *speed* too — all "slow", or all "energetic". Phase 4 §6's recipes by content type are these columns; the mistake is taking one shot from each. An aerial opener, an orbiting product shot and a handheld testimonial in the same 30 seconds is three different films.

### 7.6 Fix the rest in the grade — the hero-clip method

1. **Pick the hero clip** — the one that looks most like the Look Sentence.
2. **Match every other clip to it.** DaVinci Resolve (free edition), Color page: press **Auto Color** (A) on the hero and on each clip to match, select them, right-click the hero → **Shot Match to This Clip** — it makes clips alike, not good ([[20-colour-finishing-and-delivery]] §4); or by hand in this order — white balance, exposure, contrast, saturation.
3. **One adjustment clip over the whole timeline**: one LUT, one soft vignette (never over the watermark), one gentle sharpen-or-soften pass (the Blur palette's Sharpen or Mist; the ResolveFX sharpeners are Studio-only), and one fine grain — Studio-only as an effect, so take the free route in [[20-colour-finishing-and-delivery]] §6. Every pixel now goes through the same texture, and **uniform texture is what the eye reads as "one film."** It also hides the 720p-versus-upscaled softness gap from §2.2.
4. **When the sources are far apart, use an anchor grade**: teal-and-orange, high-contrast noir, or black-and-white with the teal accent. Mismatches vanish inside a strong grade.
5. Vids can't do any of this — it has no grade tool. The free edition of Resolve can; it's an hour to learn and it pays back on every piece ([[20-colour-finishing-and-delivery]] §3–§6 is the full method).

### 7.7 Sound is half the consistency

The ear stitches what the eye can't. Under every clip run **one continuous music bed** (Google Flow Music, the Gemini app or Vids — read the terms before you publish; [[06-phase-6-voice-lipsync-audio|Phase 6]]) and **one continuous ambience** (room tone, street). **Mute or duck Veo's per-clip ambience** — each clip's room sounds different, and that alone is a large share of "it feels stitched." Use **one VO voice**, generated once and cut over the picture (Vids AI voice-over is unlimited on AI Pro, Hindi included), instead of per-clip dialogue wherever a line doesn't need to be on-camera. One SFX per object — the same notification chime every time. **J-cut every scene change** (§6.2) so sound arrives before picture. [[19-sound-edit-design-and-mix]] is the full craft.

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
[ ] Look Sentence identical in every prompt; style reference in every still
[ ] One still per location; props bible pasted
[ ] One camera personality; one movement speed
[ ] One model; same tier where you can; same resolution, upscaled once at the end
[ ] Hero clip chosen; every clip matched to it; one adjustment clip over all
[ ] One music bed, one ambience, one VO voice; Veo's ambience ducked
[ ] Shot lengths in a band; cuts on the beat; at most 2 visible transitions
[ ] Bookends; a motif; one graphic system
```

## 8. Recipe — A 24-Second Continuous DZZLO Beat (worked example)

Goal: the dealer at the pump office, phone in hand, order arrives, tanker fills — one continuous feel, no visible seam, deliverable at 1080p.

| Step | Action                                                                                                              | Tier    | Coins   |
| ---- | ------------------------------------------------------------------------------------------------------------------- | ------- | ------- |
| 1    | Nano Banana (in Flow): A's opening still (J0) and **two join stills** with the Ravi character sheet — (J1) dealer looking at phone, (J2) dealer glancing up at tanker | —       | stills: what Flow shows (0 on Nano Banana 2 Lite) |
| 2    | Clip A: Frames→Video, **first frame = J0, last frame = J1**, 720p. Prompt ends "…holds the phone still for the final second." | Lite ×2 | 20      |
| 3    | Clip B: Frames→Video, **first frame = J1, last frame = J2**, 720p, same prompt skeleton                              | Lite ×2 | 20      |
| 4    | Clip C: Frames→Video, **first frame = J2**, tanker fills, 720p                                                      | Lite ×2 | 20      |
| 5    | Seam review (§2.3) on the Lite drafts; fix stills/prompts, not clips                                                 | —       | 0       |
| 6    | Lock A, B, C at Quality, Frames→Video from the same stills (same prompt skeletons)                                 | Quality | 300     |
| 7    | **Upscale once** to 1080p (free on AI Pro); assemble in Scenebuilder, Vids or Resolve; Shot Match in Resolve if needed | —     | 0       |
| **Total** |                                                                                                                |         | **360** + stills |

Compare: "extend, extend, extend" is cheaper in coins — each extension is a Lite take (⏣10) — but everything after the first 8 s is Lite quality, every hop is a seam to review, Flow promises no resolution for it, and when hop 2 drifts you regenerate the chain. The still-join recipe spends coins only on shots you already know are right ([[01-phase-1-the-big-picture]] Prime Directive) and ends with three Quality shots at 1080p.

## 9. Prompt Patterns for the Join

**End-of-clip hold (put at the end of every clip you intend to continue):**

```
…For the final second the camera settles and she holds the pose, eyes on
the phone, hands still, expression unchanged. No new action.
```

**Extension micro-prompt (re-paste your original prompt; keep it, add one line):**

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

- **An extended take is a Lite take.** In Flow every extension is made by Veo 3.1 Lite, and Flow states no resolution for it (the Gemini API's extensions are 720p only). If the shot must be one unbroken take longer than 8 s at Fast or Quality, Extend can't give it to you: accept the Lite chain, upscaled once to 1080p — or use the still-join.
- **Drift compounds.** Hop 3 of an extend chain has seen hop 2's re-shot second, not your original. Beyond two hops, expect to re-anchor with a still-join or a cut.
- **The re-shot second is not optional.** You can trim it, you can make it quiet, but you cannot tell Extend to leave it alone.
- **Google re-tunes this constantly** — Extend was Veo 2-only and silent in mid-2025, gained audio with Veo 3.1 that October, and in Flow today runs only on Lite. Re-check Flow Help's models page (§12) before relying on a tier or a limit.

## 11. Exercises

**11.1 — See the re-shot second (~⏣40).** Render an 8 s Lite clip with a deliberate motion in the last second (a head turn) (⏣10). Extend it — a Lite take (⏣10). Frame-step the join: watch the turn get re-shot. Now render the same clip ending on a hold and extend again (⏣20). Compare the seams. (Optional, ⏣10: extend an 8 s Fast clip you already own and look for the quality step at the seam — §2.2 fix 4.)

**11.2 — Prove the photocopy problem (~⏣30).** Take the last frame of a Lite clip from the 720p preview → Frames→Video. Then take the same frame from the upscaled download, clean it in Nano Banana → Frames→Video. Side by side.

**11.3 — Still-join (~⏣40, plus the stills at the cost Flow shows).** Make one Nano Banana join still with your Ravi sheet, and an opening still for clip A. Clip A with the opening still *first* and the join still *last*, clip B with the join still *first*, both Lite, two drafts each. Butt them together in Scenebuilder. This should be your cleanest join yet.

**11.4 — Cut instead (~⏣20).** Same beat as 11.3 but as two different shot sizes cut on action. Notice it's cheaper, faster, and nobody sees a "join" because there isn't one.

**11.5 — Break a beat (0 coins).** Take beat 3 of the promo, "The Verified Order," and answer the seven questions (§5.2). Then write it as three shots in the §5.8 table with an **Out →** for each. If you can't name the Out, the shot isn't designed yet.

**11.6 — Cut it three ways (0 coins, existing clips).** In Vids or Resolve, join any two of your clips (a) as a straight cut on action, (b) with a 1-second dissolve, (c) as a smash cut with the music dropped for a beat. Watch each one muted. Only one feels like an ad; the dissolve is the one that looks like AI.

**11.7 — Coverage for free (~⏣20, plus the still).** From an existing MS clip, generate the reaction CU two ways: a **derived board** — Save frame from the MS, make a close-up still from it in Nano Banana ("same man, same office, same light — close-up"), then Frames→Video on Lite — and **Ingredients→Video** on Lite with "close-up, same office, same light." Cut each against the MS with the 30° rule in mind. Keep whichever holds identity; note which you'd reach for next time. (Optional, ⏣40: ask Omni Flash's Edit & refine for the same close-up as a re-angle of the MS — another model, so frame-pair it.)

**11.8 — Hero-clip grade (0 coins).** Take your last stitched piece into DaVinci Resolve (free edition). Pick the hero clip, Auto Color and **Shot Match to This Clip** the rest to it, add one **adjustment clip** with a LUT and a soft vignette, lay a continuous music bed and mute Veo's ambience. (Grain is Studio-only as an effect; add the free route from [[20-colour-finishing-and-delivery]] §6 once the rest works.) Export and play it next to the original. That is usually the "nice" that was missing — and it cost nothing.

**11.9 — Storyboard set first (~⏣60, plus the stills).** In one image session — Nano Banana Pro or 2, at the cost Flow shows — make six stills of one location, each derived from the previous ("same office, same light, now…"). Animate three of them on Lite with Frames→Video and the Look Sentence. Cut them together. Now cut three Text→Video clips of the same beats. The difference is §7.4.

## 12. Sources (web-verified 2026-09-25; re-verified 2026-10-01)

Primary (Google):

- [Models & supported features — Flow Help](https://support.google.com/flow/answer/16352836) (only Veo 3.1 Lite extends, 8 s Veo clips only; Frames to Video "First" or "First and last" on every tier; no Ingredients on Quality; the Nano Banana image models; Omni Flash extend "coming soon")
- [Edit videos & build scenes in Flow — Flow Help](https://support.google.com/flow/answer/16935718) (Extend: "describe how the action should continue", Veo-only inputs, no insert / remove / camera on extended clips; Scenebuilder trims; Save frame; the original is kept; Edit & refine on up to 10 s)
- [Create videos in Flow — Flow Help](https://support.google.com/flow/answer/16353334) (Frames to Video, Ingredients; voice references only with Ingredients)
- [Google Flow credits — Flow Help](https://support.google.com/flow/answer/16526234) (cost per generation; Extend still listed under every Veo tier; 1080p upscale free on AI Pro, 4K Ultra-only; Omni Flash edit 40)
- [Veo on the Gemini API](https://ai.google.dev/gemini-api/docs/veo) (the API's Extend: "final second or 24 frames", "720p only", 7 s up to 20 times, 148 s, voice in the last second, "not Veo 3.1 Lite"; a last frame needs a first frame)
- [Gemini Omni on the Gemini API](https://ai.google.dev/gemini-api/docs/omni) (Omni's extension reads the last 10 s, up to 40 s in all; "single continuous shot", "No scene cuts")
- [Bringing new Veo 3.1 updates into Flow — The Keyword, 2025-10-15](https://blog.google/innovation-and-ai/products/veo-updates-flow/) ("generated based on the final second of your previous clip")
- [New creative controls in Google Flow — The Keyword, 2026-08-27](https://blog.google/innovation-and-ai/models-and-research/google-labs/new-creative-controls-google-flow/) (Omni Flash 1.1: start and end frames)

Secondary (practitioner write-ups — treat as indicative):

- [How to extend AI video scenes naturally in Google Flow — FourFeetz, updated 2026-07-29](https://fourfeetz.com/insights/extend-ai-video-scenes-google-flow) (finish on a stable pose; review silhouette, facial age, accessories, shadow and camera speed at the join; "enough continuity evidence"; when a separate shot is cleaner)
- [Flow Scenebuilder Extend shots — DigiWebInsight, 2025-11-11](https://digiwebinsight.com/flow-scenebuilder-extend-shots/) (delete the extension, not the original, and re-extend; it reported the box pre-filled with your prompt — Flow Help doesn't say)
- [How to extend Veo 3.1 videos beyond 8 seconds — AI Free API, 2025-12-30](https://www.aifreeapi.com/en/posts/veo-3-extend-video-length) (API-side: 720p-only extensions; repeat "at least 80%" of the original prompt)
- [Testing the limits of AI video with Veo 3.1 — The AI Filmmaker, 2025-10-18](https://theaifilmmaker.substack.com/p/testing-the-limits-of-ai-video-with) (details not visible in the saved frame get re-invented)

Film grammar, and the tools' own cut / transition features (§5–6):

- [5 tips for using Flow — The Keyword, 2025-06-25](https://blog.google/innovation-and-ai/products/flow-video-tips/) and [How to use Google Flow — Tom's Guide, 2025-06-19](https://www.tomsguide.com/ai/google-gemini/how-to-use-google-flow-the-new-ai-video-generator-meant-for-filmmakers) — history only: how Scenebuilder's Jump To and Extend worked in mid-2025 (then "only with Veo 2", per Google). Today Jump To is in no Flow Help page, and Extend runs on Veo 3.1 Lite
- [Ultimate prompting guide for Veo 3.1 — Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1) (timestamp prompting: "a complete, multi-shot sequence … within a single generation")
- [Google Vids — transitions](https://support.google.com/docs/answer/14916386) (type and duration slider; types not named) · [audio tracks](https://support.google.com/docs/answer/14999865) (tracks span scenes; Narrative / Background ducking)
- [Adding visual enhancements in Google Vids — DataCamp](https://campus.datacamp.com/courses/create-engaging-video-with-google-vids/create-engaging-video-with-google-vids?ex=7) (third party: lists fade, dissolve and slide between scenes)
- [180-degree rule — Wikipedia](https://en.wikipedia.org/wiki/180-degree_rule)
- [30-degree rule — Wikipedia](https://en.wikipedia.org/wiki/30-degree_rule)
- [Cut (transition) — Wikipedia](https://en.wikipedia.org/wiki/Cut_(transition))
- [Dissolve (filmmaking) — Wikipedia](https://en.wikipedia.org/wiki/Dissolve_(filmmaking))
- [Walter Murch — Wikipedia (*In the Blink of an Eye*, the Rule of Six)](https://en.wikipedia.org/wiki/Walter_Murch)
- [Video transitions in film, with examples — Backstage](https://www.backstage.com/magazine/article/video-transitions-75727/)
- [The hidden meaning behind popular video transitions — PremiumBeat](https://www.premiumbeat.com/blog/the-hidden-meaning-behind-popular-video-transitions/)

Look, prompting and grading consistency (§7):

- [How to create effective prompts with Veo — DeepMind prompt guide (style, lighting, lens keywords)](https://deepmind.google/models/veo/prompt-guide/)
- [DaVinci Resolve — Blackmagic Design](https://www.blackmagicdesign.com/products/davinciresolve) (the free edition) · [DaVinci Resolve 21.1 Studio features](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_Studio_21_Features.pdf) (Studio-only: Film Grain, Film Look Creator, Speed Warp, the ResolveFX sharpeners) · [DaVinci Resolve 21 Reference Manual](https://documents.blackmagicdesign.com/UserManuals/DaVinci_Resolve_21_Reference_Manual.pdf) (Shot Match after Auto Color; adjustment clips; Optical Flow; the built-in transitions)
- [Google Flow Music plans — Flow Help](https://support.google.com/flow/answer/17083870) (the music bed, §7.7) · [Gems are becoming skills — Gemini Apps Help](https://support.google.com/gemini/answer/18560919?hl=en)

---

**Next:** the Director's & Editor's track → [[11-directors-track-roadmap]] · **Back to:** [[00_README]] · Beats → shot lists: [[03-phase-3-context-and-script-planning]] · Consistency layers: [[05-phase-5-character-consistency]] · Voice & music bed: [[06-phase-6-voice-lipsync-audio]] · Camera language for the hold: [[04-phase-4-camera-control]] · Assembly: [[08-phase-8-pro-workflow-and-playbooks]] · Cheat-sheets: [[09-reference]]
