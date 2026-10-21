---
id: dt-cost-per-gain
section: senior
order: 8
level: A
title: Director：怎么证明一批数据值得投入？
quick: "按数据源分别报：目标任务的提升、旧能力（锚点）有没有下降、污染率，以及花掉的 GPU 小时和人工小时。还要测边际收益：该源再增加 10%，目标任务是否继续改善，收益接近平坦就停止扩量。条数和 token 数只描述规模，不能证明价值。"
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

我会给 VP 看一张表：每个数据源一行，列出 token 数、GPU 小时或人工小时、目标任务子集上的 $\Delta$、锚点上的 $\Delta$ 和污染率。「有 X 亿 token」或「又合成了 50 亿」只说明规模，说明不了投入换来了多少收益。

## 收益怎么测

收益要在固定模型、只动数据的对照里测出来，FineWeb-Edu 和 DataComp-LM 的公开方法都是这样做的。表里只有 token 数的话，VP 判断不了这笔 GPU 和人力花得值不值。

## 表里还要放什么

第一是边际收益：该来源再增加 10%，目标任务是否继续改善。收益接近平坦时就停止扩量，见 `dt-killed-dataset`。

第二，合成数据要另外报生成代数和验证通过率。通过率下降时，大量生成成本可能没有转化成可用数据。

第三，人工标注按 `dt-human-budget` 的逻辑算：金标和评测集带来的 $\Delta$ 往往大于 bulk 数据。把人工小时和 GPU 小时放进同一张表，才能避免得出「合成很便宜，所以可以无限加」的结论。

## 追问

- **锚点微降、目标任务大涨，发不发？** 先问这个锚点是不是产品门禁。是的话就不发。
- **小模型上 $\Delta$ 大、目标模型上 $\Delta$ 小，信哪个？** 以目标模型为准，小模型只用来做筛选。
- **合成了 50 亿条 caption，ROI 怎么报？** 报视觉切片和文本锚点的变化。AFM 2025 报告加这类 caption 是因为 alt-text 太短，所以要看图像细节理解有没有改善。
