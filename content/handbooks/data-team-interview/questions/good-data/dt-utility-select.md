---
id: dt-utility-select
section: good-data
order: 11
level: A
title: 数据选择能不能讲成一个效用函数，而不是一堆启发式？
quick: "可以。先给样本定义效用 $u(x)$，说明它为什么值得训练，再决定按阈值筛选、按桶分配配额，还是按分数加权抽样。Albalak 等人的 2024 年综述把数据选择拆成这两步。启发式、ppl、分类器、EL2N 和强化学习采样，主要区别在于怎样估计效用。"
companies:
  - apple
tags:
  - Apple
  - Data Quality
  - Data Mix
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: A Survey on Data Selection for Language Models
    url: https://arxiv.org/abs/2402.16827
    type: primary
  - title: "DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining"
    url: https://arxiv.org/abs/2305.10429
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

我会先定义样本的效用 $u(x)$，再说明分数怎样影响选择：高于阈值才保留，或按分数决定抽样概率。这样能解释每条规则为什么存在，而不只是报出 20 条规则。

常见误区是：把启发式清单当方法本身。Albalak 等 2024 综述给了一个能写在白板上的框：对每条样本估效用 $u(x)$，再用选择机制决定怎么用这个效用。启发式、ppl、分类器、EL2N、强化学习（RL） 采样，差在效用怎么定义。

## 效用从哪来

效用可以用引用次数、域名、长度、KenLM 困惑度、质量分类器分数或 CLIP 分数来估计。也可以看验证器是否通过，或偏好标注里好坏回答的分差。网页和工具轨迹的用途不同，不能共用一套分数，见 `dt-good-data-def`。

DoReMi 把 $u$ 定义在域上，不是文档上：小模型 Group DRO 学域权重，再拿去训大模型。能不能直接搬到大模型，见 `dt-doremi-mix`。

基于可验证奖励的强化学习（RLVR） 的效用是 grader 通过。偏好学习的效用是 margin。别把网页教育分接到这两段。

## 选择机制

硬切：`u >= t`。实现简单，阈值漂一点通过率就跳，见 `dt-quality-filter-code` 的软带。

配额：先保证每类数据至少有一定数量的 token，再在这一类内部按 $u$ 抽样。AFM 多语配额是这种。

重加权：不丢样本，低 $u$ 少见。FineWeb 一类常按分抽样而不是只留 top。

Top-$k$ 全局：容易只剩英语维基。按语言、按域取分位数。

用于苹果相关场景时，可以参考 AFM 的多语配额：先按训练阶段定义效用，再按语言或任务分桶选择。比较不同选择方法时，要保持模型不变。许可不过的样本效用是零，见 `dt-license-is-quality`。

## 追问

- **效用用下游 损失（loss） 当标签来学？** 可以，贵。用教师打分再蒸馏，坑和 `dt-quality-clf-synth` 相同。
- **u=1 全部留下？** 退化成只做硬门（PII、许可）。覆盖最大，噪声也最大。要对照，见 `dt-hold-model-vary-data`。
- **白皮书怎么写一句？** 「效用按阶段定义，选择按桶做，对照锁模型。」
