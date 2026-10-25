---
id: ml101-choose-k
section: unsupervised
order: 2
level: A
title: "聚类没有标签，怎么选 K、怎么评价？"
quick: "没有标签时，可以综合簇内平方距离、轮廓系数、重采样稳定性和任务可用性选择聚类方案。K 越大训练距离通常越小，因此不能只追求这个数值；这些指标依赖距离与簇形状，也无法证明存在唯一真实分组。"
tags:
  - Machine Learning
  - unsupervised
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Selecting the number of clusters with silhouette analysis"
    url: https://scikit-learn.org/stable/auto_examples/cluster/plot_kmeans_silhouette_analysis.html
    type: primary
---

聚类评价要先说清“分得好”对当前任务意味着什么。可以先用几种候选 K 比较内部结构，再检查不同样本和初始化下是否稳定，最后确认分组是否有实际用途。

K-means 的簇内平方距离会随 K 增大而下降，K 等于样本数时甚至可以为零。肘部法找下降变缓的位置，但曲线不一定有清晰拐点。

轮廓系数比较一个点与本簇、最近其他簇的距离。令 $a$ 是它到本簇其他点的平均距离，$b$ 是它到最近其他簇的平均距离，系数为：

$$s=\frac{b-a}{\max(a,b)}.$$

接近 1 表示本簇更紧、与其他簇更分开，接近零表示边界模糊，负值提示可能更接近别的簇。评价依赖所选距离，通常偏好较紧凑、分离的结构。

例如客户分群，还要抽查每群的规模、行为和后续行动是否有差异。若存在外部标签，可以算调整兰德指数等一致性指标，但标签代表的划分未必就是当前聚类目标。

## 面试追问

**不同随机种子结果不一样怎么办？**
比较多次初始化和重采样后的簇结构，而非只比较簇编号。编号可以任意置换，应看成员关系是否稳定。

**轮廓系数最高就应该选它吗？**
不一定。它偏好的几何结构可能与业务需要不同，也可能偏向过粗分组，应同时看规模、稳定性和外部任务效果。
