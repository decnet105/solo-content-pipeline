# ChatCut MCP 协议与双模剪辑控制规范

## 1. 架构总览

Antigravity 通过 MCP (Model Context Protocol) 标准与视频剪辑层交互。支持 **GUI 联动模式 (ChatCut Desktop MCP)** 与 **无头渲染模式 (Headless FFmpeg Engine)** 无缝双模切换。

```
                    +---------------------------------------+
                    |    Antigravity Agent (Gemini 3.8/3.7) |
                    +---------------------------------------+
                                        |
                    +-------------------+-------------------+
                    | (MCP Client / stdio)                  | (CLI Script / Subprocess)
                    v                                       v
      +----------------------------+        +-------------------------------+
      |  ChatCut Desktop MCP       |        | Headless FFmpeg Engine        |
      |  (实时 GUI / 交互预览 / 调音) |        | (服务器 / CI / 离线批处理)    |
      +----------------------------+        +-------------------------------+
```

## 2. 核心轨道布局标准 (Unified Multi-Track Standard)

| 轨道 ID | 轨道类别 | 作用域 | 典型操作 |
| :--- | :--- | :--- | :--- |
| **V1** | 视频主轨 (Base Video) | 承载主要故事或操作画面 | 顺序重排、1.25x/1.5x 倍速、淡入淡出、交叉溶解 (Cross Dissolve 20 帧) |
| **V2** | 视觉标注轨 (Callouts) | 关键信息高亮与步骤标签 | Dark Tech Callout Lower-Third、UI 聚焦框、数字序号角标 |
| **V3** | 装饰与水印轨 (Overlays) | 品牌与画质遮罩 | 品牌动态 Logo、电影画幅黑边 (Letterbox)、调色 LUT 滤镜 |
| **A1** | 主声轨 (Primary Audio) | 旁白 / 人声对白 / 原声 | 原声智能降噪、ASR 语音转字幕对齐、响度标准化 (-16 LUFS) |
| **A2** | 音乐轨 (BGM Track) | 氛围背景音乐 | 情绪匹配 (如 Upbeat Corporate / Suspense / Lofi)、增益 (-12dB)、淡入(1.0s)、淡出(2.5s) |
| **A3** | 音效轨 (SFX Track) | 关键节点动效音 | 转场 Whoosh、按键 Click、提示 Ding，与 V2 视觉标注严格卡点 |

## 3. MCP 注册与指令

### 3.1 客户端注册配置
```json
{
  "mcpServers": {
    "chatcut_desktop": {
      "command": "/Users/${USER}/Library/Application Support/ChatCut/chatcut-mcp",
      "args": []
    }
  }
}
```

### 3.2 常见控制指令语义映射
1. **素材重排与转场**:
   - `order`: `["demo2.mp4", "demo1.mp4"]`
   - `playback_rate`: `1.25`
   - `transition`: `{"type": "cross_dissolve", "frames": 20}`
2. **视觉内容解析与打点**:
   - 提取视频关键帧 -> 识别关键操作阶段 -> 在指定时间点自动下发 `add_text_overlay` 到 V2 轨。
3. **音乐与混音**:
   - `bgm_track`: `A2`
   - `volume_gain_db`: `-12.0`
   - `fade_in`: `1.0s`, `fade_out`: `2.5s`
