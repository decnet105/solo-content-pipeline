# 05 · From a moving picture to a real AI video production loop

The starter pipeline is good at assembling narrated vertical shorts from stills, cards,
voice, music and occasional generated clips. That is not the same problem as producing a
character-led animated shot with believable acting and continuity.

A slow zoom over a still can be an effective presentation choice. It is not evidence that
a character can turn, step, focus on an object, raise a camera, change expression and keep
the same body, face, clothing and props across every frame.

This chapter adds the production layer around the existing scripts. It is deliberately
provider-neutral and clean-room: it summarizes observable mechanisms, not third-party
code, full prompts, creator styles or media.

## The three ideas that matter most

### 1. Separate control axes

Do not solve identity, wardrobe, environment, composition, light/color, action, camera,
facial acting and sound with one pile of adjectives. Each axis needs an owner, an approved
input and a way to review the result.

A public X post proposes seven anime-prompt layers: category, era/genre/culture, rendering
medium, light/color/mood, viewpoint, environment and story feeling, with only a few
compatible terms per layer. The useful idea is axis separation; the post does not provide
enough model/version, seed, reference, failed-take or paired-test evidence to prove stable
style locking. See the [original seven-layer post](https://x.com/gaoren7716/status/2093510026019447219).

### 2. Give every reference an explicit job

The same image can be used to preserve a face, define an outfit, anchor the first frame,
show a hand-object contact or suggest motion. Those are different jobs. Record them as
different reference roles instead of hoping the provider infers purpose from array order.

Useful roles include:

```text
identity, look, expression, environment,
start_frame, end_frame, interaction,
motion_reference, temporal_structure, audio_reference
```

Provider labels such as `@Image1` are temporary adapter syntax. They do not belong in the
character or story truth.

### 3. Compare the request with the returned file

A prompt is a claim about intent. The output is evidence of what the model did.

In one public H3 demonstration, the posted prompt described a 6.18-second schedule and
repeatedly fixed a high overhead view. The attached selected video stream measured about
8.08 seconds. The high camera geometry broadly survived, while action windows shifted and
the late gaze/eye lock was not exact. That single case supports explicit reference roles
and concrete camera geometry as testable hypotheses; it does not support “longer and more
repetitive prompts obey better.” See the [original H3 post](https://x.com/LoveUolanda/status/2093598354865569980),
[MiniMax's H3 overview](https://www.minimax.io/blog/minimax-h3) and the
[fixed official prompt-skill snapshot](https://github.com/MiniMax-AI/MiniMax-H3/blob/d21241f0a4b3acbb34c97dae47fa417b7065e438/skills/h3-prompt-writing/SKILL.md).

## Reverse an image without inventing its history

“Reverse the complete prompt” is an underdetermined request. Many prompts, models, seeds,
references, control signals, edits and color transforms can converge on a similar image.

Use four labels:

- `E observed` — visible subject, geometry, pose, gaze, contact, palette, light,
  perspective, line/paint grammar, materials and defects;
- `I inferred` — a plausible but non-unique explanation;
- `H hypothesized` — an instruction worth testing;
- `unknown` — exact camera, lens, renderer, model, seed, LoRA, LUT, upscale route or
  unseen clothing unless provenance establishes it.

Then produce four separate artifacts:

1. observation ledger;
2. model-neutral visual contract;
3. current-provider adapter;
4. single-variable evaluation plan.

Terms such as “8K,” “masterpiece” and “cinematic” are not mechanisms. A named creator,
studio, title, character, brand or “same IP” should remain provenance for human study, not
the generation instruction. Re-express only rights-safe visible mechanisms.

## Build from source to screen in layers

For story-led work, keep these layers separate:

1. **Source ledger** — exact text/fact anchors and what cannot change.
2. **Visual/directing enrichment** — approved visible actions, staging, environment,
   performance and sound that make the source filmable.
3. **Continuity packs** — character identity/look, environment state, hands/props,
   expression and motion references.
4. **Neutral one-shot contract** — one continuous shot with closed duration and state.
5. **Provider adapter** — current endpoint syntax, capabilities and reference mapping.
6. **Deterministic assembly** — edit, captions, mix, color and encode from approved clips.

The provider prompt is layer 5. It must not become a second screenplay or silently invent
missing identity, action or setting decisions.

## One request, one continuous shot

Each paid generation request should describe one uninterrupted photographic shot:

- purpose and source/story anchor;
- duration and output geometry;
- start pose/state;
- preparation and weight transfer;
- main action or contact;
- braking/settling and end state;
- camera position, axis, movement and stop condition;
- gaze target and facial reaction;
- feet/support, both hands, props and contact points;
- continuity in/out and forbidden drift.

Put cuts, shot/reverse-shot, montage, subtitles, transitions, music and final pacing in the
edit/audio plan. Exact timestamps in prompt prose do not guarantee exact timing; the
returned file must be measured.

## Character motion needs more than a good first frame

A character pack should separate stable identity from changeable look and per-shot state.
Use independent identity, three-quarter/profile, full-body and hand/interaction images
rather than one contact sheet for every machine role. Track left and right hand occupancy
and every important prop's owner/container and state transitions.

For a visible reaction, use a causal sequence:

```text
stimulus -> attention -> appraisal -> expression/body response -> decision -> residual
```

For a turn, reach, step, impact or object interaction, review a rights-cleared real-world
reference at 1x speed and define support foot, pelvis/root path, joint chain, contact,
secondary motion and end pose. High frame rate or smooth optical flow does not prove
correct weight or contact.

The reusable character workflow now lives in
[`skills/character-continuity/SKILL.md`](../skills/character-continuity/SKILL.md).

## Treat paid generation as a recoverable task

Before submitting, record:

- approved input hashes and reference roles;
- provider/model/endpoint revision and official capability source;
- request ID, immutable input digest and idempotency key;
- maximum paid attempts and cost ceiling;
- external task ID and retry classification.

Permit one paid attempt per authorized request. Polling and download can retry without
starting a new generation. Rights, policy, invalid input, exhausted budget, hard QC and
human rejection are terminal for the same attempt. If the submission response is unclear,
reconcile the original task rather than paying again.

Provider `success`, a URL or a downloaded MP4 means delivery—not acceptance.

## Review the exact output

Download and hash the raw output, probe it, then watch the entire exact file at normal
speed and intended size with sound. Review:

- story action and timing;
- identity, wardrobe and accessories;
- gaze and causal facial acting;
- support/contact, hands/props and normal-speed physics;
- camera, spatial and lighting continuity;
- dialogue, ambience, music and unwanted text/watermarks;
- duration, dimensions, frame rate, codec, color and audio.

Automated checks find suspicious intervals. They do not award taste or story approval.
Only a current human verdict tied to the exact output hash may enter assembly. Missing or
rejected shots stay missing; the renderer must not silently skip them.

## What the open production repositories taught us

The audit used fixed snapshots so later changes do not rewrite the evidence:

| Repository snapshot | Useful abstraction | Do not import as proof |
|---|---|---|
| [Moyin Creator `7e5c565`](https://github.com/MemeCalculate/moyin-creator/commit/7e5c5655de94d49885e13c369f0a71212893a0aa) | staged shot compilation, identity anchors, reference-purpose records | orchestration is not body-motion QC; AGPL/commercial dual-license boundary |
| [waoowaoo `ce8edeb`](https://github.com/waooAI/waoowaoo/commit/ce8edebf7cd2fe32c37a8d628aa3edc67f544586) | source anchors, task graph, external-ID recovery, cost reserve/settle/rollback | URL readiness and soft prompt fields are not visual acceptance; CC BY-NC-SA boundary |
| [Huobao Drama `0077b43`](https://github.com/chatfire-AI/huobao-drama/commit/0077b438907666b7c22e378ed6767f7f00fec396) | reusable character/environment masters, stable reference ordering, provider adapters | multiple cuts in one generation and URL/merge completion; conflicting license metadata |
| [mk-video-studio `6e97339`](https://github.com/phoenix-gh/mk-video-studio/commit/6e9733928c9d637e50fdabc404b17a445591a8d5) | world/blocking/camera/prop locks, hand occupancy, continuity in/out, task recovery | prompt constraints are not biomechanics; PolyForm Noncommercial boundary |
| [Short Video Factory `36e1ae7`](https://github.com/YILS-LIN/short-video-factory/commit/36e1ae7b082576fa39173b65ffe4212501c37c5e) | deterministic ffmpeg normalization and assembly ideas | random stock mixing cannot provide narrative continuity; AGPL boundary |

All five systems mainly orchestrate external models. None of those snapshots supplies a
complete normal-speed biomechanics, gaze, facial-performance and exact-output human review
loop. This repository therefore adopts only independently written abstract methods; it
copies no third-party code, prompt prose, UI, style catalog or assets.

## What is enforced today

The production contract is available to the coding agent at
[`skills/video-pipeline/references/ai-motion-production.md`](../skills/video-pipeline/references/ai-motion-production.md).
The reference-study method is in
[`skills/reference-video-study/SKILL.md`](../skills/reference-video-study/SKILL.md).

The current starter scripts still cache mostly by spec/shot key. Their generated-video
route uses one start image, a fixed four-second request and a `face_free` switch; it does
not carry independent identity/look/interaction/motion references. It also submits jobs
without a durable generation ledger or automatic visual QC. The new contracts are honest
preflight/review guidance, not a claim that those controls are already implemented in
code. A future production-grade extension should add multi-role reference admission,
content-addressed caching, durable task state, cost reservation, output hashing and
fail-closed assembly before advertising them as automatic guarantees.

An approved motion take is still only one node in the full production run. It does not
prove that every required shot was selected, the edit is frame-exact, the mix/grade/
subtitles match their contracts, or a person approved the exact delivery master. Continue
with [docs/06 · End-to-end run control](06-end-to-end-run-control.md) and the reusable
[`video-run-control` skill](../skills/video-run-control/SKILL.md) for those cross-stage
gates.
