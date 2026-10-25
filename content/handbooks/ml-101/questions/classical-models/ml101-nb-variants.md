---
id: ml101-nb-variants
section: classical-models
order: 7
level: A
title: "Gaussian、Multinomial 和 Bernoulli 朴素贝叶斯怎么选？"
quick: "三种朴素贝叶斯都假设给定类别后特征条件独立，区别在特征的类条件分布。Gaussian 适合以高斯近似的连续量，Multinomial 常用于非负词频计数，Bernoulli 用二值的出现与否。先看特征含义和数值范围，再以验证结果选择，不能只按模型名判断。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Gaussian, Multinomial and Bernoulli Naive Bayes"
    url: https://scikit-learn.org/stable/modules/naive_bayes.html
    type: primary
---

选择朴素贝叶斯变体，先看一条特征在某个类别里应该怎样分布。朴素贝叶斯把类别概率与各特征的条件概率相乘，节省联合分布建模的成本；“朴素”指的是给定类别后的条件独立假设。

Gaussian 为每类、每个连续特征估均值和方差，用高斯密度解释测量值。Multinomial 常把文档看成词的计数，某个词重复出现会重复贡献证据。Bernoulli 把词是否出现编码成 0/1，同时考虑出现和缺席。[scikit-learn 官方指南](https://scikit-learn.org/stable/modules/naive_bayes.html) 对照了这些分布。

例如一封邮件里“中奖”出现五次，Multinomial 会使用次数，Bernoulli 只记录出现过；如果输入是温度、长度这类连续测量，Gaussian 才是更自然的基线。实际文本还可以评估非负的词频与逆文档频率表示（TF-IDF），但它不是严格的整数词数模型，仍应验证。

## 追问

**没见过的词会让类别概率变成零吗？**
未经平滑的离散计数估计可能如此。加性平滑给未出现事件留非零概率，平滑强度也要选择。

**特征有关联就完全不能用吗？**
不一定。分类仍可能有效，但重复证据会影响概率，预测概率尤其不能直接当成已经校准的置信度。
