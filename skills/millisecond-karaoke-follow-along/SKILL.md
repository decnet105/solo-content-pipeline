---
name: millisecond-karaoke-follow-along
description: Enforces real-time millisecond-precision karaoke follow-along highlighting across all TokyoFlow long-form (16:9) masterclasses and vertical shorts (9:16). Prohibits static/blank text during Japanese audio playback.
---

# Millisecond Karaoke Follow-Along Highlighting Skill

## Overview
This skill governs the visual rendering and audio synchronization of Japanese dialogue and drill playback across all TokyoFlow video productions (16:9 Long-Form Masterclasses and 9:16 Vertical Shorts, in both English Column A and Chinese Column B).

Every video package MUST feature active, real-time karaoke highlighting synchronized with native Tokyo Japanese audio (`ja-JP-NanamiNeural`) down to millisecond precision. Static, unhighlighted cards during Japanese speech playback are strictly prohibited.

## Core Visual Architecture

### 1. 3-Tier Multi-Line Dialogue Card Layout
Every dialogue card consists of:
- **Top Tier (Furigana / Kana)**: Accent or reading support in amber/gold (`(180, 83, 9)`).
- **Middle Tier (Main Kanji / Kana)**: Primary Japanese sentence in dark slate (`(15, 23, 42)`) on white/frosted background, font size 36-42px.
- **Bottom Tier (Hepburn Romaji)**: Pronunciation guide in muted slate (`(100, 116, 139)`).
- **Multi-Line Natural Segmentation**: Long Japanese sentences (35-45 characters) MUST be segmented into natural syntactic clauses across 2 to 3 lines to fit comfortably within the 1720px horizontal bounding box without overflow or text clipping.

### 2. Real-Time Karaoke Glow & Bouncing Mora Indicator
During audio playback of native Japanese (`dialogue.mp3`, `slow.mp3`, `drill_jp.mp3`):
- **Active Glowing Capsule**: The currently spoken token receives an active glowing rounded capsule (`fill=(254, 240, 138)`, `outline=(245, 158, 11)`, `width=3`) spanning all three tiers.
- **Red Bouncing Mora Dot**: A red indicator circle (`(220, 38, 38)`) bounces directly above the active token's center (`dot_cx = curr_x + tok_w // 2`) to guide learner cadence and pitch timing.
- **Anticipatory Lead Time**: An 80ms anticipatory lead (`t_start - 0.08s`) is applied to token timestamps so the visual focus leads human eye movement slightly ahead of speech initiation.

### 3. Whisper Millisecond Alignment Pipeline
1. Pass the Japanese audio file and token list through Whisper (`base` or `small` model) with `word_timestamps=True` and `initial_prompt=sentence_text`.
2. Map word-level timestamps to structured tokens using exact character sequence accumulation.
3. Compute exact start and end timestamps for each token in seconds.
4. During video rendering, map elapsed frame timestamp `t = frame_index / fps` against token timings. When `token.start <= t <= token.end`, mark `active_token_index`.

### 4. Frame Caching & High-Performance Video Piping
- Because each dialogue sentence contains $N$ tokens, there are only $N + 1$ discrete visual states ($N$ active token states + 1 idle state).
- Pre-render and cache the $N + 1$ composite RGB frames in memory.
- Pipe cached raw frame bytes (`proc.stdin.write(state_frames[active_idx])`) directly into ffmpeg via stdin. This delivers 200-400+ FPS rendering speeds while ensuring 100% frame-perfect millisecond karaoke highlights.

## Quality Control Enforcements
- Every release package must be verified by `tokyoflow_qc_engine.py` for millisecond karaoke video stream generation.
- Static, unhighlighted dialogue segments during speech playback trigger QC deductions.
