---
id: ml101-neighbor-centroid
section: classical-models
order: 10
level: A
title: 给两类一维样本，怎么比较最近邻与按类别均值分类？
quick: 最近邻把新点交给距离最近的训练样本所属类别，能保留局部结构，但容易受噪声和存储规模影响。按类别均值分类只比较新点到各类中心的距离，预测便宜，却会丢掉多峰和分散程度。两种方法应在符合预测场景的验证集上比较，并先确认距离、类别先验和误判代价。
companies:
  - google
tags:
  - Machine Learning
  - Classification
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: Google L5 MLE 候选人面经：一维分类与方法比较
    url: https://www.1point3acres.com/interview/thread/1116207
    type: secondary
  - title: scikit-learn Nearest Neighbors
    url: https://scikit-learn.org/stable/modules/neighbors.html
    type: primary
  - title: scikit-learn NearestCentroid
    url: https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.NearestCentroid.html
    type: primary
---

可以先用最近邻和最近类别均值做两个基线。最近邻保留局部样本位置，类别均值把整类压成一个中心；当一类有多个相距很远的群体时，后者可能丢掉决定分类所需的信息。

面经给了两组数，并要求判断另一个数属于哪类。仅凭有限样本无法知道真实分布，先确认样本如何取得、标签是否可靠，以及漏判与误判的代价。接下来可以解释两种规则的结果，再用验证数据比较。

以下是手册自定例子：A 类样本为 0、10，B 类样本为 4、5、6，查询值是 9。最近邻距离 A 类的 10 只有 1，会选 A。两类均值都是 5，按均值分类无法区分；即使规定平票规则，类别中心也已经丢掉 A 类左右分布的信息。

在 d 维数据中，最近类别均值先计算每类中心 $\mu_c$，预测时选使 $\lVert x-\mu_c\rVert_2$ 最小的类。若每类都是同方差的各向同性高斯分布，且类别先验相同，这条规则与该模型的最大后验决策一致。实际分布的方差、先验或误判成本不同，就需要重新考虑规则。

最近邻适合先探索局部形状，但一个误标样本就可能影响附近预测。可用 K 个邻居投票来平滑，K 的选择需要验证。若特征量纲不同，先在训练集上确定缩放参数，再应用到验证集与测试集，避免大数值量纲控制距离。

存储 n 个 d 维样本需要 $O(nd)$ 空间，暴力最近邻一次查询耗时 $O(nd)$。若有 C 类，保存类别均值只需 $O(Cd)$ 空间，一次预测也约为 $O(Cd)$，代价更低，但可能牺牲局部分类质量。

**按均值分类就是 K-means 吗？**
训练时利用已知类别分别计算均值，是有监督的最近类别中心分类。K-means 要在没有这些类别标签时，通过交替分配样本和更新中心来寻找聚类。二者可以共用距离计算，学习目标不同。

**新数远离所有训练样本，仍应强制选一类吗？**
这取决于产品是否允许拒识。可以在验证数据上确定距离或不确定性规则，遇到明显超出训练分布的输入时转交其他方法。最近的类别不一定代表预测可靠。

原帖还讨论高斯核密度方法，并实现 KNN。本文的数值例子与概率假设是为解释比较而补充的练习内容。
