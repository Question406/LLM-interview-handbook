---
id: dt-filter-too-hard
section: good-data
order: 6
level: S
title: 质量过滤会不会滤过头？FineWeb 和 AFM 的公开教训是什么？
quick: "会。过滤器偏好「像英语维基或教科书」的文本时，可能误删代码、公式、论坛答疑和低资源语言。应尝试不同阈值，比较各语言通过率与下游指标变化。FineWeb 与 AFM 2025 都提到减弱过强的启发式过滤；过滤严格到什么程度，要靠实验决定。"
companies:
  - apple
tags:
  - Apple
  - Data Quality
  - Filtering
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: The FineWeb Datasets
    url: https://arxiv.org/abs/2406.17557
    type: primary
  - title: FineWeb-Edu blog
    url: https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: "CCNet: Extracting High Quality Monolingual Datasets from Web Crawl Data"
    url: https://arxiv.org/abs/1911.00359
    type: primary
---

会。过滤越严格，数据不一定越好。偏好「像英语维基或教科书」的过滤器，可能把代码、公式、论坛答疑和低资源语言一起删掉。所以阈值要靠实验选：试几档不同的保留率，同时看各类内容的通过率和下游指标变化 $\Delta$，判断删掉的内容是否真的没用。

## 为什么会滤过头

问题出在「像参考语料」这个信号上。CCNet 用基于维基训练的 KenLM 困惑度筛选网页，后来不少公开数据集也把「像参考语料」当作质量信号。这种信号对有些语言和任务并不适用。FineWeb 的消融实验发现，过强的启发式规则会伤害结果；AFM 2025 报告也公开说明，他们减弱了过强的启发式规则，加入按语言调整的模型过滤，因为旧规则会丢掉有价值的 token。

具体来说，有几类内容最容易被误删：

- 代码和公式里停用词少，容易被偏好自然语言的规则丢掉。
- 按英语教科书训练的分类器，可能给非英语文本和不正式但有用的论坛答疑打低分。FineWeb-Edu 的教育分有用，但不应直接用于代码数据，见 `dt-quality-clf-synth`。
- 同一个分数阈值在不同语言上并不等价。英语和某种低资源语言都用 0.6，通过率可能差一个数量级。可以按语言调整分位数，见 `dt-ppl-filter-code`、`dt-quality-filter-code`。

过滤的收益也取决于数据原本有多脏。Muennighoff 的 datablations 发现，较脏的数据集更可能从过滤中获益；已经比较干净的数据，再过滤收益可能很小，甚至会损失覆盖。这和 FineWeb 的观察方向一致。

## 怎么选阈值

例如分别保留 10%、30%、50%，用小模型对比知识、推理、代码和多语表现。再抽查 100 条被丢弃的样本，看有没有误删，并把各类通过率写进 dataset card。某种语言的通过率明显下降时，先检查阈值，不要直接用机器翻译填满配额。

两类检查要分开处理。PII、密钥、空抽取这类确定性问题可以硬性拦截；主观质量分要留出调阈值、做消融的空间，写成固定的硬规则就没法再调了。

## 追问

- FineWeb-Edu 保留 1.3T，是否证明数据越少越好？这只是他们在特定评测中较好的结果，属于他们自己的实验设置。换了任务要重新试阈值。
- 合成数据也需要过滤吗？需要，而且要用适合任务的验证器（verifier）。教师续写的困惑度可能很低，直接用网页 ppl 过滤，会把错误内容也留下来，见 `dt-ppl-filter-code`。
- 和 SemDeDup 一起用时先做哪个？先用精确哈希和 MinHash 去掉复制内容，再做质量筛选。语义去重优先用在高价值子集上，省掉全量 embedding 的成本，见 `dt-semdedup-code`。
