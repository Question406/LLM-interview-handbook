---
id: ml101-catboost
section: ensemble
order: 10
level: A
title: "CatBoost 怎么处理类别特征与目标泄漏风险？"
quick: "CatBoost 会把类别转成数值统计，一些目标相关统计按随机排列、只用当前样本之前的记录计算，避免把自己的标签直接编码回来。Ordered boosting 进一步处理训练过程的预测偏移。它降低这些特定泄漏风险，但不能修复错误的数据切分、未来信息或外部已经泄漏的特征。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "CatBoost: Transforming categorical features to numerical features"
    url: https://catboost.ai/docs/en/concepts/algorithm-main-stages_cat-to-numberic
    type: primary
  - title: "CatBoost: unbiased boosting with categorical features"
    url: https://arxiv.org/abs/1706.09516
    type: primary
---

CatBoost 可以直接接收类别特征，并在内部构造适合树学习的数值表示。关键在于计算目标相关统计时，不让当前样本的标签直接出现在自己的特征中。

例如某个店铺在训练集中只出现一次，标签恰好为 1。直接用全训练集“该店铺的平均标签”编码，它就得到 1，模型等于提前看见答案。CatBoost 的有序统计先随机排列样本，当前记录只利用排列中更早的同类别记录，并配合先验平滑；低基数类别也可能走 one-hot，并非所有类别都用同一种编码。机制见 [类别转换官方说明](https://catboost.ai/docs/en/concepts/algorithm-main-stages_cat-to-numberic)。

Ordered boosting 则针对训练样本参与模型拟合后带来的预测偏移，使用有序构造来减轻这一问题，与类别编码是相关但不同的环节。[CatBoost 原论文](https://arxiv.org/abs/1706.09516) 同时讨论了两者。

使用时仍先切训练、验证和测试，再让特征统计只用允许的数据。若任务按未来预测，就不能因为内部随机排列就忽略时间顺序；外部把未来销量做进特征，CatBoost 也不会自动识别。

## 追问

**为什么还要先验平滑？**
稀少类别的均值波动很大，平滑让少量观测不过早产生极端编码。

**高基数类别一定用它更好？**
不一定。还要比较样本量、类别可重复性、训练成本和验证表现，不能靠模型名决定。
