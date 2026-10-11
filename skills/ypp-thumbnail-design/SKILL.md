---
name: ypp-thumbnail-design
description: Design and QC Mystory/拾得 YouTube long-form and Shorts thumbnails, using the founder-approved Sandy Lam warm human close-up as the default portrait benchmark when authentic source footage supports it. Use for YPP 封面, thumbnail, 16:9 long cover, or 9:16 Shorts cover; do not use for album artwork or abstract release covers.
---

# 拾得 YPP 封面

Every new YPP thumbnail must be made through this skill and recorded as `thumbnail_skill_invoked:true`; an ad-hoc frame grab is not a deliverable.

## Default decision

- For a named singer, actor, character, film, or MV with a suitable authentic face frame, default to the founder-approved `SL0118-S` Sandy Lam `warm-human-closeup/v1` grammar: subject/work above, one warm recognizable close-up in the middle, and one short evidence-backed hook below on a rice-paper-white box.
- Read [the Sandy Lam benchmark and contract](../youtube-ypp-demand-loop/references/thumbnail-success-benchmark.md) before using this route.
- Use the same authentic source frame for the sharp portrait and restrained blurred fill. Do not use an AI face, anonymous lookalike, unrelated collage, or a second competing image.
- If no suitable authentic close-up exists, choose another supported layout from `scripts/videogen/gen_ypp_thumbnail.py`; record why the portrait route was not possible.

## HOT_11S 拾得实时播报 (founder 2026-10-11)

- The cover must beat the YouTube top-3 Shorts on the same topic. Keep the authentic warm close-up, but make the one hook line large and high-contrast (top competitors use thick outlined headline text) so it reads first at 180 px; person recognisable at a glance.
- Score it with `scripts/videogen/hot11s_competitor_benchmark.py` (`covers.jpg` side-by-side, `cover` 0-10 with written evidence); ours must be strictly higher than the best competitor, else `HOLD_HOT11S_BELOW_TOP3_COMPETITORS` — redesign and re-measure.

## Production and QC

1. Bind the thumbnail to the current approved master version, exact source file, source timecode, and crop. A founder-supplied topic does not need an active-plan slot.
2. Generate through `scripts/videogen/gen_ypp_thumbnail.py`; long-form uses 16:9 and Shorts use 9:16. Preserve the subject as the visual focus and keep the image warm, bright, recognizable, and readable on mobile.
3. Use a rice-paper-white `#F5F1E8` text box and the official `brand_mark.py` mark tinted dark gold `#A77A2D`; never redraw the logo as plain text.
4. Generate a 180px mobile preview and require an explicit founder selection (under the 2026-10-09 daily plan autopilot the agent selects and records `selected_by: agent_daily_autopilot`) of an immutable versioned filename. Keep the compact `ypp-thumbnail-contract/v1` result inside `release-package.json`; detailed preview/QC data stays temporary. Validate with `scripts/videogen/thumbnail_contract.py` and release-package QC.
5. Any master, source frame, crop, hook, or typography change requires a new thumbnail version and fresh QC.
6. Long and ordinary Short masters publishing on/after 2026-10-13 must open on the selected cover: run `scripts/videogen/burn_opening_cover.py burn` (1.0 s opaque hold + 0.3 s dissolve, overlaid so the timeline is unchanged) and record `opening_cover_burned:PASS`. The exact-11-second route is exempt.

Fail with `HOLD_THUMBNAIL_SKILL_NOT_INVOKED` when this skill was not actually used, and `HOLD_THUMBNAIL_CONTRACT` when source, mobile preview, version binding, or founder selection is incomplete.
