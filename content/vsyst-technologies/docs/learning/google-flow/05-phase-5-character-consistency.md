# Phase 5 — Character Consistency: Beating the Crew's Amnesia

> Level: Intermediate | Time: ~1.5 hr | Outcome: you can keep the *same* face, the *same* product, and the *same* style across a dozen clips — the single hardest thing in AI video, and the thing that separates a brand from a mess. | Status: written & web-verified 2026-07-15; **tool facts re-verified and corrected 2026-10-01**.

---

## 1. The One Idea

Remember catch #1 from the [[00_README]]: **the crew forgets everyone after 8 seconds.** Type "a friendly delivery rider" into ten clips and you get ten *different* riders — different faces, different shirts, different everything. For a one-off that's fine. For a *brand*, it's fatal: your spokesperson can't have a new face in every ad.

You beat amnesia by **showing the crew a photo instead of describing a stranger.** That's the whole trick, and Flow gives you three ways to do it, which you stack like belt *and* suspenders:

```
  IDENTICAL WORDS   +   INGREDIENT PHOTO   +   START FRAME   +   EXTEND
  (describe the         (show the exact        (begin from      (continue the
   same person the       face/product —         an approved      same clip past
   same way every        Lite & Fast,           still — any      8 seconds —
   time)                 not Quality)           tier)            Lite only)
       └──────── each layer pins down more; together they lock identity ────────┘
```

No single layer is perfect. Together they're how professionals get one character through a whole campaign.

## 2. Layer 1 — Ingredients to Video (the main event)

This is Veo 3.1's headline consistency feature. An **ingredient** is a consistent visual element — a **character**, an **object/product**, or a **style** — that you pin by giving Flow a reference image. Flow states no maximum (the Veo API takes three), and every render pulls from those references instead of inventing something new. It works on Veo 3.1 **Lite and Fast** (8-second clips) and Gemini Omni Flash 1.1 — **not on Quality** (*changed in 2026*; see §5).

**How to use it (in Flow):**

1. Model name → **Video** → **Ingredients** (or type **@**).
2. Add your reference images — **upload** them or **generate** them with Nano Banana right there.
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

> **Your reference photo decides your character's consistency.** A sharp, well-lit photo produces consistent results; a blurry or low-res one, a different character every time.

Treat making the ingredient as a real step, not an afterthought. Rules that actually move the needle:

| Do                                              | Don't                                        |
| ----------------------------------------------- | -------------------------------------------- |
| Sharp, high-resolution, well-lit                | Blurry, dark, tiny, or compressed            |
| **Plain or segmented background** (subject isolated) | Busy background the model confuses for the subject |
| Neutral, clear view of the face / product       | Extreme angle, half-hidden, motion-blurred   |
| One clear subject per ingredient slot           | A collage of five things in one image        |
| Consistent lighting to how you'll use it        | Wildly different light than the target scene |

**Where the reference comes from — Nano Banana, inside Flow:**

- **Nano Banana Pro or 2** — generate a clean, front-lit "character sheet" portrait of your spokesperson on a plain background. That single still becomes your reusable ingredient. Generate the *product* the same way. (Nano Banana 2 Lite is free but weakest with references; check the cost Flow shows for the others.)
- **Several images at once** — drag a **subject**, a **scene** and a **style** image into the prompt box and describe the new still (what Whisk did until it closed in April 2026; Nano Banana Pro or 2 handle several references best).

Make your ingredients **once**, save them to `flow-content/ingredients/` in Drive, and reuse them for months. A spokesperson you generate today is a spokesperson you still have next quarter. Flow can also save one as a **Character** (`@Name`) — one or two images plus a voice, clothes included, so make one per wardrobe ([[15-continuity-bible-script-supervisor]] §3); which models honour it isn't fully documented — check live.

## 4. Layer 2 — Identical Words (the free reinforcement)

The picture does the heavy lifting, but the *text* still matters: describe the character the **exact same way every time.** Not "a rider" one clip and "a young man" the next — copy-paste the same description string.

Keep a **character bible** line you paste verbatim:

```
CHARACTER — "Ravi": a friendly Indian man, early 30s, short black hair, light
stubble, wearing a navy DZZLO polo shirt, warm approachable smile.
```

Every prompt featuring Ravi gets that exact sentence — its description, without the label: quotation marks are for speech. Words + picture pointing at the *same* identity is far stronger than either alone. (This is also exactly what a **Gemini Gem** automates in Phase 7 — it pastes the bible for you, every time, without drift.)

## 5. Layer 3 — Frames to Video (pin the first picture)

**Frames→Video** (on every Veo tier) lets you hand Flow a **first frame** (and optionally a **last frame**) as still images, and the crew animates *from* them. Because you've approved that exact opening picture, the clip can't start with a stranger — it starts with your face, your product, your framing.

This is why the Phase 3 workflow storyboards in Nano Banana first: that approved still isn't just a plan, it's the **start frame** you feed here. Story-boarded still → Frames→Video is the most controllable path in all of Flow — and the **only route to a Quality lock with a pinned identity**, since Quality takes no Ingredients: bake face and product *into the still*, draft on Lite, lock on Fast or Quality ([[14-previs-storyboard-floorplan-animatic]] §4).

## 6. Layer 4 — Extend & Scenebuilder (continuity past 8 seconds)

Within a single continuous moment, **Extend** continues an 8-second Veo clip from its *last second* (per Google), not its last frame — so second 9 looks like second 8 because it literally grew out of it. *Changed in 2026:* in Flow **only Veo 3.1 Lite extends**, so an extended take is Lite quality — expect a step at the seam after a Fast or Quality base. (Flow's credits page lists Extend under all three tiers while its models page says you must use Lite — check the model and cost Flow shows.) Prefer a cut or the still-join ([[10-deep-dive-scene-continuity]] §3.2); keep Extend for the rare long take.

**Scenebuilder** arranges, reorders and trims clips, previews and downloads — no transitions, no audio tools. Use it to check continuity *inside* a beat; use Vids (Phase 8) to assemble *separate* beats into the final cut. *Changed in 2026:* **Jump To** is in no current Flow Help page; for a new angle, use a board still → Frames→Video, Ingredients on Fast, a timestamped multi-shot prompt or an Omni Flash re-angle edit (⏣40).

> **When the seam fights you.** Per the Gemini API, Extend *re-generates the last second* of your clip and hands back one merged **720p** file, and a clip started from a saved last frame inherits that frame's softness. Both have fixes — the join-on-a-still recipe above all — in [[10-deep-dive-scene-continuity]].

> **The honest limit.** Even with all four layers, identity can still **drift** — a slightly different jawline, a shifting shirt logo, hands doing hand things. Mid-2026 Veo 3.1 is *dramatically* better than a year ago ("identity consistency is better than ever"), but it is not a locked 3D model of your actor. Practical rules: (1) keep clips short — drift compounds with length; (2) favour a still-made start frame or Ingredients over pure text; (3) hide the hardest continuity cuts behind an edit or a B-roll shot in Vids; (4) for a face that must be *pixel*-locked (regulated claims, a real named person), shoot real footage or composite — don't fake it. Knowing when *not* to use the tool is part of using it well.

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

**8.1 — Make your cast (Nano Banana 2 Lite, 0 coins).** Generate one clean, plain-background portrait of a DZZLO spokesperson ("Ravi") and one clean product still (phone showing the app). Save both to `flow-content/ingredients/`. Write Ravi's character-bible line.

**8.2 — Prove amnesia is real (cost: ~20 coins).** Text→Video, **Lite**, prompt "a friendly Indian delivery rider" — twice, no ingredient. Note the two different people. *This is the problem you're solving.*

**8.3 — Fix it with an ingredient (~20 coins).** Now **Ingredients→Video** on **Lite** with your Ravi portrait, same prompt twice. Same face both times. You just beat amnesia — feel the difference.

**8.4 — Three ingredients at once (~10 coins).** Combine Ravi + product + a style image in one Lite render (the §2 prompt). Confirm all three carry.

**8.5 — Storyboard-to-frame (~20 coins plus a still).** Make a board still from your Ravi portrait (Nano Banana Pro or 2) and run it through **Frames→Video** on Lite. Compare its controllability to a cold text→video of the same idea. This becomes your default path.

**8.6 — Extend a beat (~20 coins).** Render an 8-second Ravi clip on **Lite**, then **Extend** it once (only Lite extends). Watch continuity across the seam.

---

**Sources (re-verified 2026-10-01):** Flow Help: [models & features](https://support.google.com/flow/answer/16352836), [create videos](https://support.google.com/flow/answer/16353334), [edit & build scenes](https://support.google.com/flow/answer/16935718), [characters](https://support.google.com/flow/answer/16935308), [images](https://support.google.com/flow/answer/16729550) · [Veo — Gemini API](https://ai.google.dev/gemini-api/docs/veo) · [Whisk closure](https://workspaceupdates.googleblog.com/2026/03/whisk-is-moving-to-flow-on-april-30-2026.html). More in [[09-reference]] §9.

**Next:** [[06-phase-6-voice-lipsync-audio]] — giving your consistent character a consistent *voice*: dialogue, lip-sync, sound effects, and music, all conducted with words.
