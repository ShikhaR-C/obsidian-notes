# Phase 4 — Camera Control: Talking to the Robot Camera

> Level: Intermediate | Time: ~1 hr | Outcome: you can name any shot the way a real director does — size, angle, movement, lens — and get the camera to do exactly that instead of wandering. | Status: written & web-verified 2026-07-15; **tool facts re-verified and corrected 2026-10-01**.

---

## 1. The One Idea

The camera is a **character in the crew**, and if you don't tell it where to stand and how to move, **it decides for itself** — often a boring, static, eye-level shot, and rarely the one you had in mind. So you *always* tell it.

Good news: the crew speaks fluent **film**. Real camera words — "low-angle tracking shot," "slow dolly in," "aerial drone shot" — aren't jargon to Veo; Google's own Veo prompt guides are written in them. You don't invent a special syntax; you talk like a director, and it usually obeys. This phase is just teaching you the words.

Every camera instruction is a combination of four choices: **how big, from what angle, moving how, through what lens.**

## 2. Shot Size — How Much Do We See?

How much of the subject fills the frame. This is your emotional dial: wide = context and scale, close = emotion and detail.

| Shot size              | You see…                                  | Use it for                                        |
| ---------------------- | ----------------------------------------- | ------------------------------------------------- |
| **Extreme wide (EWS)** | Tiny subject in a big world               | Establishing a place; scale; "where are we"       |
| **Wide (WS)**          | Whole body + surroundings                 | Setting a scene; showing action in context        |
| **Medium (MS)**        | Waist-up                                   | The workhorse — spokespeople, demos, dialogue     |
| **Close-up (CU)**      | Face, or one object filling the frame     | Emotion; product hero shots; "look at *this*"     |
| **Extreme close-up (ECU)** | An eye, a fingertip, a logo detail    | Drama; texture; the app icon; a single tap        |
| **Over-the-shoulder (OTS)** | Behind one person, facing another    | Conversations; "using the app" POV                |

## 3. Camera Angle — Where Do Our Eyes Stand?

Where the camera sits relative to the subject. Angle is *attitude*: it silently tells the viewer how to feel about what they're seeing.

| Angle                        | Feeling it creates                         | Use it for                                      |
| ---------------------------- | ------------------------------------------ | ----------------------------------------------- |
| **Eye-level**                | Neutral, honest, relatable                 | Testimonials, spokespeople — trust              |
| **Low angle** (looking up)   | Powerful, heroic, aspirational             | Making a product or founder look strong         |
| **High angle** (looking down)| Small, vulnerable, overwhelmed             | The "problem" shot — before your product helps  |
| **Bird's-eye / top-down**    | Clean, organised, god's-eye clarity        | Flat-lays, maps, "the whole picture" dashboards |
| **Aerial / drone**           | Epic scale, freedom, journey               | Openers; logistics/fleet-movement grandeur      |
| **Dutch angle** (tilted)     | Unease, energy, edginess                   | Rare — tension or a deliberately quirky brand   |

> **Pairing angle to message is free storytelling.** Shoot the "before" (stressed fleet owner, Phase 3) from a **high angle** so he looks buried, then the "after" (using DZZLO) from a **low angle** so he looks in command. You just told the whole product story with two camera positions and zero extra words.

## 4. Camera Movement — How Does It Move?

The big one, because it's what people forget and what makes a clip feel *alive* versus like a screensaver. State it explicitly, every time.

| Movement                | What happens                                       | 5-year-old                     | Use it for                                   |
| ----------------------- | -------------------------------------------------- | ------------------------------ | -------------------------------------------- |
| **Static / locked**     | Camera doesn't move                                | "Camera stands still"          | Clean product shots; calm, confident talk    |
| **Pan** (left/right)    | Pivots horizontally in place                       | "Turn your head side to side"  | Revealing a space; following lateral motion  |
| **Tilt** (up/down)      | Pivots vertically in place                          | "Nod your head up/down"        | Revealing height; head-to-toe reveals        |
| **Dolly in / push-in**  | Whole camera moves *toward* subject                | "Walk closer"                  | Building focus/emotion; "pay attention"      |
| **Dolly out / pull-back** | Camera moves *away*                              | "Walk backward"                | Reveals; endings; "there's more to it"       |
| **Tracking / follow**   | Moves *alongside* a moving subject                 | "Walk next to them"            | Energy; following a rider, a product in use  |
| **Crane / jib**         | Rises or drops vertically                          | "Lift up on a swing"           | Grand reveals; establishing openers          |
| **Orbit / arc**         | Circles *around* the subject                       | "Walk in a circle around it"   | **Product hero shots** — the money move      |
| **Zoom**                | Lens magnifies (camera stays put)                  | "Squint to see closer"         | Snap emphasis; retro/energetic feel          |
| **Handheld**            | Subtle natural shake                               | "Hold the camera in your hand" | Documentary realism; authenticity; UGC feel  |
| **FPV / drone**         | Fast, swooping, first-person flight                | "Fly like a bird"              | High-energy openers; dynamic brand films     |

> **The one-move rule.** One 8-second clip gets **one** camera move. "It pushes in, then orbits, then cranes up" is three shots. Ask for one clean move and the crew nails it; ask for three and it fumbles all of them. Save the multi-move sequences for stitching in Scenebuilder/Vids (Phase 8). The exception is a planned *cut*: timestamped beats (`[00:00-00:04] … [00:04-00:08] …`) put two set-ups, one move each, in one Veo 3.1 generation.

> **Changing the camera after the render.** Flow on desktop lists **camera position & motion** edits, but its Help gives no steps (check live), and they can't touch an extended clip. A **Gemini Omni Flash 1.1** edit (⏣40) can re-angle up to 10 seconds of a clip by prompt. Both are rescues; direct the camera in the prompt.

## 5. Lens & Focus — The Photographer's Touch

The finishing layer that reads as "expensive." You don't always need it, but it's the difference between *snapshot* and *cinematic*.

| Term                        | Effect                                                       | Use it for                              |
| --------------------------- | ----------------------------------------------------------- | --------------------------------------- |
| **Shallow depth of field**  | Subject sharp, background creamy-blurred (*bokeh*)          | Product & spokesperson shots — premium  |
| **Deep focus**              | Everything sharp front-to-back                              | Dashboards, maps, "see it all" clarity  |
| **Wide-angle lens**         | Expansive, slightly exaggerated space                      | Rooms, landscapes, dynamic FPV          |
| **Telephoto / 85mm**        | Compressed, flattering, distant-feel                       | Flattering faces; isolating a subject   |
| **Macro**                   | Extreme tiny-detail close-up                               | Textures, materials, a chip on a board  |
| **Rack focus**              | Focus shifts from one thing to another mid-shot            | Directing the eye A→B; reveals          |
| **35mm film / cinematic**   | Filmic grain, gentle contrast                              | The default "make it look like a movie" |

Google's Veo prompt guides use nearly every word in §2–§5. The main exceptions — "orbit" (Google says "arc shot"), "FPV", focal lengths like "85mm" — are hints, and Google files "shot on 35mm film" under style. Google also warns that some advanced angles and lenses "are not officially supported": test an unusual one on Lite first.

## 6. Putting It Together: Stacked Camera Language

You combine the four choices into one phrase, front-loaded in the prompt — Google's own Veo formula starts the same way: [Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]. The crew reads it as a single instruction:

```
[MOVEMENT] + [SIZE] + [ANGLE] + [LENS/FOCUS]

"Slow dolly-in medium shot at eye level, shallow depth of field"
"Aerial drone shot, wide, high above, sweeping"
"Orbiting close-up, low angle, on 35mm film with soft bokeh"
"Static top-down shot, deep focus"  (perfect for a dashboard)
```

### Camera recipes by content type (steal these)

| Content                      | Camera recipe                                                          |
| ---------------------------- | --------------------------------------------------------------------- |
| **Product hero (ad)**        | Slow **orbit / arc**, close-up, low angle, shallow DoF, 35mm          |
| **Spokesperson / testimonial** | **Static** or **slow push-in**, medium, eye-level — trust           |
| **Lifestyle / UGC feel**     | **Handheld tracking**, medium-wide, eye-level — authentic            |
| **App / dashboard reveal**   | **Static top-down** or slow **push-in**, deep focus                   |
| **Big brand opener**         | **Crane up** or **aerial drone**, extreme wide — scale               |
| **"Problem" shot**           | **High angle**, static, slightly wide — subject looks overwhelmed     |
| **"Solution" shot**          | **Low angle**, slow push-in — subject looks in command                |

## 7. Exercises

**7.1 — Feel the shot sizes (cost: ~40 coins, one output each).** Same subject and prompt, render on **Lite** at EWS, MS, CU, and ECU. Line them up. *This* is your emotional dial — you'll now reach for it deliberately.

**7.2 — Prove movement matters.** Render one prompt with **no** camera instruction, then the same prompt with "slow dolly-in, shallow depth of field." Same idea, wildly different feel. Notice what the version with no instruction chose for you — usually flatter, and never your decision. That's the default you're overriding.

**7.3 — Tell a story with two angles.** Render the DZZLO "problem" beat as a **high-angle** shot, and the "solution" beat as a **low-angle** push-in. Watch the camera do the storytelling for you.

**7.4 — Build the product hero (~10 coins).** Take a product image (a Nano Banana still of the phone, its screen a plain glow — the real app is composited later, [[01-phase-1-the-big-picture|Phase 1]] §7), feed it to Flow as **Frames→Video** (start frame), and prompt an **orbiting close-up, low angle, shallow DoF, 35mm** on Lite. This is the single most reusable ad shot you'll make — save the prompt to your library.

**7.5 — Add a camera column to your library.** In `flow-content/templates.md`, add the §6 recipe table. Every future shot starts by picking a recipe row.

---

**Sources (re-verified 2026-10-01):** [Veo video prompt guide — Google Cloud](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/video/video-gen-prompt-guide) · [Veo 3.1 prompting guide — Google Cloud](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1) · [Veo — Gemini API](https://ai.google.dev/gemini-api/docs/veo) · Flow Help: [edit & build scenes](https://support.google.com/flow/answer/16935718), [credits](https://support.google.com/flow/answer/16526234). More in [[09-reference]] §9.

**Next:** [[05-phase-5-character-consistency]] — the hardest problem in AI video, solved: how to keep the *same* face, product, and style across every clip using reference stills, start frames and Ingredients.
