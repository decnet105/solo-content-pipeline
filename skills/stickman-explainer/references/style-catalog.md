# Style catalog: character DNA, environment specs, anti-deformation rules

These are text fragments meant to go straight into an image/video-generation
prompt — keep them in English even if the rest of your project is in another
language, since that's what most generation models are tuned on.

## 1. Style overview

- **Style 1 (minimalist line art)** — flat white or black canvas, monochrome
  lines, up to three saturated accent colors. Best for dense, logic-heavy
  explainers: mechanisms, mental models, fast-paced reasoning. Faceless,
  clothes-free character — no character-design decision to make, no IP risk.
  **Default to this unless you have a specific reason to use Style 2.**
- **Style 2 (custom character, two environments)** — a character you design
  once and lock verbatim across all six clips.
  - **Style 2A (clean studio)**: bright white studio, subtle floor grid,
    glowing UI elements. Fits modern/tech/tooling topics.
  - **Style 2B (full-color narrative scene)**: a real environment with
    cinematic lighting — a room, a street, a landscape, a historical
    setting. Fits stories that need atmosphere or a specific time and place.

## 2. Style 1: minimalist line art

### Canvas
- Light theme: `flat, uniform, digitally pure-white canvas, strictly forbid gray tint, paper texture, gradients, shadows, lighting, bloom, fog, or 3D depth.`
- Dark theme: `flat, uniform, pitch-black canvas, pure white or high-contrast line art.`
- A warm off-white canvas (`flat, uniform, warm ivory paper-toned canvas, no texture, no gradient, no 3D depth`) works too if it matches your brand better than stark white — still describe it in plain words, never a hex code.

### Character DNA
```text
A minimalist 2D stick figure with a hollow circular head, no facial features, no hair, no clothing, no filled body, uniform medium line weight.
```

### Accent colors
Up to three saturated accents, named in ordinary words and tied to your own
palette rules (swap the examples below for yours):
- `<your primary accent, e.g. warm amber>`
- `<your secondary accent, e.g. deep red>`
- `<your tertiary accent, e.g. ink blue>`

Never write a hex/RGB/Pantone code inside a generation prompt — models
sometimes render the literal notation as on-screen text.

## 3. Style 2: designing your own character anchor

**Do not reuse the source project's specific mascot** (a particular hat and
shirt combination) — that's someone else's recognizable character design.
Instead, fix your own character once, using the same locking technique:

```text
[Clip 1 anchor]
A minimalist 2D animated stick figure wearing <one or two fixed, distinctive items — e.g. a plain indigo robe and a small lantern, or a simple cap and a satchel>, with simple black stick limbs. Simple black lines, muted color accents, smooth 2D animation style.

[Clips 2–6 anchor]
The same minimalist 2D animated stick figure in <repeat the exact Clip 1 description>... Simple black lines, muted color accents, smooth 2D animation style.
```

Three anti-deformation rules, verified against real generation failures in
the source project and worth keeping as-is:

- **Never request detailed pupils, irises, or realistic facial contours** —
  even a hollow circle or a single dot for eyes; detailed eyes are a common
  trigger for "bug-eye" deformation in diffusion video models.
- **Repeat the full costume/prop description verbatim in every clip.** Drop
  it in clip 3 and the character reverts to a bare Style 1 figure, or looks
  different clip to clip.
- **Describe props as smooth and regular** to stop models from growing random
  frayed edges or texture on small objects (a hat pom-pom, a bag strap, a
  lantern's paper shade).

### Style 2A environment
```text
in a modern bright white studio space with subtle light-gray perspective grid lines on the floor plane. High-key studio lighting, clean white negative space, sleek glowing cyan and electric blue glass holographic UI elements.
```
Pair it with this negative constraint every time (without it, diffusion
models tend to add circuit-board textures and sci-fi wall panels on their
own):
```text
Negative constraints: strictly minimalist studio aesthetic, no circuit board textures, no sci-fi wall panels, no spaceship corridors, no cracked concrete, no grunge textures, no photorealistic human skin, no speech bubbles, no dialogue text boxes.
```

### Style 2B environment
```text
in a rich full-color cinematic environment [describe the specific setting — a room, a street, a landscape, a period-accurate historical scene]. Cinematic volumetric lighting, soft depth of field, atmospheric narrative mood, period-accurate props if historical, no anachronisms.
```
```text
Negative constraints: no photorealistic human skin or faces, no 3D humanoid CGI uncanny valley models, no chaotic line glitches, no speech bubbles, no dialogue text boxes, no anachronistic or out-of-period objects.
```

## 4. Motion pacing formula (all styles)

Every ~10-second clip breaks into three beats:
```text
[0–3s]: establish or inherit the visual premise from the previous clip.
[3–7s]: transform, escalate, or explain the idea through a concrete character action.
[7–10s]: land the beat and leave a state the next clip can inherit.
```
- A visible change every 2–3 seconds; never let the character stand idle.
- Avoid abstract liquid/shape morphing (e.g. "stairs melting into a clock") —
  it tends to stutter and flicker in diffusion video models. Drive motion
  with concrete actions instead: stepping, touching, opening, writing.
- Every clip's ending state must be exactly what the next clip's opening
  inherits (same pose, same object position, same camera direction).

## 5. A locked description is a prompt, not a guarantee

Same lesson as [`character-continuity`](../character-continuity/SKILL.md):
repeating an anchor description word-for-word makes consistency *likely*, not
certain. After generating all six clips, actually look at them side by side —
costume, props, line weight, proportions — before moving on. Regenerate the
clip that drifted; don't try to fix an obviously wrong character design with
color grading or cropping in post.
