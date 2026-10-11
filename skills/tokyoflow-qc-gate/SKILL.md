---
name: tokyoflow-qc-gate
description: Automated Quality Control (QC), Pre-Upload Hook & Self-Healing Auto-Repair Engine for TokyoFlow Masterclasses and Shorts before YouTube publication. Enforces 10 mandatory checkpoints and a 99-point passing threshold.
---

# TokyoFlow Quality Control, Auto-Repair Hook & Scoring Gate Skill

## Purpose
Enforces automated pre-upload Quality Control (QC) and Self-Healing Auto-Repair across all TokyoFlow educational masterclasses (16:9) and vertical shorts (9:16) based on the Enso Shide Unified Metric System (UMS) standard.

## Pre-Upload Hook Integration
The QC engine is baked directly into the master publishing pipeline (`scripts/videogen/youtube_publisher.py`) as a mandatory pre-upload hook. Every release package is audited prior to upload. If the initial score is < 99.0, the Auto-Repair engine automatically fixes deductions (sanitizing emojis, upscaling low-res backgrounds, injecting Drive links, fixing voice separation cues) and re-evaluates until reaching >= 99.0.

## Command Execution
```bash
# Run QC verification with auto-repair (default)
python3 scripts/videogen/tokyoflow_qc_engine.py <PACKAGE_DIR> [DRIVE_URL] [LANG] [--cinema]

# Run QC verification without auto-repair
python3 scripts/videogen/tokyoflow_qc_engine.py <PACKAGE_DIR> [DRIVE_URL] [LANG] --no-repair
```

## Checkpoint Protocol & Self-Healing Actions
1. **Cover Uniqueness & HD Topic Photo**:
   - Compares MD5 hash of `thumbnail.jpg` against historical releases to prevent reuse.
   - Verifies `news_bg.jpg` resolution >= 1920x1080.
   - *Auto-Repair*: Automatically upscales sub-HD backgrounds to 1920x1080 using Lanczos filtering and re-generates compliant thumbnails with dynamic bounding boxes.
2. **Cinema / Movie Backgrounds (Last Mile Standard)**:
   - For film/drama masterclasses, ensures authentic film stills or video clips are used as the persistent bottom canvas with non-repeating cuts.
3. **Typography & Text Wrapping**:
   - Verifies text line lengths, dynamic line wrapping, and bounding box margins (`draw.textbbox`) to prevent text clipping or overflow.
4. **Strict Voice Separation Discipline**:
   - Verifies that Chinese TTS (`Yunxi`) and English TTS (`Andrew`) contain zero Japanese kana, romaji, or vocabulary.
   - *Auto-Repair*: Sanitizes explainer speech cues in spec files to remove Japanese word triggers.
5. **Study Companion PDF & Passcode Outro**:
   - Verifies that 300 DPI A4 PDF is generated and uploaded to Google Drive (HTTP 200).
   - Verifies unlock passcode is displayed in video outro slides and Google Drive download link is in descriptions & comments.
   - *Auto-Repair*: Injects verified Google Drive links and outro prompts into release metadata.
6. **Karaoke Millisecond Synchronization**:
   - Verifies token-level millisecond alignment and glowing highlight progression.
7. **Shorts Follow-Along Drill Native Audio**:
   - Verifies Stage 3 follow-along drill in 9:16 Shorts plays native Tokyo Japanese audio rather than empty silence.
8. **Shorts Master Cover Injection**:
   - Verifies first 8-10 frames contain the high-contrast 9:16 master cover.
9. **Strict Zero Emoji Policy**:
   - Zero emojis anywhere across titles, descriptions, tags, subtitles, and metadata.
   - *Auto-Repair*: Permanently strips all emoji code points with 8-digit Unicode regex.
10. **Zero Unreleased App Promotion**:
    - Zero mentions of unreleased apps or app stores.
    - *Auto-Repair*: Replaces app promo text with free companion PDF and subscription CTAs.

## Gate Criteria
- Release Gate Approved: `Overall Score >= 99.0 / 100.0`
- Any package failing post-repair (< 99.0) is automatically BLOCKED from upload.
