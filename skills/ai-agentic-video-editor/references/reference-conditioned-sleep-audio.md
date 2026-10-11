# 参考音频条件生成与长时睡眠母带

适用于项目拥有一段已获人工批准的参考音频，并要求生成相似声纹但不复制旋律、不循环原片的睡眠、冥想或 ambient drone 长音轨。

## 1. 输入与授权

- 确认参考音频由项目合法持有或获准使用；只提取抽象音色、空间、密度和演奏质感，不要求复制可识别旋律。
- 记录总现金上限、每个 provider 的计划上限、已有累计花费和停止线。订阅费、税费和失败但计费的请求均计入上限。
- API key 只从 Keychain、环境变量或既有私密配置读取，永不写入 manifest、日志或命令输出。

## 2. Provider 路由

按任务能力而不是品牌优先级选择：

1. **Audio-reference composition**：适合从短参考建立相似音色并生成全新音乐。优先用于首轮声纹匹配。
2. **Audio-to-audio / init audio**：适合单变量调整参考保留强度，寻找音色相似与新内容之间的平衡。
3. **Inpainting / continuation**：适合从已通过的候选边界向后续写，并以保留上下文消除接缝。
4. **Text-only music generation**：只能作为语义基线或补充纹理；不得因为 prompt 中含有频谱数字就宣称它复用了参考声纹。

当前可用能力示例会随 provider 更新而变化，调用前核对官方 schema 与价格：

- Eleven Music v2/v2.5：短 audio reference、conditioning strength、context adherence、分段 composition/inpainting。
- Stable Audio 3：init audio、audio-to-audio、inpainting、continuation、seed、negative prompt；可本地运行时优先做零 API 成本试样。
- fal ACE-Step Audio Inpaint：低成本边界续写或局部重绘候选；它不是自动的长时声纹克隆器。
- Google Lyria text/image 模型：当 schema 不接受 audio input 时只作为文本语义基线。Lyria RealTime 的 brightness、density、mute_drums 等控制若已充分使用且人工仍否决，不得换 seed 盲抽。

## 3. 最小试样与预算闸

- 每个付费模型默认只提交 1–2 条 30–60 秒候选；本地模型可多做，但仍须逐条记账与 QC。
- 付费前计算 `planned_cost <= provider_remaining <= total_remaining`。价格无法从官方来源确认时，停止付费调用。
- 候选未过机器硬闸或人工声纹闸，不得扩时。扩时前重新计算完整时长成本。
- Provider 报错时保存原 request ID 并查询原任务；不要用同样输入重新提交来“碰碰运气”。

每次调用至少记录：provider、model、endpoint、request ID、开始/结束时间、计费时长、预估/实际费用、完整 prompt/配置、参考文件 hash、输出 hash、机器 QC、人工结论、采用或淘汰原因。

### Suno Pro 授权导出

- 只把订阅生效后生成、且账户回读明确显示 subscribed/commercial ownership 的候选纳入商用管线；免费计划旧作即使后来订阅，也不得默认追溯成商用授权。
- 新版 Suno 的试听流可能是加密媒体。CloudFront 播放地址、`forbidden` 占位 URL 或缺少 `moov`/无法被 `ffprobe` 解码的文件都不是母带，不得进入 QC。
- 优先使用已登录页面的官方 `Download → WAV → Unlock & Download`。浏览器若请求允许多文件下载，可在用户已明确要求导出这些候选时允许；保存 M4A 试听件和 WAV 母带，并在落库前分别用 `ffprobe` 与 SHA-256 验证。
- 如使用支持当前授权流程的 CLI，只允许调用官方登录会话的 `download/authorize` 工作流；不得抓取或记录明文 cookie/JWT。授权下载会消耗计划中的 download allowance，应与现金预算分开记录。
- Suno WAV 当前可能为 48 kHz；`resynthesize_sleep_reference.py` 要求 44.1 kHz。保留 48 kHz 原母带，另生成 44.1 kHz、24-bit 工作副本，记录重采样器和参数。

## 4. 提示与条件结构

把参考音频负责的内容与文本负责的内容分开：

- 参考音频：声纹、制作质感、立体声深度、配器倾向、细微旋律密度。
- 正向文本：使用场景、能量、包络、空间和允许的演化速度。
- 负向文本或 negative styles：人声、吟唱、鼓、打击乐、pulse、ostinato、arpeggio、rhythmic pumping、亮铃、高频 shimmer、pipe organ、church harmony、cinematic crescendo、sharp attacks、sudden events。

不要同时要求“无旋律”和“保留参考的细腻音乐性”。睡眠产品应允许微弱、无抓耳动机的 micro-melodic movement，同时禁止前景主题、节拍和戏剧性和声终止。

### 文本基线的频谱/声场校准

- `very low`、`sub-bass`、`almost unchanged` 连续叠加时，文本音乐模型容易把“安全催眠”误解成单一低频毯：频谱中心过低、谐波变化过少、立体声相关度过高。不要用更多同义低频词补救。
- 目标是 G 类“中低音宽带”时，正向提示改写为：`broad low-mid body`、`muted upper partials without bright highs`、`diffuse decorrelated stereo depth`、`slow irregular micro-harmonic drift`、`breathing crest and headroom`。这比单纯强调 sub-bass 更接近丰富、细腻、浩瀚而不刺耳的结果。
- “无明显事件”不等于“完全不变”。允许低幅、非周期、无主题的细节迁移；否则模型会把 chroma movement 和 crest factor 一并压扁。
- 文本基线若通过睡眠硬闸但与参考在频谱中心、立体声相关度、crest 或微和声变化上显著偏离，只能记为安全基线，不能标记为参考复现或直接扩时。

## 5. 验收顺序

每条候选按固定顺序处理，前一闸失败即停止：

1. 文件完整性、时长、采样率、声道和 hash。
2. 严格人声/吟唱检测。
3. 打击乐能量、onset peakiness、beat periodicity、短窗 RMS 突变。
4. 频谱分布、立体声相关度、微动态与高频注意力事件。
5. 参考相似度：传统频带指标之外，加入 OpenL3/CLAP 等音频嵌入或等价感知特征；加入规则谐波梳状度，惩罚不需要的管风琴感。
6. 等响度人工盲听：参考、当前最佳、候选三方比较。机器通过不等于可采用。

所有候选统一到相同试听 LUFS；不得用简单低通、加噪或大幅压低音量掩盖模型本身的节奏、声场或质感缺陷。

## 6. 长时构建

- 先得到至少一条人工通过的连续源母带，再扩展到 8–15 分钟；不要直接从 30 秒跳到数小时。
- 延长优先使用 continuation/inpainting 和高上下文保持；相邻段保留足够上下文，并用 15–30 秒长交叉淡化对账接缝。
- 长时母带可分为低音主体、中低音细节、夜空气三个独立层。用互不相同且不锁拍的超慢包络分别控制滤波、音量、声像和纹理密度，形成长超级周期。
- 对最终成品运行滑动 30 秒音频指纹；发现与参考原片或成品内部近似精确重复时，重排或重新生成对应区域。
- 三小时母带至少抽检开头、15/30/60/90/120/150 分钟、结尾，以及每个生成接缝；最终 AAC/MP4 重新执行全部音频硬闸。

当云模型无法通过周期性硬闸、而参考音频为项目自有素材时，可先用本技能的 `scripts/resynthesize_sleep_reference.py` 生成长颗粒声纹样片。它用长重叠颗粒、轻微时间伸缩/移调和非同步慢包络打散原时间结构；该路线仍须执行全部机器与人工闸，不得把“算法生成”当成质量豁免。

若人工要求“节奏再慢”，不要优先对整条成品做统一 `atempo`：相位声码器可能引入细碎 onset，表面 BPM 下降但事件密度反而上升。优先从长颗粒阶段重建：增加 `--grain-min/max-seconds`，降低 `--rate-min/max`，并用互不锁拍的 `--advance-min/max-fraction` 控制重叠密度。临床睡眠研究常见 60–80 BPM，但 ambient 产品的目标不是制造清晰的 60 BPM 拍点；应同时压低 pulse clarity、event density、brightness、accent 和动态阶跃，并以人工舒适度复核。

当候选音色已过人工闸、但仅因隐性 pulse 或段落增益阶跃失败时，可在项目拥有商用权的 WAV 上做异步时间漂移、非整数延迟扩散和无攻击的慢增益校正。处理后必须从严格人声闸开始全量复检；不得以低通、降音量或修改阈值伪造通过。优先保留频谱重心、带宽、立体声相关度与 crest，使修复仍接近已批准参考。

长颗粒扩展后运行 `scripts/qc_audio_repeat_fingerprint.py`。默认以 8 kHz 单声道解码、5 秒窗口、1 秒步长检查 bit-exact 重复；任何非重叠重复窗口均失败。它只证明没有精确短循环，不替代滑动感知相似度、接缝试听或人工判定。
