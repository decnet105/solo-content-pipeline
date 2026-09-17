---
name: stickman-explainer
description: >
  Turn an abstract concept, mechanism, or piece of reasoning (not a concrete
  event you have footage of) into a six-scene, one-minute stick-figure /
  minimalist-animation explainer: a director's proposal you approve, then a
  package of standalone visual-generation prompts. Use when a segment is
  making an argument rather than presenting evidence, and no footage exists
  that actually fits it. Do not use this to depict, impersonate, or fabricate
  a documentary-style likeness of a real, identifiable person — the character
  must stay a neutral narrator. Inspired by the open-source
  kaomei/stickman-video-director project (MIT); rewritten here for a
  visual-only, provider-agnostic pipeline.
---

# Stickman explainer

Turn one idea into a confirmed director's proposal, then six standalone
prompts for roughly ten-second clips that a text-to-video model can render.
The result is silent, full-motion illustration — narration and music are
added afterward through this kit's own `video-pipeline`, not baked into the
generated clip.

## When to use this, and when not to

Ask three questions before reaching for this skill:

1. **Is this segment arguing a point, or showing something that happened?**
   Arguing a point (a mechanism, a piece of reasoning, a historical parallel)
   → this skill. Showing something that happened → find real footage or a
   real photo instead; a generated stand-in is not a substitute for evidence.
2. **Do you already have footage to explain over?** If yes and you just need
   a diagram or annotation layer on top of it, that's a different job — a
   semantic overlay skill, not a full-scene animated narrator. This skill is
   for when there is no underlying footage at all and something needs to
   carry the whole ten-second scene by itself.
3. **Are you depicting a real, identifiable person?** If yes, **do not** let
   this skill's character stand in for them. A stylized narrator explaining
   what someone did, or the logic behind a decision, is fine; a stylized
   character built to *be* that person — dressed and posed to pass as a
   likeness — is a fabricated depiction, not an explainer. Keep the character
   generic and let the narration carry the specifics. This is the same
   identity boundary [`video-deconstruct`](../video-deconstruct/SKILL.md)
   already draws around faces and voices — it applies here too, just in the
   opposite direction (you're generating, not reusing).

## Two things you must NOT copy from the source project

1. **Don't bake narration or music into the generation prompt.** The source
   project targets audio-native video models (Gemini's Omni Flash / Veo-style
   tools) that can render a spoken line and a music bed directly into the
   clip. Most text-to-video APIs — including the ones this kit already wires
   up in `scripts/gen_video.mjs` — do not read or speak a script; some accept
   an "add ambient sound" flag for atmosphere only. Generate **silent, visual-
   only** clips and follow this kit's existing per-shot narration pattern
   instead — see "Per-shot narration" in
   [`video-pipeline/SKILL.md`](../video-pipeline/SKILL.md#per-shot-narration-say--subtitle--its-own-voice-clip).
   Putting a full line of dialogue in a visual-generation prompt wastes tokens
   and often gets rendered as garbled on-screen text instead of being spoken.
2. **Don't reuse the source project's specific mascot design** (a named
   character in a particular hat and shirt). Use the plain faceless
   stick-figure style below, which carries no character-design baggage, or
   design your own character once and lock its description verbatim — see
   `references/style-catalog.md`. Reusing someone else's recognizable
   character in your own videos is a bad idea regardless of the license on
   the instructions that describe how to draw it.

## Workflow (approve the plan before generating anything)

1. Before planning, get all three of: the source idea/outline, the aspect
   ratio (`16:9` / `9:16` / `1:1`), and the visual style (Style 1 minimalist
   line art, or Style 2 with a custom character in either a clean studio
   environment or a full-color narrative environment — see
   `references/style-catalog.md`). Ask for whatever's missing in one message;
   never pick silently.
2. Read `references/storyboard-template.md` and `references/style-catalog.md`,
   then produce the director's proposal: a rewritten narration, a header
   block, and six scene rows. Stop and ask for approval before writing any
   generation prompt.
3. Any change to narration, structure, style, or aspect ratio invalidates the
   current approval — recompose and ask again. Approving an earlier draft is
   not approval of a revised one.
4. Only after approval, read `references/production-prompt-contract.md` and
   produce six standalone visual prompts, a stitching guide, and a narration/
   music handoff sheet for `video-pipeline`.
5. `references/example-trust-as-capital.md` works a full example end to end
   when you need one to resolve ambiguity — copy its *process*, not its topic
   or wording.

## Feeding the output back into the pipeline

- Treat each ~10-second clip as one `clip` shot in a `video-pipeline` spec;
  narration goes through that skill's existing per-shot TTS, music through
  whatever generation or library track fits the emotional arc you wrote in
  the proposal.
- Nothing about this skill exempts the segment from your normal QC — caption
  tracks, no-baked-in-subtitles-in-generated-footage, and any other release
  gate you already run still apply to this segment like any other.
- Make it obvious to the viewer that this segment is an illustration, not a
  record — a verbal transition ("picture it like this") or a small on-screen
  label works; don't let a generated-animation segment slide silently into a
  documentary-footage segment as if they were the same kind of evidence.

## Authoritative sources

- `references/style-catalog.md` — character DNA locks per style, environment
  specs, and the anti-deformation constraints that keep a character
  consistent across six independently generated clips.
- `references/production-prompt-contract.md` — how to write the six
  standalone visual prompts (visual-only: no dialogue, no music cues baked
  in) plus the narration/music handoff sheet.
- `references/storyboard-template.md` — the director's-proposal contract:
  narration rewrite, six-row storyboard, visual-density rules.
- `references/example-trust-as-capital.md` — a full worked example.
- Original methodology: kaomei/stickman-video-director (MIT). This skill is
  an independent rewrite for a silent, provider-agnostic video pipeline, not
  a copy of that project's files.
