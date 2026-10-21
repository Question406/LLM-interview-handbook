---
id: dt-repeat-epoch
section: good-data
order: 8
level: A
title: unique token 不够，把同一批数据再读几遍行不行？
quick: "可以，但要先去重，再有限地重复。Muennighoff 等人的 datablations 实验发现，固定算力下，重复到约 4 个 epoch 效果接近使用新数据，再多重复收益就很小。近重复文档不能算新数据，也不要为了凑 token 数而放松必要的质量过滤。"
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

可以，但先去重，再有限地重复。许可网页和干净的数学数据数量有限，多读几遍是合理的选择；但内容几乎相同的文档不能算作新数据，也不能为了凑 token 数放松必要的过滤。

## 重复几遍还有用

Chinchilla 的曲线默认每个 token 只见一次。Muennighoff 等专门研究了数据受限的情况，实验跑到 900B token、9B 参数：重复最多约 4 个 epoch，效果接近使用没见过的数据；再多重复，增加训练步数也几乎没有收益。

## 先确认是不是真的 unique

没做 MinHash 或精确去重就报 epoch 数，会低估重复程度。同一篇文章的多个转载版本各读四遍，实际重复次数还要再乘上转载簇的大小。Lee 等 2021 年的工作也说明，训练集里的近重复既浪费算力，也会让评测里的「新文档」对模型来说变得眼熟。所以重复之前，先按 `dt-lsh-cluster-code` 检查近重复簇；把转载也算成独立数据，后面算出的 epoch 就反映不了模型实际看了多少遍。

还有一个相关问题：放宽过滤能不能换来更多有用的新数据？datablations 发现，对噪声很多的数据做过滤收益明显，已经比较干净的数据再过滤收益较小。所以要看当前数据有多脏，见 `dt-filter-too-hard`。

他们也试过在文本不够时补入代码，确实有一定帮助。这增加的是另一类数据的覆盖，属于调整配比，不算重复训练。AFM 在 continued PT 中提高代码和数学的权重，调整的也是训练比例。

## 后训练不要套 4 epoch

监督微调（SFT）和直接偏好优化（DPO）反复训练同一批示范，更容易过拟合。数据少时要提高多样性、及时停止训练；把 1000 条读 40 个 epoch，模型很快就会背下这些示范。LIMA / s1K 是另一面，见 `dt-lima-vs-scale`。

另外，反复用上一代模型生成的数据训练下一代，可能让数据多样性越来越低，出现模型坍缩。datablations 重复的是原始数据，和这种情况要分开讨论，见 `dt-when-not-synth`。

## 追问

- **4 是常数吗？** 这是他们实验设置下的经验范围。模型更大，或者只重复部分高质量数据时，合适的重复次数可能不同。现场可以说「几个 epoch 内还行，再多要看验证集掉不掉」，别背成物理定律。
- **高质量桶多读、网页只读一遍，行吗？** 可以，这相当于提高高质量数据的训练比例。不过这类数据量小，也可能最先过拟合。
