---
name: video-pipeline
description: >
  Spec-JSON driven vertical short-video pipeline for a solo creator. One command per
  spec assembles a clip by orchestrating four AI APIs (image / image-to-video /
  music / text-to-speech) and stitching everything with PIL + ffmpeg. Use this when you
  want to produce a narrated short, add voiceover, render precise number/info cards, swap
  topics by swapping a spec, plan a bounded native-motion shot, or extend the pipeline.
  Distinguish inexpensive still-card assembly from real generated character motion; use
  explicit reference roles, paid-request recovery, exact-output review, per-shot
  narration, locally rendered exact text (animated split-flap number cards), a music bed
  carved out of the narrator's voice band, word-anchored effect timing, same-frame
  bilingual subtitles, and BT.709.
---

# Spec-JSON short-video pipeline

A reproducible way for one person to produce narrated vertical shorts. Everything a clip
needs lives in a single JSON spec; a build script turns that spec into a rendered MP4
candidate by calling AI APIs only for the assets that are missing, then assembling with
PIL + ffmpeg.

The one-command guarantee covers the starter's stills, cards, supplied clips, narration
and final assembly. It does not guarantee production-grade recurring-character animation;
the built-in generated-video experiment has the explicit limits below.

## One command per spec

```
python3 scripts/make_short.py examples/example-spec.json
```

Swapping the spec swaps the topic and produces a new clip. **Missing assets are generated
by the appropriate API; assets that already exist on disk are reused at $0.** Re-running
an unchanged cache key is therefore cheap. This file-existence cache is not cryptographic
idempotency and does not by itself notice every prompt or model change.

## The generate-missing / reuse-existing resolver

This is the heart of the pipeline. For every asset a shot references (background image,
motion clip, music bed, voice line), the builder:

1. Resolves the target path the asset should live at (the starter currently derives it
   mainly from the spec name and shot key).
2. If a file already exists there, reuse it (no API call, $0).
3. Otherwise call the API, write the result to that path, and cache it.

Consequences worth designing around:

- To change one shot, change its key or deliberately remove only that shot's cached file;
  editing prompt text alone may not invalidate the current starter cache.
- Keep prompt text in versioned files so a re-run is byte-stable and diffable.
- Because image models are non-deterministic, cache aggressively — never regenerate an
  approved asset just because the pipeline ran again.
- For a paid provider task, separately save the immutable input digest, request ID,
  provider task ID, estimated/actual cost and returned-file hash. If submission status is
  ambiguous, reconcile that task instead of submitting the same request again.

## Spec shape (generalize to your own schema)

- `intro` — optional branded hook shot (a logo card or a cold-open first frame). The first
  ~3 seconds must earn attention; a branded pre-roll usually hurts retention, so consider
  making shot 1 the hook itself.
- `shots[]` — the body. Each shot carries:
  - `image.src` — a background still (generated or reused), or a PIL-rendered card.
  - `number_card` — an exact figure drawn locally (see below); use this, not `image.gen`, for any number.
  - `say` — the narration line for this shot (see per-shot narration below).
  - `duration`, and a camera move (`kenburns` for stills, or a motion clip).
  - optional `emotion` / `speed` for the voice, and `sfx` entries.
- `outro` — closing / call-to-comment shot, folded onto the tail rather than shown as a
  separate abrupt end card.
- `music` — the BGM bed (`carve` keeps it out of the voice band; see *Music under narration*).
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

## Choose the right motion route

- A still plus zoom, pan or parallax is an inexpensive **presentation treatment**. It is
  useful for cards, documents, landscapes, timing drafts and design review, but it is not
  evidence of character animation.
- A supplied clip is real motion only if its provenance and rights are known.
- A native i2v/t2v/ref-to-video result is a **candidate motion shot**. Provider success or
  a downloadable URL proves delivery, not natural movement, identity continuity or story
  correctness.

For acting, locomotion, turns, reach/contact, prop handling, moving faces, dialogue or
cross-shot continuity, read
[the native AI motion production contract](references/ai-motion-production.md) before
making a paid request. The current starter scripts do not enforce that contract
automatically. Their built-in generated-video route is a four-second, single-start-image,
`face_free` experiment; it cannot bind separate identity/look/interaction/motion assets or
durably resume a provider task. Do not use that route for character-led motion and call it
production-ready. Use a supplied, approved clip or stop until a capable adapter and task
ledger are implemented and explicitly authorized.

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

**In the spec, use the `number_card` shot field** — `{label, number, unit, source}`. It
renders an animated **split-flap reveal** by default (each digit rolls up and locks in,
left to right, and always lands on the exact figure however short the shot;
`"animate": "static"` gives a flat PNG). Zero API cost, re-rendered every run. Standalone
tools: `scripts/gen_splitflap_card.py` (mp4) and `scripts/gen_number_card.py` (PNG).
Use a font with lining figures (`VIDEOGEN_FONT`) — some serifs draw a `0` like an `o`.
Details, safety guarantees and the font note: [docs/09](../../docs/09-number-cards-voice-mix-word-timing.md).

## Music under narration: keep the voice band clear

Flat ducking lowers every frequency equally, yet speech is understood in ~500 Hz–3 kHz, so
a bed that is "ducked 12 dB" can still be as loud as the narrator *in that band*. The
default mix is therefore a **voice carve**: split the BGM low/mid/high and compress only
the mid band hard against the narration (`music.carve`, on by default; `false` = legacy
flat ducking, bit-identical to the old output; `music.gain_db` = static bed level).

- **Measure before tuning:** `python3 scripts/measure_voice_band.py spec.json` prints how
  many dB the narration sits above the music in that band (flat vs carve). Above ~+10 dB
  is comfortable; below ~+6 dB the bed competes with the voice.
- It is a band-RMS proxy, not STI/STOI: it tells you which renders are at risk, the ears
  choose the setting. With carve on, `bgm_ducking_db` no longer applies.

## Word-anchored timing (optional)

`number_card.at_word` (+ `at_word_nth`, `at_mode: settle|start`) makes the figure lock in
as the narrator says a chosen word instead of at a fixed offset. It needs a per-shot `say`
and `pip install openai-whisper stable-ts`; the word time comes from the shot's own voice
clip (Whisper-medium transcription + stable-ts alignment, averaged, first word after each
pause snapped to the detected voiced onset). If the tools are missing the render **warns
and falls back to normal timing**; a word not in the script stops the render.

- Never anchor on a TTS engine's own word-boundary events (they fire ~65 ms before the
  audible onset) and never use Whisper large-v3 transcription for it (drops words, shifts
  everything after). Measured accuracy, English caveats and the end-to-end check are in
  [docs/09](../../docs/09-number-cards-voice-mix-word-timing.md#3-word-anchored-timing).
- Opt-in on purpose: make "effects land on words" a default only after you have watched
  it on your own material.

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

For the 1-2 hero motion shots, compile a provider prompt from an approved neutral shot
contract. Prompt quality matters, but reference admission, model capability, body
mechanics and output review matter too; more words do not guarantee obedience.

One provider request should produce one continuous photographic shot. Put cuts,
shot/reverse-shot, montage, captions, transitions and final musical timing in the edit
spec, not inside a multi-shot generation prompt.

Structure (works in any language; keep the sections):

- **Style** — realism / grain / sharpness / texture / edit rhythm. Explicitly forbid
  plastic CG skin and over-smoothing.
- **Duration** and **Aspect ratio** (e.g. 9:16).
- **Scene** — environment, lighting, depth-of-field / background blur.
- **Subject / character** — bind the approved identity/look from
  [character continuity](../character-continuity/SKILL.md) and include only the detail
  needed for this shot.
- **Audio** — sound design cues if the model supports it (often you disable the model's
  audio and lay your own music/voice in post).
- **Single-shot temporal beats** — describe the start state, preparation, action/contact,
  settling and end state so they close inside the requested duration. Avoid prose that
  asks the provider to make internal cuts.
- **Action & continuity hard-constraints** — physically correct motion, no morphing, hair,
  face and wardrobe held across all frames and adjacent approved shots, no teleporting,
  changes only at the intended anchor frame.
- **Layered negatives** — write negatives in layers (action / wardrobe / camera /
  background), the more specific the less it breaks: no face swap, no extra limbs, no
  clipping, no warped objects, no garbled text or logos, no plastic CG skin, no
  over-smoothing, no cartoon, no morph transitions, no camera shake, no watermark.

For faces, bind a rights-cleared identity reference separately from wardrobe, expression,
composition and motion references. Detailed prose can help, but “strictly consistent” is
not an identity check. When emotion needs a face, specify gaze target and the causal
expression change, then inspect the entire output at normal speed and intended size.

Cost note: motion generation is expensive (often seconds-based billing), and a still
image plus local camera treatment is near-$0. Reserve i2v/t2v for shots whose story value
depends on real motion. Before submission, set an exact request-count and cost ceiling.
Never turn an unclear response, timeout or provider error into a blind paid resubmit;
save and reconcile the original task first.

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
- **R4 — step-on-lens + 90° roll reveal + hold (edit pattern).** Treat this as several
  continuous shots joined by a motivated occlusion cut, not one provider request. It is a
  "make an entrance" beat with no dialogue, carried by music + eyes + camera:
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

- **Give identity its own reference role.** Character detail belongs in a reusable
  identity/look contract. Prompt prose alone cannot prove that the same person, wardrobe,
  face geometry and accessories survived every frame.
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
- **Adopt outside techniques by measuring, not admiring.** Re-implement the idea inside this
  pipeline, measure it on your own real files, ship it opt-in, and promote it to default only
  after a human has watched/listened to A/B versions (docs/09, last section).
- **Test with small samples, don't over-attribute.** A handful of early views is noise;
  read the direction signal, not the exact number.

## Cost / discipline

Rough order of magnitude: a stills-only card video is cheap; one i2v/t2v hero shot is a
few dollars; several motion shots run higher; per-shot TTS is cents per line. Scope your
topics first and render them one at a time — don't batch-burn budget speculatively. Log
every paid call, reserve its maximum cost, and permit no automatic paid resubmit. A
provider URL reaches only `provider_complete`; after download, hashing and technical
probe, the file may become `candidate_pending_human_review`. Normal-speed review with
sound is still required. Review anything before it goes public. For a multi-shot run,
hand exact-hash approved takes to
[`video-run-control`](../video-run-control/SKILL.md) for picture lock, finish receipts,
dependency invalidation, final-master QC, and the delivery hash gate.
