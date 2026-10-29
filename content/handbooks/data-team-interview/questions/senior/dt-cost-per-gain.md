---
id: dt-cost-per-gain
section: senior
order: 8
level: A
title: Director：怎么证明一批数据值得投入？
quick: >-
  按数据源一行一行报：目标任务的提升、regression tasks 有没有掉、contamination rate，以及花掉的 GPU
  小时和人工小时。再测边际收益，这个源再加 10% 目标任务还涨不涨，涨不动就停止扩量。条数和 token 数只说明规模，证明不了价值。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: DataComp-LM
    url: 'https://arxiv.org/abs/2406.11794'
    type: primary
  - title: FineWeb-Edu
    url: 'https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu'
    type: primary
  - title: Data Mixing Laws
    url: 'https://arxiv.org/abs/2403.16952'
    type: primary
---

我会给 VP 看一张表，每个数据源一行，列出 token 数、GPU 小时或人工小时、目标任务子集上的 $\Delta$、regression tasks 上的 $\Delta$ 和 contamination rate。「有 X 亿 token」「又合成了 50 亿」只说明规模，看不出投入换来了多少收益。

比如一批 synthetic data 花了大量 GPU 小时，表里只有条数的话，VP 判断不了这笔钱花得值不值；放上目标子集涨了多少、regression tasks 掉没掉，才能拿去和一批人工标注比。这里的收益要在固定模型、只动数据的对照里测出来，FineWeb-Edu 和 DataComp-LM 的公开方法都是这么做的。

表里还要看边际收益：这个来源再加 10%，目标任务还涨不涨，收益接近平坦时就停止扩量，见 `dt-killed-dataset`。synthetic data 另外报生成代数和验证通过率，通过率往下走，说明大量生成成本没变成可用数据。人工标注按 `dt-human-budget` 的思路算，gold labels 和 evaluation set 带来的 $\Delta$ 往往比 bulk 数据大。人工小时和 GPU 小时放进同一张表，才不会得出「合成很便宜，所以可以无限加」的结论。

## 追问

**regression tasks 微降、目标任务大涨，发不发？**
先问这个 regression tasks 是不是产品 evaluation gate，是的话就不发。

**small model 上 $\Delta$ 大、目标模型上 $\Delta$ 小，信哪个？**
信目标模型，small model 只用来做筛选。

**合成了 50 亿条 caption，ROI 怎么报？**
报视觉 evaluation slices 和文本 regression tasks 的变化。AFM 2025 报告加这类 caption 是因为 alt-text 太短，所以要看图像细节理解有没有改善。

**synthetic data 这么便宜，为什么不一直加？**
看验证通过率和边际收益。通过率在掉、收益已经平了，再加只是在烧生成成本。
