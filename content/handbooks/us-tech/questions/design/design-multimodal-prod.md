---
id: design-multimodal-prod
section: design
order: 8
level: A
title: 设计：多模态助手（图/屏/语音），模态延迟不齐
quick: >-
  语音、图像、屏幕三路到达时间差一个数量级。契约是：没到的模态不当证据，先到的可以先应答或先问。端侧保隐私和首包；云端跑重视觉。评测拆接地、正确、口头可说、各模态超时。
tags:
  - Multimodal
  - Apple
  - Google
  - Latency
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Introducing Apple Foundation Models
    url: https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Gemini — A Family of Highly Capable Multimodal Models
    url: https://arxiv.org/abs/2312.11805
    type: primary
  - title: Robust Speech Recognition via Large-Scale Weak Supervision
    url: https://arxiv.org/abs/2212.04356
    type: primary
---

Apple Intelligence / Siri、Google Gemini 相机问答、Microsoft Copilot 看屏，都会问「语音已经开始听，图还在上传怎么办」。Gemini 报告讲的是模型能力；Apple 公开叙述是 on-device 和 Private Cloud Compute。白板要的是延迟不齐、隐私和接地。不是某次现场逐字题。语音接地专项见 `apple-siri-grounded`；工具循环见 `design-agent-harness`。

## 三路时钟，不要等最慢的那个

我会先问：是否必须看图才答、屏幕是截屏还是连续帧、语音是否可打断（barge-in）、数据能否出设备、首包音频 p95。然后把每路变成带时间戳的证据流，而不是「先把所有模态拼成一个 prompt」。

典型量级（面试用数量级，现场用他们的 SLO）：

- 流式 ASR 部分假设：几百毫秒出词，整句更长。
- 图编码 / 上传：三百毫秒到数秒，看分辨率和网。
- 屏幕：全帧太贵，先 OCR + 区域裁剪 + 小视觉编码器；连续帧要采样，不要 30 fps 进大模型。

策略：

1. **查询分类。** 「现在几点」不需要等相机；「图里是什么牌子」必须等图像证据，否则拒答或追问，不许用参数记忆猜。
2. **部分证据应答。** 语音先到可以确认「我先按你说的查天气，图还在处理」。图后到再补一句，不要把两句矛盾的答案叠在一起。
3. **超时。** 每路有 deadline。超时当该模态缺失，走拒答策略，而不是拿过期缓存图当这张图。
4. **打断。** 用户说话时停 TTS、取消未发出的工具。状态机要能从「生成中」退回听。

证据 $E$ 是带模态标签的结构：ASR 文本、图像 embedding / 描述、OCR 字、工具结果。生成条件是 $(q, E_{\mathrm{ready}})$，解码要对齐到 $E$ 里的跨度，同 Siri grounded 契约。

## 端侧、云端、失败模式

隐私：截屏、相册、消息优先端侧小模型。不够再 PCC / 云，要用户可见的指示。设计成「默认上传每一帧」在 Apple 轮直接出局；在 Google / Microsoft 也要讲清楚保留期和关停开关。

对齐：用户说「这个」时，指的是当前帧还是上一张图，要把 UI 焦点和时间戳写进 $E$。语音时间轴和视频帧 ID 对不上，就会答错对象。多图要编号，口头也说编号。

失败模式：图还没到，模型用预训练知识喊出品牌（听着很自信）；ASR 把药名听错，视觉其实对，融合时信了 ASR；屏幕 OCR 把价格小数点吃掉，工具下单用错金额——金额必须走确认框；首包为了快用了小模型，大模型稍后推翻，用户听到两套说法。

延迟拆：TTFA（首包音频）、端到端、各模态等待时间、打断后静音间隔。p95 按网况分层。视觉超时率是一等公民指标，不是「偶发」。

状态机四个态就够讲：听、等模态、说、打断。图超时从「等模态」进「说」时，口头必须带「我没看到图」。禁止在等图时用预训练知识报品牌。金额、药名、车牌这类槽位，ASR 和 OCR 不一致就问一句，不要默默选一边。

## 评测

拆开：接地（答案能否在 $E$ 定位）、正确（工具/图金标）、voice fitness（长度、可 TTS）、模态缺失时的拒答是否对、延迟曲线随图像分辨率的变化。不要用 BLEU。人工集要覆盖：只有语音、只有图、图文冲突、弱网、打断。冲突时以用户当前焦点为准，并在口头里承认不确定。

和内容安全：图和屏都要过同步轻量审核，儿童安全和违法图像不能等异步，见 `design-moderation`。

## 追问

- **为什么不永远等所有模态？** 语音交互的 p95 会被最慢一路拖死，大量查询根本不需要图。
- **图后到要不要改口？** 要，但先停 TTS 再补一句纠正；两段并存会像两个助手吵架。
- **连续看屏怎么控成本？** 场景变化才重编码，差分帧、OCR 缓存、区域关注。固定 fps 进大模型会把钱和电打光。
- **端侧和云端结果不一致？** 以用户当前会话选的路径为准并审计；不要静默升级到云。
