---
id: dt-wrap-rephrase
section: good-data
order: 12
level: A
title: 用 LLM 把网页改写成干净段落，这算做好数据吗？
quick: "改写可以作为数据增强：把清理后的原文与改写版本一起训练，再验证样本效率是否提高。WRAP 在 C4 上公开报告过约 3 倍样本效率，但改写没有增加新事实，也不能自动解决许可、评测污染和教师错误。保留原文，并记录教师与来源。"
companies:
  - apple
tags:
  - Apple
  - Synthetic Data
  - Data Quality
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: "Rephrasing the Web: A Recipe for Compute and Data-Efficient Language Modeling"
    url: https://arxiv.org/abs/2401.16380
    type: primary
  - title: The Curse of Recursion / Model Collapse
    url: https://arxiv.org/abs/2305.17493
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

用 LLM 改写网页，可以改善结构和样本效率，但仍应保留原文、通过对照验证效果。它改变的是表达方式，没有增加新事实，也不能替代收集原始语料。

Maini 等的 WRAP 让 LLM 把结构较差的网页改成清晰段落，再与原文一起训练，在 C4 上公开报告过约 3 倍的预训练样本效率。Phi 的教科书合成更偏向只保留干净叙述；WRAP 则明确混合原文。不能据此把 Applebot 的所有页面都换成教师生成的文章，作为唯一预训练来源。

## 改写能解决哪些问题

改写可以整理 HTML 残留、过长列表和重复导航，让模型少用 token 学习页脚等格式噪声。

它不能自动检查事实、许可或原文是否包含评测题。改写还可能让题面更接近评测表达，所以输出要再次经过 `dt-ngram-contam-code`。

同一个 70B 教师改写全库，也可能让数据都带上相同文风。应使用多种改写指令，并保留原文分组，避免后训练主要学到教师的句子节奏。

只对原文做一次改写，记录教师版本和数据血缘。把改写结果反复交给模型继续改写，会增加模型坍塌（collapse）的风险，见 `dt-when-not-synth`。

## 在苹果场景中怎么用

能验证的合成内容先验证。不过，网页改写没有执行器可以直接判断事实是否正确，仍需要抽查。可以用它补结构或多语数据；机器翻译要另记来源，评测仍用母语者题，见 `dt-locale-data`。

对 10B 文档运行 70B 改写，可能比多训练一些原文更贵。与 SemDeDup 类似，优先针对高价值分组做，而不是默认处理全量。

## 追问

- 能只训改写、不训原文吗？WRAP 的主要结果来自混合训练。只训改写可能丢掉代码、表格和脏话等形式不整齐但有用的内容。
- 应先抽取还是先改写？先用 `dt-boilerplate-code` 取出正文，再决定是否改写。导航本身没有必要改成文章。
- 成本如何判断？比较改写成本与直接训练原文的成本和收益，优先处理高价值分组。
