---
id: dt-dclm-wet
section: labs
order: 15
level: A
title: DataComp-LM：从 Common Crawl WET 起步，为什么公开集常吃亏？
quick: "因为瓶颈往往在正文抽取。WET 是 Common Crawl 预先抽好的纯文本，抽错或漏掉的内容，后面的质量分类器补不回来。DCLM 固定同一套过滤，只把 WET 换成从 WARC 原始 HTML 重新抽取，Core 就高了至少 2.5 点。所以先定抽取，再调分类器和阈值。"
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

公开集吃亏，多半亏在第一步：正文是怎么从网页里抽出来的。C4、RedPajama、Dolma-V1 都直接用 Common Crawl 的 WET，也就是别人已经抽好的纯文本。抽取器漏掉的正文、误收的导航和页脚，后面的质量分类器补不回来。所以这题我会先问输入是 WET 还是原始 WARC，再谈过滤阈值。

## 为什么抽取决定上限

质量分类器只能在已有文本里挑。WET 用的是一套通用规则，遇到代码块、表格、公式或 JavaScript 渲染的内容，经常抽成残缺文本，或者混进大量模板文字。分类器看到的输入已经坏了，打分自然不准。代码和数学页面受影响最大，因为它们的价值恰好在这些结构里。

DCLM 做了一个干净的对照：DCLM-Pool 取 2023 年前的 Common Crawl，约 2000 亿文档，固定 RefinedWeb 那套启发式过滤，只换抽取器。用 Resiliparse 或 Trafilatura 从 HTML 重新抽取，Core 指标都比 WET 高至少 2.5 点，其中 Resiliparse 还快约 8 倍。也就是说，换抽取器本身就有稳定收益。

## 抽完之后再做过滤

抽取定下来后，DCLM 比较了多种质量信号：PageRank、语义去重、嵌入上的线性分类器、AskLLM、困惑度，最后赢的是一个 fastText 分类器，正样本取 OpenHermes-2.5 和 r/ExplainLikeImFive。用它筛出的 DCLM-Baseline 约 4T token。论文也写明这只是 baseline，代码和数学需要另外补。

过滤这一步还有两点：启发式规则要留余地，FineWeb 和 AFM 2025 报告都减弱过过强的规则（见 `dt-filter-too-hard`）；模型过滤按语言调整，代码和数学用各自适配的分类器（见 `dt-quality-clf-synth`）。去重范围也要靠下游实验选，见 `dt-global-dedup`。

## 能控制原始抓取时

如果手里有原始 HTML，可以把抽取做得更细：先用 headless 浏览器渲染页面，拿到 JavaScript 生成的内容，再对规则抽取失败的领域页面用 LLM 抽主内容。AFM 2025 报告公开描述过这种做法。LLM 抽取成本高，用在规则失败的那部分页面上就够了，见 `dt-web-extract`、`dt-llama-extract`。

如果有人说「换了某个开源网页集，分数涨了 15%」，我会先排查两件事：抽取质量有没有变，评测有没有被污染（见 `dt-synth-bench-trap`），然后再看分类器。

## 追问

- **fastText 用 OpenHermes + ELI5 当正样本，会不会偏论坛口吻？** 会。教育页面和 API 文档可能被压低分数。可以按领域训练不同分类器，再用小模型消融选阈值。DCLM 公开的阈值是在他们的数据上调出来的，换数据要重新调。
- **为什么不直接用 AskLLM 筛全库？** DCLM 比过，成本高，效果也没赢 fastText。LLM 更适合用在规则抽取失败的那部分页面上。
- **WET 完全不能用吗？** 可以当弱基线。报告里写清楚比的是 WET 还是重新抽取的文本，别人才能复现结论。

相关：抓取的许可前提见 `dt-legal-capability`。
