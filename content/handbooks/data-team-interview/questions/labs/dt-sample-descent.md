---
id: dt-sample-descent
section: labs
order: 57
level: A
title: Anthropic 作业：样本轴 double descent，对 data mix 意味着什么？
quick: "增加样本不保证评测一直变好：在插值区附近，测试误差可能先升再降。调整 data mix 时，仍要保持计算预算不变，对比旧配比和新配比在固定评测集上的表现，不能仅凭 double descent 曲线决定比例。"
companies:
  - apple
tags:
  - Anthropic
  - Scaling
  - Data Mix
  - Apple
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-12
sources:
  - title: Anthropic Machine Learning Interview Questions (AceOffer catalog)
    url: https://aceoffer.app/interviews/anthropic/machine-learning-questions
    type: secondary
  - title: "Deep Double Descent: Where Bigger Models and More Data Hurt"
    url: https://arxiv.org/abs/1912.02292
    type: primary
  - title: Training Compute-Optimal Large Language Models
    url: https://arxiv.org/abs/2203.15556
    type: primary
---

Nakkiran 等人的研究表明，改变模型规模、样本数量或训练时长，都可能出现 double descent。增加样本时，在插值区附近测试误差可能先升再降，因此把同类数据翻倍，并不保证效果持续改善。实际调整配比时，我会在相同计算预算下对比新旧 mix，同时报告目标任务和旧能力的固定评测结果。

不这么选的理由：AceOffer 记过 Anthropic MLE 4 小时作业：设计并跑样本轴 double descent 实验。把它答成「数据越多越好」或「Chinchilla 已经取消了这件事」，作业会挂。Chinchilla 管的是计算最优的参数和 文本处理单位（token） 配比，不保证每一刀过滤或每一桶合成都单调。

接到苹果：过滤太狠等于有效 $N$ 下降，可能走到曲线的坏区，见 `dt-filter-too-hard`。合成加量若全是近重复，计数涨、有效 $N$ 不涨，见 `dt-global-dedup`。决策仍是 DataComp 式消融：固定模型，只换数据，见 `dt-hold-model-vary-data`。端侧 3B 更靠近小样本区，加脏数据更容易先伤再假涨。

公开锚点：AceOffer Anthropic ML 目录「Sample-Aspect Double Descent Experiment Design」，报到 2026 年 4 月；arxiv 1912.02292；Chinchilla。

## 追问

- **作业没 GPU 怎么办？** 小模型、小词表、合成可分数据也能做出形状。面试官看的是你知不知道插值区，不是 ImageNet 分数。
- **和 epoch 重复什么关系？** Muennighoff 写过约 4 个 epoch 后回报降。那是重复同一批；本题是增加新样本时的非单调。两件事都要能分开讲，见 `dt-repeat-epoch`。
- **曲线好看就上 mix？** 好看不够。要看产品切片和安全税。double descent 是警告，不是选数的公式。
