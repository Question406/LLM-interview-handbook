---
id: ml101-boosting
section: ensemble
order: 4
level: S
title: "Bagging 和 Boosting 有什么区别？GBDT 在拟合什么？"
quick: "Bagging 把多个有差异的模型平均，主要通过降低波动改善效果；Boosting 逐步加入新模型来修正当前预测。GBDT 每一轮拟合损失对当前分数的负梯度，平方损失下这正好是残差，其他损失下不能一概称为拟合标签残差。"
tags:
  - Machine Learning
  - ensemble
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Ensembles"
    url: https://scikit-learn.org/stable/modules/ensemble.html
    type: primary
---

Bagging 让模型并行学出不同结果，再做平均；Boosting 把后一个模型接在前面的预测上，逐步降低整体损失。前者适合减少不稳定模型的方差，后者通过序列学习逐步增强表达能力，两者都可能需要控制 overfitting。

GBDT 用树表示每一步修正。当前预测为 $F_{m-1}(x)$ 时，先计算每个样本在当前预测上的负梯度 $r_i=-\partial\ell(y_i,F)/\partial F$，再训练一棵树去拟合这些值，最后更新：

$$F_m(x)=F_{m-1}(x)+\eta h_m(x).$$

$h_m$ 是这一轮学到的修正，$\eta$ 是学习率。平方损失 $\frac12(y-F)^2$ 的负梯度是 $y-F$，所以可以直观理解为补残差；binary cross entropy 下，对 logit 的负梯度是 $y-p$。

例如真实值 10、当前预测 7，平方损失给下一轮的目标是 3。用小学习率时只补其中一部分，再继续迭代，避免一次修正过猛。

## 面试追问

**Boosting 就是每轮增加错分样本权重吗？**
那更接近 AdaBoost 的常见表述。梯度提升通过负梯度定义当前应修正的方向，能处理多种可微损失。

**Boosting 必须串行到什么程度？**
下一轮依赖前一轮结果，所以轮次之间通常有依赖。每轮内部仍可并行统计候选分裂、处理特征或进行分布式计算。
