# Phase 1 — The Big Picture: How a Shot Is Born, and What Every Coin Buys

> Level: Easy | Time: ~30 min | Outcome: you understand the whole pipeline, you've made your first talking clip on the *cheap* tier, and you can budget a promo in credits before you spend one.

---

## 1. The One Idea

You are not a camera operator. **You are a director.**

A camera operator points a lens and presses record. A director never touches the camera — they *describe what they want* and a crew makes it happen. Google Flow makes you the director and gives you a robot crew that will shoot literally anything you can describe. Your entire skill set is: **describe well, keep things consistent, and don't waste the crew's time.**

That's the mindset shift. Everything hard about Flow is hard because people keep trying to be the *camera* ("how do I get exactly this pixel?") when the job is to be the *director* ("here is a clear note; go"). Directors who write clear notes get great footage. Directors who mumble get garbage and burn the budget.

## 2. The Four Surfaces You'll Actually Touch

The stack in the [[00_README]] has a dozen tools, but on a normal day your hands are on **four browser tabs**. Know which tab does which job so you stop reaching for the wrong one:

| Tab                 | You go here to…                                                    | 5-year-old name        |
| ------------------- | ------------------------------------------------------------------ | ---------------------- |
| **Gemini**          | Think, write the script, and turn ideas into Veo prompts           | The "help me plan" desk |
| **Imagen / Whisk**  | Make still pictures — ad images, and reference photos for the crew | The drawing table       |
| **Flow**            | Turn those pictures and prompts into actual video with sound       | The film set           |
| **Vids / Drive**    | Glue clips together, add captions, and file the finished work      | The editing bench       |

The mistake beginners make is living **only** in the Flow tab — typing prompts straight into the film set and hoping. Pros spend most of their time at the **planning desk** and the **drawing table**, and arrive at the film set already knowing exactly what they want. Cheaper, faster, better. (Why it's cheaper is §4.)

## 3. The Life of One Shot

Here is how a single good 8-second clip is actually born. Memorise this loop — you'll run it hundreds of times.

```
①  Idea            "Show our delivery app being used at a chai stall"
        │
②  Prompt          Gemini turns it into a 7-part note (Phase 2)
        │
③  Draft  ⏣10      Render on Veo 3.1 LITE. Is the idea even right?
        │            └─ No?  Fix the note, draft again. Still cheap.
        │
④  Iterate ⏣20     Happy with the idea → render on FAST. Tune camera, timing, voice.
        │            └─ Not quite?  Nudge the note, iterate again.
        │
⑤  Lock   ⏣100     Only now, when it's *right*, render once on QUALITY.
        │
⑥  Extend / Stitch  Add seconds (Scene Extension) or join shots (Scenebuilder/Vids)
        │
⑦  File            Save to Drive with its prompt. (Future-you will thank you.)
```

⏣ = credits. Read steps ③–⑤ again: **you climb the price ladder only as your confidence climbs.** You never pay 100 coins to find out whether an idea works — you pay 10. This one habit is worth more than every prompt trick in this course combined.

> **Why "save the clip *with* its prompt" (step ⑦)?** Because in three weeks the client will say "make three more like that one." If you saved the prompt, that's a five-minute job. If you didn't, you're reverse-engineering your own footage. Flow TV exists precisely because prompts are that valuable — see [[09-reference]].

## 4. The Credit Economy (the part that pays your salary)

Let's make the Prime Directive concrete with a real job: **a 30-second Instagram promo for DZZLO**, which is roughly **four 8-second shots**.

**The amateur way — render everything at Quality:**

| Step                      | Renders | Tier    | Coins   |
| ------------------------- | ------- | ------- | ------- |
| Try shot 1 (3 attempts)   | 3       | Quality | 300     |
| Try shot 2 (4 attempts)   | 4       | Quality | 400     |
| Try shot 3 (2 attempts)   | 2       | Quality | 200     |
| Try shot 4 (3 attempts)   | 3       | Quality | 300     |
| **Total**                 | **12**  |         | **1,200** ❌ |

That's **over our entire monthly jar** — for *one* promo. The amateur is now locked out until next month.

**The pro way — draft cheap, commit expensive:**

| Step                              | Renders | Tier    | Coins  |
| --------------------------------- | ------- | ------- | ------ |
| Block all 4 shots, find the ideas | 8       | Lite    | 80     |
| Tighten the 4 keepers             | 6       | Fast    | 120    |
| Lock the 4 finals                 | 4       | Quality | 400    |
| **Total**                         | **18**  |         | **600** ✅ |

Same 4 finished shots, **more** iterations, **half** the jar. The pro made the promo *and* has 400 coins left for the next one. The only difference is *which tier they were on when they were still guessing.*

**Rules of thumb that fall out of this:**

- **Never render an unproven idea at Quality.** If you're not sure it'll work, you're drafting → Lite.
- **Batch your Lite drafts.** Explore 3–4 variations at once (30–40 coins) instead of one-at-a-time perfectionism.
- **A Quality render is a *commitment ceremony*, not an experiment.** If you find yourself rendering the same shot at Quality twice, your process broke upstream — go back to Fast.
- **Vertical (9:16) and horizontal (16:9) cost the same.** Frame for the platform from the start; don't render both "to be safe."

## 5. Four Ways to Start a Shot

The crew can begin from four different kinds of note. Picking the right starting point is half the battle — and three of the four are how you fight the "crew forgets everyone" problem.

| Start from…          | What you give                                   | Best for                                                      | 5-year-old version                          |
| -------------------- | ----------------------------------------------- | ------------------------------------------------------------- | ------------------------------------------- |
| **Text → Video**     | Just words                                      | Brand-new scenes, quick concepts, "what if"                   | "Draw me a dog." (You get *some* dog.)      |
| **Frames → Video**   | A first image (± a last image) + words          | Precise starts/ends; animating a still you already love       | "Start from *this* picture and move."       |
| **Image → Video**    | One image to animate + words                    | Bringing an Imagen ad-still or product photo to life          | "Make *this photo* move."                   |
| **Ingredients → Video** | Up to **3 reference images** + words         | **Keeping the same character / product / style** across clips | "Use *this exact actor* and *this logo*."   |

Text-to-video is where everyone starts and where consistency goes to die — every clip invents a new face. The moment your content needs the *same* spokesperson or the *same* product twice, you graduate to **Frames** and **Ingredients** (Phase 5). Most professional marketing work starts from an image, not from text, for exactly this reason: a picture pins down what words leave to chance.

## 6. Exercises

**6.1 — Make your first talking clip (cost: ~10 coins).** In Flow, Text→Video, **Veo 3.1 Lite**, paste exactly this:

```
Medium shot of a friendly young Indian shopkeeper standing at a small
roadside chai stall, holding a phone. He looks at the camera and says:
"Orders sorted, chai in hand." Warm morning light, gentle street sounds,
a kettle steaming in the background. Handheld, natural, documentary style.
```

Watch what you get for 10 coins: a person, a voice, moving lips, ambient sound, and a camera feel — all from four sentences. *This* is the crew.

**6.2 — Prove the Prime Directive costs nothing to obey.** Render 6.1 twice more on **Lite**, changing only one word each time (`chai` → `coffee`, `morning` → `evening`). Three explorations for ~30 coins. Notice you now *know* which one to commit — before spending a single Quality coin.

**6.3 — Budget a real job.** Open a Sheet in Drive. Plan a **DZZLO 30-second promo** as 4 shots. Write, for each shot, the tier you'd draft on and the tier you'd lock on, and total the coins. Aim to come in under **600**. This sheet is the skeleton you'll fill with real prompts by the end of Phase 8.

**6.4 — Start the archive habit.** Make a Drive folder `flow-content/`. Every clip you keep from now on gets saved there *with its prompt in the filename or a sidecar note*. Miss this and you'll re-earn the lesson the expensive way.

---

**Next:** [[02-phase-2-prompting-basics]] — the 7 parts every good note has, and the word budget that keeps the crew from getting confused.
