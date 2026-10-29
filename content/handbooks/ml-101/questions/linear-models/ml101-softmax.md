---
id: ml101-softmax
section: linear-models
order: 9
level: A
title: Softmax 回归如何处理多分类？
quick: >-
  Softmax 回归为每个互斥类别计算线性分数，再把分数 normalization 成和为 1 的概率，用多分类 cross entropy
  联合训练。类别之间共享同一个分母，提高某类概率就会挤压其他类。它适合单标签多分类；多标签通常改用各类别独立 sigmoid。
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'scikit-learn: Multinomial logistic regression'
    url: >-
      https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html
    type: primary
---

Softmax 回归把二分类逻辑回归扩展到多个互斥类别：每类有一个线性分数，所有类别一起竞争概率质量。训练用真实类别的负 log probability，让正确类别相对其他类别得分更高。

对类别 $k$，输入特征是 x，$w_k$、$b_k$ 是该类的系数和截距，先算分数 $z_k=w_k^\top x+b_k$，再算 $p_k=e^{z_k}/\sum_j e^{z_j}$。因此概率非负、总和为 1，单条样本 cross entropy 是 $-\log p_y$。例如分数是 $(\log 2,0,0)$，概率就是 $(1/2,1/4,1/4)$，选最高概率的类即可。

实现时先减去所有分数的最大值，再求指数，概率保持不变而数值更稳定。训练是联合的多项逻辑回归；one-vs-rest 则分别训练多个二分类器，目标不同。[scikit-learn LogisticRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html) 说明了 multinomial 与二分类扩展的区别。

## 追问

**三个类可以同时判为正吗？**
标准 softmax 假设单个样本属于一个类。允许多标签时，每类独立 sigmoid 和 binary cross entropy 更合适。

**所有分数都加同一个常数会怎样？**
概率不变，分子分母的共同倍数抵消。因此分数绝对值本身不代表分类置信度。
