---
id: dt-utility-select
section: good-data
order: 11
level: A
title: 数据选择能不能讲成一个效用函数？
quick: >-
  可以。先给样本定义效用 $u(x)$，说明它为什么值得训练，再决定按阈值筛、按桶分配额，还是按分数加权 sampling。Albalak 等 2024
  年的综述就是这样拆成两步的。启发式、ppl、分类器、EL2N 和 RL sampling，区别主要在效用怎么估。
companies:
  - apple
tags:
  - Apple
  - Data Quality
  - Data Mix
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: A Survey on Data Selection for Language Models
    url: 'https://arxiv.org/abs/2402.16827'
    type: primary
  - title: 'DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining'
    url: 'https://arxiv.org/abs/2305.10429'
    type: primary
  - title: Apple Intelligence Foundation Language Models Tech Report 2025
    url: >-
      https://machinelearning.apple.com/research/apple-foundation-models-tech-report-2025
    type: primary
---

可以。我会先给样本定义效用 $u(x)$，再说分数怎样影响选择：高于阈值才留，按桶分配额，或者按分数决定 sampling 概率。这样每条规则为什么存在，都能用效用讲清楚。

这个框来自 Albalak 等 2024 年的综述，简单到能画在白板上：对每条样本估一个效用 $u(x)$，再用一个选择机制决定怎么用它。启发式、ppl、分类器、EL2N、RLsampling 都能装进这个框，区别在效用怎么定义。

## 效用从哪来

效用可以用引用次数、域名、长度、KenLM perplexity、质量分类器分数或 CLIP 分数来估，也可以看 verifier 通没通过，或者偏好标注里好坏回答的分差。关键是按训练阶段定义。比如在基于 verifiable reward 的 RL（RLVR）里，效用就是 grader 是否通过；在 preference learning 里，效用是 margin；网页的教育分不该拿到这两个阶段去用。网页和 tool-use trajectories 用途不同，各要各的分数，见 `dt-good-data-def`。许可不合格的样本，效用直接为零，见 `dt-license-is-quality`。

效用也可以定义在域上。DoReMi 先用 small model 和 Group DRO 学出各个域的权重，再拿这些权重去训 large model，权重能不能直接搬过去见 `dt-doremi-mix`。

## 怎样用效用做选择

最简单的是硬切，只留 `u >= t` 的样本，实现容易，但阈值稍微一漂，通过率就跳，缓解办法见 `dt-quality-filter-code` 里的软带。想保住覆盖，就用配额：先保证每类数据至少有一定 token，再在类内按 $u$ sampling，AFM 的 multilingual 配额就是这么做的。也可以不丢样本，只让低 $u$ 的出现得少一些，FineWeb 一类工作常按分数 sampling。

比较不同的选择方法时，模型保持不变，见 `dt-hold-model-vary-data`。

## 追问

**能不能用下游损失（loss）当标签来学效用？**
可以，但贵。改用 teacher 打分再 distillation，又会遇到和 `dt-quality-clf-synth` 一样的坑。

**所有样本 u=1、全部留下呢？**
那就退化成只做必须满足的验收条件（PII、许可）。覆盖最大，噪声也最大，要用对照判断值不值。

**白皮书里怎么用一句话写？**
「效用按阶段定义，选择按桶做，对照锁定模型。」

**直接取全局 Top-$k$ 行不行？**
容易出事，最后可能只剩英语维基。要按语言、按域取分位数。
