---
id: dt-dclm-wet
section: labs
order: 15
level: A
title: DataComp-LM：从 Common Crawl WET 起步，为什么公开集常吃亏？
quick: >-
  因为瓶颈常在正文抽取。WET 是 Common Crawl 预先抽好的纯文本，抽错漏掉的内容后面的质量分类器补不回来。DCLM 固定同一套过滤、只把 WET
  换成从 WARC 原始 HTML 重新抽取，Core 就高了至少 2.5 点，所以先定抽取，再调分类器和阈值。
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
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: >-
      DataComp-LM: In search of the next generation of training sets for
      language models
    url: 'https://arxiv.org/abs/2406.11794'
    type: primary
  - title: The FineWeb Datasets
    url: 'https://arxiv.org/abs/2406.17557'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

公开集吃亏，多半亏在第一步：正文是怎么从网页里抽出来的。C4、RedPajama、Dolma-V1 都直接用 Common Crawl 的 WET，也就是别人已经抽好的纯文本。抽取器漏掉的正文、误收的导航和页脚，后面的质量分类器补不回来。所以这题我会先问输入是 WET 还是原始 WARC，再谈过滤阈值。

举个例子，一篇讲排序算法的教程，代码块在 WET 里被抽成了一堆没有缩进的碎行，旁边还混着侧栏的推荐文章。分类器看到的就是这样一段文本，给它打低分很正常，可原网页其实是好数据。WET 用的是一套通用规则，碰到代码块、表格、公式或 JavaScript 渲染的内容，经常抽得残缺，或者混进大量模板文字。代码和数学页面受影响最大，它们的价值恰好在这些结构里。

DCLM 做了一个很干净的对照。DCLM-Pool 取 2023 年前的 Common Crawl，约 2000 亿文档，固定 RefinedWeb 那套启发式过滤，只换抽取器。用 Resiliparse 或 Trafilatura 从 HTML 重新抽，Core 指标都比 WET 高至少 2.5 点，Resiliparse 还快约 8 倍。换抽取器本身就有稳定的收益。

抽取定下来，才轮到过滤。DCLM 比了 PageRank、semantic deduplication、embedding 上的线性分类器、AskLLM、perplexity，最后赢的是一个 fastText 分类器，正样本取 OpenHermes-2.5 和 r/ExplainLikeImFive，筛出来的 DCLM-Baseline 约 4T token。论文也写明这只是 baseline，代码和数学要另外补。过滤时启发式规则要留余地，FineWeb 和 AFM 2025 报告都减弱过过强的规则，见 `dt-filter-too-hard`；模型过滤按语言调，代码和数学用各自适配的分类器，见 `dt-quality-clf-synth`；deduplication 范围也靠下游实验选，见 `dt-global-dedup`。

如果手里有原始 HTML，抽取还能做得更细：先用 headless 浏览器渲染页面，拿到 JavaScript 生成的内容，再对规则抽取失败的领域页面用 LLM 抽主内容，AFM 2025 报告公开描述过这种做法。LLM 抽取成本高，用在规则失败的那部分页面上就够了，见 `dt-web-extract`、`dt-llama-extract`。

## 追问

**有人说换了某个开源网页集，分数涨了 15%，你先查什么？**
先查抽取质量有没有变，再查评测有没有被 contamination（见 `dt-synth-bench-trap`），最后才看分类器。

**fastText 用 OpenHermes + ELI5 当正样本，会不会偏论坛口吻？**
会。教育页面和 API 文档可能被压低分数。可以按领域训不同的分类器，再用 small model ablation study 选阈值。DCLM 公开的阈值是在他们的数据上调出来的，换数据要重新调。

**为什么不直接用 AskLLM 筛全库？**
DCLM 比过，成本高，效果也没赢 fastText。LLM 更适合用在规则抽取失败的那部分页面上。

**WET 完全不能用吗？**
可以当弱 baseline。报告里写清楚比的是 WET 还是重新抽取的文本，别人才能复现结论。

相关：`dt-legal-capability`（抓取的许可前提）
