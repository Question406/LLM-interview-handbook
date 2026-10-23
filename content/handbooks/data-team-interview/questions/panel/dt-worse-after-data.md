---
id: dt-worse-after-data
section: panel
order: 10
level: S
title: Panel：加了一批数据，目标切片掉了，怎么查？
quick: "先复现只换数据的对照，排除步数、解码和奖励的变化；确认是数据造成的，再按切片、新旧题、抽查、配比、可学性的顺序查负迁移、标签错误、配比失控、过难样本和评测泄漏。旧题降而新题不变，也可能只是洗掉了污染。按查到的证据调整对应的数据，全部回滚会把有用的部分一起丢掉。"
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

先确认新旧实验用的是同样的模型初始化和训练设置，只有 `dataset_version` 不同。别的设置也改了，就还不能把退步归到数据头上，这时丢掉所有新数据或去改学习率都太早。

举个例子，摘要切片掉了 2 档，对照是同一步数。切开看，英语锚点掉了；新加的论坛多语数据计划占 3%，实际份额到了 11%；过滤器还把带列表的好摘要当成 boilerplate 扔了。处理是回滚这个来源，修好过滤器，论坛配额锁在 3%，锚点集强制进每个 batch。结论落在这个来源配比失控上，和多语数据本身好坏无关。

第一步只让数据变。步数、打包长度、温度、奖励模型（RM）要是一起改了，就分不清是不是数据的问题，先分别做对照。能复现「只加数据、别的不动也会掉」，再往下查，版本怎么记见 `dt-repro-lineage`。常见的原因有负迁移、标签反了、泄漏被洗掉之后显出真实水平，或者评测本身不稳。

接着我会先切片。目标切片掉了，英语摘要、安全、格式这些锚点也掉了，像是被新数据挤占；只有目标掉、邻近任务却变好，更像新数据的标签反了，或者题太难。再看新旧题，旧门禁掉了、按时间切出的新题没变，可能是把泄漏洗掉了，能力本来就没那么高（`dt-contamination`）。然后抽查新数据，看有没有过程是假的、语言标错、工具轨迹不可回放、图文对不齐，质量门见 `dt-quality-filter-code`。

再看配比，新来源的实际 token 份额是不是远超计划。按条数定配额，会忽略不同样本的长度差异。最后看可学性，强化学习（RL）或拒绝采样时整组全错，组里就没有学习信号（`dt-teacher-bias`）。

查到是负迁移，就先给锚点来源保留最低配额，降低新来源的采样强度，或者把它挪到更靠后的训练阶段。mid-training 对整体能力的影响范围通常比 post-training 更广。AFM 抬高多语比例时用课程保护英语，就是在提前防这个问题。

## 追问

**能不能用损失（loss）判断？**
不能。新领域的 loss 高并不意外，是否退步要看固定任务的评测，混合后的交叉熵损失（CE）说明不了。

**小模型没掉、大模型掉了？**
容量不同，过拟合和挤占的阈值也不同。以目标模型的冻结集为准，小模型只用来做筛选。

**人评的方差比 2 档还大？**
报置信区间和样本量。样本不够就先别下结论，见 `dt-annotator-protocol`。

**查到是新数据的问题，全部回滚行不行？**
不划算。全部回滚会把有用的部分一起丢掉，按查到的证据调整对应的那个来源就行，比如上面只回滚了论坛来源、修了过滤器。
