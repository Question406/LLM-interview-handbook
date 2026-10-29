---
id: dt-wrap-rephrase
section: good-data
order: 12
level: A
title: 用 LLM 把网页改写成干净段落，这算做好数据吗？
quick: >-
  算一种有用的 data augmentation，前提是和原文一起用：清理后的原文和改写版本一起训，再验证样本效率有没有提高。WRAP 在 C4
  上公开报告过约 3 倍样本效率，但改写不增加新事实，也解决不了许可、evaluation contamination 和 teacher
  错误，所以要保留原文，记下 teacher 和来源。
companies:
  - apple
tags:
  - Apple
  - Synthetic Data
  - Data Quality
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: >-
      Rephrasing the Web: A Recipe for Compute and Data-Efficient Language
      Modeling
    url: 'https://arxiv.org/abs/2401.16380'
    type: primary
  - title: The Curse of Recursion / Model Collapse
    url: 'https://arxiv.org/abs/2305.17493'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

算，前提是和原文一起用。用 LLM 改写网页能改善结构、提高样本效率，但它改的只是表达方式，不增加新事实。所以要保留原文、和改写版本一起训，再用对照验证效果。

举个例子，一个网页里塞满了 HTML 残留、过长的列表和重复导航，改写成清楚的段落后，模型就少花 token 去学页脚这类格式噪声。Maini 等的 WRAP 就是这么做的：让 LLM 把结构较差的网页改写成清晰段落，再和原文一起训，在 C4 上公开报告过约 3 倍的 pre-training 样本效率。Phi 的教科书合成更偏向只保留干净的叙述，WRAP 则明确混了原文。所以 WRAP 支持的是混合训练，把抓到的网页全换成 teacher 生成的文章、当作唯一的 pre-training 来源，它没有验证过。

改写管不了事实和许可，也发现不了原文里藏着的评测题。它还会带来新问题：同一个 70B teacher 改写全库，数据可能都带上同一种文风。我会用多种改写指令，保留原文分组，免得 post-training 主要学到 teacher 的句子节奏。另外只对原文改写一次，并记下 teacher 版本和数据血缘；把改写结果反复交给模型继续改，会增加模型坍塌（collapse）的风险，见 `dt-when-not-synth`。

## 验证和成本

能验证的合成内容要先验证。网页改写没有 executor 能直接判断事实对不对，所以还是要抽查。

成本也得算。对 10B 文档跑 70B 的改写，可能比多训一些原文还贵。我会把改写的成本，和直接训练原文的成本与收益放在一起比；和 SemDeDup 类似，优先处理高价值分组，全量改写之前先算清值不值。

## 追问

**能只训改写、不训原文吗？**
WRAP 的主要结果来自混合训练。只训改写，可能丢掉代码、表格和脏话这类形式不整齐但有用的内容。

**先抽取还是先改写？**
先用 `dt-boilerplate-code` 取出正文，再决定要不要改写。导航本身没必要改成文章。

**改写能拿来补 multilingual 数据吗？**
可以用来补结构或 multilingual 数据。机器翻译要另外记来源，评测仍然用母语者写的题，见 `dt-locale-data`。

**改写过的数据还要查 contamination 吗？**
要。改写甚至可能让题面更接近评测的写法，输出要再过一遍 `dt-ngram-contam-code`。
