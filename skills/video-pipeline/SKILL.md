---
name: video-pipeline
description: >
  Spec-JSON driven vertical short-video pipeline for a solo creator. One command per
  spec renders an end-to-end clip by orchestrating four AI APIs (image / image-to-video /
  music / text-to-speech) and stitching everything with PIL + ffmpeg. Use this when you
  want to produce a narrated short, add voiceover, render precise number/info cards, swap
  topics by swapping a spec, or extend the pipeline. Core ideas: generate-missing /
  reuse-existing asset resolver, per-shot narration where each shot's line is its own
  subtitle and its own voice clip on the timeline, PIL-rendered numbers (never let the
  image model draw digits or text), same-frame bilingual subtitles, and BT.709 for
  playback safety.
---

# Spec-JSON short-video pipeline

A reproducible way for one person to produce narrated vertical shorts. Everything a clip
needs lives in a single JSON spec; a build script turns that spec into a finished MP4 by
calling AI APIs only for the assets that are missing, then assembling with PIL + ffmpeg.

## One command per spec

```
python3 scripts/make_short.py examples/example-spec.json
```

Swapping the spec swaps the topic and produces a new clip. **Missing assets are generated
by the appropriate API; assets that already exist on disk are reused at $0.** Re-running a
spec is therefore cheap and idempotent — only new or changed shots cost money.

## The generate-missing / reuse-existing resolver

This is the heart of the pipeline. For every asset a shot references (background image,
motion clip, music bed, voice line), the builder:

1. Resolves the target path the asset should live at (deterministic, derived from the spec
   — e.g. a hash of the prompt + shot id).
2. If a file already exists there, reuse it (no API call, $0).
3. Otherwise call the API, write the result to that path, and cache it.

Consequences worth designing around:

- Change one shot's prompt and only that shot regenerates; the rest are free.
- Keep prompt text in versioned files so a re-run is byte-stable and diffable.
- Because image models are non-deterministic, cache aggressively — never regenerate an
  approved asset just because the pipeline ran again.

## Spec shape (generalize to your own schema)

- `intro` — optional branded hook shot (a logo card or a cold-open first frame). The first
  ~3 seconds must earn attention; a branded pre-roll usually hurts retention, so consider
  making shot 1 the hook itself.
- `shots[]` — the body. Each shot carries:
  - `image.src` — a background still (generated or reused), or a PIL-rendered card.
  - `say` — the narration line for this shot (see per-shot narration below).
  - `duration`, and a camera move (`kenburns` for stills, or a motion clip).
  - optional `emotion` / `speed` for the voice, and `sfx` entries.
- `outro` — closing / call-to-comment shot, folded onto the tail rather than shown as a
  separate abrupt end card.
- `music` — the BGM bed.
- `narration` / `voice` — top-level voice defaults (voice id, speed, ducking level).
- `transitions` — per-cut transition choices.

## Four-API orchestration

Wrap each provider behind a tiny caller so the builder only knows "give me an asset":

- **Image model** (a GPT-image-class model): still backgrounds and scene plates.
- **Image-to-video / text-to-video model**: real motion from a still or from a prompt.
- **Music model**: instrumental BGM.
- **TTS model**: narration / voiceover.

Keep API keys out of the repo and out of logs (load from a config path or env; never
print them). Log every paid call somewhere (a simple ledger CSV) — these APIs bill per
call and per second and it adds up fast.

## Per-shot narration (say = subtitle = its own voice clip)

Whole-track voiceover drifts out of sync with per-shot subtitles. The fix that holds:

- Each shot gets a `say` string. **The moment any shot in the spec has a `say`, switch the
  whole build into per-shot mode.**
- For each shot: run TTS on that one line → the clip's duration is set to (or stretched to
  fit) that voice clip → the subtitle for the shot is exactly that line.
- Position each voice segment on the finished timeline by absolute offset (ffmpeg
  `adelay`), computed from the running shot start — do **not** chain segments end-to-end,
  which accumulates drift.
- Per-shot `emotion` / `speed` let you act the line (upbeat during setup, softer at a
  reflective beat).

Clip stretching: if a line is longer than its source clip, time-stretch the video
(`setpts`) to cover it — but not beyond ~2.5×. Past ~3× the motion stalls and stutters.
For long lines, give the shot more source seconds instead of over-stretching.

## Precise number / info cards (the trust layer)

**Never let the image model render numbers or text — it garbles them every time.** Any
shot whose job is to show a figure, a date, a stat, or a document detail must be a
**PIL-rendered card**, not an AI image:

- Render the exact string with PIL onto your base color, content in the upper-middle,
  leaving the lower band free for subtitles.
- This produces a clean, legible "data" look that also contrasts nicely against the
  aged / textured AI scene plates around it.
- Source your figures from authoritative references (cite them), so the numbers are
  defensible — the whole point of a clean number card is trust.

## Same-frame bilingual subtitles

If you subtitle in two languages, render **both on the same frame** (primary language
larger, secondary smaller/dimmer) in a single render. Do not produce two separate videos.
One frame, two lines, one export.

## BT.709 for playback safety

Some players show untagged or `yuvj420p` exports as washed-out or fully black on certain
devices. On the final encode, force BT.709 and standard `yuv420p`:

```
-pix_fmt yuv420p -colorspace bt709 -color_primaries bt709 -color_trc bt709
```

Verify with `ffprobe` before delivery that the color tags are present.

## Color / tone discipline

- Define a small, consistent palette (one light base, one dark ink for text, one accent
  for ritual/CTA) and stick to it across every clip — consistency reads as a brand.
- If you want a distinctive look, avoid pure-black backgrounds and plain black-text-on-
  white; carry impact with type size and rhythm instead of loud color.
- On dark video, set subtitles in the light base color with a subtle shadow; reserve the
  accent for the CTA.
- Keep the overall tone warm and forward-looking; don't sell anxiety.

---

## Director-style cinematic text-to-video prompts

For the 1-2 hero motion shots, write the prompt like a shot list a director would hand a
DP — this is what separates a cinematic clip from generic AI slop. **Use a strong LLM as a
"director" to write these prompts**; a lazy one-line prompt is the real reason AI faces
and motion look fake.

Structure (works in any language; keep the sections):

- **Style** — realism / grain / sharpness / texture / edit rhythm. Explicitly forbid
  plastic CG skin and over-smoothing.
- **Duration** and **Aspect ratio** (e.g. 9:16).
- **Scene** — environment, lighting, depth-of-field / background blur.
- **Subject / character** — describe the character in *detail* (see the face lesson
  below) and demand "strictly consistent" to prevent identity drift across shots.
- **Audio** — sound design cues if the model supports it (often you disable the model's
  audio and lay your own music/voice in post).
- **Per-shot, timecoded** — for each shot: camera position, camera move (dolly / tracking
  / pan), the action, and where the hard cut lands on the beat.
- **Action & continuity hard-constraints** — physically correct motion, no morphing, hair
  / face / angle / wardrobe held across a cut, no teleporting, changes only at the
  intended anchor frame.
- **Layered negatives** — write negatives in layers (action / wardrobe / camera /
  background), the more specific the less it breaks: no face swap, no extra limbs, no
  clipping, no warped objects, no garbled text or logos, no plastic CG skin, no
  over-smoothing, no cartoon, no morph transitions, no camera shake, no watermark.

For faces: modern models render faces well when the prompt pins them down. Prefer writing
the character in detail — age, hair, brows, skin, sweat, build, expression, wardrobe, plus
"strictly consistent" — over avoiding faces. Face-avoidance (back-of-head / silhouette /
over-the-shoulder) is a shortcut for when you don't need a face, not a rule. When emotion
needs a face, write the face.

Cost note: motion generation is expensive (seconds-based billing), and a still image +
Ken Burns is near-$0. Reserve i2v/t2v for 1-2 key atmosphere shots; render number cards
and most scenes as stills. Provider balances can lag ~1h after top-up — a "locked" error
right after paying is usually propagation delay, retry later.

## Reusable camera-move templates

Keep a small library of moves you can drop onto any topic:

- **R1 — low tracking dolly-in.** Low camera glides along the side/behind a row of objects
  and pushes in, then hard-cuts to an over-the-shoulder close push. Good for crowd / set
  establishing shots. Line the like objects up facing the *same* direction (not toward
  each other); use haze / light ratio for depth.
- **R2 — over-the-shoulder slow push.** From directly behind a person, over the shoulder,
  shallow depth of field with focus on the screen/object in front of them; extremely slow
  dolly-in to a hold. Naturally hides the face (only the back of the head), so it's a clean
  emotion / focus shot — put the story on the screen they're looking at.
- **R3 — Ken Burns.** Slow zoom/pan (in / out / punch-in) over a still, paired with the
  per-shot subtitle. The near-$0 workhorse for number cards, document cards, and period
  stills when there's no motion budget.
- **R4 — step-on-lens + 90° roll reveal + hold (showcase move).** A "make an entrance"
  beat with no dialogue, carried by music + eyes + camera:
  1. **Step-on-lens (0–1.4s):** ultra-low ground-level up-angle, a foot/leg pressing close
     to the lens, ultra-wide (~13–16mm) perspective stretch, subject towering; high-
     contrast sky/skyline behind. Front 3 seconds hold the viewer.
  2. **Leg sweep + hidden cut + 90° roll (1.4–2.0s):** the leg sweeps across the lens
     creating occlusion + motion blur while the camera rolls ~90° on the same beat,
     revealing the subject in close-up. Land the beat on the reveal frame (second punch).
  3. **Held gaze (2.0–5.5s):** action settles, only faint breathing / hair / eyes to
     camera — near-still softness. The whole move is aggressive-then-soft contrast.
  - Align music downbeats to the cut points (roughly 0.1 / 0.8 / 1.6 / ~1.95 reveal / hold
    after 3.0s at 30fps).
  - When you reuse this on a topic, decide in advance *who* steps on and *what* is revealed.

## Production lessons (generalized)

- **Describe characters in detail rather than avoiding faces.** Identical / plastic AI
  faces come from lazy prompts, not from the model's limits. Pin the character down and
  demand consistency to get a distinct, believable face.
- **Style may vary, theme stays consistent.** Live-action, cinematic anime, or a
  game-style character composited into a real scene are all fair game per topic — keep the
  series theme coherent.
- **Multi-person shots: give each person a different action.** A row of people doing the
  identical motion (all typing in sync, all turning the same way) reads as copy-pasted
  puppets. Write each person their own beat (one typing, one leaning in on a mouse, one
  reclined, one lighting a cigarette, one glancing at a neighbor's screen).
- **Physically-correct action orientation.** Motion must obey physics (a dunk faces the
  hoop, not a back-facing reverse). To show both the action direction *and* the face, put
  the camera behind the target (e.g. above/behind the hoop looking back at the player).
- **Screens carry meaning but no readable text.** A screen in shot should imply content
  (a game HUD, a chat window, an icon), because it advances the story — but keep it to
  silhouettes / icons, never legible words (the model garbles text).
- **TTS number pronunciation.** Some TTS reads a bare year like "1999" as one giant
  number. Write years in the script as *spoken* digits (in Chinese, 一九九九 not 1999);
  subtitles can still show Arabic numerals.
- **Voice selection.** Pick a warm, non-shrill narrator that fits the material; render 2-3
  short samples and choose one before rendering everything — don't gamble a full render on
  an unheard voice.
- **SFX must survive the BGM.** A subtle sound gets buried under music. Make SFX punchy and
  use sidechain compression (ducking) so the BGM dips under voice/SFX; verify a specific
  effect is actually present with a narrowband `volumedetect` before delivery.
- **Keep endings warm / positive.** Don't land on "empty room / cold blue / desolation"
  (reads as bleak). End on warm light, a treasured memory, forward motion — put the final
  frame on the brightest / highest point, not a sinking empty shot.
- **Don't cut the music off abruptly.** Fade the BGM out over ~0.8s → 2.0s, not a hard
  stop. Let a voiceless tail shot carry the music up and gently down.
- **Fold the CTA onto the tail** rather than tacking on a separate abrupt end card, and
  keep the brand mark in a single consistent corner across the whole series.
- **Test with small samples, don't over-attribute.** A handful of early views is noise;
  read the direction signal, not the exact number.

## Cost / discipline

Rough order of magnitude: a stills-only card video is cheap; one i2v/t2v hero shot is a
few dollars; several motion shots run higher; per-shot TTS is cents per line. Scope your
topics first and render them one at a time — don't batch-burn budget speculatively. Log
every paid call. Review anything before it goes public.
