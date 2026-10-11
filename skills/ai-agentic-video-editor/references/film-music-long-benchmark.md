# 电影／音乐人物横版长片标杆

本合同源于创始人确认通过的 `TM1001-L`《甜蜜蜜》《新不了情》v9。它约束以后新制或返工中的电影／音乐人物横版长片；不能只复制片尾样式而忽略文字、原声、配乐、口播或 QC。

`TM1001-L` v9 的精确 SHA-256 为 `887620c3ad5d72669aa4014b5d571b230807fcca838581c54b3c286866c67f75`。该母版按确认时版本保留 3 秒翻牌，不追溯重渲；自 2026-09-27 起的新制作固定执行 4.0 秒翻牌。

## 生产合同

0. 主题必须逐字取自 active YPP plan；先交大纲并由创始人确认精确 SHA-256，才允许制作母版。大纲修改必须重新确认，缺失即 `HOLD_OUTLINE_NOT_APPROVED`。
1. 正文以真实连续影视／演出画面为主体。左上来源和提示框统一米纸白 `#F5F1E8` 底、暗金 `#A77A2D` 字与细边，尺寸只够承载短标签；不得用深蓝实底或巨型框。电影、剧集、歌曲名逐项使用完整 `《》`。
2. 字幕严格沿用《甜蜜蜜》`TM1001-L v9` 的实际成片规格：在 1920×1080 画布中使用 `x=410, y=925, w=1100, h=112` 的米纸白 `#F5F1E8` 半透明纯矩形（约 94% 不透明度、无描边），宋体约 39px、深墨蓝 `#12365E`、居中、最多两行；等比 1280×720 工作画布为 `x=273, y=617, w=734, h=75`、26px。不得用“低于画高 20%”代替该精确规格，也不得保留原片字幕再叠一层新字幕。
3. 普通话旁白默认 Microsoft Edge TTS `zh-CN-YunjianNeural +5%`。渲染前列出语义风险短语；生成后用 ASR／强制对齐核对文字、词级时间戳与内部静音。`他亲眼见过` 必须作为连续 cue，中间最大静音不超过 `180ms` 且不超过该句中位词间隔的 `1.5×`。无法可靠对齐即重写或重生，不转成人工听审。
4. 唯一订阅口播完整落在成片 60–90 秒内，实际时长 8–10 秒。继续本片动态画面、同一音乐和正常字幕；不出现右上角、左上角或居中的专门订阅框。对前后各 15 秒自动核对镜头连续性、字幕覆盖、音轨角色、语音活动和增益包络。
5. 先登记本片对白、环境声、现场演唱和 OST 的可用窗口。电影／音乐题材优先让可追溯原声承担证据与情绪；自制 BGM 只托旁白和转场，进入原声窗口前撤净。所有 stem 总装前锁回 48 kHz。
6. 片尾固定四段：本片点题原声 → 4.0 秒透明人物／订阅机械翻牌 → 三页半透明“接下来上映”节目单 → 独立 3.0 秒温馨原画与本片 OST。顺序不可互换，也不能插入长下档预告。
7. 4.0 秒翻牌从第一张人物卡开始运动算到整板撤下，编码容差一帧。底图继续播放本片连续原画；人物肖像只能取自有来源时码的真实影像帧。卡壳米纸白、字和边暗金、辅助字深墨蓝、阴影暖褐；右上官方圆相暗金。机械中缝只允许出现在纯数字卡格；人物肖像、文字、标点、Logo 等非数字内容在翻动帧与落定帧都不得有贯穿内容的横线。
8. 节目单严格沿用《甜蜜蜜》`TM1001-L v9`：9 秒内依次翻出三条 active YPP 节目，每条约 3 秒，而不是只做一张泛化预告牌。1920×1080 成片的主卡位于 `x=350, y=325, w=1220, h=430`（占画面约 `25.32%`），米纸白 `#F5F1E8`、alpha `164/255`、暗金细边；等比 1280×720 工作画布为 `x=233, y=217, w=813, h=287`。每条必须同时出现日期、slot id、节目／人物名、active plan 完整命题与“目标排期 · 以频道最终发布为准”；两条之间用约 0.36 秒上下机械翻页过渡。左上只显示米纸白底暗金字的“接下来上映”，不得显示“三页节目单／每页约三秒”等制作说明；同一影视／MV 温馨底图在半透明卡后清楚可见，标题不得占大半画面，落定标题区域无贯穿横线，右上使用约 86px 的官方暗金标记。节目单阶段延续本片已登记电影／MV 原声，不混入下一档正片声音。
9. 末三秒使用本片可追溯的连续温馨镜头，撤掉旁白与对白，切回已经登记并完成配乐 QC 的本片 OST／歌曲 cue。正式 OST 保持权利／Content ID HOLD，直到另有发行证据。
10. 中文长片先绑定精确 SHA-256 交创始人确认；确认后才做语言包，语言包完成后才开放 Short。母版任一字节改变，下游语言包、字幕、封面和 Short 的绑定全部失效。

## QC 合同

每个候选母版建立 `film-music-long-qc/v1` JSON，并运行。`TM1001-L` 冻结参考可保留历史 `film-music-long/v1`；2026-09-27 起所有新制作必须声明 `film-music-long/v2`，从而把 active plan、大纲确认、节目单原声和专用封面 skill 一并纳入硬闸：

```bash
python3 scripts/videogen/qc_film_music_long.py --manifest path/to/<content-id>.film-music-long-qc.json
```

最少字段如下；布尔项必须来自可复跑脚本证据或创始人对精确母版 hash 的明确确认，不得按意图填写。人工试听不再是 QC 字段或发布前置条件。

```json
{
  "schema": "film-music-long-qc/v1",
  "content_standard": "film-music-long/v2",
  "planning": {
    "topic_source": "docs/growth/content/active-ypp-plan.json",
    "slot_id": "ACTIVE-PLAN-SLOT-ID",
    "active_plan_sha256": "64 lowercase hex",
    "outline": {
      "sha256": "64 lowercase hex",
      "reviewed_sha256": "same 64 lowercase hex",
      "founder_verdict": "APPROVED"
    }
  },
  "master": {
    "file": "path/to/master.mp4",
    "sha256": "64 lowercase hex",
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "audio_sample_rate": 48000,
    "audio_channels": 2
  },
  "text_treatment": {
    "upper_left_fill": "#F5F1E8",
    "upper_left_text": "#A77A2D",
    "upper_left_border": "#A77A2D",
    "work_titles": ["《片名》"],
    "subtitle_max_lines": 2,
    "subtitle_box_height_ratio": 0.2,
    "double_subtitles_absent": true
  },
  "narration": {
    "tts_backend": "Microsoft Edge TTS",
    "voice_id": "zh-CN-YunjianNeural",
    "rate": "+5%",
    "semantic_prosody_pass": true,
    "risk_phrases": [{"text": "他亲眼见过", "expected_grouping": "他亲眼见过", "asr_text": "他亲眼见过", "max_internal_silence_ms": 96, "pass": true}]
  },
  "cta": {
    "count": 1,
    "in": 75.6,
    "out": 85.5,
    "dedicated_subscription_overlay": false,
    "normal_subtitles": true,
    "continuous_story_picture": true,
    "continuity_review": "PASS_AUTOMATED"
  },
  "music_scoring": {
    "invoked": true,
    "brief": "path/to/music-brief.md",
    "original_sound_seconds": 300,
    "original_sound_ratio": 0.25,
    "final_lufs": -16,
    "final_true_peak_dbtp": -1.2,
    "final_audio_qc": "PASS",
    "rights_status": "HOLD_RIGHTS_OR_CONTENT_ID_CHECK"
  },
  "ending": {
    "order": ["point_original_sound", "endcast", "programme", "warm_ost_tail"],
    "endcast": {
      "duration_seconds": 4.0,
      "transparent_over_original_picture": true,
      "portrait_sources_traceable": true,
      "non_numeric_midline_absent": true,
      "official_mark_dark_gold": true
    },
    "programme": {
      "pages": 3,
      "active_plan_file": "docs/growth/content/active-ypp-plan.json",
      "title_bindings": [{"slot_id": "NEXT-L", "title": "active plan 的逐字标题"}],
      "background_picture_visible": true,
      "translucent_text_boxes": true,
      "instruction_text_absent": true,
      "title_through_line_absent": true,
      "upper_left_rice_paper_dark_gold": true,
      "official_mark_dark_gold": true,
      "registered_current_film_or_mv_original_audio": true
    },
    "warm_ost_tail": {
      "duration_seconds": 3.0,
      "continuous_warm_original_picture": true,
      "registered_current_film_ost": true,
      "original_climax_selected": true,
      "voiceover_absent": true,
      "dialogue_absent": true,
      "ost_audible": true,
      "no_clipping": true
    }
  },
  "thumbnail": {
    "skill_invoked": true,
    "skill": ".agents/skills/ypp-thumbnail-design/SKILL.md",
    "reference": "SL0118-S"
  },
  "evidence": {
    "contact_sheet": "path/to/contact-sheet.jpg",
    "cta_continuity": "path/to/cta.mp4",
    "ending_continuity": "path/to/ending.mp4",
    "settled_endcast_frame": "path/to/endcast.png",
    "programme_frames": ["path/to/page1.png", "path/to/page2.png", "path/to/page3.png"]
  },
  "automated_audio_qc": {
    "verdict": "PASS",
    "report": "path/to/full-length-audio-qc.json",
    "full_decode": true,
    "asr_alignment": true,
    "language_id": true,
    "silence_dropout": true,
    "loudness_true_peak": true,
    "source_switch_envelopes": true
  },
  "founder_review": {
    "founder_exact_hash": "PASS"
  }
}
```

QC 必须核对媒体存在、SHA-256、1920×1080、30 fps、AAC 48 kHz 双声道、active plan 绑定、大纲精确 hash 确认、CTA 时间和次数、4.0 秒翻牌、三页节目单与其本片影视／MV 原声、active plan 标题、末三秒、配乐和专用封面 skill 调用与证据路径。音频再跑全长解码、LUFS／true peak／削波、静音／掉音、语言识别、ASR／强制对齐、风险短语内部停顿、原声保留、切换点包络及 hash 唯一性；任一失败即 HOLD，代表性采样只作诊断。画面仍用逐帧抽样和像素／OCR／身份来源合同检查机械翻牌、字幕、颜色、透明度、Logo 与错片；不再要求完整 1× 人工听看。
