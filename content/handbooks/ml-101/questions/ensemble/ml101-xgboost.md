---
id: ml101-xgboost
section: ensemble
order: 5
level: S
title: XGBoost 相比基础 GBDT 增加了什么？
quick: >-
  普通 gradient boosting 每轮训练一棵树，去改善当前预测的错误。XGBoost
  在这个框架上，用目标的一阶和二阶信息评价候选更新，并对树复杂度加 regularization。
tags:
  - Machine Learning
  - ensemble
  - 口述改写 2026-10-28
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-28'
sources:
  - title: 'XGBoost: Introduction to Boosted Trees'
    url: 'https://xgboost.readthedocs.io/en/stable/tutorials/model.html'
    type: primary
  - title: 'Chen and Guestrin: XGBoost — A Scalable Tree Boosting System'
    url: 'https://arxiv.org/abs/1603.02754'
    type: primary
---

## 回答思路

> **问题与场景：** 普通 gradient boosting 每轮训练一棵树，去改善当前预测的错误。
>
> **做法与原因：** 例如两种切分带来的训练 loss 降幅接近时，叶子数与叶子权重的惩罚会影响选择。
>
> **检查与取舍：** 我会在相同划分与调参预算下比较效果，并检查 early stopping。

## 可以这样回答

普通 gradient boosting 每轮训练一棵树，去改善当前预测的错误。XGBoost 在这个框架上，用目标的一阶和二阶信息评价候选更新，并对树复杂度加 regularization。

例如两种切分带来的训练 loss 降幅接近时，叶子数与叶子权重的惩罚会影响选择。Shrinkage、sampling 与缺失值处理也帮助控制训练与泛化。

我会在相同划分与调参预算下比较效果，并检查 early stopping。它不是因为名字不同就一定胜过所有 GBDT 实现。

## 技术备查

XGBoost 把提升树训练中的目标、正则和计算过程组织得更完整。理解它可以先看如何决定一棵新树的叶子输出，再看如何高效找分裂。

设新树有 $T$ 个叶子，叶子输出为 $w_j$，常见复杂度项是 $\gamma T+\frac\lambda2\sum_jw_j^2$。在固定树结构下，把损失在当前预测附近展开到二阶，可以得到叶子最优输出：

$$w_j^*=-\frac{G_j}{H_j+\lambda}.$$

$G_j$ 和 $H_j$ 分别是落入该叶子的样本一阶导数与二阶导数之和，$\lambda$ 惩罚大叶子输出。将左右子叶的最优目标与父叶比较，并扣除新增叶子的成本，就得到分裂收益。这解释了为什么叶子样本的梯度证据不足时，不值得继续分裂。

原论文还讨论了稀疏感知的分裂、加权分位数近似和缓存等系统优化。常见实现会学习缺失值默认进入哪一侧；数据缺失机制变化时仍要重新验证，不能把自动处理缺失理解为无需检查数据。

## 面试追问

**用了二阶信息就一定比一阶方法更准确吗？**
不一定。它帮助构造局部优化近似，但最终效果还受损失、数据、模型约束和超参数影响，二阶近似也不等于直接找到全局最优。

**为什么同时要限制树深、叶子权重和树数？**
它们约束不同自由度。深度控制交互结构，叶子惩罚限制每次修正幅度，树数与学习率控制累积拟合程度，应该联合验证。
