---
id: dt-hold-model-vary-data
section: good-data
order: 10
level: S
title: 怎样证明一批数据是好的？固定模型，只换数据
quick: "固定架构、训练设置和算力预算，只换一项数据因素，用同一套固定评测比较目标任务和其他能力。DataComp、DataComp-LM 和 FineWeb-Edu 都是这个对照思路。小模型也能做，但选出的方案最后要在大模型上确认一次。"
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

固定算力、模型架构和训练设置，只换数据，再在同一套下游评测上比。过滤得更严本身证明不了什么；资源有限时，用小模型做同预算对照也算证据。

这样做是为了能归因。比如同时换了来源、过滤器和配比，平均分涨了、代码分掉了，你说不清是哪一项干的，可能是过滤网页时把代码误删了，也可能是配比变了。Gadre 等的 DataComp 把训练代码和算力固定下来，让参与者只比数据选择方案；DataComp-LM 把同样的思路搬到语言模型上；FineWeb-Edu 则公开了不同 cutoff 的消融。

## 对照怎么安排

先把不变的部分定死：同一个 tokenizer、同一个模型，以及同样的 token 预算或 GPU 小时。然后一次只改来源、过滤规则、配比或去重方式里的一项。Mixing law 能给配比一个初始建议，但还是要在对照里验证，见 `dt-data-mix-quota`。

评测套件也固定下来，按任务切片报结果，这样才看得出上面那种「平均涨、代码掉」。用来看其他能力的锚点评测见 `dt-neg-transfer`；实验前先排查污染，见 `dt-contamination`。

模型规模上，公开做法常先用 1B 级模型做数据决策，再把效果好的配比用到大模型上，DoReMi 也用代理模型，见 `dt-doremi-mix`。小模型和大模型对数据的反应可能不一样，所以最后还是要在大模型上确认一次，这比把整个配比网格都在大模型上跑一遍便宜得多。

结果按 `dt-cost-per-gain` 记：token 数、费用、目标指标变化 $\Delta$、锚点指标变化 $\Delta$ 和污染率。收益不再随投入增长时，就该考虑停了。Director 要判断值不值，一句「又多了 2T」是回答不了的。

## 追问

**没有 GPU 做消融怎么办？**
至少做过滤前后的人工抽查，报告污染率、长度和语言分布。这些证据比训练对照弱，面试时要说清还缺哪些验证。

**小模型涨了，大模型没变化，怎么解释？**
这说明代理模型有偏差。把结果记下来，别把小模型上的趋势当成普遍规律。

**合成数据做对照，要额外记什么？**
要记生成了多少代、验证器（verifier）通过率和教师版本。通过率在掉、你还在加条数，说明数据质量已经变了，两批数据就不能再当成同条件下的数量对照。

**这和数据飞轮有什么关系？**
持续迭代里每次新加的失败样本，也要有对照、固定评测和版本追踪，见 `dt-data-intervention`。
