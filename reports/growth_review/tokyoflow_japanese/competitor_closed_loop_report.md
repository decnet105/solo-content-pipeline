# Daily Competitor Benchmark & Closed-Loop Retention Audit · tokyoflow_japanese
> **Audit Date**: 2026-11-08 16:58:28 UTC | **Channel**: `tokyoflow_japanese`

## 1. Top 3 Competitor Outlier Scan & Reverse-Engineering Ratings

| Rank | Competitor Channel | Subscribers | Median Views | Top Outlier Title | Outlier X | Overall Score |
| :---: | :--- | :---: | :---: | :--- | :---: | :---: |
| #1 | **けんさんおかえり Japanese** | 221,000 | 42,977.5 | *1 Hour Easy Japanese Listening 🇯🇵 | Learn N5 ...* | **3.41x** | `87.0 / 100` |
| #2 | **Speak Japanese Naturally** | 525,000 | 36,753.0 | *Going to a Supermarket and Making Dinner | Ja...* | **4.98x** | `89.8 / 100` |
| #3 | **Mochi Real Japanese** | 327,000 | 12,036.0 | *Difference between あげる、もらう、くれる🇯🇵* | **3.89x** | `87.8 / 100` |

### Detailed Dimension Scores (Scale 1-10)

| Dimension | Top #1 Score | Top #2 Score | Top #3 Score | Benchmark Avg | Our Current Score | Gap Delta | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Cold Open Hook** | 8.9 | 9.4 | 9.1 | **9.1** | 6.2 | `+2.9` | **HIGH** |
| **Visual Dynamics** | 8.8 | 8.8 | 8.8 | **8.8** | 5.2 | `+3.6` | **CRITICAL** |
| **Information Cadence** | 7.5 | 8.0 | 7.5 | **7.7** | 7.5 | `+0.2` | **MODERATE** |
| **Packaging Thumbnail** | 9.0 | 9.5 | 9.2 | **9.2** | 5.8 | `+3.4` | **CRITICAL** |
| **Narrative Arc** | 8.8 | 8.8 | 8.8 | **8.8** | 7.0 | `+1.8` | **HIGH** |
| **Sound Engineering** | 9.2 | 9.2 | 9.2 | **9.2** | 8.8 | `+0.4` | **MODERATE** |

**Overall Score Gap**: Our Channel `65.2` vs Competitor Benchmark `88.1` (Net Deficit: **`-22.9 pts`**)

---

## 2. Root Cause Attribution & Physical Metric Discrepancies

| Metric | Current Measured Baseline | Competitor Benchmark Target | Corrective Action Directives |
| :--- | :---: | :---: | :--- |
| **Static Frame Ratio** | `89.3%` | `≤ 65.0%` | Enforce Ken Burns pan/zoom and dynamic subtitles to cut static ratio < 0.65 |
| **Thumbnail Words** | `44 words` | `≤ 6 words` | Slash cover text from 44 words down to <= 6 words with bold high-contrast font |
| **Mobile Legibility (168x94)** | `0.17` | `≥ 0.60` | Enforce contrast ratio >= 4.5:1 and 168x94 mobile preview OCR pass |
| **First 30s Visual Cuts** | `1` | `≥ 5` | Inject at least 5 visual shot changes in the first 30 seconds |

---

## 3. Next-Episode Retention Upgrade Directives

```json
{
  "channel_id": "tokyoflow_japanese",
  "target_episode": "EP21",
  "generated_at": "2026-11-08T16:58:28.853562+00:00",
  "target_score_goal": 95.0,
  "directives": {
    "cold_open_hook_0_30s": {
      "action": "ABSOLUTE_ZERO_GREETING_RULE",
      "instruction": "Cut all host greetings. At 0.0s, cut directly into situational crisis or dramatic dialogue contrast.",
      "cognitive_gap": "Contrast real Tokyo native phrasing with textbook awkwardness within 15 words.",
      "first_cut_timing_sec": 1.2
    },
    "visual_dynamics_engine": {
      "max_static_ratio": 0.65,
      "min_first_30s_visual_changes": 5,
      "max_avg_shot_length_sec": 3.5,
      "ken_burns_enabled": true,
      "karaoke_highlight_glow": true
    },
    "information_cadence": {
      "target_wpm": 145,
      "micro_pause_sec": 0.35,
      "monolingual_tts_chunking": true,
      "voice_separation_discipline": "Nanami_JP_Only; Andrew_EN_Only"
    },
    "sound_engineering": {
      "voice_band_carve_db": -12.0,
      "loudness_target_lufs": -16.0,
      "sub_bass_transient_hz": 42
    },
    "packaging_mobile_shield": {
      "max_words": 6,
      "min_legibility_score": 0.6,
      "distinct_multilingual_layout": true,
      "dhash_min_hamming_distance": 12
    },
    "asset_retention_loop": {
      "companion_pdf_drive_pinned": true,
      "outro_passcode_gate": true,
      "related_video_card": true
    }
  },
  "qc_gate_enforcement": {
    "min_passing_score": 99.0,
    "auto_repair_enabled": true,
    "fail_closed_policy": "STRICT_BLOCK_UPLOAD"
  }
}
```

---

## 4. Autonomous Closed-Loop Self-Healing Guarantee
1. **Pre-Upload QC Verification**: Before publishing, `scripts/videogen/tokyoflow_qc_engine.py` executes 12 rigorous checkpoint validations.
2. **Auto-Repair Trigger**: If static frame ratio exceeds 0.70 or thumbnail legibility < 0.55, the auto-healing compiler cuts additional B-roll and resynthesizes covers.
3. **Zero-Defect Release Barrier**: Passing score \ge 99.0 is non-negotiable. Sub-99 packages are blocked from upload.