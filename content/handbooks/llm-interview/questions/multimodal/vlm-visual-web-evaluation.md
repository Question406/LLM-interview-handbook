---
id: vlm-visual-web-evaluation
section: multimodal
order: 3
level: A
title: 怎样把视觉 Web Agent 的评测拆为 OCR、icon / layout、visual reference、image matching 与端到端 web execution，避免一个 success rate 掩盖能力缺口？
quick: "按视觉能力把任务分组，分别统计感知正确率、目标元素定位准确率、动作有效率和任务成功率。再比较只给文本、只给截图和两者都给的结果，判断失败发生在哪一步。"
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

按视觉依赖把任务分成 OCR、icon / layout、visual reference、image matching 和跨页状态几组，每组单独设正确性判定，逐层报感知正确率、目标元素定位准确率、动作有效率和任务最终成功率。再跑只给文本 DOM、只给截图、两者结合三种观察条件，看失败发生在哪一步。只报一个 success rate，会把「不会读图」和「不会下单」混成同一个缺口。

比如有些视觉 Agent 主要靠 DOM 文本，其实没用上截图，总分照样不错。VisualWebArena 一类基准在设计任务时就要求 Agent 用到视觉信息，堵的就是这个口子。

五组大概是这样分的：OCR 读价格、SKU、画在图里的文字；icon / layout 认图标和空间关系，比如「左边第二个」；visual reference 找「和这张缩略图一样的商品」；image matching 比颜色、款式、图表趋势；跨页状态看购物车缩略图是否还是刚才那件。分类标签写在任务元数据里，别事后凭感觉分。纯文本就能解的任务别混进依赖视觉的类别，否则很难看出视觉编码器带来多少收益。

消融用来定位问题。加了视觉，端到端却没涨，就拆开看：是编码器没读到关键像素，planner 没用视觉字段，还是执行器没把 visual target 转成正确的点击。别让 LLM judge 只看最终的自然语言说明，网页要检查真实状态和副作用。每次运行记录类别 ID、观察条件、感知的正确性判定、元素定位是否命中和最终状态，才能比出视觉信息实际带来的收益。

任务设计时要显式关掉文本捷径：去掉价格的 DOM 文本、用纯图标按钮、要求匹配缩略图。Agent 要是还能靠 URL 猜对，说明 oracle 太松。这几种做法会让分数虚高：把能用 alt-text / aria-label 解的任务当视觉题；oracle 只看 URL 变化；拿模型自己说的「我看到了红色裙子」当感知指标；把文本可解的集合混进视觉组抬总分。

报告按错误类型和站点分别统计，并给出未见站点上的结果。数据集卡写明 OCR、icon、reference、matching 和跨页任务各占多少，某一类太少，它的表现对总分几乎没影响。消融表和分组统计表一起发布，说明视觉能力的提升发生在哪一类任务上；没有消融，就别写「视觉能力提升」。端到端结果用来判断整体是否达标，分组统计和消融用来判断该改数据、视觉模型还是 Agent 的执行流程。改进的优先级跟着分层走，OCR 差就别先上更复杂的 planner。评测包里要带分类标签、观察消融开关、感知正确性判定、元素定位结果和最终状态检查脚本。

## 追问

**DOM 里已经有价格，为什么还要 OCR 组？**
因为大量价格只画在图里或 canvas 上，这一组专门测文本观察缺少必要信息的任务。

**image matching 和 visual reference 差在哪？**
前者是属性匹配；后者要认出「和给定图相同的实例」，更依赖细粒度外观，别合并成一类。

**和失败分类题怎么接？**
分组统计先指出哪类能力容易出错，`cu-failure-taxonomy` 再用检查点定位一次运行具体在哪一层失败。

**URL 变了算成功吗？**
不算。还要查页面状态和业务副作用，不然会奖励乱跳。
