---
id: ml101-kmeans
section: unsupervised
order: 1
level: S
title: K-means 的目标和迭代步骤是什么？
quick: >-
  K-means 最小化样本到所属 cluster 中心的平方距离和，交替把样本分给最近中心、把中心更新为 cluster
  mean。目标会逐步不增，但可能停在局部解；需要关注初始化、尺度、离群点，以及数据是否适合这种按欧氏距离形成的 cluster。
tags:
  - Machine Learning
  - unsupervised
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'scikit-learn: Clustering'
    url: 'https://scikit-learn.org/stable/modules/clustering.html'
    type: primary
---

K-means 用 K 个中心概括数据，希望每个点离自己的中心尽量近。中心是坐标均值，不一定是数据里真实存在的点。

设 cluster 为 $C_1,\ldots,C_K$，中心为 $\mu_k$，目标是：

$$\min_{C,\mu}\sum_{k=1}^K\sum_{x_i\in C_k}\lVert x_i-\mu_k\rVert^2.$$

先初始化中心，再反复执行分配与更新。固定中心时，给每个点选择最近中心最优；固定分组时，cluster mean 使平方距离和最小，所以两步都不会增加目标。

例如一维数据 0、2、8、10，初始中心为 0 和 10，分组后分别得到 0、2 与 8、10，新中心变成 1 和 9；再次分配不变，就稳定下来。

不同初始化可能得到不同局部解，因此常用 K-means++ 并做多次初始化。尺度差异会改变欧氏距离，离群点会拉动均值；细长、弯曲或密度差异大的 cluster 也可能不适合它。

## 面试追问

**收敛意味着找到全局最优吗？**
不意味着。交替优化只能保证在相应条件下目标不增并达到稳定解，初始中心不同可能落到不同局部解。

**K-means 可以直接用任意距离吗？**
原始均值更新与平方欧氏距离配套。换成任意距离后，均值未必是最优中心，应该选择相应算法，例如使用代表样本的 K-medoids。
