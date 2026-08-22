# Solo Content Pipeline

**A starter kit + guide for building your own automated content pipeline by _directing_ an AI coding agent — even if you can't code.**

Turn a single JSON file into a finished vertical short: AI-generated images, video, music, and voiceover, stitched together with subtitles and cinematic transitions. Plus a set of reusable "skills" that encode how to write social posts and replies that don't sound like a robot.

I'm a solo builder, not a professional programmer. I described what I wanted to an AI coding agent, looked at what came out, said "no, more like this," and repeated until it worked. This repo is the result — and a guide so you can do the same.

> The leverage here is **clear communication + taste + iteration**, not coding skill. If you can describe what a good video looks like, you can build this.

---

## What you'll build

- **One spec, one video.** Write (or edit) a `spec.json` describing your shots, narration, and music. Run one command. Get a finished `.mp4`.
- **AI assets, on demand.** The pipeline calls out to AI providers for images, short video clips, background music, and a voiceover — only for the pieces you don't already have.
- **Reusable "skills."** Small instruction files that teach a coding agent _your_ standards — how to write a post, how to reply in a forum without getting flagged, how to build a video — so it never re-learns them from scratch.

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

When it finishes you'll have a finished vertical short in `output/`. Open it, see what you'd change, edit the spec, run it again.

---

## Repo map

- `scripts/make_short.py` — the conductor. Reads a spec, generates or reuses each asset, renders subtitles and number cards, and stitches everything with ffmpeg.
- `scripts/gen_image.mjs` — calls an image-generation API for a still.
- `scripts/gen_video.mjs` — calls a text/image-to-video API for a short clip.
- `scripts/gen_music.mjs` — calls a music-generation API for a backing track.
- `scripts/gen_voice.mjs` — calls a text-to-speech API for narration.
- `scripts/gen_number_card.py` — draws a crisp "big number" card locally (no AI — AI can't render exact numbers cleanly).
- `examples/example-spec.json` — a complete, runnable spec you can copy and edit.
- `examples/prompts/example-t2v.txt` — a director-style prompt for a text-to-video shot.
- `skills/video-pipeline/SKILL.md` — how to drive the video pipeline.
- `skills/social-post/SKILL.md` — how to write a post that doesn't read as AI.
- `skills/social-reply/SKILL.md` — how to reply in a community without getting flagged.
- `docs/` — the tutorials below.

## Docs

- [01 · Getting started](docs/01-getting-started.md) — install everything, get your keys, run the example.
- [02 · The video pipeline](docs/02-video-pipeline.md) — the spec format, the generate-or-reuse trick, cinematic prompts, and how to keep costs low.
- [03 · Social content](docs/03-social-content.md) — the two writing "skills" and the reality of posting in communities.
- [04 · How this was built](docs/04-how-this-was-built.md) — the meta story: how a non-coder built all of this by directing an agent.

## How it was built (teaser)

Every script here was written by an AI coding agent that I directed in plain English. I never opened a blank code file. I described outcomes, ran the result, pointed at what was wrong, and iterated — and whenever I learned a lesson, I had the agent save it as a reusable skill file so it would never forget. The full story (and a playbook you can copy) is in [docs/04-how-this-was-built.md](docs/04-how-this-was-built.md).

## Costs & providers (honest note)

This pipeline calls **paid** AI APIs. Every image, video clip, music track, and voiceover generation costs real money — usually cents, but text-to-video can add up fast (it's often priced per second). The scripts are deliberately **provider-agnostic**: they read your keys from environment variables, so you plug in whichever image / video / music / speech providers you like. Tips for keeping the bill small are in [docs/02](docs/02-video-pipeline.md#cost-tips). Never hard-code or commit a key — the `.gitignore` already blocks the usual suspects.

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, ship your own.

---

## 中文速览 (TL;DR)

- 这是一套「用 JSON 造竖屏短视频」的开源起步套件：写一个 spec 文件，跑一条命令，AI 出图/出片/配乐/配音，自动拼成成片。
- 我不是程序员——整套脚本都是我用大白话「指挥」AI 编程助手写出来的，看结果、说哪里不对、反复迭代。
- 还附带几个可复用的「技能」文件，教 AI 按你的标准写社媒帖子和回复，不带 AI 腔。
- 核心不是会写代码，而是**把想要的效果讲清楚 + 有审美 + 肯迭代**。完整故事见 [docs/04](docs/04-how-this-was-built.md)。
