# FFmpeg 无头视频管线引擎规范

当本地未安装 ChatCut Desktop GUI 时，本管线自动降级为高精度 FFmpeg 脚本生成与执行模式，实现 100% 相同的时间轴与混音效果。

## 1. 核心滤镜链规范 (Filter Complex Architecture)

### 1.1 视频拼接与交叉溶解 (Cross Dissolve with Speedup)
- 变速：`setpts=PTS/1.25`
- 衔接：`xfade=transition=fade:duration=0.67:offset=65.8`

### 1.2 视觉标签与 Lower-Third 绘制
使用 `drawbox` + `drawtext` 或 PNG 序列覆叠：
```
[v_main][v_callout] overlay=x=40:y=H-h-40:enable='between(t, 11.15, 14.15)' [v_out]
```

### 1.3 伴奏 BGM 混音与淡入淡出 (Audio Mixing & Ducking)
- 音量衰减：`volume=-12dB`
- 淡入淡出：`afade=t=in:st=0:d=1.0, afade=t=out:st=84.8:d=2.5`
- 伴奏混音：`amix=inputs=2:duration=first:dropout_transition=2`

### 1.4 电影／音乐人物长片时间线合同

时间线必须显式登记 `content_standard: film-music-long/v1`，并包含 `cta`、`text_treatment`、`music_scoring`、`ending`、`programme` 与 `qc_evidence`。片尾顺序固定为：点题原声 → 4.0 秒透明人物／订阅机械翻牌 → 三页半透明“接下来上映”节目单 → 独立 3.0 秒温馨原画与本片 OST。不得靠片长相减猜测节点；每段都要有绝对 in/out、来源时码、声音角色和渲染资产 hash。

正文左上来源／提示框及节目单左上标签固定为米纸白 `#F5F1E8` 底、暗金 `#A77A2D` 字与细边。订阅口播必须在 60–90 秒、实长 8–10 秒，并写 `dedicated_subscription_overlay:false`。节目单标题从 active YPP plan 读取，禁止把制作说明渲进画面。

渲染后使用 `scripts/videogen/qc_film_music_long.py --manifest <qc-contract.json>`；合同字段与自动音频 QC 要求见 [电影／音乐长片标杆](film-music-long-benchmark.md)。脚本 PASS 证明合同、媒体、画面证据与全长自动音频门齐全，但不授予素材或 OST 发行权；人工试听不再是交付前置条件。

## 2. 最终导出标准
- 编码：H.264 (`libx264`), crf=18, preset=slow
- 音频：AAC 320kbps, 48kHz
- 容器：MP4 (faststart 优化流媒体首帧播放)
