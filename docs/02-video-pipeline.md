# 02 · The Video Pipeline

This is the heart of the kit: a single command that turns one JSON file into a finished vertical short.

```bash
python3 scripts/make_short.py examples/example-spec.json
```

The script (`make_short.py`) is the **conductor**. It reads your spec, makes sure every asset the video needs actually exists (generating the missing ones by calling the AI APIs), records each shot's narration, draws your subtitles, then hands the whole shot list to ffmpeg to animate, transition, and encode into one `.mp4`. The output path is whatever you put in the spec's `out` field.

You never touch the code. You edit the spec. Understanding the spec _is_ understanding the pipeline.

The rest of this page walks through `examples/example-spec.json` — the runnable "3 ocean facts" demo — field by field. Everything here is copied straight from that file, so the docs and the example can't drift apart. Copy it, change the words, run it again.

---

## The spec, top to bottom

Here is the complete demo spec. Read it once for shape, then we'll go through it piece by piece.

```json
{
  "name": "ocean-facts",
  "out": "output/ocean-facts.mp4",

  "brand_intro": true,
  "intro": {
    "title": "3 things\nyou didn't know\nabout the ocean",
    "subtitle": "a 30-second dive",
    "dur": 2.6
  },

  "music": {
    "prompt": "calm cinematic ambient underwater, soft felt piano and slowly swelling strings, gentle 80 BPM, spacious and hopeful, no drums, instrumental",
    "start": 0.0,
    "instrumental": true
  },

  "voice": { "voice_id": "audiobook_male_2", "speed": 1.0 },

  "shots": [
    {
      "key": "deep",
      "primary": "The deepest point is 11 km down.",
      "say": "The ocean's deepest point plunges almost eleven kilometers, deeper than the tallest mountain is high.",
      "image": {
        "gen": "photorealistic deep ocean trench, shafts of blue light fading into darkness, tiny particles drifting, wide cinematic underwater shot, no text, no watermark"
      },
      "motion": "in",
      "mode": "cover",
      "emotion": "neutral"
    },
    {
      "key": "oxygen",
      "primary": "Half your oxygen comes from the sea.",
      "say": "Here's the wild part. Every second breath you take comes from the ocean, made by microscopic drifting plankton.",
      "image": {
        "gen": "photorealistic sunlit ocean surface seen from just below the waterline, golden light rays, floating plankton particles, serene, cinematic, no text, no watermark"
      },
      "motion": "out",
      "mode": "cover",
      "emotion": "happy"
    },
    {
      "key": "unexplored",
      "primary": "We've mapped less than a quarter of it.",
      "say": "And most of it is still a mystery. We have mapped more of the moon than our own sea floor.",
      "image": {
        "gen": "photorealistic sonar-style map of a dark unexplored ocean floor, faint glowing topographic contour lines, moody deep blue, cinematic, no text, no watermark"
      },
      "motion": "panL",
      "mode": "cover",
      "emotion": "neutral"
    }
  ],

  "brand_outro": true,
  "outro": {
    "title": "Follow for more",
    "subtitle": "one small fact a day",
    "cta": "Save this for later",
    "dur": 2.4
  },

  "publish": {
    "title": [
      "3 ocean facts that sound fake (but aren't)",
      "The ocean is weirder than you think"
    ],
    "hashtags": "#Shorts #ocean #science #didyouknow",
    "category": "Education",
    "language": "English"
  }
}
```

### Top-level fields

- `name` — a short, file-safe label for this video (no spaces or slashes). It names the working cache folder and the publish package.
- `out` — where the finished `.mp4` is written, e.g. `"output/ocean-facts.mp4"`. This is the path the run command produces.
- `brand_intro` — `true` to show the opening text card described in `intro`; `false` to skip it so your first real shot is the cold open.
- `intro` — the opening text card: `title` (use `\n` to force line breaks), `subtitle`, and `dur` (seconds on screen). It's a plain paper card built from your text — there's no bundled logo or branding.
- `music` — one backing track for the whole video (see [Music](#music) below).
- `voice` — the default narrator for every shot's `say` line: `voice_id`, `speed`, and an optional `emotion` (see [Voice and narration](#voice-and-narration)).
- `shots` — the body of the video, an ordered list (see [A shot](#a-shot)).
- `brand_outro` — `true` to show the closing card described in `outro`; `false` to end on the last shot.
- `outro` — the closing text card: `title`, `subtitle`, a `cta` line, and `dur`.
- `publish` — metadata for the auto-generated publish notes file (see [The publish package](#the-publish-package)).

A few optional top-level fields don't appear in the demo but are worth knowing:

- `transitions` — override the shot-to-shot transitions (see [Transitions](#transitions)). Omit it to use the built-in default set.
- `sfx` — a list of sound effects to layer in (see [Sound effects](#sound-effects)).
- `end_logo` — optional corner branding: `{ "logo": "path/to/logo.png", "cta": "your line" }`, faded onto the last shot. Omit it to run brand-free.
- `bgm_ducking_db` — how hard to push the music down under narration, in dB (default `-12`; a bigger number ducks harder).

### A shot

Each entry in `shots` is a few seconds of screen time. The fields:

- `key` — a short unique id (`deep`, `oxygen`…). It labels the shot and is how its generated assets are cached (see [The generate-or-reuse resolver](#the-generate-or-reuse-resolver-why-re-runs-are-cheap)).
- `primary` — the main on-screen subtitle line.
- `secondary` — an optional second-language subtitle shown smaller beneath `primary` (great for bilingual reach — both languages on the **same** frame, not two separate exports).
- `say` — the narration for this shot. The pipeline sends this text to the text-to-speech API, lays the resulting voice under the shot, **and sizes the shot to the length of that voice line** (plus a small tail). That's why narrated shots don't set a duration. Omit `say` for a silent shot — but then you must give the shot a `dur`.
- `dur` — seconds on screen. Usually omitted, because a shot with `say` is timed to its narration. Set it explicitly only for a silent shot.
- A **visual source** — exactly one of `image`, `clip`, or `seedance` (see [The kinds of visual](#the-kinds-of-visual) below).
- `motion` — the Ken Burns camera move applied to a still: `"in"`, `"out"`, `"panL"`, or `"punchin"` (defaults to `"in"`).
- `mode` — how the picture fills the vertical frame: `"cover"` fills and crops (default); `"fit"` shrinks to fit and pads the edges.
- `emotion` / `speed` — optional per-shot overrides for the narrator on this line (e.g. `"emotion": "happy"` for the upbeat fact). They override the top-level `voice` defaults.
- `pad` — optional extra seconds held after the voice line ends (default `0.5`).

---

## The kinds of visual

Every shot shows one thing. This choice is also your main cost lever.

### 1. `image` — a generated or supplied still (cheap)

Two ways to fill a shot with a still:

```json
"image": { "gen": "a prompt describing the picture" }
```

```json
"image": { "src": "assets/my-photo.png" }
```

- `gen` — the pipeline generates the still from this prompt the first time and caches it. This is what all three demo shots use.
- `src` — point at an image file you already have (a photo, a screenshot, or a number card — see below). It's used as-is and never generated.

To give a still a presentation move, set the shot's `motion` field:

- `"in"` / `"out"` — a slow push in or pull out.
- `"panL"` — a slow drift across the frame.
- `"punchin"` — a quick punch in that settles.

This "Ken Burns" treatment is done entirely by ffmpeg and costs nothing extra. It remains
a moving still, not character animation. It is a good default for fact cards, documents,
landscapes, timing drafts and other shots whose meaning does not depend on body or facial
performance.

### 2. `clip` / `seedance` — real motion video (expensive, save for heroes)

For a shot that genuinely moves, use one of these instead of `image`:

```json
"clip": "assets/my-hero-clip.mp4"
```

```json
"seedance": { "prompt": "director-style motion description", "face_free": true }
```

- `clip` — the path to a motion `.mp4` you already have. The pipeline drops it straight in. An optional `clip_ss` on the shot sets a start offset (seconds) into that clip.
- `seedance` — generate a few seconds of motion from the shot's still via an image-to-video model. It animates the still produced by that same shot's `image` (so give the shot an `image` too, as the first frame). The `prompt` is a director-style motion description (see [Director-style prompts](#director-style-prompts)). A returned clip is a review candidate, not automatic proof of natural motion or continuity.

Generated motion is the most impressive and the most expensive part — often billed per second of output. Rule of thumb: **one, maybe two motion shots per video** — a hero opener or a payoff moment. Everything else is stills.

> The current starter uses `face_free` as a conservative routing switch. With
> `"face_free": false`, it skips generation and falls back to a Ken Burns still. That
> fallback avoids spending on a risky face, but it does not turn the still into real
> acting. For character-led animation, use approved identity/motion references and the
> production loop in [docs/05](05-production-quality-loop.md), then review the whole clip.
> The included `seedance` path currently sends one start image for a fixed four-second
> request and has no multi-reference or durable task ledger, so it is not the executor for
> that character-production contract.

### 3. Number cards — a crisp on-screen number (free, and important)

If your content has a key statistic, **do not** ask an image model to render the number — image models smear digits into gibberish. Instead, render the number cleanly with local text rendering, then use it as a shot's still.

A number card is **not** a spec field. It's a two-step workflow:

1. Draw the card with the standalone tool:

   ```bash
   python3 scripts/gen_number_card.py --number 384400 --unit km \
     --label "average distance" --out assets/card.png
   ```

   (Other options: `--source "NOAA"` for a small credit line, `--num-size 340` to resize the figure.)

2. Reference the PNG it produced as that shot's still, via `image.src`:

   ```json
   {
     "key": "distance",
     "primary": "About 384,400 km away.",
     "say": "On average, it's about three hundred eighty-four thousand kilometers away.",
     "image": { "src": "assets/card.png" },
     "motion": "in",
     "mode": "fit"
   }
   ```

The result is free, razor-sharp, and on-brand. Any time a figure, date, or label matters, make it a number card and reference it with `image.src`.

---

## The generate-or-reuse resolver (why re-runs are cheap)

This is the single most important behavior to understand. For every asset a shot needs, the conductor either **uses a file you supplied** or **generates one and caches it**:

- A `src` (image), a `clip` path, or a `music.file` points at a file you already have. It's used as-is. Cost: nothing.
- A `gen` prompt, a `seedance` block, a `music.prompt`, or a `say` line has no file yet, so the matching API is called. The result is written into the working cache folder `tmp/videogen/spec-<name>/`, keyed by the shot's `key`.
- On the **next** run, if that cached file already exists, it's reused instead of regenerated.

So your **first** run of a spec generates everything and costs money. Every run after that is nearly instant and nearly free, because the assets are cached on disk.

To **change one shot**, edit that shot and delete its cached file in `tmp/videogen/spec-<name>/` (for example `img_<key>.png` or `say_<key>.mp3`), or give the shot a new `key`. Next run regenerates only that one asset; everything else is reused. Delete the whole `tmp/videogen/spec-<name>/` folder only when you want a fresh start. This is what makes iterating feel fast and cheap instead of scary and expensive.

This is a file-existence cache, not strict request idempotency: changing prompt, voice or
model text does not necessarily invalidate a file whose shot key stayed the same. For a
paid video task, separately save an immutable input digest, request ID, provider task ID,
cost and downloaded-file hash. If submission status is unclear, reconcile that original
task rather than submitting it again.

---

## Music

```json
"music": {
  "prompt": "mood + instrument + tempo + length, instrumental",
  "start": 0.0,
  "instrumental": true
}
```

One track for the whole video, generated once (from `prompt`) and cached like everything else — or supply your own with `"file": "assets/track.mp3"` instead of `prompt`. Fields:

- `prompt` — describe the _feeling_ and the _instrumentation_ (as in the demo). Give an approximate length a little longer than your video.
- `file` — use this instead of `prompt` to bring your own track.
- `start` — seconds into the track to start from, so you can align its energy peak to a key shot.
- `instrumental` — keep it wordless so lyrics don't fight the narration.

The conductor trims the track to the video's length, fades it out at the end, and ducks it under the voiceover so narration stays clear (see `bgm_ducking_db`).

---

## Voice and narration

The narrator is set once at the top level and can be nudged per shot:

```json
"voice": { "voice_id": "audiobook_male_2", "speed": 1.0 }
```

- `voice_id` — which voice to use. Render a couple of short samples and pick one before committing to a full render.
- `speed` — talking speed (`1.0` is normal).
- `emotion` — an optional acting cue for the delivery.

Each shot's `say` line is spoken in this voice, and **the shot's on-screen time is set to the length of that spoken line** (plus the shot's `pad`). Because every line is voiced and subtitled per shot, the picture, the narration, and the captions stay naturally in sync. Set `emotion` or `speed` on an individual shot to act that one line (upbeat during a fun fact, softer at a reflective beat).

---

## Transitions

By default the pipeline applies a built-in, varied set of transitions between shots, so you don't have to specify anything — the demo omits transitions entirely. To take control, add a top-level `transitions` array of `[type, duration]` pairs, one per cut (a video with N segments has N−1 cuts; the intro and outro cards count as segments):

```json
"transitions": [
  ["zoomin", 0.28],
  ["smoothleft", 0.20],
  ["fadewhite", 0.14],
  ["smoothup", 0.20]
]
```

If you give fewer pairs than there are cuts, the default set is cycled to fill the rest. Available transition types:

- `zoomin` — a quick zoom into the next shot. Energetic.
- `smoothleft` / `smoothright` — a smooth slide in from the side.
- `smoothup` — a smooth slide up.
- `fadewhite` — a brief white flash. Good for a reveal or a beat change.
- `hblur` — a horizontal blur wipe.

Match transitions to your music. A flash or slide landing on a musical hit feels intentional; the same transition on a random frame feels sloppy.

---

## Sound effects

An optional top-level `sfx` list layers sound effects onto the narration timeline. Each entry anchors a file to a shot by its `key`:

```json
"sfx": [
  { "file": "assets/whoosh.wav", "at_shot": "oxygen", "offset": 0.0, "vol": 0.8 }
]
```

- `file` — the sound file.
- `at_shot` — the `key` of the shot to anchor to.
- `offset` — seconds to nudge relative to that shot's start.
- `vol` — playback volume (default `0.8`).

Because a subtle effect gets buried under music, the pipeline ducks the music under the combined voice and SFX track.

---

## The publish package

After rendering, the conductor writes a plain-text publish notes file next to your video (`<out>.publish.md`) with title candidates, a description, tags, and upload options. The `publish` block feeds it:

- `title` — an **array** of title candidates to choose from.
- `description` — the post body.
- `hashtags` — a single string of hashtags, e.g. `"#Shorts #ocean #science"`.
- `tags` — a list of keyword tags.
- `category`, `language`, `playlist` — upload metadata.

Everything here is optional; sensible defaults are derived from your `intro` title and narration when a field is missing. Review anything before it goes public.

---

## Director-style prompts (for `seedance` shots)

Image-to-video models reward concrete, filmable instructions over a keyword salad. Compile
one continuous photographic shot per provider request; keep cuts, montage, transitions,
captions and final musical timing in the edit spec. The example in
`examples/prompts/example-t2v.txt` follows this basic structure — describe, in order:

1. **Subject** — what's in frame. ("A weathered lighthouse on a rocky headland.")
2. **Action / motion** — what moves, and how. ("Slow push-in; low mist drifts over a calm sea.")
3. **Camera** — shot size and movement. ("Low aerial push, gentle handheld float, shallow depth of field.")
4. **Lens & look** — focal feel and film character. ("Anamorphic, subtle film grain, muted teal-and-amber grade.")
5. **Lighting** — source, direction, quality. ("First warm dawn light breaking the horizon.")
6. **Mood** — the emotional tone in a word or two. ("Quiet, hopeful, cinematic.")

Concrete, physical, filmable language beats adjectives. "Slow push-in, dawn light raking across the wet rock" gives the model something to do; "beautiful amazing epic 4K" does not. Put this text in the shot's `seedance.prompt`. More detail or repeated instructions still do not prove provider obedience; measure and review the returned file.

A good habit: don't hand-write these. Ask a strong "director" model (your coding agent, or a capable text model) to _write the prompt for you_ from a one-line brief — "write me a cinematic image-to-video prompt for a quiet dawn lighthouse reveal." Taste in picking the best of a few options beats trying to author the perfect prompt yourself. More on that in [docs/04](04-how-this-was-built.md).

---

## Cost tips

Generated motion video is where budgets die. Keep the bill small:

- **Default to stills + Ken Burns for card/fact formats.** A strong still with a slow push costs a fraction of a video clip. Do not use it as a substitute when the story depends on character acting, contact or real movement.
- **Reserve `seedance` (or a supplied `clip`) for one or two hero moments** per video — the opener or the payoff. Not every shot needs to move on its own.
- **Number cards are free.** Any figure, date, or label should be a number card referenced via `image.src`, never an AI-rendered image.
- **Lean on the cache deliberately.** Once an asset looks right, preserve it and its input record. When changing a shot, invalidate only its cache key/file and never assume prompt edits were detected automatically.
- **Keep motion shots short.** Since video is usually billed per second, a 3–4 second hero clip costs half of an 8-second one. Cut to a still before the motion overstays.
- **Prototype with stills, then add the hero.** Get your timing, narration, and subtitles right with cheap stills first; add the one expensive `seedance` shot last, once the structure is locked.

Do the math before a big batch: roughly, `(number of motion shots) × (seconds each) × (per-second price)` is the part that matters; stills, cards, one music track, and short voice lines are rounding errors by comparison.

Set a maximum request count and cost before submitting. A timeout, ambiguous response or
provider URL is not permission to pay again. Provider completion means the file is ready
to inspect; only a normal-speed review of the exact downloaded hash can accept it.

---

## Where to go next

- Want to write posts and replies to go with your videos? See [docs/03 · Social content](03-social-content.md).
- Curious how a non-programmer built all of this? See [docs/04 · How this was built](04-how-this-was-built.md).
- Need recurring characters, real generated motion, reference analysis, task recovery and exact-output QC? See [docs/05 · Production quality loop](05-production-quality-loop.md).
- The `skills/video-pipeline/SKILL.md` file is the condensed version of everything above, written so a coding agent can drive the pipeline for you on request.
