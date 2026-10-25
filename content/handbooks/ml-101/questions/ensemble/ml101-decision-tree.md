---
id: ml101-decision-tree
section: ensemble
order: 1
level: S
title: "决策树怎么选分裂点？Gini 和熵有什么区别？"
quick: "分类树会比较候选特征和阈值，选择让子节点加权不纯度下降最多的切分。Gini 和熵都衡量节点类别是否混杂，通常都能工作；回归树则常按平方误差下降切分。单步最优是贪心选择，不保证整棵树全局最优。"
tags:
  - Machine Learning
  - ensemble
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Decision Trees"
    url: https://scikit-learn.org/stable/modules/tree.html
    type: primary
---

决策树不断问条件问题，把标签不同的样本分开。每次选一个特征和阈值，让分裂后的样本更集中在同一类别。

设节点中第 $k$ 类比例为 $p_k$，Gini 不纯度是 $1-\sum_k p_k^2$，熵是 $-\sum_k p_k\log p_k$。纯节点两者都为零。分裂收益是父节点不纯度减去左右子节点按样本数加权的不纯度。

例如十个样本里五正五负，Gini 是 0.5。某次切分让左右各有五个样本，分别四正一负和一正四负，每个子节点 Gini 都是 0.32，加权后仍为 0.32，收益就是 0.18。算法用同样办法比较其他阈值。

Gini 和熵对类别比例的响应不同，但没有一个总能得到更好的树。训练会递归做局部选择，再用深度、叶子样本数或剪枝控制复杂度。具体支持哪些类别特征和缺失值，要看实现。

## 面试追问

**回归树的叶子为什么常输出均值？**
用平方误差时，一个叶子内使总平方残差最小的常数就是样本均值。改用绝对误差时，相应最优常数是中位数。

**局部最好的切分为什么可能错过好方案？**
有些规律需要先做一个当前收益很小的切分，后面的分裂才有明显收益。贪心树只看当前候选收益，可能受限，例如特征交互很强的任务。
