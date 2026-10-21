---
id: dt-web-extract
section: panel
order: 20
level: A
title: Panel：网页抽取失败有哪些，LLM 抽取什么时候才上？
quick: "LLM 抽取放在最后一档：先用静态规则抽取，失败了用 headless 浏览器重试，规则仍处理不好的领域页面才用 LLM 抽主内容，因为每页都跑大模型太贵。常见失败是把导航当正文、JavaScript 页面为空、扫描 PDF、广告打断正文。抽取器本身会改写文本，版本要记录，便于追查数据变化。"
companies:
  - apple
tags:
  - Apple
  - Web Crawl
  - Extraction
  - Applebot
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: The FineWeb Datasets
    url: https://arxiv.org/abs/2406.17557
    type: primary
  - title: Applebot model training and individual privacy rights
    url: https://support.apple.com/en-us/120320
    type: primary
---

LLM 抽取只在最后一档用：先做静态抽取，失败后用 headless 浏览器重试，规则仍处理不好的领域页面，再用 LLM 提取主内容。每页都调用一次 70B 成本太高；只依赖 `trafilatura` 一种规则，又可能抽不到 JavaScript 渲染的内容。

## 为什么抽取值得这么认真

抽取错误发生在训练之前，正文一旦被损坏，后面的过滤很难补回来。我见过的失败模式有：版权声明被当成正文、论坛回复顺序错乱、表格变成乱码、图片的 caption 丢失导致图文对不齐。图文对齐是后面阶段的事，但抽取阶段至少要让 alt 文本和图片待在一起。

## 现场的处理顺序

1. **先过 robots、付费墙和登录墙。** 不允许使用的页面不该进训练，见 `dt-legal-capability`。
2. **静态抽取。** 正文过短或者看起来像导航，放进 quarantine。
3. **headless 重试。** 只对静态抽取失败的 URL 用 headless，仍然为空的标成 `js_empty`。现代网站的大量内容不在静态 HTML 里，AFM 2025 也加强了 headless：整页加载、动态交互、执行 JS。
4. **领域页面才用 LLM 抽主内容。** 论文、文档、菜谱这类页面值得用；通用的列表页用规则就够。AFM 2025 把 LLM 放进抽取，主要用于领域文档，公开说法是效果常常比纯规则好，规则抽取仍然保留。
5. **抽出的正文继续走后续检查**：语言识别、PII、质量过滤、评测指纹。抽取器本身也会改写文本，所以它的版本要记录。过滤这一步也别定得太严，过于严格的启发式规则会丢掉好的 token，AFM 就减弱了规则，加重了按语言调整的模型过滤。

## 追问

- **LLM 抽取会不会把评测题写进正文？** 会，如果页面附近有评测题。抽完之后仍要比对评测指纹。
- **headless 成本怎么控制？** 只对静态抽取失败的 URL 使用。全量使用会大幅增加成本。
- **扫描版 PDF 怎么处理？** 走 OCR 桶，别当成短文本处理，并和 text-rich 的视觉数据汇合，见 `dt-multimodal-data`。
