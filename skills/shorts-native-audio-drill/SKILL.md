---
name: shorts-native-audio-drill
description: Enforces direct native Tokyo Japanese audio playback during Stage 3 follow-along drill in all 9:16 Shorts pipelines, eliminating silence and maximizing auditory reinforcement.
---

# Shorts Native Audio Follow-Along Drill Skill

## Overview
This skill governs the audio and visual synchronization pipeline for Stage 3 (Follow-Along / Shadowing Drill) across all TokyoFlow 9:16 Shorts (both English Column A and Chinese Column B).

## Rationale & Core Principles
1. **Zero Dead Air**: In pre-recorded video formats (YouTube Shorts), viewers cannot receive interactive microphone feedback. Silent waiting windows cause audience drop-off and feel empty.
2. **Double Native Exposure**: Playing the native Tokyo standard Japanese voice (`ja-JP-NanamiNeural`) during Stage 3 provides learners with a second auditory exposure, allowing them to shadow simultaneously with accurate rhythm, pitch accent, and mora cadence.
3. **Millisecond Visual-Audio Lock**: Stage 3 token highlights must be synchronized with the drill audio using Whisper millisecond alignment rather than linear time estimates.

## Production Specifications

### 1. Spoken Cue Narration (Stage 2 Transition)
Before the 3-2-1 countdown beeps, synthesize a crisp prompt instructing the viewer to speak along with the native voice:
- **English Column A (`en-US-AndrewNeural`)**:
  - Script: `"Now your turn! Read along with native audio in 3, 2, 1, go!"`
  - Voice Rate: `+6%`
- **Chinese Column B (`zh-CN-YunxiNeural`)**:
  - Script: `"轮到你跟读啦！跟着东京原声一起大声读，3、2、1，开口！"`
  - Voice Rate: `+6%`

### 2. Native Japanese Drill Audio (Stage 3)
- **Voice Actor**: Pure Tokyo Standard (`ja-JP-NanamiNeural`)
- **Speech Rate**: `-10%` to `-12%` (clarified, natural drill speed)
- **Pitch**: `+2Hz`
- **File Asset**: `05_jp_drill.mp3`

### 3. Whisper Alignment & Glowing Karaoke
- Pass `05_jp_drill.mp3` through Whisper timestamp extraction (`align_sentence_tokens_with_audio`) with `initial_prompt=sentence`.
- Apply 60ms anticipatory visual lead so the active token glows right as the mora begins.
- In frame rendering, set `stage_title`:
  - English: `"[STEP 3] YOUR TURN: READ ALONG WITH NATIVE AUDIO"`
  - Chinese: `"【第3步】听原声跟读：开口大声读"`

### 4. Applicable Pipelines
- `scripts/trend_radar/daily_trend_producer.py`
- `scripts/videogen/build_all_chinese_shorts.py`
- `scripts/videogen/build_all_shorts.py`
- `scripts/videogen/build_batch_english_ep12_ep19.py`
