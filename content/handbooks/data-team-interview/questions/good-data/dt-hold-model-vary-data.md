---
id: dt-hold-model-vary-data
section: good-data
order: 10
level: S
title: 怎样证明一批数据是好的？固定模型，只换数据
quick: "固定架构、训练设置和算力预算，只换一项数据因素，用同一套固定评测比较目标任务与其他能力。DataComp、DataComp-LM 和 FineWeb-Edu 都是这种对照思路。小模型也能做，但选出的方案仍要在大模型上确认效果。"
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

要证明一批数据更好，就固定算力、模型架构和训练设置，只换数据，再在同一套下游评测上比较。过滤得更严格本身证明不了什么；资源有限时，用小模型做同预算对照也能提供证据。

这样做是为了能归因。同时换来源、过滤器和配比，结果变了也说不清是哪一项起的作用。Gadre 等的 DataComp 把训练代码和算力固定下来，让参与者只比较数据选择方案；DataComp-LM 把同样的思路用到语言模型上；FineWeb-Edu 则公开了不同 cutoff 的消融结果。

## 对照怎么安排

先把不变的部分定死：相同的 tokenizer、相同的模型，以及相同的 token 预算或 GPU 小时。然后一次只改变来源、过滤规则、配比或去重方式中的一项。Mixing law 可以给配比一个初始建议，但仍要在对照实验里验证，见 `dt-data-mix-quota`。

评测套件也要固定，并按任务切片报告结果。平均分上升、代码分下降，可能说明过滤网页时误删了代码。用来检查其他能力的锚点评测见 `dt-neg-transfer`；实验前还要排查污染，见 `dt-contamination`。

模型规模上，公开方法常先用 1B 级模型做数据决策，再把效果较好的配比用到大模型上，DoReMi 也用代理模型，见 `dt-doremi-mix`。小模型和大模型对数据的反应可能不同，所以最后仍要在大模型上确认一次；这比把整个配比网格都在大模型上跑一遍便宜得多。

## 结果怎么报

按 `dt-cost-per-gain` 记录 token 数、费用、目标指标变化 $\Delta$、锚点指标变化 $\Delta$ 和污染率。收益不再随投入增加时，就该考虑停了。Director 要判断投入值不值，只有一句「又多了 2T」是回答不了的。

合成数据还要记录生成了多少代、验证器（verifier）通过率和教师版本。如果通过率在下降，你还在继续加条数，数据质量已经变了，两批数据就不能再当作同条件下的数量对照。

## 追问

- 没有 GPU 做消融怎么办？至少做过滤前后的人工抽查，报告污染率、长度和语言分布。这些证据比训练对照弱，面试时要说明还缺哪些验证。
- 小模型提高了，大模型没变化，怎么办？这说明代理模型有偏差。把结果记录下来，不要把小模型上的趋势当成普遍规律。
- 和数据飞轮有什么关系？持续迭代中每次新增失败样本，也要有对照、固定评测和版本追踪，见 `dt-data-intervention`。
