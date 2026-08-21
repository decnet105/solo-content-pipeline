# 04 · How This Was Built

Here's the honest truth behind this repo: **I'm not a professional programmer.** I didn't write these scripts. I couldn't have written `make_short.py` from a blank file if you'd paid me. I built this whole pipeline by describing what I wanted to an AI coding agent, running what it made, telling it what was wrong, and repeating until it worked.

If that sounds too good to be true, it isn't — but it also isn't magic. There's a method, and the method is learnable. This page is that method, so you can do the same thing.

The one idea to hold onto: **the leverage is clear communication, taste, and iteration — not coding skill.** You already have opinions about what a good video looks like and what a human-sounding sentence reads like. That judgment is the scarce ingredient. The agent supplies the coding.

---

## The loop, in six moves

### 1. Describe the outcome in plain language

I never started with "what functions do I need." I started with what I wanted to _end up holding_: "I want to feed in a JSON file that lists a few shots — each with an image prompt, some narration, and subtitles — and get back a finished vertical video with music. Write me a script that does that."

Describe the **result and the shape of the inputs**, not the implementation. You're the client with a clear brief; the agent is the contractor. You don't tell a contractor which hammer to swing.

### 2. Let the agent write the scripts

The agent proposes an approach and writes the code. Let it. Don't try to pre-architect it in your head — you'll get it wrong and slow everything down. Ask it to explain its plan in plain English if you want to follow along, but let it own the actual code.

A useful nudge early on: "keep it simple, and make it so I change content by editing a data file, not by editing code." That one instruction is why this whole pipeline is spec-driven (more on that in move 6).

### 3. Run it, look at the output, say what's wrong, iterate

This is the real work, and it's work you're perfectly equipped for. You run the command. You watch the video. And then you react like a director, not an engineer:

- "The subtitles are too small on a phone."
- "The music is louder than the narration — duck it under the voice."
- "The transition into shot 3 feels random. Land it on the beat."
- "This zoom is too fast; it looks cheap."

You don't need to know _how_ to fix any of that. You need to **notice** it and **say** it. The agent translates your reaction into a code change. Then you run it again and react again. Ten laps of that and you have something good.

The whole skill is that feedback loop: run → look → point at what's wrong → let the agent fix it → run again. It's the same loop whether you're building software or directing a film.

### 4. When you learn a lesson, save it as a reusable "skill"

This is the move most people miss, and it's the one that compounds.

Every time I figured something out the hard way — "never ask an image model to draw a number, it comes out as garbage," "reserve video generation for one hero shot to save money," "forums delete posts with store links" — I didn't just fix it that once. I told the agent: **"Save that as a rule in a skill file so you never forget it."**

That's what the files in `skills/` are: distilled lessons. Next time I ask the agent to build a video or write a post, it reads the relevant skill first and already knows all my hard-won rules. The knowledge stops living in my head (where I forget it) and starts living in a file (where it accumulates). Your agent gets a little smarter about _your_ standards every single time you use it.

A skill file is nothing fancy — it's a plain-text list of do's, don'ts, and worked examples. Start one the moment you correct the agent on the same thing twice.

### 5. Use a strong "director" model for the cinematic prompts

Not all writing is equal. The prompts that drive text-to-video are their own craft — they read like a film director's shot notes (see [docs/02](02-video-pipeline.md#director-style-prompts)). I don't hand-write them and I don't use a weak model for them. I ask a **strong, expressive model** to write them from a one-line brief, generate a few options, and I pick the best one with my taste.

The pattern generalizes: use your best model for the parts that need judgment and flair (cinematic prompts, the hook of a post), and let cheaper, faster automation handle the mechanical parts (stitching, encoding, file management). Matching the model to the difficulty of the task is itself a skill worth building.

### 6. Keep it spec-driven, so changing content is editing data, not code

Because I insisted early that content live in a JSON spec, changing what a video is _about_ never means touching code. New topic? Copy the spec, rewrite the prompts and narration, run it. The engine stays put; only the data changes.

This is the difference between a one-off script and a **pipeline**. A pipeline you can point at a hundred different topics without fear. Ask your agent to design things this way from the start — "make the behavior driven by a data file I can edit" — and you get reuse for free.

---

## What actually made the difference

Looking back, the things that mattered had nothing to do with programming ability:

- **Being specific.** "Make it better" gets you nothing. "The text is hard to read on a bright background — add a subtle dark scrim behind the subtitles" gets you exactly what you wanted.
- **Looking closely.** The quality came from watching each result carefully and catching the small wrong things. Taste is just paying attention.
- **Iterating without ego.** The first version is always rough. That's fine. You're not failing; you're on lap two.
- **Writing lessons down.** The skills folder is my second brain. It's why the fifth video was faster to make than the first.
- **Letting the agent own the code.** Every time I tried to micromanage the implementation, I slowed us both down. My job was the _what_ and the _good enough / not yet_; the agent's job was the _how_.

---

## You can do this

If you can describe what you want, notice when something is off, and keep going after the first draft, you already have everything this took. Start with the example spec. Change one thing. Run it. React. Ask the agent to fix it. Save what you learn.

That's the whole game. Go make something.
