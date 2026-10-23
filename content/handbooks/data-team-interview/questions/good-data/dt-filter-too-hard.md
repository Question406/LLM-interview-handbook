---
id: dt-filter-too-hard
section: good-data
order: 6
level: S
title: 质量过滤会不会滤过头？FineWeb 和 AFM 的公开教训是什么？
quick: "会。过滤器偏好「像英语维基或教科书」的文本，就可能把代码、公式、论坛答疑和低资源语言一起删掉。阈值要试几档，比较各语言通过率和下游指标变化。FineWeb 和 AFM 2025 都提到减弱过强的启发式，滤到多严要靠实验定。"
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

会。过滤越严，数据不一定越好。偏好「像英语维基或教科书」的过滤器，会把代码、公式、论坛答疑和低资源语言一起删掉。所以阈值要靠实验来选：试几档保留率，同时看各类内容的通过率和下游指标变化 $\Delta$，判断删掉的东西是不是真的没用。

举个例子，英语和某种低资源语言都用 0.6 当阈值，通过率可能差一个数量级。同一个分数在不同语言上并不等价，得按语言调分位数，见 `dt-ppl-filter-code`、`dt-quality-filter-code`。

毛病出在「像参考语料」这个信号上。CCNet 用基于维基训练的 KenLM 困惑度筛网页，后来不少公开数据集也拿「像参考语料」当质量信号，可它对有些语言和任务并不适用。代码和公式里停用词少，容易被偏好自然语言的规则丢掉；按英语教科书训练的分类器，会给非英语文本和不正式但有用的论坛答疑打低分。FineWeb-Edu 的教育分有用，但不该直接拿去筛代码数据，见 `dt-quality-clf-synth`。

公开报告里也能看到这个教训。FineWeb 的消融发现过强的启发式规则会伤结果；AFM 2025 报告公开说他们减弱了过强的启发式，加入按语言调整的模型过滤，因为旧规则会丢掉有价值的 token。过滤的收益还取决于数据原本有多脏，Muennighoff 的 datablations 发现较脏的数据更可能从过滤中获益，已经比较干净的数据再滤，收益可能很小，甚至损失覆盖，和 FineWeb 的观察方向一致。

## 阈值怎么选

我会分几档跑，比如保留 10%、30%、50%，用小模型对比知识、推理、代码和多语表现。再抽 100 条被丢掉的样本看有没有误删，把各类通过率写进 dataset card。某种语言的通过率明显掉了，先回头查阈值，别直接拿机器翻译把配额填满。

两类检查分开处理。PII、密钥、空抽取这种确定性问题可以硬性拦掉；主观质量分要留出调阈值、做消融的空间，写成固定硬规则就没法再调了。

## 追问

**FineWeb-Edu 只保留了 1.3T，是不是说明数据越少越好？**
不是这个意思。这是他们在特定评测上较好的结果，属于他们自己的实验设置，换了任务要重新试阈值。

**合成数据也要过滤吗？**
要，而且要用适合任务的验证器（verifier）。教师续写的困惑度往往很低，直接拿网页 ppl 去筛，会把错误内容也留下，见 `dt-ppl-filter-code`。

**和 SemDeDup 一起用，先做哪个？**
先用精确哈希和 MinHash 去掉复制内容，再做质量筛选。语义去重优先用在高价值子集上，省掉全量 embedding 的成本，见 `dt-semdedup-code`。

**某个语言通过率掉了很多，怎么办？**
先查是不是阈值没按语言调。分位数调好之后再看下游，不要用机器翻译去补配额。
