---
id: dt-web-extract
section: panel
order: 20
level: A
title: Panel：网页抽取失败有哪些，LLM 抽取什么时候才上？
quick: "先尝试静态规则抽取，失败后用 headless 浏览器重试；仍处理不好的领域页面，再考虑 LLM 提取主内容。常见问题包括把导航当正文、JavaScript 页面为空、扫描 PDF 和广告打断正文。抽取模型的版本也要记录，便于追查数据变化。"
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

先检查 robots 规则，不允许使用的页面不进训练。允许的页面先做静态抽取，失败后用 headless 浏览器重试；规则仍处理不好的领域页面，再用 LLM 提取主内容。抽取错误会在训练前就损坏正文，后续过滤很难补回来。

每页都调用一次 70B 成本太高；只依赖 `trafilatura` 一种规则，又可能抽不到 JavaScript 渲染的内容。AFM 2025 两条都写了：加强 headless，另外把 LLM 放进抽取。

## AFM 如何改进抽取

他们加强了 headless：整页加载、动态交互、跑 JS。现代站大量内容不在静态 HTML 里。另外把 LLM 放进抽取，尤其是领域文档，用来识别主内容，公开说法是常常比纯规则好。规则仍在。过于严格的启发式规则会丢掉好 token，所以他们减弱规则、加重按语言的模型过滤。

现场我会排这个顺序：

1. robots / 付费墙 / 登录墙。过不了就不该进训练，见 `dt-legal-capability`。
2. 静态抽取。正文过短或像导航，进 quarantine。
3. headless 重试。仍空，标 `js_empty`。
4. 领域页（论文、文档、菜谱）才 LLM 抽主内容。通用列表页不要。
5. 抽出的正文走语言、PII、质量、评测指纹。抽取器本身会改写，版本要记。

失败模式我见过这些：版权声明当正文、论坛回复顺序乱、表格变成乱码、图的 caption 丢了导致图文对不齐。图文对齐是后一段的事，抽取阶段至少别把 alt 和图拆开。

## 追问

- **LLM 抽取会不会把评测题写进正文？** 会，如果页面附近有。抽完仍要比评测指纹。
- **headless 成本？** 只对静态抽取失败的 URL 使用 headless。全量使用会增加很大成本。
- **PDF 扫描件？** 走 OCR 桶，不要当短文本。和 text-rich 视觉数据汇合，见 `dt-multimodal-data`。
