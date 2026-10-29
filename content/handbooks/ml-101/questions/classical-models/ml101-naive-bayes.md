---
id: ml101-naive-bayes
section: classical-models
order: 4
level: S
title: "朴素贝叶斯的独立性假设是什么？为什么需要平滑？"
quick: "朴素贝叶斯假设在类别已知时，各特征条件独立，因此可以把每个特征的类条件概率相乘，再乘类别先验来分类。文本计数中未出现的词会导致零概率，拉普拉斯平滑给计数加上小的伪计数，避免一个未见事件抹掉全部证据。"
tags:
  - Machine Learning
  - classical-models
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Naive Bayes"
    url: https://scikit-learn.org/stable/modules/naive_bayes.html
    type: primary
---

朴素贝叶斯先估计每类常见的特征，再用贝叶斯公式判断新样本最像哪一类。“朴素”指给定类别后把特征当成条件独立，原始特征之间并不要求完全独立。

类别为 $y$、输入为 $x=(x_1,\ldots,x_d)$ 时，分类规则是：

$$\hat y=\arg\max_y P(y)\prod_{j=1}^dP(x_j\mid y).$$

比较类别时，贝叶斯公式中的输入概率 $P(x)$ 相同，可以省去。实际通常累加 log probability，避免很多小数相乘下溢。

以文本多项式模型为例，某词在某类文档里没出现，直接按频数估计会得到零，整段文档的类条件概率也变成零。平滑后词概率可以写成 $(N_{yc}+\alpha)/(N_y+\alpha V)$：$N_{yc}$ 是该类中这个词的次数，$N_y$ 是该类总词数，$V$ 是 vocabulary 大小，$\alpha$ 是伪计数。

词与词常有关联，模型仍可能给出不错的分类，但概率容易过度自信，因此概率质量要另外检查。

## 面试追问

**平滑系数越大越稳健吗？**
过大也会把各词概率拉得过于接近，抹掉真正的类别差异。应在开发数据上选择。

**连续特征也能直接用词频公式吗？**
不能直接照搬。Gaussian Naive Bayes 等模型会为连续特征指定类条件分布；不同变体对应不同特征含义和假设。
