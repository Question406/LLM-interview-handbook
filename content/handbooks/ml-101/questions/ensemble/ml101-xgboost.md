---
id: ml101-xgboost
section: ensemble
order: 5
level: S
title: "XGBoost 相比基础 GBDT 增加了什么？"
quick: "XGBoost 把树的复杂度惩罚直接写进目标，用梯度和 Hessian 的二阶近似计算叶子权重与分裂收益，同时提供稀疏缺失值处理和高效训练实现。它属于梯度提升树体系，效果取决于数据与调参，不能保证所有任务都胜过其他模型。"
tags:
  - Machine Learning
  - ensemble
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "XGBoost: Introduction to Boosted Trees"
    url: https://xgboost.readthedocs.io/en/stable/tutorials/model.html
    type: primary
  - title: "Chen and Guestrin: XGBoost — A Scalable Tree Boosting System"
    url: https://arxiv.org/abs/1603.02754
    type: primary
---

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
