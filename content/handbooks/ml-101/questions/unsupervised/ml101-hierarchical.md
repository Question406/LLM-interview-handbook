---
id: ml101-hierarchical
section: unsupervised
order: 6
level: A
title: 层次聚类的 single、complete、average 和 Ward 怎样选择？
quick: >-
  single 看最近点，容易连成长链；complete 看最远点，倾向紧凑 cluster；average 平均所有 cross-cluster
  点距；Ward 每次选择 within-cluster SSE 增量最小的合并，要求欧氏几何。先确定距离和希望保留的形状，再比较稳定性。
tags:
  - ML101
  - unsupervised
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-22'
sources:
  - title: 'scikit-learn: Hierarchical clustering'
    url: >-
      https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering
    type: primary
---

层次聚类每次合并两个 cluster，linkage 决定“两个 cluster 有多远”。single 取最近点距离，complete 取最远点距离，average 取全部 cross-cluster 点对距离的平均；Ward 则比较合并后的 within-cluster SSE 增加多少。 [scikit-learn: Hierarchical clustering](https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering)

比如两团紧密样本中间有一串稀疏点，single 可能沿着这条桥把两团连成一个 cluster。complete 对 cluster 的最远两点更敏感，倾向限制直径；average 是折中；Ward 倾向形成方差较小的 cluster，但不适合直接配任意非欧氏距离。

我会先按业务确定度量和特征尺度，再画合并树，在不同切分高度检查 cluster 大小与稳定性。若希望发现弯曲形状，可评估 single，同时检查噪声造成的桥接；若是 standardization 数值上的紧凑分组，可从 Ward 或 average 做基线。

## 追问

**Ward 就是选中心最近的一对吗？**
不完全是。平方误差增量还与两个 cluster 的样本数有关，不能仅看中心距离。

**必须提前给 number of clusters 吗？**
可以先构建树，再按目标 number of clusters 或合并距离阈值切分。切点仍需要验证，树图不会自动给出真实类别。

**层次聚类适合特别大的数据吗？**
要看实现和连接约束。距离计算和存储可能很贵，先估算规模，再考虑抽样或受约束版本。
