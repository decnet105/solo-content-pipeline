# 07 · Tearing down a competitor's video

Every other doc in this kit is about *making* a video. This one is about the
opposite direction: learning from someone else's, so you stop reinventing
technique from scratch every time you see something that works.

```bash
python3 scripts/deconstruct_video.py "https://example.com/their-video" \
  --out output/deconstruct/their-video \
  --extract-audio
```

That's the whole tool. It fetches the source — yt-dlp for a URL (respecting
whatever access controls and terms apply; it does not bypass a login,
paywall, CAPTCHA, or anti-bot protection), or a local file used as-is — and
writes into the output folder:

- `frames/` — densely sampled stills, 2fps by default, capped so a
  ten-minute video doesn't produce thousands of images (`--fps` and
  `--max-frames` control this).
- `contact-sheet.jpg` — every sampled frame tiled into one image. Look at this
  first: you can see a video's whole rhythm — where the cuts cluster, where it
  slows down, where the color shifts — before reading anything frame by frame.
- `frames.json` / `frames.csv` — a timestamped manifest, one row per sampled
  frame, so you can cite an exact second in your notes instead of eyeballing
  it.
- `audio.mp3` (with `--extract-audio`) — mono 16kHz, enough for a
  transcription pass if you want the narration or dialogue in text.

The script's job stops there. It gathers evidence; it does not decide whether
a hook is good or whether a transition fits your brand. That's
[the `video-deconstruct` skill](../skills/video-deconstruct/SKILL.md).

## Doing the actual teardown

Hand the contact sheet, a handful of key frames, and the manifest to your
coding agent (or open them yourself), then work through the eleven dimensions
in
[`references/deconstruct-framework.md`](../skills/video-deconstruct/references/deconstruct-framework.md):
hook, first-15% retention, shot pacing, transitions, color grade, music,
copy, split-screen use, subtitle typography, emotional arc, and audience
resonance. For each one you're writing down two different kinds of notes and
must not blur them together:

- what you actually **observed** — "at 0:03 it cuts to a close-up of the
  hands, captioned in bold sans-serif" — a checkable fact tied to a timestamp;
- what you're **inferring** — "I think the close-up is there to make the
  motion legible before the wide shot" — your read of *why*, which might be
  wrong, and which you should never write down as if it were established
  fact.

Anything you can't settle from the video alone — "would our audience respond
to this the way theirs did," "can we actually reproduce this transition in
ffmpeg" — goes in a third bucket: untested. It's fine, even expected, for a
teardown to end with open questions.

## The part that actually matters: the adoption filter

The teardown itself is not the deliverable. A list of "here's what they did"
is trivia. The deliverable is a decision, technique by technique: **adopt,
skip, or why** — checked against your own positioning, your own palette
rules, your own established voice, and your own audience, not against how
well the technique worked for the source's audience and goal.

A video optimized for impulse purchases and a video optimized for watch-time
retention are not chasing the same outcome. A transition that reads as
exciting on a fast-cut product ad can read as a jarring mismatch on a slower,
warmer piece — copying it because "it clearly worked for them" skips the
actual judgment call. The skill's do-not-copy checklist exists for exactly
this: conversion mechanics that don't match your model, effects that clash
with your visual identity, anything that leans on urgency or anxiety you
wouldn't otherwise use — these get a default "skip" unless you have a
specific reason to override it.

## Feed it back or it didn't happen

The last step is the one it's easiest to skip: write at least one concrete
line into wherever the lesson will actually get reused — a note in
`video-pipeline`'s prompt guidance, an addition to your subtitle-style notes,
an entry in a music-brief library, a line in a hook-writing checklist. A
teardown that changes nothing about how you make your next video was a
research exercise, not a production input. If you can't name the one file
that gets updated, the teardown isn't finished yet.

## Adapting this to a different project or niche

Nothing here is Claude-specific. `SKILL.md` and `deconstruct-framework.md` are
plain Markdown, and `deconstruct_video.py` is a standalone script — any coding
agent that can read a file and run a shell command can follow this, including
[OpenAI's Codex CLI](01-getting-started.md), which this kit's own setup guide
lists as an interchangeable alternative to Claude Code. Tell your agent "read
`skills/video-deconstruct/SKILL.md` and its framework
reference, then tear down `<competitor URL>`" and it works the same way
regardless of which agent you picked. If you're on Codex CLI and want it
loaded automatically instead of pasted in every time, add one line to your
project's `AGENTS.md` pointing at the skill file — Codex reads that file on
its own.

Moving this into someone else's project (a different niche, a different
platform, a different audience) needs almost no changes:

- The six-step loop, the eleven dimensions, the evidence-chain labels, and the
  sampling script all transfer as-is — they were never specific to this kit's
  content style.
- Exactly two things are project-specific and need rewriting, not copying:
  the **"decide" clause** in each dimension (it references *your* palette
  rules, *your* established voice, *your* audience — a cooking channel and a
  finance channel will decide differently even when they observe the same
  technique) and the **do-not-copy checklist** (a different niche has
  different techniques it should default to rejecting). Have the agent ask a
  few questions first — what's the niche, the visual identity, the typical
  video length and tone, the actual audience — and write the answers directly
  into that project's copy of `deconstruct-framework.md`, the same way
  [`gen_number_card.py`](../scripts/gen_number_card.py) ships with an example
  palette commented "customize for your brand" instead of leaving it
  unstated.
- Point step 6 (feed back) at wherever *that* project's production skill or
  script actually lives — this kit's `video-pipeline` is just this kit's name
  for it.

One thing should not change when you adapt this: the rights and identity
boundary below. "Don't reuse their soundtrack, face, voice, or watermark" is a
copyright and platform-policy line, not a brand preference, and it holds
regardless of niche.

## What this is not

This is not a way to acquire assets. Never take the source's actual
soundtrack and use it as your own background music — platform content-ID
systems catch this even inside a heavily edited, transformative piece.
Don't reuse an identifiable face, voice, account handle, platform UI chrome,
or watermark; you're learning structure, not borrowing identity. And don't
repeat an unverified on-screen claim as fact in your own script just because
a popular video said it with confidence — mark it untested and either verify
it or leave it out.

If a finding is worth showing the actual source clip to explain (a specific
transition, a specific composition), keep that use transformative and check
you actually have the right to publish it before it goes anywhere public —
the same exact-output review gate that governs a finished production applies
here too. See
[`ai-motion-production.md`](../skills/video-pipeline/references/ai-motion-production.md)
and [`video-run-control`](../skills/video-run-control/SKILL.md) for how that
gate works.
