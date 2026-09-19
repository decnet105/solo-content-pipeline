# 09 · Number cards, a voice-first music mix, and word-anchored timing

Three small upgrades to the unglamorous parts of a short — the figure card,
the music bed under the narrator, and *when* things happen relative to the
words. Each one was built natively in this pipeline and **measured on real
renders** before it was allowed to become a default. The last section is the
method, because it is the part worth copying.

Everything here is in `scripts/` and works from a plain spec field. None of it
costs an API call.

---

## 1. A number card that moves: the split-flap reveal

A number card is the trust layer of a fact short: the figure is drawn locally
(never by an image model, which garbles digits). It is also the flattest beat
in the video. A mechanical departure-board flip — each digit rolling up and
locking in — gives that beat motion, and the contrast (an old analog mechanism
landing on a precise, modern figure) is the point.

```json
{
  "key": "depth",
  "primary": "Almost eleven kilometres down.",
  "say": "The deepest point in the ocean is almost eleven kilometres down.",
  "number_card": { "label": "Deepest point", "number": "10935", "unit": "metres down", "source": "Challenger Deep, approx." }
}
```

`number_card` is now the standard way to show a figure; `animate` defaults to
`"splitflap"`, and `"animate": "static"` gives the old flat card. You can also
render one by hand:

```bash
python3 scripts/gen_splitflap_card.py output/cards/depth.mp4 \
  --label "Deepest point" --number 10935 --unit "metres down" --source "Challenger Deep, approx."
```

**How it works.** Every digit is a cassette that steps through `0 … target`;
non-digit characters (a `%`, a letter, a unit glyph) flip once from a blank
cassette; spaces are gaps. Frames are drawn with PIL and piped straight into
ffmpeg as an opaque libx264 mp4, which `make_short.py` then uses like any other
`clip`. Cassettes lock in left to right.

**Why it is safe as a default.** A card must never end on a half-flipped
digit, however short the shot is, so:

- a row wider than the frame shrinks its font automatically (`--num-size` is
  only an upper bound);
- the flip is capped at 60% of the shot (1–3 s); if it would not fit, flip
  time and stagger are compressed proportionally, never below two frames per
  flip, so it still reads as a flip;
- cassettes that never move (the trailing zeros of `1200`) are not counted as
  flip time;
- a float tolerance on the final frame prevents a permanent seam line across
  the last digit (a bug we hit while building it, now guarded).

**Font note.** The default serif renders old-style figures on some systems
(the `0` looks like a small `o`). For a number card you usually want lining
figures: point `VIDEOGEN_FONT` at a font that has them, and at one with CJK
glyphs if your unit or label is Chinese/Japanese/Korean. The palette at the
top of the script is an example; change it to yours.

---

## 2. Keep the music out of the voice band

**The problem.** Flat ducking (a sidechain compressor on the whole music
track) lowers every frequency by the same amount. But speech is understood in
roughly the 500 Hz – 3 kHz band. A bed that is "12 dB ducked" overall can
still be as loud as the narrator *exactly there* — and that is the band older
viewers lose first.

**Measure it, don't guess.** `scripts/measure_voice_band.py` re-mixes a
rendered spec's own intermediates twice (legacy flat ducking, and the voice
carve below) and prints how many dB the narration sits above the music in
500 Hz – 3 kHz, as a median over the speech frames:

```bash
python3 scripts/measure_voice_band.py path/to/spec.json     # needs numpy, scipy, soundfile
```

What we saw:

- Across 30 already-shipped shorts from our own (private) pipeline, the gap
  had a **median of +7.5 dB**; 7 of the 30 were below +6 dB and the worst had
  the music *louder* than the narrator in that band (−4.0 dB). Re-mixed with
  voice carve the same 30 came out at a **median of +15.8 dB**, worst +4.7 dB.
- On the starter pipeline in this repo, one real music track under a 25-second
  narration: **+1.3 dB with flat ducking → +12.2 dB with voice carve.**
- Rule of thumb: above about +10 dB is comfortable; below about +6 dB the bed
  is competing with the voice.

**The fix ("voice carve", on by default).** The music is split into low / mid
/ high with a 4th-order Linkwitz-Riley crossover (250 Hz and 4.2 kHz). Only the
mid band is compressed hard against the narration (ratio 12, threshold 0.02,
6 ms attack, 380 ms release); low and high are only nudged (ratio 1.5), so the
bed keeps its warmth and air. The music is delayed 30 ms so the compressor is
already closing when a syllable starts. Numbers are in `CARVE_DEFAULTS` in
`scripts/make_short.py`.

In a spec:

```json
"music": { "file": "assets/bed.mp3", "carve": true, "gain_db": -3 }
```

- `carve` — omit for the default (on); `false` restores flat ducking (then
  `bgm_ducking_db` applies again — with carve on it does not); an object
  overrides individual tuning values, and an unknown key raises an error
  instead of being ignored.
- `gain_db` — the bed's static level before ducking.
- The legacy path is preserved exactly: with `carve: false` the audio track is
  **bit-identical** to what the previous version produced (we checked the
  decoded-audio MD5), so old specs can be re-rendered unchanged.

**How the default was chosen.** Three settings (old / default / stronger)
were rendered from the same narration and bed and *listened to*; the
default was picked by ear. The measurement tells you which renders are at risk;
the ears decide the setting.

**Caveats.** The metric is a band-RMS ratio — a proxy, not STI/STOI, and not a
substitute for listening. One narration and one track is an illustration, not
a survey.

---

## 3. Word-anchored timing

**The problem.** You want the figure to lock in *as the narrator says
"twelve hundred"*, not at a fixed offset that drifts every time the script or
the voice changes. Because every shot's `say` line is its own voice clip, the
clip can be analysed on its own — the missing piece is *when, inside the clip,
a chosen word starts.*

```json
"number_card": { "number": "1200", "unit": "dollars",
                 "at_word": "twelve hundred", "at_mode": "settle" }
```

- `at_word` — the word or phrase to anchor to (must appear in the shot's
  `say`). `at_word_nth` picks the 2nd, 3rd … occurrence.
- `at_mode` — `"settle"` (default): the last digit locks in as the word
  starts, so the flip is already underway just before it; `"start"`: the flip
  begins on the word.
- Needs a per-shot `say`. Set `voice.language` (a Whisper language code, default
  `"en"`) to the language the narrator really speaks, or `number_card.at_lang` per
  shot.
- Optional install: `pip install openai-whisper stable-ts numpy` (the medium
  model is a download of about 1.5 GB; a clip takes a few seconds on a laptop CPU, and
  the result is cached by audio-content hash, so re-renders are instant).
- If the tools are missing or a clip can't be aligned, the render **warns and
  falls back to the normal timing** instead of failing. A word that is not in
  the script is a spec error and stops the render.
- To just see a word's time: `python3 scripts/word_anchor.py say_x.mp3 "the exact script" --word paycheck --lang en`.

**What we measured** (on 40 real Mandarin narration clips — 526 word onsets,
three TTS voices — using the TTS engine's word boundaries, shifted +64 ms, as
ground truth; details below on why the shift):

- Spread the script evenly over the clip: p95 error 412 ms — unusable.
- Pause detection + punctuation only (no ML): median 40 ms, p95 153 ms, 81% within 100 ms.
- Whisper-medium forced alignment: median 29 ms, p95 149 ms (the first word after a pause runs late, p95 241 ms).
- Whisper-medium transcription with your script as the prompt: median 29 ms, p95 160 ms.
- **Average of the last two, then snap each phrase's first word to the detected voiced onset (what ships): median 22 ms, p95 about 106 ms, 94% within 100 ms.**

The chosen method never missed by more than 300 ms in that set. Two things it
deliberately avoids:

- **Don't use the TTS engine's word-boundary events as anchors.** The ones we
  measured fire about 65 ms *before* the audible onset (we checked against the
  voiced onset after a pause). Everything here is computed from the waveform.
- **Don't use Whisper large-v3 transcription for this.** On the same clips 13.5%
  of words were more than 300 ms off (worst case 6 s) because it drops words
  and shifts everything after them, and its forced alignment was consistently
  ~117 ms early. Medium was better *for this job*.

**English.** On 20 English lines (231 words, three neural TTS voices) the same code
agrees with the engine's boundaries at a median of +96 ms — what you would
expect from the ~65 ms boundary lead plus a small late bias — with a p95
spread of 149 ms after removing 64 ms, and nothing beyond 300 ms. The
Mandarin study had an independent audible-onset check for phrase-initial words;
English did not, so treat the English numbers as weaker evidence.

**End to end.** Measuring the *final mp4* frame by frame (when do the digits
stop changing vs. when the word is spoken), the card landed **+19 / +111 /
+32 ms** from the spoken word on Mandarin and **+55 / +126 / +75 ms** on English —
always slightly late, which is the direction a viewer forgives most, and
within about four frames at 30 fps. The +111 ms one was a word in the middle of
a phrase, where alignment has no pause to snap to.

**Why it is opt-in.** It adds a heavy optional dependency and a few CPU-seconds
per clip. And "the effect happens on the word" is a taste decision, not an
accuracy one — make it the default only after you have watched it on your own
material. The same anchor could drive subtitle emphasis, a B-roll cut or a
sound effect; that is not built.

---

## 4. How these three were chosen: learn it natively, then measure it

This is the reusable part. When a tool or framework does something impressive:

1. **Read it for the technique, don't adopt the sandbox.** Work out *what idea*
   produces the effect (here: band-limited ducking, a mechanical-reveal
   animation, word-level timestamps).
2. **Re-implement it inside the pipeline you already have**, at its smallest
   useful size — no second runtime, no new hosted service, nothing that
   changes how the rest of the pipeline runs.
3. **Measure on your own real files**, not on the vendor's demo: your shipped
   videos, your narration, your voices. Write down the metric first. If no
   number moves on your data, drop it — that is a result too.
4. **Ship it opt-in.** Old specs must still render identically (check the
   output, not the code).
5. **Promote to default only after a human has looked or listened** to
   A/B versions, and keep a one-line opt-out.
6. **Write down what you did *not* verify.** The caveats above are as much a
   part of the result as the numbers.
