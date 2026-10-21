---
id: dt-utility-select
section: good-data
order: 11
level: A
title: 数据选择能不能讲成一个效用函数？
quick: "可以。先给样本定义效用 $u(x)$，说明它为什么值得训练，再决定按阈值筛选、按桶分配配额，还是按分数加权抽样。Albalak 等人的 2024 年综述把数据选择拆成这两步。启发式、ppl、分类器、EL2N 和强化学习采样，区别主要在于怎样估计效用。"
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

可以。我会先定义样本的效用 $u(x)$，再说明分数怎样影响选择：高于阈值才保留，按桶分配配额，或者按分数决定抽样概率。这样每条规则为什么存在，都能用效用解释清楚。

这个框来自 Albalak 等 2024 年的综述，简单到能写在白板上：对每条样本估计效用 $u(x)$，再用一个选择机制决定怎样使用这个效用。启发式、ppl、分类器、EL2N、强化学习（RL）采样都能放进这个框，区别在效用怎么定义。

## 第一步：效用从哪来

效用可以用引用次数、域名、长度、KenLM 困惑度、质量分类器分数或 CLIP 分数来估计，也可以看验证器是否通过，或者偏好标注里好坏回答的分差。

关键是按训练阶段定义。网页和工具轨迹用途不同，各自要有自己的分数，见 `dt-good-data-def`。在基于可验证奖励的强化学习（RLVR）里，效用就是 grader 是否通过；在偏好学习里，效用是 margin。网页的教育分不要拿到这两个阶段用。

许可不合格的样本，效用直接为零，见 `dt-license-is-quality`。

效用也可以定义在域上。DoReMi 把 $u$ 定义在域上：先用小模型和 Group DRO 学出各个域的权重，再拿这些权重去训大模型。权重能不能直接搬到大模型，见 `dt-doremi-mix`。

## 第二步：怎样用效用做选择

- 硬切：只保留 `u >= t` 的样本。实现简单，但阈值稍微漂一点，通过率就会跳，缓解办法见 `dt-quality-filter-code` 里的软带。
- 配额：先保证每类数据至少有一定数量的 token，再在类内按 $u$ 抽样。AFM 的多语配额就是这种做法。
- 重加权：不丢样本，只让低 $u$ 的样本出现得少一些。FineWeb 一类工作常按分数抽样。
- 全局 Top-$k$：容易最后只剩英语维基。要按语言、按域取分位数。

比较不同的选择方法时，模型要保持不变，见 `dt-hold-model-vary-data`。

## 追问

- **能不能用下游损失（loss）当标签来学效用？** 可以，但贵。如果改用教师打分再蒸馏，会遇到和 `dt-quality-clf-synth` 一样的坑。
- **所有样本 u=1、全部留下呢？** 那就退化成只做硬门（PII、许可）。覆盖最大，噪声也最大，要用对照来判断值不值。
- **白皮书里怎么用一句话写？** 「效用按阶段定义，选择按桶做，对照锁定模型。」
