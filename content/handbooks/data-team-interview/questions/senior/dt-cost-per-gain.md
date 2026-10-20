---
id: dt-cost-per-gain
section: senior
order: 8
level: A
title: Director：怎么报「这批数据值不值得」，不要只报条数？
quick: "每个数据源分别报告目标任务的改善、旧能力是否下降、污染率，以及 GPU 小时和人工成本。再增加该源 10% 后，收益是否继续增加也要测；边际收益很小时停止扩量。条数和 token 数只能描述规模，不能单独证明价值。"
companies:
  - apple
tags:
  - Apple
  - ROI
  - Data Mix
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: DataComp-LM
    url: https://arxiv.org/abs/2406.11794
    type: primary
  - title: FineWeb-Edu
    url: https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu
    type: primary
  - title: Data Mixing Laws
    url: https://arxiv.org/abs/2403.16952
    type: primary
---

VP 时间短，可以用一张表说明：每个数据源一行，列出 token 数、GPU 小时或人工小时、目标任务子集 $\Delta$、锚点 $\Delta$、污染率。条数和「又合成了 50 亿」不是收益。

只报「有 X 亿 token」，无法说明投入带来了多少收益。FineWeb-Edu / DataComp-LM 的公开方法就是固定模型只动数据。用户日志看起来「免费」，治理上不是可选项，ROI 表里根本不该有这一行。

## 现场摊一张表

还要报告边际收益：该来源增加 10% 后，目标任务是否继续改善。收益接近平坦时停止增加，见 `dt-killed-dataset`。合成还要报代数和验证通过率，通过率下降时，大量生成成本可能没有转化为可用数据。

人标用 `dt-human-budget` 的逻辑：金标和评测的 $\Delta$ 往往大于 bulk 的 $\Delta$。把人时和 GPU 小时放同一张表，避免「合成很便宜所以无限加」。

苹果约束：用户日志看起来「免费」，治理上不是可选项。ROI 表里根本不该有这一行。

## 追问

- **锚点微掉、目标大涨？** 先问锚点是不是产品门禁。是就不发。
- **小模型 $\Delta$ 大、目标模型 $\Delta$ 小？** 以目标模型为准。小模型只筛选。
- **50 亿 caption 怎么报 ROI？** 不报条数，报视觉切片和文本锚点。AFM 用它们是因为 alt-text 太短，需要看它们是否改善图像细节理解，不能只看数量。
