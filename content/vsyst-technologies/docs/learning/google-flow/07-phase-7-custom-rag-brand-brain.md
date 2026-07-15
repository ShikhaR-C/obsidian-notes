# Phase 7 — Custom RAG: Building Your Brand Brain

> Level: Advanced | Time: ~2 hr | Outcome: a reusable "DZZLO Content Director" — a Gemini Gem that reads a NotebookLM knowledge base of *your* brand and turns any one-line brief into on-brand scripts, prompts, and character bibles automatically.

---

## 1. The One Idea

Everything so far, you did **by hand** — pasting the context header, the character bible, the style sentence into every chat. That works, but it drifts and it's slow. The payoff phase is to **give the AI a memory box of your brand and never retype any of it again.**

That memory box is **RAG**. In 5-year-old terms:

> A normal AI answers from what it remembers of the whole internet — so it gives you *generic* answers and sometimes makes stuff up. A **RAG** AI, before it answers, **runs to a filing cabinet of *your* documents, reads the right page, and answers from that.** It's the difference between a stranger guessing about DZZLO and an employee who's read the whole handbook.

RAG stands for **R**etrieval (go get the right page) **A**ugmented (add it to) **G**eneration (making the answer). You don't need to build any of the plumbing — Google already made both pieces:

| Piece                 | 5-year-old            | The real tool                              |
| --------------------- | --------------------- | ------------------------------------------ |
| The **filing cabinet**| The memory box        | **NotebookLM** — you fill it with your docs |
| The **employee**      | Assistant who read it | **A Gemini Gem** — grounded on that notebook |

Build these two once and every future brief comes out sounding like DZZLO, using DZZLO's real facts, with DZZLO's spokesperson and voice — with zero manual pasting.

## 2. Why This Is the Whole Point

Without a brand brain, Gemini writes *plausible* prompts. With one, it writes *correct, on-brand* ones. The difference:

| Without brand brain                          | With brand brain (grounded)                                   |
| -------------------------------------------- | ------------------------------------------------------------- |
| "A logistics app" (generic)                  | "DZZLO — one-screen fleet OMS for small Indian transporters"  |
| Invents a spokesperson every time            | Always "Ravi," pulled from the character bible                |
| Random tone                                  | Your exact voice: trustworthy, warm, plain-spoken             |
| Forgets your teal-and-white palette          | Bakes brand colours into every style sentence                 |
| You re-teach it your product every chat      | It already knows — because it *read the notebook*             |

This is also what makes the whole pipeline *scale*: one brief in, a week of consistent content out, because the consistency lives in the brain instead of in your memory.

## 3. Build Step 1 — Fill the Memory Box (NotebookLM)

Create a NotebookLM notebook called **"DZZLO Brand Brain."** Then feed it everything that defines the brand. The richer the cabinet, the better the employee:

| Put in the notebook            | So the AI can…                                          |
| ------------------------------ | ------------------------------------------------------- |
| **Brand guidelines**           | Match tone, colours, do's & don'ts                      |
| **Product docs / feature list**| State true facts about DZZLO, not invented ones         |
| **Tone-of-voice guide**        | Write in your voice, not generic-AI voice               |
| **Character bibles**           | Reuse Ravi (and any others) identically                 |
| **Ingredient index**           | Know which reference images exist and when to use them  |
| **Winning prompts**            | Reuse what already worked (this is gold — see §6)       |
| **Do / Don't list**            | Avoid off-brand claims, banned words, wrong framing     |
| **Audience / persona notes**   | Pitch to real customers, in their language              |
| **Past scripts & taglines**    | Stay consistent with what's already out there           |

> Sources can be Google Docs, PDFs, pasted text, even links. Keep it **curated** — a tidy cabinet beats a hoard. Put the messy raw material in, then a one-page "start here" summary doc at the top; NotebookLM reads structure well.

## 4. Build Step 2 — The Gemini Gem (the employee)

A **Gem** is a custom, reusable Gemini persona. You build it with the **PACT** framework — **P**ersona, **A**ssignment, **C**ontext, **T**emplate — and, crucially, you **connect the NotebookLM notebook as a grounding source** so it reasons on top of your brand brain (Google wired NotebookLM notebooks in as a Gemini source in 2026).

Paste this into a new Gem's instructions and adapt:

```
── PERSONA ──
You are the DZZLO Content Director: an expert short-form video producer who
knows Veo 3.1 cold and writes only in DZZLO's brand voice — trustworthy,
warm, plain-spoken, never hypey.

── ASSIGNMENT ──
Turn any one-line brief into a complete, on-brand production plan:
  1. A context header (audience, platform, goal, message, brand feel, duration)
  2. A hook→value→proof→CTA shot list sized to the platform's shot budget
  3. A finished Veo 3.1 prompt per shot — all 7 ingredients, 100–150 words,
     present tense, "no subtitles" on any shot with dialogue
  4. The exact character-bible line and voice description for any speaker
  5. Which saved ingredient images each shot should use

── CONTEXT ──
Ground every answer in the "DZZLO Brand Brain" notebook: use its real product
facts, tone-of-voice, character bibles, palette, and winning prompts. Never
invent a product feature that isn't in the notebook. Keep the brand-feel
sentence identical across all shots in a plan.

── TEMPLATE ──
Output in this order, with headings: CONTEXT · SHOT LIST (table) ·
PROMPTS (numbered) · CAST & VOICE · INGREDIENTS TO USE · EST. CREDIT BUDGET.
```

Now the Gem is a permanent, on-brand production assistant. You type *"15-second Reel promoting our new live-tracking feature"* and it hands back the entire plan — grounded in real DZZLO facts, cast with Ravi, in your voice, budgeted in credits. Copy the prompts straight into Flow and draft on Lite.

## 5. The Grounded Pipeline

Phase 7 upgrades the whole [[00_README]] diagram: the brand brain now sits *upstream* of everything and feeds it consistency for free.

```
   one-line brief
        │
        ▼
  DZZLO Content Director (Gem)
        │  ◄── grounded on ── NotebookLM "DZZLO Brand Brain"
        ▼
  full plan: script · shot list · 7-ingredient prompts · cast · voice · budget
        │
        ├──► Imagen/Whisk  (make/pull the ingredients it named)
        └──► Flow / Veo 3.1 (draft Lite → Fast → lock Quality)
                    │
                    ▼
              Vids → Drive → publish
                    │
                    ▼
     winning prompt ──► back into the Brand Brain  (§6)
```

## 6. Close the Loop — The Brain Gets Smarter

The step everyone skips, and the one that compounds: **every clip that performs well, put its prompt back into the notebook** under "Winning prompts," tagged with what it was for. Next month the Gem retrieves *your own proven winners* as examples and writes even better plans. Your brand brain isn't static documentation — it's a flywheel that learns what works for DZZLO specifically. Six months in, it's a genuine competitive moat no prompt-copying competitor has.

> **The honest caveat.** Grounding **reduces** hallucination; it doesn't abolish it. The Gem can still occasionally state a feature slightly wrong or drift off-voice. So the human stays in the loop: **skim every plan for factual and brand accuracy before you spend coins.** RAG makes the AI a well-briefed junior, not an unsupervised one. Also: NotebookLM/Gem availability and the exact "add notebook as source" flow are evolving through 2026 — if the direct connection isn't in your account yet, the fallback is to paste a one-page brand summary into the Gem's CONTEXT block by hand. Less elegant, nearly as effective.

## 7. Exercises

**7.1 — Seed the cabinet (0 coins).** Create the "DZZLO Brand Brain" notebook. Add at least: the product feature list, a one-page tone-of-voice note, Ravi's character bible, and your best 3 prompts from earlier phases.

**7.2 — Write the start-here doc (0 coins).** Add a single summary doc at the top: what DZZLO is, who it's for, the voice in five adjectives, the palette, the cast. This is the page the AI reads first.

**7.3 — Build the Gem (0 coins).** Create the Content Director Gem with the §4 PACT instructions. Connect the notebook as a source (or paste the summary into CONTEXT if connection isn't available).

**7.4 — One brief, full plan (0 coins).** Give it *"15-second Reel promoting live fleet tracking."* Read the output critically: right facts? right voice? Ravi cast? budget sane? Note every correction — those corrections are missing notebook content; add them.

**7.5 — Draft the machine's plan (~40 coins).** Take the Gem's prompts into Flow, draft the shots on Lite. Judge how much closer to "done" the first draft is than a cold prompt would've been. That gap is your brand brain earning its keep.

**7.6 — Close the loop.** Pick your best result and file its prompt back into the notebook under "Winning prompts." You've started the flywheel.

---

**Next:** [[08-phase-8-pro-workflow-and-playbooks]] — the assembly line, plus copy-paste playbooks for marketing films, ads, promos, tutorials, and images.
