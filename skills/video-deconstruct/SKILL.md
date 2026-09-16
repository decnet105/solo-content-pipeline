---
name: video-deconstruct
description: >
  Deconstruct a competitor's or reference creator's published video into a
  growth-and-craft teardown across eleven dimensions — hook, early retention,
  pacing, transitions, color, music, copy, split-screen use, subtitle
  typography, emotional arc, and audience resonance — then judge each
  technique against your own brand before feeding lessons back into your
  production skills. Use when asked to reverse-engineer, "break down," or
  learn from someone else's already-published video for technique. Do not use
  this to reproduce, republish, or pass off the source video or its assets as
  your own.
---

# Video deconstruct (competitor/reference teardown)

Tear a published video apart to learn *why* it works, decide which mechanisms
are actually worth adopting, and update your own skills so the lesson sticks.
**This is a learning loop, not a production step** — it does not generate or
publish anything.

This is a different job from
[`reference-video-study`](../reference-video-study/SKILL.md), which does
forensic, parameter-level reverse engineering of one shot or effect to
reproduce it in your own AI generation pipeline. Use this skill instead when
the question is about a whole published video's growth mechanics — why does
it hook, retain, and resonate — not how one specific effect was technically
produced. The two chain naturally: a teardown here can flag a shot worth a
deeper technical study there.

## One command

```bash
python3 scripts/deconstruct_video.py <url-or-file> --out output/deconstruct/<name> --extract-audio
```

Fetches the source (yt-dlp for a URL, respecting whatever access controls and
terms apply; a local file is used as-is) → dense frame sampling (2fps by
default, capped so a long video doesn't produce thousands of images) → a
contact sheet + timestamped frame manifest, and optionally an extracted audio
track for transcription. The script only gathers evidence — an agent (or you)
does the actual teardown from what it produces.

## When to use

Someone hands you a link or file and says "break this down" / "figure out why
this works" / "what should we learn from this." Run this skill to produce a
teardown report plus an explicit adoption decision, then write at least one
line back into a production skill or reference doc so the lesson doesn't have
to be relearned next time.

## The six-step loop

1. **Acquire** — pull the source only through channels its terms and access
   controls actually allow; a local file is used directly. Record the source
   URL, creator attribution, and the date you accessed it.
2. **Sample** — dense, uniform sampling reviewed as a set via the contact
   sheet, not one frame at a time. Look closer around cuts, the opening
   seconds, and anything that looks like a deliberate effect.
3. **Tear down dimension by dimension** — read the contact sheet, key frames,
   and frame manifest (plus a transcript or captions if available), and score
   each of the eleven dimensions in
   [`references/deconstruct-framework.md`](references/deconstruct-framework.md).
4. **Separate the evidence chain** — for every claim, mark it
   ✅ *observed* (a timestamped fact), 💡 *inferred* (your read of why, which
   can be wrong), or ⏳ *untested* (needs an experiment or a call only a human
   can make). Never present an inference as a fact.
5. **Filter independently** — this is the actual point of the exercise, not a
   formality. For every technique, decide **adopt / skip / why**, judged
   against your own positioning, palette rules, established voice, and
   audience — not against how well it worked for the source's audience and
   goal, which may not be yours.
6. **Feed back** — write the adopted lessons into wherever they'll actually be
   reused: `video-pipeline` defaults, a subtitle-style note, a music-brief
   library, a hook-writing checklist. A teardown that changes nothing in your
   own production practice was wasted effort — every run should produce at
   least one concrete update.

## Eleven dimensions

Hook (first second) · first-15%-retention mechanism · shot pacing ·
transitions · color grade · music (genre / impact / arc / sync points) · copy
(hook line / payoff / comment bait / information density) · split-screen or
multi-frame composition · subtitle typography · emotional arc · audience
resonance (why *your* audience specifically would react, not audiences in
general). What to look at, what to ask, and how to judge fit for each
dimension is in the framework reference below.

## Rights and identity boundary

You are studying structure and technique, not acquiring assets:

- Never use the source's actual soundtrack as your own background music —
  content-ID systems match it even inside a transformative edit.
- Don't reuse an identifiable face, voice, account handle, platform UI chrome,
  or watermark. Structure is fair game; identity is not.
- Don't repeat an unverified on-screen claim as fact just because a popular
  video stated it — flag it as ⏳ untested instead.
- If a finding requires showing or quoting the actual source clip, keep that
  use transformative and verify you have the right to publish before anything
  goes public — see the exact-output review gate in
  [`ai-motion-production.md`](../video-pipeline/references/ai-motion-production.md)
  and [`video-run-control`](../video-run-control/SKILL.md) for how a finished
  piece actually gets cleared.

## Authoritative sources

- [`references/deconstruct-framework.md`](references/deconstruct-framework.md)
  — the eleven dimensions in full, the evidence-chain convention, the report
  template, and a do-not-copy checklist.
- `scripts/deconstruct_video.py` — the fetch-and-sample tool (yt-dlp + ffmpeg,
  no other dependencies).
- Feed findings into `video-pipeline`, your subtitle/typography notes, your
  music-brief library — wherever the lesson needs to live so it isn't
  relearned on the next reference video.
