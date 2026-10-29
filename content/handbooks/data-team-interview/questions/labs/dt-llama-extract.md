---
id: dt-llama-extract
section: labs
order: 12
level: A
title: Llama 3 §3.1：自研 HTML 抽取，URL / 文档 / 行三级 deduplication，哪级会 false rejection 好文本？
quick: >-
  最容易 false rejection 好文本的是行级
  deduplication：它删掉导航这类重复模板，也会删掉反复出现的好句，所以要按内容类型抽查。URL 级保留最新版本，文档级
  near-duplicates 的范围用下游实验选；抽取阶段数学、代码和 multilingual 分开处理，保留数学和代码结构以及图片 alt 文本。「每
  30M 篇中超过 6 次」是 Llama 自己的阈值，换数据要重新验证。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: primary
  - title: 'CCNet: Extracting High Quality Monolingual Datasets from Web Crawl Data'
    url: 'https://arxiv.org/abs/1911.00359'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

三级里最容易 false rejection 好文本的是行级 deduplication。它的本意是删掉导航、页脚这类在大量页面上重复的模板行，可高频出现的好句子，比如百科里的常见表述、某类引用句，也会被一起删掉。URL 级和文档级的风险小一些，不过文档级 deduplication 的范围同样要靠实验选。

先看 Llama 3 怎么做。它用自研解析器抽 HTML，保留数学、代码结构和图片 alt 文本，去掉 markdown 标记。deduplication 分三级：URL 级同一 URL 只保留最新版本的内容；文档级用全局 MinHash 去掉 near-duplicates 文档；行级把每 30M 篇文档分一个桶，某行在桶里出现超过 6 次就删除。语言识别用 fastText，区分 176 种语言。另外，他们按网站域名丢掉 personally identifiable information (PII) 密度高的网站和成人网站。

每一级都要单独定规则。抽取器本身先评估效果、记下版本。数学、代码和 multilingual 内容结构差别很大，一个通用抽取规则加一个通用质量分类器处理不好这三类，所以抽取和过滤要分别设计，见 `dt-quality-clf-synth`。

deduplication 的严格程度也要靠实验定。Llama 用全局 MinHash，FineWeb 选了快照内 deduplication，说明 deduplication 范围本身就是一个超参数，要用下游 ablation study 判断。行级 deduplication 尤其要按内容类型抽查，看删掉的是 boilerplate 还是高频好句。

## 追问

**6 次、30M 这个阈值能直接拿来用吗？**
不能，那是 Llama 自己的数，换数据要重新验证，能借的是方法。AFM 2025 报告公开写了用 headless 浏览器渲染、再用 LLM 抽主内容，也没给行级 deduplication 这类阈值。

**markdown 为什么有害？**
Llama 的 ablation study 显示，在以网页为主的 pre-training 里，markdown 标记本身不像自然语言。README、论文这类领域文档另说。

**行级删掉的好句补不回来怎么办？**
影响通常不大。高频百科句被删了，模型仍能从留存的页面里学到；相比之下，boilerplate 残留更伤。但还是要按内容类型检查，免得某类引用句被整类删光。

**PII 怎么处理？**
Llama 按域名丢掉高 PII 网站和成人网站，也就是在来源这一层先做限制，见 `dt-legal-capability`。

相关：`dt-web-extract`（LLM 抽取的做法）、`dt-global-dedup`（FineWeb 的 deduplication 范围）
