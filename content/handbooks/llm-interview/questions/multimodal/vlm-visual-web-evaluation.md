---
id: vlm-visual-web-evaluation
section: multimodal
order: 3
level: A
title: 怎样把视觉 Web Agent 的评测拆为 OCR、icon / layout、visual reference、image matching 与端到端 web execution，避免一个 success rate 掩盖能力缺口？
quick: 用能力分桶和逐层指标：感知正确率、元素 grounding、动作有效率、任务成功率；再按是否依赖视觉信息做文本/视觉消融。端到端失败必须能回溯到具体视觉能力，而非只报总分。
tags:
  - VisualWebArena
  - Evaluation
  - VLM
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: VisualWebArena
    url: https://arxiv.org/abs/2401.13649
    type: primary
---

网页任务若只报一个 success rate，会把「不会读图」和「不会下单」混成同一个缺口。很多所谓视觉 Agent，真正用到的是 DOM 文本；截图只是陪跑。我会讲分桶 oracle、文本 / 视觉消融，以及端到端失败能回溯到哪一种视觉能力。VisualWebArena 一类基准的价值正在于视觉依赖被显式设计进任务，而不是事后看截图。

## 按视觉依赖分桶

至少五桶，每桶独立 oracle：OCR（读价格、SKU、画在图里的文字）；icon / layout（认图标、空间关系「左边第二个」）；visual reference（「和这张缩略图一样的商品」）；image matching（颜色 / 款式 / 图表趋势）；跨页状态（购物车缩略图是否仍是刚才那件）。桶标签写在任务元数据里，不能事后凭感觉分。纯文本可解的任务不要混进视觉桶，否则视觉编码器的贡献会被刷没。DOM 已有价格仍设 OCR 桶，是因为大量价格只画在图或 canvas 上。image matching 是属性匹配；visual reference 是「与给定图相同实例」，更依赖细粒度外观，不要并成一桶。

## 分层指标与消融

逐层报：感知正确率、目标元素 grounding、action validity、任务终态成功率。做三种观察消融：只给文本 DOM、只给截图、两者结合。若加视觉后端到端不涨，要拆开看：编码器没读到关键像素、planner 没用视觉字段、还是执行器没把 visual target 转成正确点击。不要让 LLM judge 只看最终自然语言说明；网页必须检查真实状态与副作用。记录：桶 ID、观察条件、感知 oracle、grounding 命中、终态。没有消融表，就不能说「我们上了视觉」。

## 能刷的点与报告

评测上能刷的是：把可用 alt-text / aria-label 的任务当视觉题；oracle 只看 URL 变化；用模型自己的「我看到了红色裙子」当感知指标；把文本可解集混进视觉桶抬总分。报告按桶和站点切片，并给出跨域（未见站点）数字。改进优先级来自分层，而不是总分：OCR 差就别先上更复杂的 planner。e2e 是门禁；分桶加消融才决定改数据、改视觉模型还是改 Agent loop。评测包要带：桶标签、观察消融开关、感知 oracle、grounding 命中、终态脚本。没有消融就不要写「视觉能力提升」。我会按桶指出当前短板，不报一个 VisualWebArena 总分了事。任务设计时显式关掉文本捷径：去掉价格的 DOM 文本、用纯图标按钮、要求匹配缩略图。若 Agent 仍能靠 URL 猜对，说明 oracle 太松，不是视觉真的好。

分桶比例写进数据集卡：OCR、icon、reference、matching、跨页各占多少。某一桶过少，总分会被其它桶稀释。消融表与分桶表一起出，宣称视觉升级时必须指出是哪一桶在动。

我会讲分桶和消融，不讲一个 VisualWebArena 分数。能指出当前是 OCR 差还是 reference 差，以及 DOM-only 消融是否已经能做对，才知道该改哪一层。

## 追问

- **DOM 已经有价格为什么还要 OCR 桶？** 因为大量价格只画在图里或 canvas 上；这桶就是为文本观察故意缺失的任务准备的。
- **image matching 和 visual reference 差在哪？** 前者是属性匹配；后者是「与给定图相同实例」，更依赖细粒度外观。
- **和失败分类题怎么接？** 分桶给出能力先验；`cu-failure-taxonomy` 用 checkpoint 把单次 run 钉到其中一层。
- **URL 变了算成功吗？** 不够。还要查页面状态和业务副作用，否则会奖励乱跳。
