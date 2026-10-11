---
name: jlpt-masterclass-pipeline
description: Standardized production pipeline and QC discipline for TokyoFlow JLPT 1-Hour Masterclasses and Shorts (Bimodal English and Chinese).
---

# TokyoFlow JLPT Masterclass Production Pipeline & Quality Standard

This skill codifies the complete standard operating procedure (SOP) for producing 1-hour JLPT Masterclasses (16:9 Long-Form, ~50-60 mins) and accompanying 9:16 Shorts, across both English (Column A) and Chinese (Column B) editions.

## 1. Core Production Standard & Fixed Architecture

- **Visual Tone**: Light & Engaging Study Aesthetic (轻松明亮备考风). Never flat black or dark canvases. Must feature authentic photographs of Japanese students studying in Tokyo (classrooms, libraries, study cafes).
- **Typography**: Apple PingFang SC (Semibold for titles/kanji, Regular for explanations) with multi-level fallbacks. Dynamic text wrapping and bounding box calculation to prevent clipping.
- **5-Stage Pedagogical Flow**:
  1. Japanese native (`ja-JP-NanamiNeural`) reads question stem TWICE.
  2. 5-second pure silent thinking countdown (`anullsrc`, dynamic 5s -> 1s HUD). No dead air, no oral drill.
  3. Japanese native reveals correct answer with golden glowing card and green 正解 badge.
  4. 4-Option Analysis Grid: Full breakdown for all 4 choices (Translation + Correct/Incorrect Tag + In-depth Reason why it is right or wrong + Core grammar formula).
  5. Example sentence read TWICE with Whisper millisecond karaoke highlight + 4 key vocabulary cards read TWICE with card highlight.
- **Strict Voice Separation Discipline**:
  - English explainer (`en-US-AndrewNeural`) or Chinese explainer (`zh-CN-YunxiNeural`) must NEVER pronounce Japanese words, kana, or romaji.
  - All Japanese words and sentences are 100% exclusive to Tokyo standard native (`ja-JP-NanamiNeural`).
- **Cover Burn-in Discipline**:
  - 16:9 Masterclass: Burn first-frame master cover (`thumbnail.jpg`) for exactly **1.5 seconds**.
  - 9:16 Shorts: Burn first-frame vertical cover (`short_thumbnail.jpg`) for exactly **1.0 second**.
- **External URL Traffic Policy**:
  - Never place direct external download links (Google Drive, Dropbox, etc.) inside YouTube video descriptions (to avoid algorithmic shadowbanning/traffic restriction).
  - Always place study companion PDF download links inside the **Pinned Comment** (`pinned_comment.txt`). Video description only directs viewers: "Download link available in pinned comment! Passcode: TOKYOFLOW".

## 2. Release Configuration & Publishing Matrix

| Dimension | Column A (English Edition) | Column B (Chinese Edition) |
| :--- | :--- | :--- |
| **Package Name** | `JLPT_N5_Mega_Masterclass_1Hour-v1.0-en` | `JLPT_N5_Mega_Masterclass_1Hour-v1.0-zh` |
| **Japanese Audio** | `ja-JP-NanamiNeural` | `ja-JP-NanamiNeural` |
| **Explainer Voice** | `en-US-AndrewNeural` | `zh-CN-YunxiNeural` |
| **16:9 Playlist** | `PLHUEYGzrBe-s` | `PLVchR4TmK56E` |
| **9:16 Shorts Playlist**| `PLVxXRTmSmcAM` | `PLTpb6FPYqYC4` |
| **JLPT N5 Column** | `PLY_ZLcqTrnU8` | `PLPBpfF_GX60Q` |
| **Publish Time** | 08:00 AM EDT | 08:00 AM EDT (per schedule request) or 20:00 EDT |
| **Subscriber Notification** | `notifySubscribers = True` | `notifySubscribers = False` |
| **Study PDF Passcode** | `Passcode: TOKYOFLOW` | `下载口令：TOKYOFLOW` |
| **PDF Placement** | Pinned Comment (Zero links in description) | Pinned Comment (Zero links in description) |

## 3. Automation Engines

- Question Bank Builder: `scripts/videogen/build_jlpt_n5_bank_*.py`
- Production Pipeline: `scripts/videogen/jlpt_n5_masterclass_producer.py`
- Timing & Alignment Engine: `scripts/videogen/timing_engine.py` (Whisper base + pykakasi)
- Quality Control Gate: `scripts/videogen/tokyoflow_qc_engine.py` (100.0 / 100.0 score required)
- QC Exception Waiver Ledger: `scripts/videogen/qc_waivers.json`
