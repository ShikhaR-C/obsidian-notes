# Phase 3 — Context & Script Planning: Never Face a Blank Prompt Box

> Level: Easy → Intermediate | Time: ~1 hr | Outcome: you can turn a one-line brief into a full shot list with a finished Veo prompt for every shot — all in Gemini, before you spend a single Flow coin. | Status: written & web-verified 2026-07-15; **tool facts re-verified and corrected 2026-10-01**.

---

## 1. The One Idea

**Words are free. Video is not.** So you do all your thinking, arguing, and rewriting in *words* — in Gemini — and you only walk over to the Flow film set once the entire plan is locked.

A one-line idea ("promo for DZZLO") is not a plan. A **plan** is: who's it for, where will it play, what's the one message, and what are the exact shots that deliver it. Gemini is your **writers' room** — it turns the idea into that plan in about five minutes. Skipping this step is why beginners sit staring at the Flow prompt box, improvising 100-coin renders. Planners never improvise on the film set.

Two jobs live here, and they happen in order:

- **Context planning** — telling Gemini *the situation* so its output is actually usable.
- **Script planning** — turning that context into a message, a script, a shot list, and finally a Veo prompt per shot.

## 2. Context Planning: Load the Situation First

If you ask Gemini "write me a video ad," you get generic mush, because *it doesn't know your situation.* Context planning is filling in the situation **once**, at the top, so everything downstream is on-target. Six blanks:

| Context blank    | Why the crew needs it                                       | DZZLO example                                        |
| ---------------- | ----------------------------------------------------------- | ---------------------------------------------------- |
| **Audience**     | Changes tone, pace, language, references                    | Small-fleet transport owners, 30–50, Tier-2 India   |
| **Platform**     | Sets aspect ratio, length, and hook speed                   | Instagram Reels → 9:16, ≤30 s by choice (Reels allow far longer), hook in 2 s |
| **Goal / CTA**   | The one action the viewer should take                       | "Book a demo" — drive sign-ups                       |
| **Key message**  | The single thing they must remember                         | "DZZLO puts your whole fleet in one screen"          |
| **Brand feel**   | Tone + look so it matches everything else you make          | Trustworthy, modern, warm; not flashy or corporate   |
| **Duration**     | Decides how many shots (clips of up to 8 s) you're budgeting | 30 s → **4 shots**                                   |

Paste those six lines into Gemini as a header and *keep them* at the top of the chat. Every prompt it writes after that inherits the situation. (In Phase 7 you'll bake this permanently into a **Gemini Gem** so you never retype it — but learn it manually first.)

> **The 8-second reality drives the whole plan.** Because a Veo clip runs at most 8 seconds (4, 6 or 8; Ingredients clips 8), your duration divides straight into a **shot count**: 15 s ≈ 2 shots, 30 s ≈ 4, 60 s ≈ 7–8 — separate shots, cut together; Extend is for the rare long take ([[05-phase-5-character-consistency|Phase 5]] §6). You are never writing "a video." You are always writing *a list of shots.* Internalise this and scripting gets ten times easier.

## 3. Script Planning: Idea → Shots → Prompts

Marketing video has a shape that's been working for a century. Don't reinvent it — fill it in. The **hook-first** structure:

```
[0–2 s]  HOOK      Stop the scroll. A problem, a question, a striking image.
[2–6 s]  VALUE     The one message. Show the product solving the problem.
[6–10 s] PROOF     A benefit, a number, a happy user — make it believable.
[final]  CTA       Tell them exactly what to do next.
```

Map that onto your shot count and you have a **shot list**. For the 30-second DZZLO Reel (4 shots):

| Shot | Beat  | What we see                                                        | ~Sec |
| ---- | ----- | ----------------------------------------------------------------- | ---- |
| 1    | Hook  | Stressed fleet owner juggling three phones and a paper ledger     | 0–7  |
| 2    | Value | Same owner, calm now, one clean DZZLO dashboard on his laptop     | 7–15 |
| 3    | Proof | Close-up of the screen: live trucks on a map, "12 orders today"   | 15–23 |
| 4    | CTA   | Owner to camera, confident: "Run your fleet from one screen."     | 23–30 |

*Now* you have four things to prompt — each a single, clear 8-second beat. The scary blank box is gone.

## 4. The Prompt-Expansion Trick (one idea → thirty prompts)

This is the highest-leverage move in the entire course. You do **not** hand-write the 7-ingredient prompt for every shot. You write a *rough* one-line note and make Gemini expand it, using the context header it already has.

Give Gemini this instruction once:

```
You are my Veo 3.1 prompt writer. Using the CONTEXT above, expand each rough
shot note below into a finished Veo prompt. Each prompt must include all seven
ingredients — subject, action, scene, camera, style, lighting/mood, audio —
in 3–6 sentences (100–150 words). Present tense. Add "no subtitles" to any
shot with dialogue. Keep the brand feel identical across all shots. Output
one prompt per shot, numbered.

Rough shots:
1. Hook — stressed fleet owner, too many phones
2. Value — same owner, calm, using DZZLO on a laptop
3. Proof — close on the dashboard, live map, order count
4. CTA — owner to camera, confident, says the tagline
```

(100–150 words and "no subtitles" are course habits, not Google's rules: Google's only stated limit is 1,024 tokens, and its dialogue rule is quotation marks around speech — [[02-phase-2-prompting-basics|Phase 2]] §3–4.)

Gemini hands back four polished, mutually-consistent prompts. You read them, tweak a word or two, and you're ready to draft on Lite. **One brief → a whole shot list of finished prompts, in minutes.** Scale this and one person produces a week of content in an afternoon.

> **Why let Gemini write them instead of you?** Three reasons: (1) it never forgets an ingredient, (2) it keeps the *brand feel* line identical across shots — which is half of consistency — and (3) it's the seam where your **brand brain** plugs in (Phase 7). A human writing four prompts by hand will drift; Gemini pinning the same style sentence across all four won't.

## 5. Storyboard Before You Shoot (stills are ~free-ish, and catch mistakes)

Before committing *any* video coins, make a **still** for each shot with **Nano Banana** in Flow (stills are cheap — Nano Banana 2 Lite is free; check the cost Flow shows for the other image models). A storyboard frame does two jobs:

1. **Catches composition mistakes in a picture, not a 100-coin render.** Wrong framing? Fix the prompt now.
2. **Becomes the shot's starting frame.** Feed that still into Flow as **Frames→Video** (the still is its start frame) — now the video *starts* from an image you already approved, which is far more controllable than text→video and is the backbone of consistency (Phase 5). It is also the only way to lock a shot on Veo 3.1 Quality with a pinned face, because Quality takes no Ingredients.

So the real order of operations — the course's main route from here on — is:

```
brief → context → shot list → per-shot prompt (Gemini)
                                     │
                                     ▼
                          storyboard still  (Nano Banana)   ← approve composition here
                                     │
                                     ▼
                          Flow: Frames→Video, Lite draft     ← now you're spending coins on a sure thing
```

You didn't spend a video coin until the plan *and* the picture were both approved. That's the pro workflow in one diagram — the Director's track makes every shot this way ([[14-previs-storyboard-floorplan-animatic]] §4).

## 6. Exercises

**6.1 — Load the context (cost: 0 coins).** Open Gemini. Write the six-line context header for a **real** DZZLO or vsyst asset you actually need. Save it in `flow-content/briefs.md`.

**6.2 — Build a shot list (0 coins).** Using the hook→value→proof→CTA shape, turn that brief into a numbered shot list with a one-line note per shot. Keep it to your platform's shot budget (15 s→2, 30 s→4).

**6.3 — Expand with Gemini (0 coins).** Paste the §4 expansion instruction plus your shot list. Get back finished 7-ingredient prompts. Read them critically — did it keep the brand-feel line identical across every shot? If not, tell it to, and regenerate.

**6.4 — Storyboard it (Nano Banana 2 Lite stills, 0 coins).** Generate one still per shot in Flow. Lay them in a row in a Doc. Does the story read as a strip of four pictures *before* any motion? If not, your problem is in the plan, and you just caught it for the price of four stills instead of four Quality renders.

**6.5 — Only now, draft one (cost: ~10 coins per output).** Take shot 1, feed its approved still into Flow as Frames→Video (start frame) with its prompt, render on **Lite**. Notice how much more it looks like what you *intended* than a cold text→video would have. That gap is what planning bought you.

---

**Sources (re-verified 2026-10-01):** Flow Help: [models & features](https://support.google.com/flow/answer/16352836), [credits](https://support.google.com/flow/answer/16526234) · [Veo — Gemini API](https://ai.google.dev/gemini-api/docs/veo) · [Veo 3.1 prompting guide — Google Cloud](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1) · [Reels ad specs — Meta](https://www.facebook.com/business/ads-guide/update/video/instagram-reels). More in [[09-reference]] §9.

**Next:** [[04-phase-4-camera-control]] — the film words that tell the robot camera exactly where to stand and how to move, so your shots look directed instead of accidental.
