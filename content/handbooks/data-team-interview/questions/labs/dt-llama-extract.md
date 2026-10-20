---
id: dt-llama-extract
section: labs
order: 12
level: A
title: Llama 3 §3.1：自研 HTML 抽取，URL / 文档 / 行三级去重，哪级会误杀好文本？
quick: "数学、代码和多语言内容要分别处理，提取正文时保留数学和代码结构，以及图片 alt 文本。行级去重能删导航，也可能误删反复出现的好句；去重范围需要用下游实验选择。「每 30M 篇中超过 6 次」是 Llama 的公开阈值，不能当作苹果内部规则。"
companies:
  - apple
tags:
  - Meta
  - Llama
  - Extraction
  - Dedup
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: "CCNet: Extracting High Quality Monolingual Datasets from Web Crawl Data"
    url: https://arxiv.org/abs/1911.00359
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先评估抽取器的效果，并记录它的版本。数学、代码和多语言内容分别处理，不能全部套用同一个通用质量分类器，见 `dt-quality-clf-synth`。三级去重也要分别选择规则：同一 URL 保留最新版本；文档级近重复的处理范围通过下游消融实验选择；行级去重删除导航等重复模板，但也可能误删高频好句，需要按内容类型检查。

`dt-web-extract`、`dt-global-dedup` 分别讨论 AFM 和 FineWeb 的相关做法；这里用 Llama 的公开方法说明在苹果场景下如何作选择。

回答抽取问题，不能停在「调用 trafilatura」，也不能认为去重越严格越好。Llama 使用全局 MinHash，FineWeb 选择快照内去重。范围本身是需要实验选择的超参数，应通过下游消融判断。

接到苹果：AFM 写了 headless 和 LLM 抽主内容，没写行级 6/30M 这种阈值。可以借鉴的是评估抽取器、按内容分别处理，以及用下游实验选择去重范围。6 次、30M 是 Llama 的数。他们发现，对主要用网页训练的模型，保留 markdown 标记可能有害；README 和论文等领域文档要另作判断。Llama 按网站域名丢弃个人信息密度高的网站和成人网站，Applebot 也避开大规模汇聚个人信息的站点，两者都在限制来源，见 `dt-legal-capability`。输入是 Applebot 公开页和许可集。

Llama 3 使用自研解析器，保留数学、代码结构和图片 alt 文本，并去掉 markdown 标记。同一 URL 留最新内容，全局 MinHash 去除近重复文档；每个 30M 篇文档的桶中，某行出现超过 6 次就删除。fastText 用来区分 176 种语言。

## 追问

- **markdown 为什么有害？** 他们的消融：网页为主的预训练里，markdown 标记本身不像自然语言。领域文档（README、论文）另说。
- **行级删掉的好句补不回来？** 高频百科句被删，模型仍能从留存页学到。boilerplate 残留更伤。仍要按内容类型检查，避免某类引用句被全部删掉。
- **PII？** Llama 写了按域丢掉高 PII / 成人站。和 Applebot 避开大规模汇聚个人信息的站是同一类门，见 `dt-legal-capability`。
