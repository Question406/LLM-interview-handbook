---
id: ml101-lda-qda
section: classical-models
order: 5
level: A
title: LDA 和 QDA 的分布假设如何决定 decision boundaries？
quick: >-
  LDA 和 QDA 都假设每个类别内的特征服从多元高斯分布，再用贝叶斯规则分类。LDA 让各类共享协方差，比较类别时二次项抵消，decision
  boundary 是线性的；QDA 为各类单独估协方差，可产生 quadratic decision boundary。QDA
  更灵活，也需要更多数据稳定估计。
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'scikit-learn: Linear and Quadratic Discriminant Analysis'
    url: 'https://scikit-learn.org/stable/modules/lda_qda.html'
    type: primary
---

线性判别分析（LDA）和二次判别分析（QDA）的关键区别是各类别是否共享协方差，也就是特征怎样一起波动。两者都先建立“这个类别会产生什么特征”的高斯模型，再比较给定特征后的类别概率。

设类别 k 的均值是 $\mu_k$、协方差是 $\Sigma_k$。高斯对数密度包含 $-\tfrac12(x-\mu_k)^\top\Sigma_k^{-1}(x-\mu_k)$，其中 x 是特征向量。LDA 令所有 $\Sigma_k$ 相同，两个类别比较时共同的 x 二次项消去，得到 linear decision boundary；QDA 保留各类不同协方差，二次项通常不能消去。[官方推导](https://scikit-learn.org/stable/modules/lda_qda.html#mathematical-formulation-of-the-lda-and-qda-classifiers) 展开了这一过程。

例如两类测量结果像两个宽度、方向相近的椭圆云团，LDA 用共享形状可能够用；一类细长、一类接近圆形时，QDA 能表达不同扩散方式。但每类都估一套矩阵需要更多样本，小样本高维时容易不稳定，应验证并考虑协方差收缩。

## 追问

**LDA 要求每个特征互相独立吗？**
不要求。完整协方差可以包含相关性；条件独立是假设更强的朴素贝叶斯常用条件。

**QDA 总比 LDA 好吗？**
不一定。灵活性提高的同时估计方差也增大，数据不足时共享协方差反而更稳。
