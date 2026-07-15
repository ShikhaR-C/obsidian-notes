# Phase 5 — Character Consistency: Beating the Crew's Amnesia

> Level: Intermediate | Time: ~1.5 hr | Outcome: you can keep the *same* face, the *same* product, and the *same* style across a dozen clips — the single hardest thing in AI video, and the thing that separates a brand from a mess.

---

## 1. The One Idea

Remember catch #1 from the [[00_README]]: **the crew forgets everyone after 8 seconds.** Type "a friendly delivery rider" into ten clips and you get ten *different* riders — different faces, different shirts, different everything. For a one-off that's fine. For a *brand*, it's fatal: your spokesperson can't have a new face in every ad.

You beat amnesia by **showing the crew a photo instead of describing a stranger.** That's the whole trick, and Flow gives you three ways to do it, which you stack like belt *and* suspenders:

```
  IDENTICAL WORDS   +   INGREDIENT PHOTO   +   START FRAME   +   EXTEND
  (describe the         (show the exact        (begin from      (continue the
   same person the       face/product —         an approved      same clip past
   same way every        up to 3 refs)          still)           8 seconds)
   time)
       └──────── each layer pins down more; together they lock identity ────────┘
```

No single layer is perfect. Together they're how professionals get one character through a whole campaign.

## 2. Layer 1 — Ingredients to Video (the main event)

This is Veo 3.1's headline consistency feature. An **ingredient** is a consistent visual element — a **character**, an **object/product**, or a **style** — that you pin by giving Flow a reference image. You can use **up to 3 ingredients per generation**, and every render pulls from those references instead of inventing something new.

**How to use it (in Flow):**

1. Choose **"Ingredients to Video."**
2. Add up to three reference images — either **upload** them or **generate** them with Imagen right there.
3. In your text prompt, **describe how the ingredients should be used.** You refer to them by what they are: *"the woman"*, *"the phone"*, *"in this style."*

Example — three ingredients (a spokesperson, the product, a setting) combined:

```
Ingredients:  [1] photo of our spokesperson   [2] phone showing DZZLO app   [3] warm office style
Prompt: The woman from image 1 sits at a desk holding the phone from image 2,
smiling at the camera, in the warm office style of image 3. Medium shot,
slow push-in, eye-level. She says: "One screen for your whole fleet."
No subtitles.
```

Now the *same* spokesperson, the *same* app, and the *same* look carry across every clip in the campaign — because every clip is anchored to the same three pictures.

## 3. The Reference Image Is Everything

> "The quality of your reference photo directly affects character consistency. A sharp, well-lit photo produces consistent results. A blurry or low-res photo produces inconsistent characters every time."

Treat making the ingredient as a real step, not an afterthought. Rules that actually move the needle:

| Do                                              | Don't                                        |
| ----------------------------------------------- | -------------------------------------------- |
| Sharp, high-resolution, well-lit                | Blurry, dark, tiny, or compressed            |
| **Plain or segmented background** (subject isolated) | Busy background the model confuses for the subject |
| Neutral, clear view of the face / product       | Extreme angle, half-hidden, motion-blurred   |
| One clear subject per ingredient slot           | A collage of five things in one image        |
| Consistent lighting to how you'll use it        | Wildly different light than the target scene |

**Where the reference comes from — Imagen 4 or Whisk:**

- **Imagen 4** — generate a clean, front-lit "character sheet" portrait of your spokesperson on a plain background. That single still becomes your reusable ingredient. Generate the *product* the same way.
- **Whisk** — mix a **subject** image + a **scene** image + a **style** image into a new still. Perfect for spinning up on-brand ingredients and variations fast, and Whisk *Animate* can even push a still straight to video.

Make your ingredients **once**, save them to `flow-content/ingredients/` in Drive, and reuse them for months. A spokesperson you generate today is a spokesperson you still have next quarter.

## 4. Layer 2 — Identical Words (the free reinforcement)

Ingredients do the heavy lifting, but the *text* still matters: describe the character the **exact same way every time.** Not "a rider" one clip and "a young man" the next — copy-paste the same description string.

Keep a **character bible** line you paste verbatim:

```
CHARACTER — "Ravi": a friendly Indian man, early 30s, short black hair, light
stubble, wearing a navy DZZLO polo shirt, warm approachable smile.
```

Every prompt featuring Ravi gets that exact sentence. Words + ingredient photo pointing at the *same* identity is far stronger than either alone. (This is also exactly what a **Gemini Gem** automates in Phase 7 — it pastes the bible for you, every time, without drift.)

## 5. Layer 3 — Frames to Video (pin the first picture)

**Frames→Video** lets you hand Flow a **first frame** (and optionally a **last frame**) as still images, and the crew animates *from* them. Because you've approved that exact opening picture, the clip can't start with a stranger — it starts with your face, your product, your framing.

This is why the Phase 3 workflow storyboards in Imagen first: that approved still isn't just a plan, it's the **start frame** you feed here. Story-boarded still → Frames→Video is the most controllable path in all of Flow.

## 6. Layer 4 — Extend & Scenebuilder (continuity past 8 seconds)

Within a single continuous moment, **Scene Extension** generates the next clip *from the last frame of the current one* — so second 9 looks like second 8 because it literally grew out of it. Chained, this is how you get past 60 seconds while staying consistent.

**Scenebuilder** ("Jump To") is the timeline where you extend, re-time, and stitch shots together into a scene. Use it to keep continuity *inside* a beat; use Vids (Phase 8) to assemble *separate* beats into the final cut.

> **The honest limit.** Even with all four layers, identity can still **drift** — a slightly different jawline, a shifting shirt logo, hands doing hand things. Mid-2026 Veo 3.1 is *dramatically* better than a year ago ("identity consistency is better than ever"), but it is not a locked 3D model of your actor. Practical rules: (1) keep clips short — drift compounds with length; (2) favour Ingredients + start-frame over pure text; (3) hide the hardest continuity cuts behind an edit or a B-roll shot in Vids; (4) for a face that must be *pixel*-locked (regulated claims, a real named person), shoot real footage or composite — don't fake it. Knowing when *not* to use the tool is part of using it well.

## 7. Consistency Isn't Just Faces

The same machinery locks your **brand**, not only people:

| Keep consistent | How                                                                        |
| --------------- | ------------------------------------------------------------------------- |
| **Product**     | A clean product still as an ingredient; identical product description text |
| **Logo**        | Logo as an ingredient + "DZZLO logo clearly visible on the shirt/screen"    |
| **Style / look**| A style-reference image as ingredient #3; identical style sentence in every prompt |
| **Color / mood**| Bake brand colours into the style sentence ("DZZLO teal and white palette") |

Style consistency is what makes ten different shots feel like *one campaign*. The Phase 7 brand brain exists to make that style sentence automatic across everything you generate.

## 8. Exercises

**8.1 — Make your cast (Imagen).** Generate one clean, plain-background portrait of a DZZLO spokesperson ("Ravi") and one clean product still (phone showing the app). Save both to `flow-content/ingredients/`. Write Ravi's character-bible line.

**8.2 — Prove amnesia is real (cost: ~20 coins).** Text→Video, **Lite**, prompt "a friendly Indian delivery rider" — twice, no ingredient. Note the two different people. *This is the problem you're solving.*

**8.3 — Fix it with an ingredient (~20 coins).** Now **Ingredients→Video** with your Ravi portrait, same prompt twice. Same face both times. You just beat amnesia — feel the difference.

**8.4 — Three ingredients at once (~10 coins).** Combine Ravi + product + a style image in one Lite render (the §2 prompt). Confirm all three carry.

**8.5 — Storyboard-to-frame.** Take an approved Imagen still and run it through **Frames→Video**. Compare its controllability to a cold text→video of the same idea. This becomes your default path.

**8.6 — Extend a beat.** Render an 8-second Ravi clip, then use **Scene Extension** to grow it to ~16 seconds. Watch continuity hold across the seam.

---

**Next:** [[06-phase-6-voice-lipsync-audio]] — giving your consistent character a consistent *voice*: dialogue, lip-sync, sound effects, and music, all conducted with words.
