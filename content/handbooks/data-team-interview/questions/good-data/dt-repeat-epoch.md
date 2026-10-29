---
id: dt-repeat-epoch
section: good-data
order: 8
level: A
title: unique token 不够，把同一批数据再读几遍行不行？
quick: >-
  可以，但先 deduplication，再有限地重复。Muennighoff 等的 datablations 发现，固定算力下重复到约 4 个
  epoch，效果接近用新数据，再多收益就很小。near-duplicates 文档不能算新数据，也别为了凑 token 数放松必要的质量过滤。
companies:
  - apple
tags:
  - Apple
  - Scaling
  - Dedup
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12T00:00:00.000Z
sources:
  - title: Scaling Data-Constrained Language Models
    url: 'https://arxiv.org/abs/2305.16264'
    type: primary
  - title: Training Compute-Optimal Large Language Models
    url: 'https://arxiv.org/abs/2203.15556'
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: 'https://arxiv.org/abs/2107.06499'
    type: primary
---

可以，但先 deduplication，再有限地重复。许可网页和干净的数学数据就那么多，多读几遍是合理的；可内容几乎相同的文档不能算新数据，也不能为了凑 token 数放松必要的过滤。

几遍算合适，有公开数据可以参考。Chinchilla 的曲线默认每个 token 只见一次，Muennighoff 等专门研究了数据受限的情况，实验跑到 900B token、9B 参数：重复最多约 4 个 epoch，效果接近用没见过的数据；再往上重复，加训练步数也几乎没收益。

难点在于先确认数据是真的 unique。比如同一篇文章有好几个转载版本，每个都读四遍，实际重复次数还要再乘上转载 cluster 的大小。没做 MinHash 或 exact deduplication 就报 epoch 数，会把重复程度低估一大截。Lee 等 2021 年的工作也说明，training set 里的 near-duplicates 既浪费算力，又会让评测里的「新文档」对模型来说变得眼熟。所以重复之前，先按 `dt-lsh-cluster-code` 查 near-duplicates cluster；把转载也算成独立数据，算出来的 epoch 就反映不了模型实际看了多少遍。

还有一个相关的问题：放宽过滤能不能换来更多有用的新数据？datablations 发现，对噪声很多的数据做过滤收益明显，已经比较干净的数据再滤收益较小，所以得看当前数据有多脏，见 `dt-filter-too-hard`。他们也试过在文本不够时补代码，确实有一定帮助。

## post-training 别套 4 epoch

SFT 和直接 preference optimization（DPO）反复训同一批示范，更容易 overfitting。数据少时要提高多样性、及时停；把 1000 条读 40 个 epoch，模型很快就把示范背下来了。LIMA / s1K 是另一面，见 `dt-lima-vs-scale`。

## 追问

**4 是常数吗？**
不是，这是他们实验设置下的经验范围。模型更大，或者只重复部分高质量数据时，合适的次数可能不同。现场可以说「几个 epoch 内还行，再多要看 validation set 掉不掉」，别背成物理定律。

**高质量桶多读、网页只读一遍，行吗？**
可以，这相当于提高高质量数据的训练比例。不过这类数据量小，也可能最先 overfitting。

**拿上一代模型生成的数据反复训下一代，算重复训练吗？**
不算，要分开讨论。datablations 重复的是原始数据；反复用上一代的生成数据训下一代，可能让多样性越来越低，出现 model collapse，见 `dt-when-not-synth`。

**文本不够时补代码，算不算重复训练？**
不算。这增加的是另一类数据的覆盖，属于调 data mix，AFM 在 continued PT 里提高代码和数学的权重也是这一类。
