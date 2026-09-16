---
name: reference-video-study
description: Deconstruct a public or user-supplied reference video into source-bound evidence about shots, motion, acting, color, sound and prompt claims, then design a single-variable production experiment. Use when asked to study, reverse-engineer or compare reference videos. Do not bypass access controls, copy protected media/prompts, imitate a named creator, or directly produce/publish a finished film.
---

# Reference video study

The goal is not to admire a clip or copy its prompt. Build evidence that distinguishes
what a source claims from what its output actually does, then test one transferable
mechanism in your own context.

## Acquire lawfully and bind the source

Use a public URL, a visible signed-in page the user may access, or a local file the user
provided. Do not bypass login, paywall, CAPTCHA, anti-bot or download restrictions.

Record:

- canonical source URL and a concise paraphrase of the visible post/page claim;
- creator attribution, publication date and access time;
- selected media stream, duration, dimensions, frame rate, codecs and SHA-256;
- whether prompt, model/version, seed, references, edits and failed takes are available;
- sampling density and which dimensions were not reviewed at normal speed with sound.

Keep third-party media and full frame/audio extraction in an ignored temporary directory.
Long-term records should contain only the minimum evidence needed to support the finding.
For a third-party long prompt, store the URL, source, hash when lawfully obtainable, short
compliant excerpts and a paraphrase—not the full prompt. Retain full text only when it is
user-owned or its license explicitly permits that use.

## Separate screen study from motion input

When the production needs real-world mechanics but the user cannot record a rehearsal,
keep three artifacts distinct:

1. `external_screen_study` — film, television, anime or web video inspected only to learn
   action phases, blocking, timing, gaze, contact and camera behavior;
2. `rights_cleared_motion_source` — user-owned, commissioned, public-domain, or explicitly
   licensed footage/mocap whose license, consent/likeness terms and intended use have been
   checked;
3. `shot_specific_neutral_proxy` — a faceless, voiceless neutral rig made for the exact
   shot, with no source pixels, recognizable performer, original background or source
   audio, and with authored support, weight, hands, prop contact and timing.

A visible movie scene or YouTube URL may support `external_screen_study`; access to it does
not grant download, derivative-use or AI-input rights. Never promote copyrighted screen
media to model input from availability, attribution, a short excerpt or a fair-use guess.
Use a separately rights-cleared motion source for the kinematic basis. Record negative
examples too: a camera raised over the head, floating feet or slow-motion weight transfer
can be valuable evidence without becoming a reference input.

A pose trace or rough 2D skeleton is a `research_fixture`. It can reveal detection gaps and
timing questions, but it is not a production proxy: it does not establish depth, foot lock,
contact, balance, prop attachment or a continuous whole-body performance. Production use
requires the canonical lineage, rights and normal-speed human gates in
[the native motion contract](../video-pipeline/references/ai-motion-production.md).

## Separate claim from evidence

Label every statement:

- `C claim` — post, prompt, README or author statement;
- `E evidence` — directly observed media/code/file fact;
- `I inference` — a falsifiable explanation based on evidence;
- `H hypothesis` — a mechanism worth testing in your own production;
- `D decision` — adopt for test, hold or reject;
- `R result` — the outcome of a controlled experiment.

Prompt text proves only what was requested. It does not prove timing, identity, gaze,
motion, sound or camera instructions were obeyed. Compare important `C` items against the
actual output and record `achieved`, `partial`, `shifted`, `contradicted` or `not tested`.

## Analyze on independent axes

Review only the axes the evidence can support:

- scene/shot boundaries and actual duration;
- composition, camera height/angle/axis and camera movement;
- subject identity, wardrobe, props and environment continuity;
- action phases, real-time speed, support/contact and secondary motion;
- gaze target, facial-performance sequence and dialogue behavior;
- palette roles, light sources, contrast, line/paint/surface grammar and detail density;
- editing rhythm, transitions, dialogue, ambience, SFX, music and mix;
- technical delivery, artifacts, text/watermarks and visible failures.

Uniform sampling is useful for the whole work; add denser diagnostic sampling around cuts,
fast motion, hands/contact, face changes and suspected defects. Frame sheets cannot replace
watching motion at 1x. Waveforms and codec probes cannot replace listening.

## Reverse prompts as visual re-expression

A frame cannot reveal its unique original prompt or hidden production settings. Write an
observation ledger with `observed / inferred / hypothesized / unknown`, then convert it to
a rights-safe model-neutral contract. Do not fill unseen clothing, exact lens, renderer,
model, seed, LUT or resolution with confident invention.

Do not put a named creator, studio, film, character, brand or “same IP” into a generation
prompt. Translate useful findings into independently expressible mechanisms such as
palette hierarchy, light direction, edge treatment, material wear, camera geometry and
action timing.

## Produce a bounded study package

Return:

1. a source/evidence manifest;
2. a concise timeline with representative timestamps rather than a reconstructive copy;
3. claim-versus-output findings;
4. provisional pattern cards with source, evidence, limits and risk;
5. one minimal paired experiment.

Each pattern remains `provisional` after one source. License and access terms control what
may be retained or reused. Copy no third-party code, prompt prose, UI, style catalog or
media into a commercial project unless the license clearly permits it.

## Test before consolidation

Change one variable while holding story, assets, model/version, duration, aspect ratio,
audio and budget constant. For stochastic generation, use multiple paired attempts rather
than one lucky output. Bind each output hash, cost and review verdict.

Judge the treatment at normal speed and intended size, then place it back into the full
scene. A pattern may become a production default only after the relevant quality axes
pass, a human approves the exact result and it reproduces in a second context.

Studying a reference never authorizes a paid request or publication. Hand approved
findings to the relevant production skill as `pattern_id`, source/hash, `C/E/I/H`,
rights/retention state, tested axis, limits and current evidence status—never as an
unqualified original prompt. For character or native-motion findings, route to
[character continuity](../character-continuity/SKILL.md) and
[the native motion contract](../video-pipeline/references/ai-motion-production.md). Do not
turn the study itself into a film.
