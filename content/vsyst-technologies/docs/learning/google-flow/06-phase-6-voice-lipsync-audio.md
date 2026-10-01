# Phase 6 — Voice, Lip-Sync & Audio: Conducting the Sound Department

> Level: Intermediate | Time: ~1 hr | Outcome: you can make a character speak a line with matching lip movement, shape *how* the voice sounds, and layer sound effects, ambience, and music — all from the prompt. | Status: written & web-verified 2026-07-15; **tool facts re-verified and corrected 2026-10-01**.

---

## 1. The One Idea

Veo 3.1 has a **built-in sound department**, and you conduct it with **words**. This is the feature that leaves every silent-video tool behind: Veo 3.1 "excels at generating realistic, synchronized sound, from multi-person conversations to precisely timed sound effects," in Google's words.

Sound has three jobs, and you write each one into the prompt:

| Job                     | The question           | 5-year-old                          |
| ----------------------- | ---------------------- | ----------------------------------- |
| **Dialogue**            | *What* is said?        | "What words come out of their mouth?" |
| **Voice modulation**    | *How* does it sound?   | "Is it a deep voice or a squeaky one?" |
| **Sound design**        | What *else* do we hear?| "What other sounds are around them?"  |

Get all three and an 8-second clip stops being footage and becomes a *scene.*

## 2. Dialogue: The Quotes-and-Colon Rule

Two formatting rules do 90% of the work, and skipping them is a common reason people get subtitles splattered across their clip or a voice reading the wrong words.

**Rule 1 — put the exact words in quotes.** Veo speaks what's inside the quotation marks — Google's own rule for speech.

**Rule 2 — use the colon, then quotes** (`Speaker: "line"`), as Google's examples do. This tells Veo *"this is spoken dialogue,"* which improves delivery **and**, in practice, cuts down on burned-in captions. Pair it with `no subtitles` — a course habit, not a Google rule.

```
The man says: "Welcome to DZZLO." No subtitles.
```

not

```
The man welcomes everyone to DZZLO and there is text on screen
```

The second version invites narration weirdness and a caption bar. The first just… talks.

**Rule 3 — one breath.** A Veo clip is at most 8 seconds. Write a line a real person could say in one calm breath — roughly **10–20 words, max.** Cram in a paragraph and Veo either rushes it into gibberish or cuts it off.

> **Word-count → seconds math:** natural speech is ~2–3 words/second. So ~8 seconds ≈ **16–20 words** of comfortable dialogue, less if you also need a beat of silence. Write to that budget. Longer script? That's *two shots*, not one — plan it in [[03-phase-3-context-and-script-planning]].

> **Hinglish lines.** Google says languages other than English "have not been evaluated" on Veo or Omni — they may work, but results vary. Hear every Hindi line on a Lite draft before you lock it ([[16-directing-performance-and-dialogue-scenes]] §6).

## 3. Lip-Sync: It's Automatic (if you help it)

You don't ask for lip-sync — **it just happens** when you provide quoted dialogue; the mouth matches the words — usually, so check every take. Your job is to make it *easy* for the crew:

| For clean lip-sync…                         | Why                                             |
| ------------------------------------------- | ----------------------------------------------- |
| **One clear speaker** per clip              | Two people talking at once confuses the sync    |
| **Speaker facing the camera**, front-ish    | Mouth is visible → sync is accurate             |
| **Name who's speaking** if others are present| "The woman on the left says:" removes ambiguity |
| **Medium or closer** shot                   | The face is big enough to animate the mouth well |
| Pair with an **ingredient** or **start still** (Phase 5) | The *same* face speaks across every clip |

The combination that makes a reusable brand spokesperson: **a pinned face (an ingredient or a start still) + quoted dialogue (lip-sync) + `no subtitles`.** That's a talking-head presenter you can generate on demand, forever.

## 4. Voice Modulation: Describe the Voice You Want

Veo **generates** a voice from your *description* — you sculpt it with adjectives. Think of it as casting plus a direction note. The dials:

| Dial          | Words that work                                                        |
| ------------- | --------------------------------------------------------------------- |
| **Age**       | young / middle-aged / elderly                                          |
| **Gender**    | male / female                                                         |
| **Accent**    | Indian English / British / American / neutral                         |
| **Pitch/tone**| deep, warm, gravelly / bright, light, cheerful                        |
| **Pace**      | slow and reassuring / brisk and energetic                             |
| **Emotion**   | calm, confident / excited / gentle / authoritative                    |

Stack them into a **speaker description**, then give the line:

```
A warm, confident middle-aged man with a friendly Indian English accent
says, slowly and reassuringly: "Your fleet, finally in one place."
No subtitles.
```

> **The honest limit on voice consistency.** Veo *generates* a fresh voice from your words in every clip — and Flow documents no way to clone a voice from an uploaded sample. So describing the voice identically across clips gets you *close*, but the timbre can wander clip-to-clip. When a **locked** brand voice matters: (1) an **Omni Flash voice reference** (`@Voice`) — Flow's second model, not Veo, and only together with Ingredients; (2) a Flow **Character** (`@Name`), one or two images bundled with a voice — check live which models honour it; (3) for a narrator never seen on screen, one voice-over laid under the picture — **Vids AI voice-over** is unlimited on AI Pro, Hindi included; (4) for two short lines, one 8-second take of the character saying both (together inside §2's 20-word budget), cut apart in the edit — one generation, one voice. For most social content, describing the voice consistently is good enough; [[16-directing-performance-and-dialogue-scenes]] §11 tests when it isn't. A realistic synthetic voice can count as AI content to disclose ([[20-colour-finishing-and-delivery]] §12).

## 5. Sound Design: Everything Else You Hear

Silence reads as "cheap AI clip." Fill the world with sound in **separate sentences** — Veo handles audio best when it's described distinctly from the action. Three layers:

| Layer            | What it is                                        | Prompt example                                            |
| ---------------- | ------------------------------------------------- | --------------------------------------------------------- |
| **Sound effects**| Distinct, specific sounds tied to the action      | "A soft chime as the notification appears."               |
| **Ambience**     | The background bed that makes a place feel real    | "Gentle background hum of a busy office."                 |
| **Music**        | Mood/genre bed under it all                       | "Upbeat, optimistic corporate background music."          |

Full sound-designed prompt:

```
Medium shot, slow push-in, of Ravi at his desk looking at his laptop and
smiling. He says: "Twelve deliveries, all on track." A soft chime as an
order confirms. Gentle office ambience in the background. Light, upbeat
corporate music. No subtitles.
```

That's dialogue + SFX + ambience + music in four short sentences — a complete soundstage.

## 6. When Veo's Music Isn't Enough: Lyria / Google Flow Music

Veo's built-in music is great for a bed, but it's *generic* and you can't reuse the exact track. For a **signature sound** — a jingle, a consistent brand music bed across every video — generate a dedicated track in **Google Flow Music** (Lyria 3.5, included with AI Pro on its own credits) or in the Gemini app or Vids — describe genre, mood, tempo, instruments — then lay it under your clips in **Vids**. One custom bed, reused across a whole campaign, is a cheap way to make everything feel like one brand.

**Read the terms** before it goes into an ad (Google lists "commercial use rights" for Flow Music on AI Pro); rights aren't disclosure — YouTube asks you to label AI music ([[20-colour-finishing-and-delivery]] §12). Cutting a cue to picture: [[19-sound-edit-design-and-mix]] §9.

```
Layering plan:
  Veo clip audio  → keep dialogue + SFX + ambience
  Veo music       → turn down or off
  Flow Music bed  → your reusable brand track, added in Vids
```

## 7. The Complete Audio Recipe

The order to think about sound, every clip:

```
1. Is anyone speaking?  → quoted line, colon format, ≤20 words, "no subtitles"
2. How should the voice sound?  → age + accent + tone + emotion, in front of the line
3. What one SFX sells the action?  → one distinct sound
4. What's the ambience?  → one background-bed sentence
5. Music?  → mood in-prompt, OR a Flow Music bed added later in Vids
```

## 8. Exercises

**8.1 — First words (cost: ~20 coins).** Render Ravi (ingredient from Phase 5, Lite) saying a one-breath line with the colon format and `no subtitles` — once in English, once in Hinglish. Confirm: right words, lips match, no caption bar.

**8.2 — Same words, four voices (~40 coins).** Keep the line identical; change only the *voice description* — young/energetic, elderly/gentle, deep/authoritative, bright/cheerful. Hear how much casting lives in adjectives.

**8.3 — Break the one-breath rule on purpose.** Give Veo a 40-word paragraph. Watch it rush or cut off. Now you'll respect the ~20-word budget forever.

**8.4 — Build a soundstage.** Take a silent clip you already like and re-render it with the full §5 recipe (dialogue + SFX + ambience + music). Compare. The sound-designed version feels twice as expensive.

**8.5 — Test locked voice vs. described voice (~20 coins).** Render the same line in two Lite clips with an *identical* voice description. Listen for timbre drift. Decide, for a real DZZLO asset, whether "close enough" works or you need one of §4's locked routes ([[16-directing-performance-and-dialogue-scenes]] §11.3 scores it).

**8.6 — Make a brand bed (0 Flow coins).** Generate a 30-second upbeat corporate track in **Google Flow Music**. Save it, with the terms you read, to `flow-content/audio/`. This is your reusable music bed for the Phase 8 playbooks.

---

**Sources (re-verified 2026-10-01):** [Veo 3.1 prompting guide — Google Cloud](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1) · Gemini API: [Veo](https://ai.google.dev/gemini-api/docs/veo), [Omni](https://ai.google.dev/gemini-api/docs/omni) · Flow Help: [create videos](https://support.google.com/flow/answer/16353334), [characters](https://support.google.com/flow/answer/16935308) · [Google AI Pro benefits](https://support.google.com/googleone/answer/14534406) · Vids: [AI voice-over](https://support.google.com/docs/answer/15070345), [limits](https://support.google.com/docs/answer/15609411). More in [[09-reference]] §9.

**Next:** [[07-phase-7-custom-rag-brand-brain]] — the payoff: build a "brand brain" in **Gemini Notebook** (formerly NotebookLM) and a Gemini Gem that reads it, so every script, prompt, and voice comes out on-brand automatically.
