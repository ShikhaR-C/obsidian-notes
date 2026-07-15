# Phase 2 — Prompting Basics: The 7-Part Note

> Level: Easy | Time: ~45 min | Outcome: you can write a Veo prompt that has every part it needs, in the right length, and you know why vague and over-stuffed prompts both fail.

---

## 1. The One Idea

A good prompt is a **director's note**, and every director's note answers the same seven questions: **who, doing what, where, shot how, in what style, in what light, and what do we hear.**

Miss one and the robot crew *guesses* — and a guessing crew is why your spokesperson suddenly has the wrong hair, the camera sits still when you wanted a push-in, or the clip comes out silent. You are not writing poetry. You are filling in a form the crew already expects. Learn the seven blanks and you never hand in an incomplete note again.

## 2. The Seven Ingredients

Here they are, each in 5-year-old terms and in one real example line:

| # | Ingredient          | The question it answers      | 5-year-old                         | Example fragment                                          |
| - | ------------------- | ---------------------------- | ---------------------------------- | --------------------------------------------------------- |
| 1 | **Subject**         | Who or what is in the shot?  | "Who's in the picture?"            | *a friendly young Indian delivery rider*                  |
| 2 | **Action**          | What are they doing?         | "What are they doing?"             | *checks his phone and smiles, then hops on his scooter*   |
| 3 | **Scene / Context** | Where are we?                | "Where are they?"                  | *on a busy Mumbai street at golden hour*                  |
| 4 | **Camera**          | Where's the camera & how does it move? | "Where do our eyes stand?" | *low-angle tracking shot following him from the side*     |
| 5 | **Style**           | What does it look like?      | "Cartoon or real?"                 | *cinematic, warm, shot on 35mm film*                      |
| 6 | **Lighting / Mood** | What's the light & feeling?  | "Is it bright and happy?"          | *soft golden-hour backlight, hopeful mood*                |
| 7 | **Audio**           | What do we hear?             | "What sounds do we hear?"          | *upbeat street ambience; he says: "Fastest route, let's go."* |

Stack those seven and you get a note the crew can shoot without guessing:

```
Low-angle tracking shot following a friendly young Indian delivery rider from
the side as he checks his phone, smiles, and hops on his scooter on a busy
Mumbai street at golden hour. Cinematic and warm, shot on 35mm film, soft
golden-hour backlight, hopeful mood. Upbeat street ambience; he says:
"Fastest route, let's go."
```

That's four sentences, ~55 words, all seven ingredients. It will render a usable clip on the *first* Lite draft — which is the whole point.

> **You don't always need all seven.** A product beauty shot has no dialogue; an abstract logo animation has no "subject" in the human sense. But you should **decide** to drop one, not *forget* it. Run the list in your head every time, like a pilot's checklist.

## 3. The Word Budget: 3–6 Sentences, 100–150 Words

More words is **not** more control. Past about 150 words the crew starts dropping details on the floor — and worse, it starts *contradicting itself* because you've told it fifteen things and some of them fight.

| Prompt length         | What happens                                                              |
| --------------------- | ------------------------------------------------------------------------ |
| **< 15 words**        | Vague. The crew invents 90% of it. Fine for happy accidents, bad for briefs. |
| **~100–150 words** ✅  | The sweet spot. Enough to pin the shot down, short enough to stay coherent. |
| **> 200 words**       | Detail salad. The crew ignores half, and the half it keeps may clash.    |

The fix for "it ignored my detail" is almost never *more words*. It's **better-chosen** words, or **splitting the idea into two shots.** If you're cramming five actions into eight seconds, the problem isn't the prompt — it's that you're asking for a scene when the crew only shoots shots (see [[03-phase-3-context-and-script-planning]]).

**The 8-second rule of thumb:** one clip = **one subject, one main action, one camera move.** "He walks in, sits, opens the app, frowns, then smiles" is five shots pretending to be one. Pick the single beat that matters.

## 4. Say What You *Want*, Not What You Don't

ComfyUI people reach for a "negative prompt" here. Veo mostly doesn't work that way — **you describe the world you want to see**, and the unwanted thing simply isn't in it. Want no clutter? Describe a *clean* desk. Want no crowd? Describe a *quiet* street.

There is one useful exception worth memorising, because Veo's native audio loves to burn subtitles into the picture:

> To stop on-screen captions appearing, add **`no subtitles`** (and/or `no text, no captions`) to the prompt, **and** format dialogue with the colon trick from [[06-phase-6-voice-lipsync-audio]]. This one is real and you'll use it constantly.

Beyond that, resist the urge to list everything you hate. A pile of "no X, no Y, no Z" just teaches the crew to *think about* X, Y, and Z. Positive, concrete, present-tense description wins.

## 5. The Fill-in Template

Tape this to your monitor. It's the seven ingredients as a blank you can complete in 60 seconds:

```
[CAMERA: shot type + movement] of [SUBJECT: who, specific look] who
[ACTION: one main thing, present tense] in/at [SCENE: where + time of day].
[STYLE: cinematic / cartoon / VHS / product-render] with [LIGHTING + MOOD].
[AUDIO: ambience + SFX]; [SPEAKER] says: "[one short line]".
```

Worked example for a **tutorial** clip:

```
Screen-facing medium shot of a calm female product specialist in a bright
modern office who points to the left as if to on-screen UI, in a clean
minimal setting at midday. Crisp, professional corporate style with soft
even lighting and a confident, friendly mood. Quiet room tone; she says:
"Tap 'New Order' to get started." No subtitles.
```

Worked example for a **product image-in-motion** ad (no dialogue):

```
Slow 180-degree orbit around a sleek smartphone floating above a matte
navy surface, screen showing the DZZLO dashboard, in a dark premium studio.
High-end product-render style, dramatic rim lighting with a single soft
key light, sophisticated and aspirational mood. Deep ambient hum and a
soft whoosh as the camera arcs.
```

Notice: the ad drops ingredient #7's dialogue but keeps its *sound design*. That's a deliberate drop, not a forgotten one.

## 6. The Four Ways Beginners Waste Coins Here

Every one of these is a note problem, and every one is fixable before you spend a Quality coin:

1. **The mumble.** "A nice ad for our app." → The crew invents everything. **Fix:** run the seven-ingredient checklist.
2. **The novel.** 300 words, twelve adjectives per noun. → Detail salad. **Fix:** cut to 100–150 words; keep the concrete nouns, drop the mood-adjective pile-up.
3. **The five-in-one.** Five actions crammed into one 8-second clip. → The crew rushes or ignores four of them. **Fix:** split into shots; plan them in Phase 3.
4. **The contradiction.** "Bright cheerful morning" + "moody dark shadows." → The crew picks one at random. **Fix:** read your note back and delete the fights.

## 7. Exercises

**7.1 — Fill the blank three times (cost: ~30 coins).** Using the §5 template, write three prompts for a DZZLO promo: one spokesperson shot, one product-in-motion shot, one lifestyle shot. Render each once on **Lite**. Grade them: which ingredient was weakest in each? Rewrite that one line.

**7.2 — Prove length isn't power.** Take your best prompt from 7.1. Make a **bloated** 250-word version and a **starved** 12-word version. Render all three on Lite (fixed idea). See for yourself: the 100-word one wins. Keep the three clips side by side — this lesson only sticks once you've *watched* it fail.

**7.3 — Kill the subtitles.** Render a talking-spokesperson prompt **without** `no subtitles`, then **with** it. Confirm the caption disappears. You'll want this reflex for every dialogue shot.

**7.4 — Build your template file.** Save the §5 template into `flow-content/templates.md` in Drive, with your three best 7.1 prompts underneath as starting points. This file grows into your prompt library ([[09-reference]]).

---

**Next:** [[03-phase-3-context-and-script-planning]] — how to use Gemini to turn one idea into a whole shot list, so you're never staring at a blank prompt box again.
