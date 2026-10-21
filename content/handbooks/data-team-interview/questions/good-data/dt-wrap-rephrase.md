---
id: dt-wrap-rephrase
section: good-data
order: 12
level: A
title: 用 LLM 把网页改写成干净段落，这算做好数据吗？
quick: "算一种有用的数据增强，前提是和原文一起用：把清理后的原文与改写版本一起训练，再验证样本效率是否提高。WRAP 在 C4 上公开报告过约 3 倍样本效率，但改写没有增加新事实，也不能自动解决许可、评测污染和教师错误。要保留原文，并记录教师与来源。"
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

算一种有用的数据增强，前提是和原文一起用。用 LLM 改写网页可以改善结构、提高样本效率，但它改变的只是表达方式，没有增加新事实。所以要保留原文、和改写版本一起训练，并用对照验证效果。

## 公开证据说明了什么

Maini 等的 WRAP 让 LLM 把结构较差的网页改写成清晰的段落，再和原文一起训练，在 C4 上公开报告过约 3 倍的预训练样本效率。Phi 的教科书合成更偏向只保留干净的叙述；WRAP 则明确混合了原文。所以 WRAP 的证据支持的是混合训练；把抓到的网页全部换成教师生成的文章、当作唯一的预训练来源，它没有验证过。

## 改写能解决什么，不能解决什么

改写能整理 HTML 残留、过长的列表和重复导航，让模型少花 token 去学页脚这类格式噪声。

它不能自动检查事实、许可，也不能发现原文里有没有评测题。改写甚至可能让题面更接近评测的表达，所以输出要再过一遍 `dt-ngram-contam-code`。

改写还会带来新问题。同一个 70B 教师改写全库，数据可能都带上同一种文风。应该用多种改写指令，并保留原文分组，避免后训练主要学到教师的句子节奏。另外，只对原文做一次改写，并记录教师版本和数据血缘；把改写结果反复交给模型继续改写，会增加模型坍塌（collapse）的风险，见 `dt-when-not-synth`。

## 验证和成本

能验证的合成内容要先验证。网页改写没有执行器能直接判断事实对不对，所以仍需要抽查。可以用它补结构或多语数据；机器翻译要另外记录来源，评测仍然用母语者写的题，见 `dt-locale-data`。

成本也要算。对 10B 文档跑 70B 的改写，可能比多训练一些原文还贵。和 SemDeDup 类似，优先处理高价值分组，全量改写要先算清值不值。

## 追问

- 能只训改写、不训原文吗？WRAP 的主要结果来自混合训练。只训改写，可能丢掉代码、表格和脏话这类形式不整齐但有用的内容。
- 先抽取还是先改写？先用 `dt-boilerplate-code` 取出正文，再决定要不要改写。导航本身没必要改成文章。
- 成本怎么判断？比较改写的成本和直接训练原文的成本与收益，优先处理高价值分组。
