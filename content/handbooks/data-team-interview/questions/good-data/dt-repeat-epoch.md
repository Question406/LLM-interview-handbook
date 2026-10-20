---
id: dt-repeat-epoch
section: good-data
order: 8
level: A
title: unique token 不够，把同一批数据再读几遍行不行？
quick: "可以在去重后有限地重复训练。Muennighoff 等人的 datablations 实验发现，固定算力下，重复到约 4 个 epoch，效果接近使用新数据；再增加重复，收益就很小。近重复文档不能算新数据，也不要为了凑 token 数而放松必要的质量过滤。"
companies:
  - apple
tags:
  - Apple
  - Scaling
  - Dedup
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Scaling Data-Constrained Language Models
    url: https://arxiv.org/abs/2305.16264
    type: primary
  - title: Training Compute-Optimal Large Language Models
    url: https://arxiv.org/abs/2203.15556
    type: primary
  - title: Deduplicating Training Data Makes Language Models Better
    url: https://arxiv.org/abs/2107.06499
    type: primary
---

先去重，再考虑让模型多读几遍。许可网页和干净的数学数据数量有限，但不能为了凑 token 数而放松必要的过滤。内容几乎相同的文档，也不能算作新数据。

没有做 MinHash 或精确去重，就直接报 epoch 数，会低估重复程度。同一篇文章的多个转载版本各读四遍，实际重复次数还要乘上转载簇的大小。Chinchilla 的曲线默认每个 token 见一次。Muennighoff 等跑到 900B token、9B 参数：数据受限时，重复最多约 4 epoch，效果接近使用未见过的数据；再多重复，增加训练步数也几乎没有收益。Lee 等 2021：训练集里的近重复浪费算力，也会让评测里的「新文档」变熟。

## 重复之前先问是不是真的 unique

先按 `dt-lsh-cluster-code` 检查近重复簇。如果把转载也算成独立数据，后面计算的 epoch 就不能反映模型实际看了多少遍。

datablations 发现，对噪声很多的数据进行过滤有明显收益；已经较干净的数据，再过滤的收益较小。所以放宽过滤能否增加有用的新数据，要看当前数据有多脏，见 `dt-filter-too-hard`。

他们也试过在文本不足时补入代码，确实有一定帮助。这增加的是另一类数据的覆盖，不属于重复训练。AFM 在 continued PT 中提高代码和数学的权重，调整的也是训练比例。

## 后训练不要套 4 epoch

监督微调（SFT）和直接偏好优化（DPO）反复训练同一批示范时，更容易过拟合。数据少时，要提高多样性并及时停止训练，不靠把 1000 条读 40 epoch。LIMA / s1K 是另一边，见 `dt-lima-vs-scale`。

反复用上一代模型生成的数据训练下一代，可能让数据多样性越来越低，出现模型坍缩。这与 datablations 中重复原始数据约 4 个 epoch 的实验不同，见 `dt-when-not-synth`。

苹果：报告写了 13.4T，没把 epoch 写清楚。面试只说公开的 token 量，不猜内部重复率。许可不够时先去重、再有限重复，让高质量数据多读几遍，相当于增加它在训练中的比例。

## 追问

- **4 是常数吗？** 这是他们实验设置下的经验范围。模型更大，或只重复部分高质量数据时，适合的重复次数可能不同。现场说「几个 epoch 内还行，再多要看验证掉不掉」，不要背成物理定律。
- **高质桶多读、网页只读一遍？** 可以，这相当于提高高质量数据的训练比例。不过这类数据量小，也可能最先过拟合。
- **苹果 13.4T 是 unique 吗？** 报告没把 epoch 写清楚。面试只说公开的 token 量，不猜内部重复率。
