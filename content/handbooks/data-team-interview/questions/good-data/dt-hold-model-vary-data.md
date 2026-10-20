---
id: dt-hold-model-vary-data
section: good-data
order: 10
level: S
title: 怎样证明一批数据是好的？固定模型，只换数据
quick: "固定架构、训练设置和算力预算，只换一项数据因素，用同一套固定评测比较目标任务与其他能力。DataComp、DataComp-LM 和 FineWeb-Edu 都体现了这种对照思路。小模型也能做，但选出的方案仍要在大模型上确认效果。"
companies:
  - apple
tags:
  - Apple
  - Evaluation
  - Data Quality
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: DataComp-LM
    url: https://arxiv.org/abs/2406.11794
    type: primary
  - title: "DataComp: In search of the next generation of multimodal datasets"
    url: https://arxiv.org/abs/2304.14108
    type: primary
  - title: FineWeb-Edu blog
    url: https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu
    type: primary
  - title: Data Mixing Laws
    url: https://arxiv.org/abs/2403.16952
    type: primary
---

要证明一批数据更好，固定算力、模型架构和训练设置，只更换数据，再比较同一套下游评测。过滤严格本身不能证明效果；资源有限时，小模型同预算对照也能提供证据。

Gadre 等的 DataComp 把训练代码和算力固定，让参与者比较数据选择方案。DataComp-LM 将同样思路用于语言模型，FineWeb-Edu 则公开了不同 cutoff 的消融结果。它们都避免了同时换来源、过滤器和配比后无法归因的问题。

## 对照怎么安排

使用相同 tokenizer、相同模型，以及相同 token 预算或 GPU 小时。一次只改变来源、过滤规则、配比或去重方式中的一项。Mixing law 可以给配比的初始建议，但仍需要在对照实验中验证，见 `dt-data-mix-quota`。

评测套件要固定，并按任务切片报告结果。平均分上升、代码分下降，可能说明过滤网页时误删了代码。用于检查其他能力的锚点评测见 `dt-neg-transfer`；实验前还要排查污染，见 `dt-contamination`。

公开方法中，常先用 1B 级模型做数据决策，再把效果较好的配比用于大模型。DoReMi 也使用代理模型，见 `dt-doremi-mix`。小模型与大模型对数据的反应可能不同，所以仍需在大模型上做一次确认；这比把整个配比网格都在大模型上跑一遍便宜。

## 结果怎么报

按 `dt-cost-per-gain` 记录 token 数、费用、目标指标变化 $\Delta$、锚点指标变化 $\Delta$ 和污染率。收益已经不再随投入增加时，就考虑停止。Director 要判断投入是否值得，只有「又多了 2T」无法回答这个问题。

合成数据还要记录生成了多少代、验证器（verifier）通过率和教师版本。通过率下降时继续增加条数，会改变数据质量；不能再把两批数据当作相同条件下的数量对照。

## 追问

- 没有 GPU 做消融怎么办？至少做过滤前后人工抽查，报告污染率、长度和语言分布。这些证据弱于训练对照，面试时应说明还缺哪些验证。
- 小模型提高、大模型没变化怎么办？这说明代理模型存在偏差。记录结果，不要把小模型上的趋势当成普遍规律。
- 和数据飞轮有什么关系？持续迭代每次新增失败样本时，也应有对照、固定评测和版本追踪，见 `dt-data-intervention`。
