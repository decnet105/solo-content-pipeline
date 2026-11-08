---
name: tokyoflow-qc-gate
description: Automated Quality Control (QC), Pre-Upload Hook & Self-Healing Auto-Repair Engine for TokyoFlow and autonomous video pipelines before YouTube publication. Enforces 12 mandatory checkpoints and a 99-point passing threshold aligned with top competitor benchmarks.
---

# TokyoFlow Quality Control, Auto-Repair Hook & Competitor-Aligned Gate Skill

## Purpose
Enforces automated pre-upload Quality Control (QC) and Self-Healing Auto-Repair across educational masterclasses (16:9) and vertical shorts (9:16). Enforces rigorous quantitative thresholds reverse-engineered from Top 3 YouTube competitors to eliminate static slide retention crashes, thumbnail unreadability, and acoustic fatigue.

## Pre-Upload Hook Integration
The QC engine is executed directly before package bundling and upload (`scripts/videogen/youtube_publisher.py`). If the initial score is `< 99.0`, the Auto-Repair engine automatically fixes deductions and re-evaluates. Packages scoring `< 99.0` post-repair are **strictly blocked from release**.

## Command Execution
```bash
# Run QC verification with auto-repair (default)
python3 scripts/videogen/tokyoflow_qc_engine.py <PACKAGE_DIR> [DRIVE_URL] [LANG] [--cinema]

# Run QC verification with competitor gap analysis
python3 scripts/competitor_closed_loop_engine.py --validate-qc <PACKAGE_DIR>
```

---

## 12 Mandatory Checkpoints (Competitor-Aligned Standard)

1. **Cover Uniqueness & Perceptual dHash Distance**:
   - Computes 64-bit difference hash (`dHash`) of `thumbnail.jpg` against historical releases. Hamming distance must be `> 10` (MD5 alone is insufficient to prevent layout duplication).
   - Background resolution must be `== 1920x1080` (16:9) or `1080x1920` (9:16).

2. **Mobile Thumbnail Readability & OCR Gate**:
   - Downscales thumbnail to $168\times94\text{ px}$ (mobile feed preview size).
   - OCR word count must be `≤ 8 words`.
   - Contrast/Legibility score must be `≥ 0.55`. Layouts for different languages (EN vs ZH) must have distinct visual compositions.

3. **Visual Density & Anti-Static Frame Gate**:
   - `static_ratio ≤ 0.70` across the entire video.
   - At least `≥ 4` visual changes / camera movements in the first 30 seconds.
   - Average Shot Length (ASL) `≤ 15.0 seconds`. Zero unbroken static holds $> 25\text{s}$.

4. **Dynamic Motion & Ken Burns Telemetry**:
   - Ensures continuous subtle zoom/pan (`Ken Burns`) or parallax displacement on 2D assets to prevent eye fatigue.

5. **Strict Voice Separation & Co-Teaching Monolingual Chunks**:
   - Explainer host voices (`Yunxi` / `Andrew`) must contain zero Japanese phonetic triggers.
   - Japanese spoken segments must use native acoustic models (`Nanami` / `Keita`).
   - Isolated grammatical particles are speech-decoupled (`は` -> `wa`, `へ` -> `e`, `を` -> `o`).

6. **Audio Loudness & Voice-Band Carving**:
   - Integrated loudness strictly calibrated to `−14.0` to `−19.5 LUFS`, True Peak `≤ −1.0 dBFS`.
   - Voice-band carve: BGM frequencies between $500\text{Hz} - 3\text{kHz}$ attenuated by `≥ 10 dB` under dialogue.

7. **Karaoke Millisecond Synchronization & Word Anchors**:
   - Text highlight progression aligned to spoken audio within `±30 ms` using forced alignment (`word_anchor.py`).

8. **Shorts 0.0s First Frame Master Cover Hard-Burn**:
   - Master 9:16 title card baked into frames 0-10 (`1.0s` duration for Shorts, `1.5s` for Long form) with perceptual MAE $\le 20.0$.

9. **Companion PDF Drive Asset & Outro Passcode Loop**:
   - Unencrypted 300 DPI A4 PDF uploaded to Google Drive with verified HTTP 200 reader access.
   - Passcode clearly displayed on outro screen; direct link placed in top-level pinned comment.

10. **Strict Zero-Emoji Discipline**:
    - Zero emoji code points across title, description, tags, and onscreen graphics. High-contrast typography capsules used exclusively.

11. **Pacing Ladder & Target Duration Alignment**:
    - Video duration must strictly match channel growth phase (`6-8 min` for cold start, `8-10 min` for growth, `10-12 min` for mature, `60 min` for biweekly compilations).

12. **Sub-Bass Attention Pulse & Outro Retention Lock**:
    - Key conceptual reveals punctuated with subtle sub-bass transients ($38-45\text{Hz}$ at $-6\text{dB}$).
    - Outro cuts clean within 5 seconds of lesson conclusion with Related Video card active.

---

## Gate Criteria
- **Release Approved**: Score $\ge 99.0 / 100.0$
- **Blocking Defect**: Score $< 99.0$ automatically halts pipeline and invokes self-healing auto-repair.
