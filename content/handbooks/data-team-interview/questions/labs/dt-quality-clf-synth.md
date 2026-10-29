---
id: dt-quality-clf-synth
section: labs
order: 7
level: A
title: Llama / Phi / FineWeb-Edu：质量分类器用合成标签训，坑在哪？
quick: >-
  坑在于一个分类器、一个阈值套所有数据：teacher 偏爱正式英文时，论坛内容和 low-resource 语言会被大量误删，和评测同族的分类器还会让
  contamination 更容易混进来。所以按语言和领域分别训练或 calibration，代码、数学、对话不用网页教育价值标准；阈值用 small
  model 下游实验选，teacher 版本和抽查一致率记进 dataset card。
companies:
  - apple
tags:
  - Meta
  - FineWeb
  - Quality Filter
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: The FineWeb Datasets
    url: 'https://arxiv.org/abs/2406.17557'
    type: primary
  - title: The Llama 3 Herd of Models
    url: 'https://arxiv.org/abs/2407.21783'
    type: primary
  - title: Textbooks Are All You Need
    url: 'https://arxiv.org/abs/2306.11644'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

最大的坑是把 Llama、Phi 或 FineWeb-Edu 的做法简化成「全球一个分类器、一个阈值」。合成标签来自 teacher model，teacher 的偏好会原样带进过滤结果。

比如 teacher 偏爱正式英文，一篇讲修车经验的论坛帖、一篇写得很好的 low-resource 语言文章，分数都会偏低，阈值一卡就被删掉了。阈值太严本身也是问题：启发式规则太严会丢掉好 token，模型过滤的阈值太严也一样。

所以分类器要分开做。先由人或 teacher model 标一小批 seed，分清教育内容、垃圾内容、代码这些类别，标签来自许可网页加人工抽查。然后让 teacher 扩充标签，人工抽查、calibration，再蒸一个能批量处理网页的小分类器。过滤时先执行明确的硬性规则，再跑分类器，阈值按语言调，见 `dt-quality-filter-code`；代码、数学和对话各用适合自己的分类器。阈值用 small model 的下游实验来选。最后把合成标签用的 teacher 版本和抽查一致率写进 dataset card，见 `dt-repro-lineage`。

## 追问

**分类器和评测同族会怎样？**
过滤会偏向「长得像评测的页面」，contamination 也更容易混进来。比如用和 GSM8K 同族的分类器打分，留下的数学页面会越来越像考题，见 `dt-synth-bench-trap`。

**公开的几家是怎么做的？**
Llama 3 用 Llama 2 训出质量分类器；FineWeb-Edu 用 Llama-3-70B-Instruct 合成教育分，再滤出 1.3T；Phi 走教科书风格。FineWeb 对 cutoff 做过 ablation study，AFM 2025 也更多地使用模型过滤，并按语言选择标签。

**PPL 过滤呢？**
适合当辅助检查。CCNet 把 reference model 的低 perplexity 当作质量信号，它偏向常见文风，对 long-tail 知识不友好。

**分类器分数能拿来挖新数据吗？**
能，但判断内容是否新颖时，还要看它和现有数据的距离，见 `dt-novel-bootstrap`。
