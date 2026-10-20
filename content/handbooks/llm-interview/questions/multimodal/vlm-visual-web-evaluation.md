---
id: vlm-visual-web-evaluation
section: multimodal
order: 3
level: A
title: 怎样把视觉 Web Agent 的评测拆为 OCR、icon / layout、visual reference、image matching 与端到端 web execution，避免一个 success rate 掩盖能力缺口？
quick: "按视觉能力分组，分别统计感知正确率、目标元素定位准确率、动作有效率和任务成功率。再比较只给文本、只给截图和两者都给的结果，判断失败发生在哪一步。"
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

网页任务若只报一个 success rate，会把「不会读图」和「不会下单」混成同一个缺口。有些视觉 Agent 主要依赖 DOM 文本，实际上没有使用截图。因此，要按能力分组设置正确性判定，再比较不同观察条件下的结果，找出失败发生在哪一步。VisualWebArena 一类基准会在设计任务时就要求 Agent 使用视觉信息。

## 按视觉依赖分组统计

至少分成五类，每类单独设置正确性判定：OCR（读价格、SKU、画在图里的文字）；icon / layout（认图标、空间关系「左边第二个」）；visual reference（「和这张缩略图一样的商品」）；image matching（颜色 / 款式 / 图表趋势）；跨页状态（购物车缩略图是否仍是刚才那件）。分类标签写在任务元数据里，不能事后凭感觉分。纯文本可解的任务不要混进依赖视觉的类别，否则很难看出视觉编码器带来的收益。DOM 已有价格仍设 OCR 桶，是因为大量价格只画在图或 canvas 上。image matching 是属性匹配；visual reference 是「与给定图相同实例」，更依赖细粒度外观，不要合并成一类。

## 分层指标与消融

逐层报告感知正确率、目标元素定位准确率、动作有效率和任务最终成功率。做三种观察消融：只给文本 DOM、只给截图、两者结合。若加视觉后端到端不涨，要拆开看：编码器没读到关键像素、planner 没用视觉字段、还是执行器没把 visual target 转成正确点击。不要让 LLM judge 只看最终自然语言说明；网页必须检查真实状态与副作用。记录类别 ID、观察条件、感知的正确性判定、元素定位是否命中和最终状态，以便比较视觉信息实际带来的收益。

## 能刷的点与报告

评测中容易产生误导的做法包括：把可用 alt-text / aria-label 的任务当视觉题；oracle 只看 URL 变化；用模型自己的「我看到了红色裙子」当感知指标；把文本可解集混进视觉桶抬总分。报告要按错误类型和站点分别统计，并给出未见过的站点上的结果。改进优先级来自分层，而不是总分：OCR 差就别先上更复杂的 planner。端到端结果用于判断整体是否达标；分组统计和消融结果用于判断该改数据、视觉模型还是 Agent 的执行流程。评测包要带分类标签、观察消融开关、感知正确性判定、元素定位结果和最终状态检查脚本。没有消融就不要写「视觉能力提升」。任务设计时显式关掉文本捷径：去掉价格的 DOM 文本、用纯图标按钮、要求匹配缩略图。若 Agent 仍能靠 URL 猜对，说明 oracle 太松。

数据集卡要写明 OCR、icon、reference、matching 和跨页任务各占多少。某一类过少，它的表现对总分影响就很小。消融表和分组统计表一起发布，说明视觉能力提升发生在哪一类任务上。

## 追问

- **DOM 已经有价格为什么还要 OCR 桶？** 因为大量价格只画在图里或 canvas 上；这一类就是专门测试文本观察缺少必要信息的任务。
- **image matching 和 visual reference 差在哪？** 前者是属性匹配；后者是「与给定图相同实例」，更依赖细粒度外观。
- **和失败分类题怎么接？** 分组统计先指出容易出错的能力；`cu-failure-taxonomy` 再用检查点定位一次运行具体在哪一层失败。
- **URL 变了算成功吗？** 不够。还要查页面状态和业务副作用，否则会奖励乱跳。
