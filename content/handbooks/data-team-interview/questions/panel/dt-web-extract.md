---
id: dt-web-extract
section: panel
order: 20
level: A
title: Panel：网页抽取失败有哪些，LLM 抽取什么时候才上？
quick: 假设网页抽取后看起来很干净，却把代码缩进和表格对应关系删掉了。清理广告之外，还必须保住训练需要的内容结构。
companies:
  - apple
tags:
  - Apple
  - Web Crawl
  - Extraction
  - Applebot
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: The FineWeb Datasets
    url: 'https://arxiv.org/abs/2406.17557'
    type: primary
  - title: Applebot model training and individual privacy rights
    url: 'https://support.apple.com/en-us/120320'
    type: primary
---

## 回答思路

> **问题与场景：** 假设网页抽取后看起来很干净，却把代码缩进和表格对应关系删掉了。
>
> **做法与原因：** 我会按网页类型检查正文遗漏、模板残留、编码、数学公式与表格。
>
> **检查与取舍：** 验证不能只看抽取后字符数或人工观感，还要检查不同语言与内容类型的覆盖，以及后续任务效果。

## 可以这样回答

假设网页抽取后看起来很干净，却把代码缩进和表格对应关系删掉了。清理广告之外，还必须保住训练需要的内容结构。

我会按网页类型检查正文遗漏、模板残留、编码、数学公式与表格。先修可解释的解析规则；规则难覆盖的复杂页面，再用 LLM 抽取，并对原文核验新增或遗漏的信息。

验证不能只看抽取后字符数或人工观感，还要检查不同语言与内容类型的覆盖，以及后续任务效果。

## 技术备查

LLM 抽取只放在最后一档：先做静态抽取，失败了用 headless 浏览器重试，规则还处理不好的领域页面，再用 LLM 提主内容。每页都调一次 70B 成本太高；只靠 `trafilatura` 一种规则，又可能抽不到 JavaScript 渲染的内容。

抽取值得这么认真，是因为错误发生在训练之前，正文一旦被弄坏，后面的过滤很难补回来。常见的失败有版权声明被当成正文、论坛回复顺序错乱、表格变成乱码、图片的 caption 丢了导致 image-text pairs 不齐。image-text pairs 齐是后面阶段的事，但抽取阶段至少要让 alt 文本和图片待在一起。

动手的顺序是这样。先过 robots、付费墙和登录墙，不允许使用的页面不该进训练（`dt-legal-capability`）。然后静态抽取，正文过短或者看起来像导航的，放进 quarantine。

静态抽取失败的 URL 才用 headless 重试，还是空的标成 `js_empty`。现代网站的大量内容不在静态 HTML 里，AFM 2025 也加强了 headless：整页加载、动态交互、执行 JS。

论文、文档、菜谱这类领域页面才值得用 LLM 抽主内容，通用的列表页用规则就够。AFM 2025 把 LLM 放进抽取，主要用在领域文档上，公开说法是效果常常比纯规则好，规则抽取也还保留着。

抽出的正文接着走语言识别、PII、质量过滤、评测指纹这些检查。抽取器本身也会改写文本，所以它的版本要记下来。过滤这一步别定得太严，过于严格的启发式规则会丢掉好的 token，AFM 就减弱了规则，加重了按语言调整的模型过滤。

## 追问

**LLM 抽取会不会把评测题写进正文？**
会，如果页面附近有评测题。抽完之后仍要比对评测指纹。

**headless 成本怎么控制？**
只对静态抽取失败的 URL 用。全量用会大幅增加成本。

**扫描版 PDF 怎么处理？**
走 OCR 桶，别当成短文本处理，并和 text-rich 的视觉数据汇合，见 `dt-multimodal-data`。

**为什么抽取器的版本也要记？**
抽取器本身会改写文本。换了版本，正文就可能跟着变，记下版本才能追查数据是从哪一步开始变的。
