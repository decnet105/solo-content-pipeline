# Solo Content Pipeline

**A starter kit + guide for building your own automated content pipeline by _directing_ an AI coding agent — even if you can't code.**

Turn a single JSON file into a finished vertical short: AI-generated images, video, music, and voiceover, stitched together with subtitles and cinematic transitions. Plus a set of reusable "skills" that encode how to write social posts and replies that don't sound like a robot.

I'm a solo builder, not a professional programmer. I described what I wanted to an AI coding agent, looked at what came out, said "no, more like this," and repeated until it worked. This repo is the result — and a guide so you can do the same.

> The leverage here is **clear communication + taste + iteration**, not coding skill. If you can describe what a good video looks like, you can build this.

---

## What you'll build

- **One spec, one video candidate.** Write (or edit) a `spec.json` describing your shots, narration, and music. Run one command. Get a rendered `.mp4` candidate; final delivery still requires review of the exact output.
- **AI assets, on demand.** The pipeline calls out to AI providers for images, short video clips, background music, and a voiceover — only for the pieces you don't already have.
- **A way to learn from other people's videos, too.** Point a separate tool at any competitor or reference video and get a structured, eleven-dimension teardown — hook, retention, pacing, color, music, copy, and more — with an explicit adopt/skip filter, not just admiration.
- **Reusable "skills."** Small instruction files that teach a coding agent _your_ standards — how to write a post, preserve a recurring character, study a reference, tear down a competitor's video, build a video, review paid AI motion, and control a run end to end — so it does not re-learn them from scratch.

## Who this is for

- Beginners and non-programmers who can clearly describe what they want.
- Creators who want to automate the boring parts of short-form content.
- Anyone curious what one person can build by directing an AI agent well.

You do **not** need to know Python, JavaScript, or ffmpeg. You need a Mac, a few API keys, and patience to iterate.

---

## 60-second Quickstart

**Prerequisites** (see [docs/01-getting-started.md](docs/01-getting-started.md) for the hand-holding version):

- macOS with [Homebrew](https://brew.sh)
- Node.js, Python 3, and ffmpeg
- API keys for four provider categories: image generation, text-to-video, music, and text-to-speech

```bash
# 1. Clone
git clone https://github.com/decnet105/solo-content-pipeline.git
cd solo-content-pipeline

# 2. Install tools (once)
brew install node python ffmpeg

# 3. Set your API keys (never commit these — see docs/01)
export IMAGE_API_KEY="..."
export VIDEO_API_KEY="..."
export MUSIC_API_KEY="..."
export VOICE_API_KEY="..."

# 4. Make a video from the example spec
python3 scripts/make_short.py examples/example-spec.json
```

When it finishes you'll have a rendered vertical-short candidate in `output/`. Open it, review the exact file, see what you'd change, edit the spec, and run it again.

---

## Repo map

- `scripts/make_short.py` — the conductor. Reads a spec, generates or reuses each asset, renders subtitles and number cards, and stitches everything with ffmpeg.
- `scripts/gen_image.mjs` — calls an image-generation API for a still.
- `scripts/gen_video.mjs` — calls a text/image-to-video API for a short clip.
- `scripts/gen_music.mjs` — calls a music-generation API for a backing track.
- `scripts/gen_voice.mjs` — calls a text-to-speech API for narration.
- `scripts/gen_number_card.py` — draws a crisp "big number" card locally (no AI — AI can't render exact numbers cleanly).
- `scripts/deconstruct_video.py` — fetches a competitor or reference video (URL or local file) and produces dense frame samples, a contact sheet, and a timestamped manifest for a teardown.
- `examples/example-spec.json` — a complete, runnable spec you can copy and edit.
- `examples/prompts/example-t2v.txt` — a director-style prompt for a text-to-video shot.
- `skills/video-pipeline/SKILL.md` — how to drive the video pipeline.
- `skills/video-pipeline/references/ai-motion-production.md` — the fail-closed contract for real generated motion, paid-task recovery, reference roles and exact-output review.
- `skills/video-run-control/SKILL.md` — end-to-end artifact lineage, picture lock, finishing receipts, invalidation, and the final human hash gate.
- `skills/video-run-control/references/run-manifest-contract.md` — the generic run-manifest contract behind that control skill.
- `skills/character-continuity/SKILL.md` — identity/look, expression, hands, props and recurring-character continuity.
- `skills/reference-video-study/SKILL.md` — evidence-first reference study and single-variable experiments (for reproducing a specific technique in your own generation pipeline).
- `skills/video-deconstruct/SKILL.md` — the eleven-dimension competitor/reference-video teardown: hook, retention, pacing, color, music, copy, subtitles, emotional arc, resonance, plus the evidence-chain discipline and adoption filter that feed lessons back into your own skills.
- `skills/video-deconstruct/references/deconstruct-framework.md` — the full checklist, report template, and do-not-copy list behind that skill.
- `skills/social-post/SKILL.md` — how to write a post that doesn't read as AI.
- `skills/social-reply/SKILL.md` — how to reply in a community without getting flagged.
- `docs/` — the tutorials below.

## Learning from a competitor's video

The kit isn't only for generating video — it also ships a tool for the
opposite direction: breaking down someone else's already-published video to
learn *why* it works, instead of just admiring it.

```bash
python3 scripts/deconstruct_video.py "https://example.com/their-video" \
  --out output/deconstruct/their-video \
  --extract-audio
```

This fetches the source (yt-dlp for a URL — it respects whatever access
controls and terms apply, so it never bypasses a login, paywall, CAPTCHA, or
anti-bot protection; a local file is used as-is) and writes into the output
folder:

- `frames/` — densely sampled stills (2fps by default, capped so a long video
  doesn't produce thousands of images)
- `contact-sheet.jpg` — every sampled frame tiled into one image, so you can
  scan a video's entire rhythm at a glance before reading anything frame by
  frame
- `frames.json` / `frames.csv` — a timestamped manifest of every sampled frame
- `audio.mp3` (with `--extract-audio`) — mono 16kHz audio, useful for a
  transcription pass

The script only gathers evidence — it draws no conclusions. From there, hand
the contact sheet, key frames, and manifest to your coding agent (or read them
yourself) and work through the
[`video-deconstruct` skill](skills/video-deconstruct/SKILL.md): score the
video across eleven dimensions — hook, first-15% retention, shot pacing,
transitions, color grade, music, copy, split-screen use, subtitle typography,
emotional arc, and audience resonance — while keeping a strict line between
what you **observed** (a timestamped fact), what you're **inferring** (your
read of why, which can be wrong), and what's still **untested**.

The report itself isn't the point. The skill's actual output is an explicit
**adopt / skip / why** decision for every technique, judged against your own
brand and audience rather than copied just because it worked for theirs, with
at least one lesson written back into your own production skills so you don't
relearn it on the next reference video. It is structural learning, not asset
reuse: never take their soundtrack as your own background music (content-ID
systems catch this even inside a transformative edit), and don't reuse an
identifiable face, voice, account handle, platform UI, or watermark. The full
checklist, evidence-chain convention, and do-not-copy list live in
[`skills/video-deconstruct/references/deconstruct-framework.md`](skills/video-deconstruct/references/deconstruct-framework.md);
the step-by-step walkthrough is in
[docs/07](docs/07-competitor-video-teardown.md), including how to move it into
a different project or niche — with either Claude Code or OpenAI Codex CLI —
without copying anything that's specific to this kit.

## Docs

- [01 · Getting started](docs/01-getting-started.md) — install everything, get your keys, run the example.
- [02 · The video pipeline](docs/02-video-pipeline.md) — the spec format, the generate-or-reuse trick, cinematic prompts, and how to keep costs low.
- [03 · Social content](docs/03-social-content.md) — the two writing "skills" and the reality of posting in communities.
- [04 · How this was built](docs/04-how-this-was-built.md) — the meta story: how a non-coder built all of this by directing an agent.
- [05 · Production quality loop](docs/05-production-quality-loop.md) — the difference between moving a still and real animation, plus reference roles, task recovery, motion/character gates and output QC.
- [06 · End-to-end run control](docs/06-end-to-end-run-control.md) — artifact DAGs, selected-take picture lock, OTIO/color/audio receipts, invalidation, and exact-master delivery approval.
- [07 · Tearing down a competitor's video](docs/07-competitor-video-teardown.md) — how to run the teardown tool, work the eleven dimensions, and turn "here's what they did" into an adopt/skip decision that actually updates your own production practice.

## How it was built (teaser)

Every script here was written by an AI coding agent that I directed in plain English. I never opened a blank code file. I described outcomes, ran the result, pointed at what was wrong, and iterated — and whenever I learned a lesson, I had the agent save it as a reusable skill file so it would never forget. The full story (and a playbook you can copy) is in [docs/04-how-this-was-built.md](docs/04-how-this-was-built.md).

## Costs & providers (honest note)

This pipeline calls **paid** AI APIs. Every image, video clip, music track, and voiceover generation costs real money — usually cents, but text-to-video can add up fast (it's often priced per second). The scripts are deliberately **provider-agnostic**: they read your keys from environment variables, so you plug in whichever image / video / music / speech providers you like. Tips for keeping the bill small are in [docs/02](docs/02-video-pipeline.md#cost-tips). Never hard-code or commit a key — the `.gitignore` already blocks the usual suspects.

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, ship your own.

---

## 中文速览 (TL;DR)

- 这是一套「用 JSON 造竖屏短视频」的开源起步套件：写一个 spec 文件，跑一条命令，AI 出图/出片/配乐/配音，自动拼成候选片；正式交付仍需对最终文件做精确人审。
- 我不是程序员——整套脚本都是我用大白话「指挥」AI 编程助手写出来的，看结果、说哪里不对、反复迭代。
- 还附带可复用的「技能」文件，覆盖社媒写作、角色连续性、参考片取证、真正 AI 动画的费用与任务恢复，端到端成片的版本、总装和最终 hash 人审，以及一套**拆解分析竞品/参考视频**的技能——抓帧出联系单+时戳清单后，按钩子/前15%留存/节奏/转场/调色/BGM/文案/字幕/情绪弧/共鸣等十一维拆解，证据必分「观察到的事实/自己的推断/待验证」三档，每条技法给出用/不用的独立判断（不因为对方有效就照搬），并至少把一条心得写回自己的技能文件，见 [skills/video-deconstruct](skills/video-deconstruct/SKILL.md) 与 [docs/07](docs/07-competitor-video-teardown.md)。
- 核心不是会写代码，而是**把想要的效果讲清楚 + 有审美 + 肯迭代**。完整故事见 [docs/04](docs/04-how-this-was-built.md)。
