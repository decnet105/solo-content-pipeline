# Director's proposal contract

Produce a readable proposal and stop for approval before writing any
generation prompt.

## Rewrite the source into narration

Write a narration of roughly 130–150 words in English (or, if you're working
in another language, a length that reads naturally in ~55–65 seconds of
speech at a normal pace — Mandarin runs closer to 220–280 characters for the
same duration; don't just translate the English word count).

- Preserve the source's core claim, names, numbers, and factual meaning.
  **Don't invent unsupported facts, statistics, quotes, or claims** — if the
  source is thin, strengthen it with a clearer example or a sharper framing
  of what's already there, not with made-up specifics.
- Fix a weak opening with an immediate hook.
- Cut repetition from a long source; expand a short one with a relevant
  example or a callback, not padding.
- Prefer natural spoken phrasing over a literal, stiff translation.

If you're producing this for a multi-language caption pipeline, also write a
reference translation of the narration — it doesn't go into any generation
prompt, it's just for your captions/dub track.

## Proposal header (in this order)

1. Title (and a reference-language title if relevant)
2. Core message and opening hook
3. Aspect ratio and visual style (Style 1, or Style 2A/2B with a short
   description of the environment)
4. Narration language, pace, word/character count, and estimated duration
5. Up to three accent colors (Style 1) or the environment's mood (Style 2),
   in plain words, with what each one represents
6. Music direction, emotional turn, and overall arc — this goes to whatever
   generates or selects your music, not into a visual-generation prompt

## Choosing a narrative pattern

- **Mechanism / reasoning**: counter-intuitive hook → setup → reveal the
  mechanism → play out the consequence → tie back to what it means → one
  closing line.
- **Character action**: situation → choice → consequence → meaning.
- **Motivational**: hook → recognition → escalation → reframe → action →
  payoff.

Pick whichever fits the source; don't force reasoning content into a
motivational arc or vice versa.

## Six-scene storyboard

Write six scenes, each covering roughly ten seconds, each field spelled out
as its own line (don't compress this into a table — it gets hard to scan
once the visual-device list gets long):

- **Time**: which of the six ~10-second scenes this is
- **Narrative job**: what this scene does in the argument; no two scenes
  should do the same job
- **Stick-figure scene**: the concrete visual content and metaphor
- **Motion / camera / transition**: character action, camera movement, how
  it enters and exits
- **Narration line**: the portion of the narration spoken during this scene
- **Reference translation**: if you're maintaining one
- **Music / SFX note**: for your music and sound-design step, not the
  visual-generation prompt

## Visual-density rule

Each scene needs at least four of these (pick what fits, don't force all of
them into every scene):

- a concrete character action (running, touching, writing, opening)
- an environmental change
- a specific visual metaphor (not an unrelated flashy effect)
- an icon-only diagram, arrow, or symbol (no visible text)
- particles, energy, or light
- a camera push/pull/pan/orbit/track
- a foreground wipe or object crossing the lens
- a match cut or motion-matched transition

Aim for a perceptible change every 2–3 seconds. Every effect should clarify
or intensify what the narration is saying at that moment — cut anything that's
just spectacle.

## No visible text in generated scenes

Default every generated clip to **no visible words, letters, numbers,
captions, or interface copy**. Message bubbles, cards, clocks, and
notifications should be icon-only. If you want a short on-screen phrase,
list it separately as a post-production overlay note — never put it inside
the generation prompt, where it usually comes out garbled anyway. This mirrors
how you're already handling captions elsewhere in this kit: burned-in text
comes from your own subtitle rendering step, not from the generation model.

## Composition by aspect ratio

- `16:9`: left-center-right staging, lateral tracking, horizontal match cuts,
  deliberate negative space.
- `9:16`: foreground/background depth, stacked vertical reveals, keep the
  edges clear of wherever your platform's UI sits (like button rails).
- `1:1`: compact, center-weighted action, short travel paths.

Changing the aspect ratio means re-staging the composition, not just
reformatting the same blocking.

## Continuity between scenes

Every scene must end on a specific, nameable state — a pose, an object's
position, a camera direction — that the next scene explicitly inherits. Name
both sides of the connection in the proposal.

## Ending the proposal

Ask the person approving it to do one of three things:
- approve the current proposal and move to generating the six prompts;
- name a specific scene or narration line to revise; or
- change something global (aspect ratio, style, narration language, tone) —
  which invalidates the current approval and requires a new proposal.

Don't write any generation prompt before this approval.

## Self-check before moving on

- Source, aspect ratio, and style are all known — none silently defaulted.
- Narration length matches the target duration for its language.
- Six scenes, each with a distinct narrative job.
- Every scene has three timed beats, at least four visual devices, and a
  named continuity connection to the next one.
- No more than three accent colors, described only in plain words.
- Any on-screen text is listed separately as a post-production overlay, not
  embedded in a generation prompt.
- No unsupported fact, statistic, or quote was invented to fill space.
- No scene depicts a real, identifiable person as if the character were them.
