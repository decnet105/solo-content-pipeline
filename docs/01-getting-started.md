# 01 · Getting Started

This is the slow, hand-holding version. It assumes you've never used a terminal seriously and you don't write code. That's fine — that's exactly who this was built for. Take it one box at a time. If something errors, jump to [Troubleshooting](#troubleshooting) at the bottom; almost every first-timer hits one of those.

Everything here is for **macOS**. Windows and Linux can work too, but the commands differ and the video tooling is fussier — Mac is the smooth path.

---

## Step 0 · The one tool that changes everything: an AI coding agent

You will not be writing code. You'll be _talking to_ a coding agent that writes and fixes code for you, right inside your terminal. Install **one** of these — they're interchangeable for everything in this repo:

- **Claude Code** — Anthropic's coding agent CLI.
- **OpenAI Codex CLI** — OpenAI's coding agent CLI.

Pick whichever you already have an account for. Both can read this repo, run the scripts, look at the errors, and fix them while you describe what you want in plain English. Throughout these docs, "the agent" means whichever one you chose.

Follow the official install instructions for the one you pick (a web search for its name plus "install" lands you there). Once installed, you start it by opening the Terminal app, going into this project folder, and running its command (e.g. `claude` or `codex`). You'll know it worked when it greets you and waits for you to type.

> **Why this matters:** if you get stuck on _any_ step below, you can literally paste the error into the agent and say "I'm following a setup guide and hit this — what do I do?" It's your safety net for the whole process.

---

## Step 1 · Install the plumbing (Homebrew, Node, Python, ffmpeg)

**Homebrew** is the "app store for command-line tools" on Mac. Open the **Terminal** app (find it with Spotlight: press Cmd+Space, type "Terminal") and paste this, then press Return:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

It may ask for your Mac password (you won't see characters as you type — that's normal). When it's done, install the three tools this pipeline needs:

```bash
brew install node python ffmpeg
```

- **Node.js** runs the small API-caller scripts (the `.mjs` files).
- **Python 3** runs the main conductor script and the number-card drawer.
- **ffmpeg** is the video engine that stitches, animates, and encodes everything.

Verify they're all there:

```bash
node --version
python3 --version
ffmpeg -version
```

Each should print a version number. If any says "command not found," see [Troubleshooting](#troubleshooting).

---

## Step 2 · Get the project onto your Mac

If you were handed a link to this repo, clone it (replace the URL with the real one):

```bash
git clone <this-repo-url> solo-content-pipeline
cd solo-content-pipeline
```

`cd` means "change into this folder." From now on, run every command **from inside this folder**. If you close Terminal and come back, do `cd` into the project again first.

---

## Step 3 · Get your API keys

The pipeline itself is free and open. The **AI generations cost money**, and to buy them you need an account and an API key from each of four provider categories:

- **Image generation** — makes the still pictures.
- **Text-to-video** — turns a prompt or a still image into a few seconds of motion.
- **Music generation** — makes a short backing track.
- **Text-to-speech (voice)** — reads your narration aloud.

You can start with fewer — for example, images + music + voice, and skip text-to-video entirely (it's the most expensive part, and static images with motion look great; see [docs/02](02-video-pipeline.md#cost-tips)).

Each provider gives you a long secret string — that's your **API key**. Treat it like a password. Anyone who has it can spend your money.

### Storing keys safely (never commit them)

The safest, simplest approach: set them as **environment variables** in your terminal. Paste this (with your real keys) into Terminal before running the pipeline:

```bash
export IMAGE_API_KEY="paste-your-image-key-here"
export VIDEO_API_KEY="paste-your-video-key-here"
export MUSIC_API_KEY="paste-your-music-key-here"
export VOICE_API_KEY="paste-your-voice-key-here"
```

These last only until you close the Terminal window. To make them stick, add the same four lines to the end of your shell profile file (`~/.zshrc` on modern Macs). You can even ask the agent: _"Add these four export lines to my ~/.zshrc for me."_

**Rules that keep you safe:**

- Never paste a key into a file that lives inside the project unless that file is git-ignored. This repo's `.gitignore` already blocks `.env`, `*.key`, and any `keys/` folder — so a file named `.env` in the project root is safe to use if you prefer that over shell exports.
- Never paste a key into a chat, screenshot, or public post.
- If you ever leak one, **revoke it** in the provider's dashboard and make a new one. That's it — no lasting harm.

---

## Step 4 · Run the example

With your keys set, make the sample video:

```bash
python3 scripts/make_short.py examples/example-spec.json
```

The first run does real work: it calls the APIs to generate each image, the music, the voiceover (and a video clip if the example uses one), saves them, then renders subtitles and stitches the whole thing. Expect it to take a couple of minutes and cost a small amount. When it finishes, look in the `output/` folder for the finished `.mp4`. Open it and watch.

**The magic part:** run the exact same command again. The second time it's nearly instant and nearly free, because the pipeline **reuses** the assets it already generated instead of paying to remake them. That's the generate-or-reuse trick explained in [docs/02](02-video-pipeline.md).

---

## Step 5 · Make it yours

Open `examples/example-spec.json` in any text editor (or ask the agent to open it). Change the narration text, swap an image prompt, retitle it. Save, and run the command again. Only the pieces you changed get regenerated; everything else is reused. That fast, cheap edit loop is the whole point.

When you're ready to understand every field, read [docs/02 · The video pipeline](02-video-pipeline.md).

---

## Troubleshooting

**"command not found: brew"** — Homebrew installed but isn't on your PATH yet. It usually prints a two-line "Next steps" snippet at the end of install telling you exactly what to paste. Paste those two lines, then close and reopen Terminal. Still stuck? Paste the message to your agent.

**"command not found: node / python3 / ffmpeg"** — the `brew install` didn't finish, or the terminal is stale. Re-run `brew install node python ffmpeg`, then close and reopen Terminal so it picks up the new tools.

**"python: command not found" but python3 works** — always use `python3` (with the 3). On macOS plain `python` often doesn't exist.

**An API call fails with "401 / unauthorized / invalid key"** — the key is missing, mistyped, or has an extra space. Re-run the `export` line for that provider, and double-check you copied the whole string. Remember exported keys vanish when you close Terminal — set them again in a fresh window.

**"insufficient funds / quota / billing" error** — your provider account needs a payment method or has run out of credit. This is on the provider's side, not the script. Add credit in their dashboard.

**It generated something ugly or wrong** — that's expected on early runs. Tweak that shot's prompt in the spec, then delete the shot's cached asset in `tmp/videogen/spec-<name>/` (for example `img_<key>.png`) so it gets remade, and run again. Only that shot regenerates. Iterating on prompts is normal and the point.

**Anything else** — you have a coding agent. Copy the full error, paste it in, and say what you were trying to do. That loop — run, read the error, ask the agent, try again — is the actual skill this whole repo teaches.
