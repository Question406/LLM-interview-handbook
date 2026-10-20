---
id: dt-worse-after-data
section: panel
order: 10
level: S
title: Panel：加了一批数据，目标切片掉了，怎么查？
quick: "先复现只换数据的对照，排除步数、解码和奖励变化。再按任务与来源检查负迁移、标签错误、配比失控、过难样本和评测泄漏。旧题降而新题不变，也可能是去除了污染；根据具体证据调整数据。"
companies:
  - apple
tags:
  - Apple
  - Debugging
  - Negative Transfer
  - Evaluation
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Data Mixing Laws
    url: https://arxiv.org/abs/2403.16952
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
  - title: FineWeb-Edu
    url: https://huggingface.co/spaces/HuggingFaceFW/blogpost-fineweb-edu
    type: primary
---

先确认新旧实验是否使用同样的模型初始化和训练设置，只改变了 `dataset_version`。如果其他设置也改了，还不能把退步归因于数据；也不应直接丢掉所有新数据或改学习率。

不这么选的理由：步数、打包长度、温度、奖励模型（RM） 要是一起改了，分不清是数据。常见是负迁移、标签反了、泄漏被洗掉之后原形毕露，或者评测自己不稳。别先回滚到「数据越多越好」。

## 同一份权重上，只该动 dataset_version

如果步数、打包长度、温度或 RM 同时改变，先分别对照。能复现「只加数据、别的不动」再往下查。版本怎么记见 `dt-repro-lineage`。

然后按这个顺序挖：

1. 切片。目标掉、锚点（英语摘要、安全、格式）也掉，像挤占。只有目标掉、邻域反而好，更像新数据标签反了，或者过难。
2. 新旧题。旧门禁掉、时间切新题不变，可能是你把泄漏洗掉了，能力本来就没那么高，见 `dt-contamination`。
3. 抽查新数据。过程假、语言标错、工具轨迹不可回放、图文对不齐。质量门见 `dt-quality-filter-code`。
4. 配比。新来源的实际 token 份额是否远超计划。按条数看配额，可能忽略不同样本的长度差异。
5. 空组 / 可学性。强化学习（RL） 或拒绝采样全错，见 `dt-teacher-bias`。

发现负迁移后，先保留锚点来源的最低配额，降低新来源的采样强度，或把它挪到更后的训练阶段。mid-training 对整体能力的影响范围通常比 post-training 更广。AFM 抬多语时用课程护英语，就是提前防这题。

现场我会这么讲：「通知摘要掉了 2 档。对照是同一步数。切开：英语锚点掉，新加的论坛多语份额实际到了 11% 而不是计划 3%，过滤器把带列表的好摘要当 boilerplate 扔了。我回滚该源，修过滤器，论坛配额锁 3%，锚点集强制进每个 batch。」别让评委听成「多语有害」。

## 追问

- **能不能用 损失（loss） 判断？** 新域 loss 高并不意外。是否退步，要看固定任务评测，不能只用混合后的交叉熵损失（CE）判断。
- **小模型没掉、大模型掉？** 容量不同，过拟合和挤占的阈值不同。以目标模型的冻结集为准，小模型只当筛选。
- **人评方差盖过 2 档？** 报置信区间和样本量。不够就先别定论，见 `dt-annotator-protocol`。
