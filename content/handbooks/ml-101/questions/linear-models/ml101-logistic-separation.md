---
id: ml101-logistic-separation
section: linear-models
order: 8
level: A
title: "逻辑回归遇到完全可分数据为什么系数会变大？"
quick: "完全可分时，无正则逻辑回归可以不断放大分离方向的系数，把训练概率推近 0 或 1，似然继续提高，却没有有限的最优系数。增加迭代次数不会解决这个问题。先排查泄漏或稀少组合，再用正则化等有限估计方案，并验证留出概率表现。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "statsmodels: Incomplete convergence in maximum likelihood estimation"
    url: https://www.statsmodels.org/stable/pitfalls.html#incomplete-convergence-in-maximum-likelihood-estimation
    type: primary
  - title: "scikit-learn: LogisticRegression"
    url: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
    type: primary
---

完全可分数据下，无正则逻辑回归的最大似然估计可能没有有限解。决策边界已经把训练样本全分对，继续放大系数仍能提高正确类别的概率，优化器就有动力继续增大它们。

设第 i 条样本的特征为 $x_i$、标签为 $y_i\in\{-1,1\}$，w 是系数、b 是截距。若存在方向使所有 $y_i(w^\top x_i+b)>0$。沿该方向把参数乘越来越大的常数，损失 $\log(1+e^{-y_i(w^\top x_i+b)})$ 会越来越接近零，却在有限参数处达不到零。例如所有正例的 x 都大于 0、负例都小于 0，斜率就能一直增大。

实际会看到巨大系数、很大的标准误或收敛警告。应检查是否有标签泄漏、样本太少或类别组合稀疏，再考虑 L2 等正则化；不能把“训练正确率满分”当成概率估计可靠。边界问题见 [statsmodels pitfalls](https://www.statsmodels.org/stable/pitfalls.html#incomplete-convergence-in-maximum-likelihood-estimation)。

## 追问

**多训练几轮能收敛吗？**
不能创造有限最大似然解。损失可能几乎不变，但系数还在移动，数值停止不代表统计估计存在。

**加 L2 为什么有效？**
参数继续增大会受到平方惩罚，目标形成有限取舍；正则强度仍要验证，系数解释也变成带惩罚的估计。实现见 [LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)。
