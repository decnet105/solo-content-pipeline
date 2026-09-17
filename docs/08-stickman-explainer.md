# 08 · Explaining an idea with a stick figure, not a camera

Every other skill in this kit assumes you have — or are generating — footage
of something. This one is for the opposite situation: you're making an
argument, not showing an event, and there's no footage that actually fits.

## The three questions that decide whether you need this

1. **Is this segment arguing a point, or presenting evidence of something
   that happened?** Arguing a point (a mechanism, a piece of reasoning, a
   historical parallel) is what this skill is for. If you're presenting
   evidence, go find the real footage or photo instead — a generated
   stand-in doesn't substitute for it.
2. **Do you already have footage to explain over?** If yes, and you just
   need to annotate or diagram on top of it, that's a different kind of
   explainer than this one — a full-scene animated narrator is for when
   nothing is on screen yet.
3. **Are you depicting a real, identifiable person?** If yes, this skill's
   character must never stand in for them. It stays a neutral narrator
   explaining what someone did or the logic behind a decision — never a
   stylized likeness built to pass as that person. That line matters for the
   same reason [`video-deconstruct`](../skills/video-deconstruct/SKILL.md)
   won't let you reuse someone else's face or voice: a viewer needs to be
   able to tell illustration from documentary record.

## What you get

1. **A director's proposal** — a rewritten narration, a chosen aspect ratio
   and visual style, and six ~10-second scenes, each with a narrative job,
   a visual description, and a continuity link to the next scene. You
   approve this before anything gets generated.
2. **Six standalone visual-generation prompts** — silent, visual-only,
   locked to a consistent character and environment across all six clips.
3. **A narration/music handoff sheet** — the actual spoken line and a music
   direction for each scene, kept completely separate from the generation
   prompts.

Work through
[`skills/stickman-explainer/SKILL.md`](../skills/stickman-explainer/SKILL.md)
for the full contract; this doc is the walkthrough.

## Why the prompts don't contain any dialogue

This skill is adapted from an open-source project built for audio-native
video models that render spoken lines and music directly into a clip. Most
text-to-video APIs — including whatever you've wired into
`scripts/gen_video.mjs` — don't do that: they render a silent (or, at best,
ambient-sound) clip and nothing else. Writing a full narration line into one
of these prompts doesn't produce narration; it either gets ignored or shows
up as garbled on-screen text.

So the six visual prompts only ever contain environment, character,
composition, motion, and negative constraints. The actual spoken line for
each scene lives in the handoff sheet, and gets voiced through this kit's
existing per-shot narration step — see
[`video-pipeline`'s per-shot narration section](../skills/video-pipeline/SKILL.md#per-shot-narration-say--subtitle--its-own-voice-clip).
Music works the same way: a direction in the handoff sheet, not a cue baked
into a generation prompt.

## Designing your own character, not borrowing one

The source project ships a specific mascot — a particular hat, a particular
shirt. Don't reuse it; it's someone else's recognizable character design,
regardless of the license on the instructions describing how to draw it.
Two options instead:

- **Style 1**, a faceless minimalist stick figure with no costume at all —
  zero design decisions, zero risk, works for almost any dense/logical
  content.
- **Style 2**, where you design one small, distinctive costume or prop once
  and lock its exact wording across all six clips, the same anchor technique
  the source project uses — just with your own design instead of theirs.

`skills/stickman-explainer/references/style-catalog.md` has the exact
locking language and the anti-deformation rules (no detailed pupils, repeat
the costume description verbatim every clip, keep small props smooth-edged)
that keep a generated character from drifting or deforming clip to clip —
these are lessons from real generation failures, worth keeping even if you
change everything else.

## A full example

`skills/stickman-explainer/references/example-trust-as-capital.md` walks a
complete idea — why an old private bank's real asset was the trust it had
earned, not the coin on its counter — from the director's proposal through
two fully written generation prompts. Copy its process and level of detail,
not its topic; and note that it's a teaching example, not verified script
content — run any real factual claim through your own research before it
goes in front of an audience.

## Feeding it back into the pipeline

Each ~10-second clip becomes one `clip` shot in a `video-pipeline` spec, same
as any other generated footage. Nothing about this skill exempts the segment
from whatever release checks you already run — caption tracks, no burned-in
text from the generation step, and so on all still apply. And make the
illustration legible as illustration: a verbal transition or a small label
so a viewer never mistakes a generated explainer scene for documentary
footage of a real event.
