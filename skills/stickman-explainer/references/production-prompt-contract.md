# Production prompt contract (visual-only)

Use this only after the director's proposal is approved. Full style specs
are in `style-catalog.md`.

## Why this looks different from the source project

The project this skill is adapted from targets audio-native video models
(Gemini's Omni Flash / Veo-style tools) that render spoken dialogue and music
directly into the generated clip, so its prompts bake in a narrator-voice
description and a music cue on every clip. Most text-to-video APIs —
including whichever one you've wired into `scripts/gen_video.mjs` — don't
work that way: they render a silent (or, at most, ambient-sound) clip and
nothing else. Writing a full spoken line into a prompt for one of these
models doesn't produce narration; at best it's ignored, at worst the model
tries to paint the words on screen as garbled text.

So the output here splits into two pieces:

1. **Six visual-only prompts** — environment, character, composition, motion,
   negative constraints. No dialogue, no narrator-voice description, no music
   cue. These go straight to your video-generation script.
2. **A narration/music handoff sheet** — the actual line spoken during each
   scene, its tone, and a music direction. This doesn't go into any
   generation prompt; it feeds your `video-pipeline` per-shot narration step
   (see
   [`video-pipeline/SKILL.md`](../video-pipeline/SKILL.md#per-shot-narration-say--subtitle--its-own-voice-clip))
   and whatever generates or selects your music.

If you're doing a cheap standalone test on an audio-native model (e.g. a free
tier of a Gemini-style tool) just to sanity-check a character design or a
piece of motion before committing to your paid pipeline, it's fine to add the
narrator-voice and music-lock language back in for that one-off test — just
don't carry it into the prompts you actually feed your production pipeline.

## Package order

1. Global lock summary (aspect ratio, style, character/environment
   definition, accent colors, overall camera/transition strategy — a review
   summary for a human; each prompt below still repeats its own locks in
   full)
2. Six standalone visual prompts
3. Stitching guide
4. Narration/music handoff sheet

## Order within each prompt

1. **Output spec**: ~10 seconds, the chosen aspect ratio, a target resolution
   and frame rate
2. **Environment/background**: from `style-catalog.md` for the chosen style
3. **Character lock**: Style 1's fixed faceless description, or the Style 2
   anchor approved in Phase A, repeated in full (first clip states it fully;
   later clips say "the same [...]" and repeat it verbatim)
4. **Palette**: plain color words only, no hex/RGB/Pantone
5. **Composition for this aspect ratio**
6. **Inherited first-frame state** from the previous clip
7. **Three timed beats** — `[0–3s]` `[3–7s]` `[7–10s]` — describing what each
   beat visually expresses (not the narration text itself; just enough for
   you to check the visuals actually match what's being said at that moment)
8. **Optional ambient sound** (only if your model has an "add audio" flag,
   and only non-verbal cues — footsteps, a page turning, a mechanical sound —
   never dialogue or "narrator says...")
9. **Outgoing transition state** that the next clip inherits
10. **Negative constraints** — the general list below plus whatever's
    specific to the chosen style

Every prompt should be usable on its own, without needing another prompt's
context to make sense.

## Wording for density without drift

Use this phrase when you want a lot of visual events without inviting
character/style drift:

> rapid scene changes, kinetic motion-graphic transformations, and frequent visual events, while preserving an identical stick-figure design, constant line weight, and strict temporal consistency

Avoid "rapid *style* changes" — that phrasing tends to make models change the
drawing style itself, not just the pace of events.

## Motion notes (avoiding stutter)

- No abstract liquid/shape morphing (e.g. "stairs melting into a clock") —
  it tends to flicker and drop frames in diffusion video models.
- Drive motion with concrete actions instead: stepping, touching, opening,
  writing. Never leave the character idle for more than a second or two.

## General negative-constraint list (include in every prompt)

```text
Do not generate photorealism, unwanted 3D humanoid rendering, realistic facial features (pupils, detailed eyes, lips) or hair unless approved, extra limbs, malformed anatomy, disconnected lines, changed proportions, broken or changing line weight, inverted theme colors, unexplained colors, unintended characters, irrelevant spectacle, visible words, letters, numbers, technical color notation, palette labels, interface copy, captions, subtitles, logos, or watermarks, speech bubbles, comic dialog balloons, or visual text boxes.
```
Add the style-specific constraints from `style-catalog.md` after this.

## Stitching guide

List all six clips in order. For each cut, name the exact ending state of one
clip and the exact opening state of the next, plus any trim or short
crossfade needed to make the join clean.

## Narration/music handoff sheet

For each of the six scenes, list:

- the narration line, exactly as approved in the director's proposal — don't
  quietly edit it at this stage
- a tone/delivery note (flat statement, a pause before the turn, etc.)
- a music direction for that scene (mood, instrumentation) for whatever
  generates or picks your background track
- any ambient sound effect called for in step 8 above, so you can confirm
  it actually made it into the final edit

## Before moving on

- The current proposal was actually approved.
- Exactly six standalone prompts, each usable on its own.
- Each one repeats its aspect ratio, style, character, palette, composition,
  and negative-constraint locks in full.
- Each one has all three timed beats and at least four visual devices
  (carried over from the proposal's density rule).
- Every clip's ending matches the next clip's opening exactly.
- No dialogue, no narrator-voice description, no music cue, and no
  hex/RGB/Pantone color code appears in any generation prompt.
- The narration/music handoff sheet matches the approved proposal word for
  word — nothing was silently rewritten at this stage.
