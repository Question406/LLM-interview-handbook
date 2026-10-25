---
id: ml101-dbscan
section: unsupervised
order: 3
level: A
title: "DBSCAN 如何聚类？和 K-means 有什么区别？"
quick: "DBSCAN 把邻域足够密集的核心点连接成簇，再附上边界点，无法归入簇的样本标为噪声。它不需要预先指定簇数，能处理非球形结构，但对距离、邻域半径和密度差异敏感；高维距离失效时也会困难。"
tags:
  - Machine Learning
  - unsupervised
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Clustering"
    url: https://scikit-learn.org/stable/modules/clustering.html
    type: primary
---

DBSCAN 根据密度把点连起来。给定邻域半径 eps 和最少邻居数 min_samples，某点周围足够拥挤时就成为核心点，相连的核心点可以扩展出同一个簇。

例如二维平面上两条弯月形点云，K-means 的最近中心分组可能把弯月切开。DBSCAN 可以沿着每条弯月中连续的稠密区域扩展，并把远处孤立点标成噪声。

核心点的邻域样本数达到阈值；靠近核心点但本身不够密的点属于边界点；既非核心、又不在任何核心点邻域里的点为噪声。常见实现的邻域计数包括点自身，参数含义要查清。

半径太小会产生很多碎簇和噪声，太大又会把不同区域连起来。统一半径很难同时适应稀疏簇和稠密簇，选择距离、缩放以及参数时要结合数据分布。

## 面试追问

**不需要 K 就代表不用调参吗？**
仍然要选 eps、min_samples 和距离。它把“多少簇”的假设换成了“多近、多密才算相连”的假设。

**边界点的分配一定唯一吗？**
不一定。一个边界点可能靠近多个簇的核心点，具体分配可能受遍历顺序影响；核心点形成的连通结构通常更稳定。
