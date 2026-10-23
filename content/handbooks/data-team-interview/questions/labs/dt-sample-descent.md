---
id: dt-sample-descent
section: labs
order: 57
level: A
title: Anthropic 作业：样本轴 double descent，对 data mix 意味着什么？
quick: "意味着增加样本不保证评测一直变好：在插值区附近，测试误差可能先升再降，同类数据翻倍也可能变差。所以调 data mix 时，在相同计算预算下对比新旧配比在固定评测集上的表现，同时看目标任务和旧能力。double descent 只是提醒结果可能非单调，比例还是由消融来定。"
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

对 data mix 来说，它意味着多加数据本身不保证变好。增加样本时，测试误差在插值区附近可能先升再降，同类数据翻一倍，效果也不一定继续改善。所以调配比时，我会在相同计算预算下对比新旧 mix，同时报告目标任务和旧能力在固定评测上的结果。

Nakkiran 等人（arxiv 1912.02292）表明，改模型规模、样本数量或训练时长，都可能出现 double descent。落到样本轴上，就是靠近插值区时，多加样本也可能让测试误差上升。比如往 mix 里把某一类数据翻一倍，固定评测可能先掉一截，再往上加才回来，只看一个点就会下错结论。

日常的数据决策里有好几处会碰到它。过滤太狠等于有效样本数 $N$ 下降，可能走到曲线的坏区，见 `dt-filter-too-hard`。合成数据加量时要是全是近重复，计数涨了，有效 $N$ 却没涨，见 `dt-global-dedup`。小模型更靠近小样本区，加脏数据更容易先变差、再假性上涨。最后怎么定，还是靠 DataComp 式的消融，固定模型只换数据，见 `dt-hold-model-vary-data`。

题目来源是 AceOffer 的 Anthropic ML 目录里的「Sample-Aspect Double Descent Experiment Design」，一个 MLE 4 小时作业：设计并跑样本轴 double descent 实验，报道到 2026 年 4 月。

## 追问

**Chinchilla 不是已经告诉我们数据该加多少了吗？**
Chinchilla 管的是计算最优时参数量和 token（文本处理单位）数的配比，它不保证每一次过滤、每一桶合成都让效果单调变好。把这题答成「数据越多越好」或「Chinchilla 已经取消了它」，作业会挂。

**作业没有 GPU 怎么办？**
用小模型、小词表、合成的可分数据，也能做出曲线形状。面试官看的是你知不知道插值区，ImageNet 分数不重要。

**这和 epoch 重复是什么关系？**
是两件事。Muennighoff 写过大约 4 个 epoch 之后回报下降，那是重复同一批数据；这题讲的是增加新样本时的非单调，见 `dt-repeat-epoch`。

**曲线好看就能上这个 mix 吗？**
不够，还要看产品切片和安全税。double descent 只提醒曲线可能非单调，选数据还是靠消融。
