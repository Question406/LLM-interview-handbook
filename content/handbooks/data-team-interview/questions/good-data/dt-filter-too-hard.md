---
id: dt-filter-too-hard
section: good-data
order: 6
level: S
title: 质量过滤会不会滤过头？FineWeb 和 AFM 的公开教训是什么？
quick: "会。过滤器偏好「像英语维基或教科书」的文本时，可能误删代码、公式、论坛答疑和低资源语言。应尝试不同阈值，比较各语言通过率与下游指标变化。FineWeb 与 AFM 2025 都提到减弱过强的启发式过滤；过滤严格程度需要实验验证。"
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

过滤越严格，数据不一定越好。要尝试不同阈值，同时观察保留率和下游指标变化 $\Delta$，判断删掉的内容是否真的无用。

CCNet 使用基于维基训练的 KenLM 困惑度筛选网页，后来不少公开数据集也把「像参考语料」当作质量信号。但这种信号不能直接代表所有语言和任务。FineWeb 的消融实验发现，过强的启发式规则会伤害结果。AFM 2025 也公开说明，他们减弱了过强规则，加入按语言调整的模型过滤，因为旧规则会丢弃有价值的 token。

## 过滤过头时会发生什么

代码和公式含有较少停用词，可能被偏好自然语言的规则丢弃。

按英语教科书训练的分类器，可能给非英语文本和非正式但有用的论坛答疑低分。FineWeb-Edu 的教育分可以有用，但不应直接用于代码数据，见 `dt-quality-clf-synth`。

同一个分数阈值，在不同语言上也不等价。例如，英语和某种低资源语言都用 0.6，通过率可能差一个数量级。可以按语言调整分位数，见 `dt-ppl-filter-code`、`dt-quality-filter-code`。

Muennighoff 的 datablations 还发现：较脏的数据集更可能从过滤中获益；已经较干净的数据，再过滤的收益可能很小，甚至损失覆盖。这个方向与 FineWeb 的观察一致。

## 怎么选阈值

例如，分别保留 10% / 30% / 50%，用小模型对比知识、推理、代码和多语表现。再抽查 100 条被丢弃的样本，判断是否误删，并把各类通过率写进 dataset card。某种语言通过率明显下降时，先检查阈值，不要直接靠机器翻译填满配额。

PII、密钥、空抽取等确定性问题可以硬性拦截。主观质量分则应允许调整阈值、做消融，不能把两类检查都处理成不可调的硬规则。

苹果公开的方向是减弱过强启发式、加入按语言调整的模型过滤。FineWeb-Edu 保留 1.3T 的结果属于它自己的实验，不能说成苹果内部配方。

## 追问

- FineWeb-Edu 保留 1.3T，是否证明数据越少越好？这是他们在特定评测中的较佳结果。换任务后要重新试阈值，不能当成通用最优。
- 合成数据也需要过滤吗？需要，但应使用适合任务的验证器（verifier）。教师续写的困惑度可能很低，直接用网页 ppl 过滤会把错误内容也留下，见 `dt-ppl-filter-code`。
- 和 SemDeDup 一起用时先做什么？先用精确哈希和 MinHash 去掉复制内容，再做质量筛选。语义去重优先用于高价值子集，避免承担全量 embedding 的成本，见 `dt-semdedup-code`。
