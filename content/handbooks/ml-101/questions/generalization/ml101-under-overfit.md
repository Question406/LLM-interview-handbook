---
id: ml101-under-overfit
section: generalization
order: 9
level: S
title: "怎么判断欠拟合和过拟合？"
quick: "训练和验证都表现差时，先检查优化是否完成、特征和模型是否足够；训练明显好于验证时，再排查过拟合、数据泄漏或分布差异。学习曲线和复杂度曲线能帮助决定该加数据、改特征还是加强正则。"
tags:
  - Machine Learning
  - generalization
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Validation curves and learning curves"
    url: https://scikit-learn.org/stable/modules/learning_curve.html
    type: primary
  - title: "Google ML Crash Course: Gradient descent"
    url: https://developers.google.com/machine-learning/crash-course/linear-regression/gradient-descent
    type: primary
---

我会先比较同一指标下的训练表现和验证表现，再改变训练样本量或模型复杂度看趋势。两边都差通常提示模型没有学好；训练好、验证差提示模型可能过度依赖训练样本。

例如训练集准确率 99%，验证集 70%，可以逐步限制树深度，观察训练分数是否略降、验证分数是否上升。如果两边都在 60%，先确认标签、特征和训练过程正常，再尝试更合适的特征或更强模型。

这些数字只能当诊断线索。训练集和验证集来自不同地区，也可能出现很大的差距。先核对切分、标签口径和数据预处理，再用学习曲线判断增加样本是否可能缩小差距，避免把所有问题都归到模型复杂度上。

## 面试追问

**验证分数比训练分数高可能吗？**
可能。训练时加入噪声或正则、两批数据难度不同、样本量太小，都可能造成这种现象。要保证评价阶段采用可比较的流程。

**训练损失不降算欠拟合吗？**
先查优化。学习率不合适、梯度实现错误或预处理有问题时，即使模型表达能力足够也学不到。确认能拟合一个小样本后，再讨论模型容量。
