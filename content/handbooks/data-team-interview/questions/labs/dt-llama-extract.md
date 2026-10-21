---
id: dt-llama-extract
section: labs
order: 12
level: A
title: Llama 3 §3.1：自研 HTML 抽取，URL / 文档 / 行三级去重，哪级会误杀好文本？
quick: "最容易误杀好文本的是行级去重：它能删掉导航等重复模板，也会删掉反复出现的好句，所以要按内容类型检查。URL 级保留最新版本，文档级近重复的范围用下游实验选。抽取阶段数学、代码和多语言要分别处理，保留数学和代码结构以及图片 alt 文本。「每 30M 篇中超过 6 次」是 Llama 公开的阈值，换数据要重新验证。"
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

三级里最容易误杀好文本的是行级去重。它的本意是删掉导航、页脚这类在大量页面上重复的模板行，但高频出现的好句子（比如百科里的常见表述、某类引用句）也会被一起删掉。URL 级和文档级的风险小一些，但文档级去重的范围同样要靠实验选。

## Llama 3 怎么做

Llama 3 用自研解析器抽 HTML，保留数学、代码结构和图片 alt 文本，去掉 markdown 标记。去重分三级：

- **URL 级**：同一 URL 只保留最新版本的内容。
- **文档级**：用全局 MinHash 去掉近重复文档。
- **行级**：每 30M 篇文档分一个桶，某行在桶里出现超过 6 次就删除。

语言识别用 fastText，区分 176 种语言。另外，他们按网站域名丢掉个人信息密度高的网站和成人网站。

## 为什么每一级都要单独选规则

抽取器本身要先评估效果并记录版本。数学、代码和多语言内容的结构差别很大，一个通用抽取规则加一个通用质量分类器处理不好这三类，所以要分别设计抽取和过滤，见 `dt-quality-clf-synth`。AFM 2025 报告公开写了用 headless 浏览器渲染、再用 LLM 抽主内容，但没给行级去重这类阈值。6 次、30M 是 Llama 自己的数，可以借鉴的是方法。

去重的严格程度也要靠实验定。Llama 用全局 MinHash，FineWeb 则选了快照内去重，说明去重范围本身是一个超参数，要用下游消融来判断。行级去重尤其要按内容类型抽查，看删掉的是 boilerplate 还是高频好句。

## 追问

- **markdown 为什么有害？** Llama 的消融显示，在以网页为主的预训练里，markdown 标记本身不像自然语言。README、论文这类领域文档另说。
- **行级删掉的好句补不回来怎么办？** 高频百科句被删了，模型仍能从留存的页面里学到；相比之下，boilerplate 残留更伤。但仍要按内容类型检查，避免某类引用句被整类删光。
- **PII 怎么处理？** Llama 按域名丢掉高 PII 网站和成人网站，也就是在来源这一层先做限制，见 `dt-legal-capability`。

相关：LLM 抽取的做法见 `dt-web-extract`，FineWeb 的去重范围见 `dt-global-dedup`。
