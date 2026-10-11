---
name: authentic-scene-background
description: Enforces authentic scene photo or video background retention across all TokyoFlow long-form (16:9) and shorts (9:16) video pipelines, preventing solid/flat canvases and ensuring Last Mile-grade cinematic immersion.
---

# Authentic Scene Photo & Video Background Retention Skill

## Overview
This skill governs the visual compositing pipeline for all TokyoFlow Japanese video generation tools. Every frame rendered must incorporate authentic visual photography or motion video footage as the foundational layer, matching the high-production aesthetic established in the Last Mile masterclass.

## Core Rules

### 1. Fresh Image Generation & Absolute Non-Reuse Discipline
When producing any long-form episode, masterclass, or short:
1. Every release package and scenario MUST feature brand-new, freshly generated or newly shot authentic Tokyo photographs.
2. Strictly PROHIBITED: Hardcoding or falling back to historical static scene images (e.g. recycling `scene_yamanote_platform.jpg`, `scene_tokyo_skyline.jpg` across releases).
3. If fresh photos are needed, invoke high-resolution photorealistic asset generation (e.g. `generate_image`) with specific real-world Tokyo scene prompts (such as modern Tokyo sunny classroom, library, study cafe, Omotesando, Roppongi, Shinjuku) and store them under the active package or dedicated release asset directory.
4. Check for episode-specific authentic photo `news_bg.jpg` in `docs/youtube_releases/{package_id}/`.
5. NEVER initialize a blank solid canvas `Image.new("RGB", (w, h), color)` without compositing an authentic photorealistic base image.

### 2. Compositing Parameters
- **16:9 Long-Form**:
  - Resize & crop to 1920x1080 (focus at 58% center-right).
  - Apply contrast enhance 1.15x, color enhance 1.18x.
  - Apply cosine alpha gradient on the left side (0 to 1200px) with `(8, 12, 22)` dark tone.
  - Apply bottom vignette (y=850..1080) for footer/CTA readability.
  - Translucent HUD cards with crisp 2-3px borders and high-contrast typography.
- **9:16 Shorts**:
  - Resize & crop to 1080x1920.
  - Apply dark top gradient (y=0..280) and bottom gradient (y=1500..1920).
  - Central HUD cards rendered with semi-transparent dark container `(24, 24, 37, 230)` or `(30, 41, 59, 230)` so the background scene remains clearly perceptible.

### 3. Pipeline Integration Check
- `multilingual_video_producer.py`: Pass `bg_image_path` to all frame rendering routines (`render_follow_along_frame`, `render_breakdown_frame`, `render_static_intro_slide`, `render_outro_slide`).
- `build_all_shorts.py` & `build_all_chinese_shorts.py`: Load `news_bg.jpg` per episode, process 9:16 crop, and render frames on top of the background image.
- `slide_designer.py`: Maintain base photo compositing with cosine shading.
- `weekend_cinema_producer.py`: Maintain continuous movie action stream under RGBA transparent HUD.
