---
name: character-continuity
description: Build reusable, rights-cleared identity, wardrobe, expression, hand/prop and per-shot continuity records for AI images or video. Use when a character must remain coherent across frames in one generated clip, or across multiple looks, shots or clips. Do not use to imitate a real person without permission, write the story, or approve a finished film.
---

# Character continuity

Treat a recurring character as a versioned production asset, not a paragraph that gets
rewritten for every shot. Preserve identity separately from what may change.

## Establish authority and rights

Record whether the character is original, commissioned, licensed or based on a consenting
person. Bind source files and approvals by exact path/hash. A descriptive filename,
provider success or visual resemblance is not permission.

Keep three layers distinct:

- **Identity** — stable face/body geometry, age band, proportions and distinguishing
  features.
- **Look** — hair state, wardrobe, footwear, accessories, makeup, wear and story-time
  condition.
- **Shot state** — pose, gaze, expression phase, hand occupancy, held props, contact and
  visibility for one shot.

A new outfit must not silently change identity. A pose reference must not become the face
reference just because both appear in one image.

## Build independent canonical views

Create and approve independent source images at useful resolution. A practical base pack
usually includes:

- front bust or head-and-shoulders identity master;
- left/right three-quarter views;
- a profile when the production will use it;
- front full body with neutral, weight-bearing stance;
- rear/full-body wardrobe view when required;
- dedicated hand/prop interaction close-ups for important tools.

A contact sheet is for human comparison. Do not use one composite sheet as the only
machine reference when the provider can accept the independent views. Reject duplicate
files disguised as new angles, malformed/low-information images and views with unresolved
identity or rights.

A single sample image does not establish unseen body proportions, hands, footwear, prop
construction or rear wardrobe. Mark those fields unknown until independently designed and
approved; do not invent them and call them observed continuity.

## Design specificity without perfect symmetry

Define concrete, mutually compatible traits across face shape, jaw/cheek structure,
brows, eyes, nose, mouth, hairline, build, posture and one or two distinctive marks.
Allow natural left/right asymmetry, material wear and small lived-in irregularities.

Do not rely on “handsome,” “beautiful,” “cinematic” or a creator/style name. Translate
appeal into visible design decisions: silhouette, proportion, expression, line weight,
palette hierarchy, material texture and how the character carries weight.

## Eyes, gaze and facial acting

For each shot, identify the story stimulus and actual gaze target. Describe a causal
performance transition:

```text
stimulus -> attention shift -> appraisal -> visible response -> decision -> residual state
```

Bind eyelids, iris/pupil direction, brows, mouth/jaw, cheeks/nose-side tension, breathing
and head/body response to that sequence. “Looks emotional” is not executable. Direct eye
contact with the audience is valid only when the story calls for it; otherwise look at the
person or object that causes the reaction.

## Wardrobe, accessories and props

Give every look a stable ID and record period/context, layers, fit, materials, palette,
wear, closures, pockets and accessories. A character's work and taste should shape these
choices; do not give every person the same generic outfit.

Track important props as stateful objects:

```text
owner/container -> state_in -> hand/contact event -> state_out -> next owner/container
```

Record left- and right-hand occupancy independently. One hand cannot simultaneously hold
two incompatible objects, and a prop cannot disappear between continuous shots without
an explicit event.

## Per-shot continuity overlay

Do not paste the whole character bible into every provider prompt. For each shot, return a
compact overlay bound to the approved shot ID:

- visible character and look IDs;
- identity/look reference hashes and intended roles;
- start/end body pose and support state;
- gaze target and facial-performance beats;
- left/right hand occupancy, props and contact points;
- allowed occlusion and required visible features;
- continuity in/out and forbidden drift.

The story/directing layer owns why the action happens and what it changes. This skill owns
how the same identity, look, body, face, hands and props remain coherent while it happens.

For locomotion, contact, prop handling or generated dialogue, also apply
[the native motion production contract](../video-pipeline/references/ai-motion-production.md).
If rights, independent approved identity/interaction assets or a 1x motion reference are
missing for a high-risk action, the paid-generation preflight must fail.

## Approval gate

Review character views independently and side by side. Reject identity drift, duplicated
angles, mirrored directional features, eye/gaze errors, inconsistent body proportions,
wardrobe/accessory changes, impossible hands/contact and missing prop state.

Only human-approved exact assets may be bound to a paid generation request. A generated
clip still needs whole-file normal-speed review; a strong first frame does not prove the
identity survives the motion.
