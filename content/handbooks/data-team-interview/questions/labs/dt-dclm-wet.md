---
id: dt-dclm-wet
section: labs
order: 15
level: A
title: DataComp-LM：从 Common Crawl WET 起步，为什么公开集常吃亏？
quick: "先检查正文是怎样提取出来的，再讨论质量分类器。WET 是别人已经提取好的文本，WARC 和渲染后的 DOM 则允许重新抽取。DCLM 的实验中，从 HTML 重新提取文本后，Core 指标比使用 WET 高至少 2.5 点；AFM 还使用 headless 浏览器和 LLM 提取主内容。"
companies:
  - apple
tags:
  - DCLM
  - Extraction
  - Pre-training
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "DataComp-LM: In search of the next generation of training sets for language models"
    url: https://arxiv.org/abs/2406.11794
    type: primary
  - title: The FineWeb Datasets
    url: https://arxiv.org/abs/2406.17557
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先确认数据许可和 robots 规则，见 `dt-legal-capability`。然后问清输入：是从 WARC 或渲染后的 DOM 提取正文，还是使用别人已经抽好的 WET 文本？抽取后再考虑过滤：启发式不能过于严格，AFM 也曾减弱规则；模型过滤要按语言调整，代码和数学使用适合各自内容的分类器，见 `dt-quality-clf-synth`、`dt-llama-extract`。去重范围要通过下游实验选择，见 `dt-global-dedup`。遇到「开源网页集让分数提高 15%」的说法，先排查抽取质量和评测污染，再分析分类器，见 `dt-synth-bench-trap`。

一上来就谈 fastText 阈值，会漏掉更早的问题：正文是如何提取的。预训练数据设计题常从「拿一份开源网页集开训」开始。C4 / RedPajama / Dolma-V1 走 WET，抽取器丢失或误收的内容，会限制后面的质量分类器能做到什么。

接到苹果：AFM 已经在用 headless 和 LLM 抽主内容，还会处理 JavaScript 渲染带来的内容。AskLLM 全库他们比过，贵，而且没赢 fastText；LLM 提取主内容适合用在规则提取失败的领域页面上，见 `dt-web-extract`。WET 能当弱基线，报告里要写你比的是 WET 还是重抽。输入是 Applebot / 许可页，不是下载一份开源 WET 直接开训。

公开锚点：DCLM-Pool 是 2023 年前的 Common Crawl，约 2000 亿文档；同一套 RefinedWeb 启发式下，Resiliparse 和 Trafilatura 的 Core 都比 WET 高至少 2.5 点，Resiliparse 大约快 8 倍。fastText（OpenHermes-2.5 + r/ExplainLikeImFive）赢了 PageRank、语义去重、嵌入线性分类器、AskLLM、困惑度。DCLM-Baseline 大约包含 4T token；他们自己写了这份 baseline 不是生产配方，代码和数学要另补。

## 追问

- **fastText 教的是 OH + ELI5，会不会偏论坛口吻？** 会。教育页面和 API 文档的得分可能被压低。可以按领域使用不同分类器，再通过小模型消融实验选择阈值。DCLM 公开阈值是他们的数。
- **为什么不直接 AskLLM 全库？** 他们比过，贵，而且没赢 fastText。LLM 抽主内容只给规则失败的领域页，见 `dt-web-extract`。
- **WET 一点都不能用？** 能当弱基线。报告里要写你比的是 WET 还是重抽，否则别人无法复现。
