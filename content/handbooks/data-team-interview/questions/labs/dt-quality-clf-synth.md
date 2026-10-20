---
id: dt-quality-clf-synth
section: labs
order: 7
level: A
title: Llama / Phi / FineWeb-Edu：质量分类器用合成标签训，坑在哪？
quick: "按语言和领域分别训练或校准质量分类器，代码、数学和对话不能统一用网页教育价值标准过滤。合成标签要记录教师版本和人工抽查一致率；过滤阈值通过小模型下游实验选择，避免一个分类器、一个阈值误删大量好数据。"
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
updatedAt: 2026-10-12
sources:
  - title: The FineWeb Datasets
    url: https://arxiv.org/abs/2406.17557
    type: primary
  - title: The Llama 3 Herd of Models
    url: https://arxiv.org/abs/2407.21783
    type: primary
  - title: Textbooks Are All You Need
    url: https://arxiv.org/abs/2306.11644
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

先由人或教师模型标注少量种子样本，区分教育内容、垃圾内容、代码等类别。再让教师扩充标签，人工抽查并校准，最后蒸馏出能批量处理网页的小模型。过滤阈值通过小模型的下游实验选择。先执行明确的硬性规则，再运行分类器，并按语言调整阈值，见 `dt-quality-filter-code`。代码、数学和对话使用各自适合的分类器。合成标签的教师版本与抽查一致率都写进 dataset card，见 `dt-repro-lineage`。

不能把 Llama、Phi 或 FineWeb-Edu 的方法简化成「全球用一个分类器和一个阈值」。教师模型偏爱正式英文时，论坛内容和低资源语言可能被大量误删。分类器和 GSM8K 同族时，过滤会偏向「像评测的页」，污染反而更容易，见 `dt-synth-bench-trap`。

AFM 2025 也更多使用模型过滤，并按语言选择标签。启发式规则太严格会丢掉好 token，模型过滤阈值太严格也一样。分类器分数还可以帮助挖掘数据，但判断内容是否新颖时，仍需要考虑它与现有数据的距离，见 `dt-novel-bootstrap`。PPL 过滤中，CCNet 把参考模型的低困惑度作为质量信号。这容易偏向常见文风，对长尾知识不友好，可以用作辅助检查，不能作为唯一标准。标签应来自许可网页和人工抽查，不用用户文档作为起点。

公开锚点：Llama 3 用 Llama 2 训过的质量分类器；FineWeb-Edu 用 Llama-3-70B-Instruct 合成教育分，再滤出 1.3T；Phi 走教科书味。FineWeb 对 cutoff 做过消融。

## 追问

- **PPL 过滤呢？** CCNet 用参考模型低困惑当质量。它偏常见文风，长尾知识差。可当弱门，当不了唯一门。
- **合成标签要不要进 lineage？** 要。教师版本和抽查一致率写进 dataset card，见 `dt-repro-lineage`。
