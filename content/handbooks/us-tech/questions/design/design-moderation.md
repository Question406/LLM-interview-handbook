---
id: design-moderation
section: design
order: 6
level: A
title: 设计：内容安全分级，延迟、申诉、模型+规则
quick: >-
  先按类别和严重度规定放行、折叠、删除、封号等动作，再用规则和哈希处理高确信命中、模型处理语义判断、人工处理灰色案例与申诉。发送路径做低延迟检查，回溯扫描可异步；false
  rejection 和漏杀按严重度分别评估。
tags:
  - Safety
  - Meta
  - Apple
  - Moderation
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: OpenAI Moderation
    url: 'https://platform.openai.com/docs/guides/moderation'
    type: primary
  - title: Introducing Apple Foundation Models
    url: >-
      https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: System Design in a Hurry
    url: 'https://www.hellointerview.com/learn/system-design/in-a-hurry/introduction'
    type: secondary
---

## 题目描述

本题是手册归纳的系统设计练习。流量、数据量和具体 SLO 未给定时，请先列出可调整的假设，不把假设当成已披露事实。

### 场景与目标

设计处理用户内容或模型输出的内容审核系统。内容可能是文字、图片或其他媒体，系统需依据产品政策区分类别、严重度和处置动作，并允许申诉。

### 需要满足的功能

- 接收内容、上下文与适用政策版本，返回审核结论、处置状态和可追溯原因。
- 支持同步发布路径与异步复查，复杂或不确定案例能转交人工。
- 支持政策更新、申诉、纠正误判和审计。

### 约束与交付物

需先声明审核场景、policy requirements 与 risk limits，不把模型分数直接当作法律结论。需要讨论 false rejection/false acceptance、不同群体或语言的质量、延迟、人工负载与隐私。

请说明 scope 和 constraints、对外接口及返回语义、核心数据对象、主要请求的完整生命周期、故障与恢复行为，以及能验证设计是否达标的指标。题目不预先指定数据库、模型或调度算法；需要解释自己作出的选择与代价。

### 请求与结果示例

同一条被判为低严重度骚扰的评论，应按已约定政策获得相应处置；用户申诉后，系统需要找回当时的政策、证据和决定，并能记录复核结果。

## 可以这样回答

我会先定义「类别、严重度、处置动作」的映射，再安排规则、模型和人工各处理哪部分。比如低严重度骚扰可以折叠，高严重度则删除并限流；模型给出分数和证据，动作由产品政策决定。发送路径用轻量检查控制延迟，复杂案例和申诉进入人工流程。

这类设计覆盖 Meta 信息流、Google 内容生态、Apple on-device 安全和 Microsoft / OpenAI 输入输出过滤。OpenAI Moderation 公开类别分数，Apple 还强调私有内容尽量不上云。评测属于 `design-eval-platform` 的安全列，审核系统本身仍要独立设计。

## 技术备查

## 解题思路与参考答案

我会先定义「类别、严重度、处置动作」的映射，再安排规则、模型和人工各处理哪部分。比如低严重度骚扰可以折叠，高严重度则删除并限流；模型给出分数和证据，动作由产品政策决定。发送路径用轻量检查控制延迟，复杂案例和申诉进入人工流程。

这类设计覆盖 Meta 信息流、Google 内容生态、Apple on-device 安全和 Microsoft / OpenAI 输入输出过滤。OpenAI Moderation 公开类别分数，Apple 还强调私有内容尽量不上云。评测属于 `design-eval-platform` 的安全列，审核系统本身仍要独立设计。

## 分级、动作、人机分工

我会先问：UGC 还是模型输出、同步发送还是异步扫描、法律红线（CSAM、恐怖、诈骗）、是否要 on-device、申诉 SLA。接着把各类别的处置政策写成表，再决定分类器输出怎样触发动作。

类别 × 严重度 × 动作。例如骚扰：低严重折叠评论；高严重删除并限流。儿童安全、恐怖：命中即阻断并走强制报告流程，不走「模型再想想」。动作是产品/法务定的，模型只输出分数和证据。

分层：

1. **规则和哈希。** 已知违法媒体哈希、违禁词、诈骗模板、账户图特征。确定性高、可解释、延迟低。false negative 交给下一层，不要用正则覆盖全世界。
2. **模型。** 多标签分数，带 calibration。输入是文本 / 图像 / 音视频转写。灰色带（分数在两个阈值之间）送人工或只降分不删。
3. **人工。** sampling、用户举报、申诉。指南和 gold labels 陷阱同评测平台。模型版本、规则版本、证据截图要进工单，否则申诉无法复盘。

on-device（Apple 风格）：私有消息的分类尽量 on-device，云端只收聚合或用户明确上报的内容。设计里不要默认「全量日志拿去再训」。

## 延迟和通道

发送路径（发私信、发评论、模型吐词）的 p95 往往是几十到一两百毫秒，不能先跑一个大视频模型。做法：轻量文本模型同步；图像先哈希 + 小分类器；重模型异步，先发后撤要有产品授权：有的类别允许，违法必须发前拦截。

直播 / 语音：流式分片打分，窗口重叠，避免一句切两半漏掉。撤回和封禁是另外的写路径，要幂等。

失败模式：方言和 code-switch false rejection（精确率在英语很高、在少数语言崩）；对抗拼写绕过 vocabulary 但骗不过语义模型，或反过来；先发后撤造成传播；规则与模型打架（规则放行、模型删除，用户看到闪烁）；阈值按总体定，头部市场过严、尾部市场过松。

阈值我会画成两条：$\tau_{\mathrm{block}}$ 以上同步拦截；$\tau_{\mathrm{review}}$ 到 $\tau_{\mathrm{block}}$ 送队列或只降权。红线类别没有灰色带。直播分片窗口要重叠，否则一句敏感词切在 chunk boundaries 会漏。规则命中必须带规则 id，模型命中带版本号，申诉才能复盘。

不要只报一个 F1。按类别、语言、严重度拆精确率 / 召回。漏杀一条 CSAM 和漏杀一条骂人不是一个量级：用风险加权，或对红线类别设「漏杀目标接近 0、用人工补」。false rejection 看申诉撤销率、误伤率、对边缘群体的差分表现。延迟：同步路径 p95、异步积压、人工队列 SLA。

申诉：用户看到原因类别（能公开的部分）、人工复审时限、结果回写到 training set 前要脱敏和许可。撤销率突然升高，优先查规则误伤和新模型漂移，不要先加更大的模型。

同步路径 p95、异步积压和人工 SLA 都要设告警。接入生成产品时，输出过滤发现违规，还要能打断已经开始的流式 token。

和推荐 / 广告的接口：完整性是硬约束，不是排序的一个小权重，见 `design-recsys`。生成式产品的输出过滤还要防 prompt injection，见 `design-agent-harness`。

## 追问

**为什么不端到端一个 large model？**
红线需要可解释、可强制、低延迟。模型负责灰色带。全模型还有训练 contamination 和对抗不稳定。
**先发后撤行不行？**
看法律和传播速度。违法内容不行；低严重垃圾可以，但要有撤回 SLA 和用户感知。
**用户对抗拼写怎么办？**
规则会输，语义模型 + normalization（去混淆、转写）补；仍要将 human-reviewed examples 加入后续训练，别幻想一次编码搞定。
**on-device 分数和云端不一致？**
允许。on-device 保守拦截、云端再判；以用户可见动作为准做审计，不要两套日志对不上。
