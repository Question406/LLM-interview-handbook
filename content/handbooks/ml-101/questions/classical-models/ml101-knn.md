---
id: ml101-knn
section: classical-models
order: 3
level: S
title: "kNN 怎么预测？K 值和高维特征会带来什么影响？"
quick: "kNN 在训练样本中找离新样本最近的 K 个邻居，分类投票、回归取均值，也可按距离加权。K 小对局部噪声敏感，K 大更平滑却可能混合不同区域；高维无关特征会冲淡距离意义，预测时的搜索成本也要考虑。"
tags:
  - Machine Learning
  - classical-models
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Nearest Neighbors"
    url: https://scikit-learn.org/stable/modules/neighbors.html
    type: primary
---

kNN 假设相近输入通常有相近输出。训练主要保存样本，预测时根据选定距离查找邻居，分类看多数标签，回归平均目标值。

比如新用户最近的五个训练邻居中，有三人购买、两人没购买，均匀投票就判为购买。这里三比二只是一种局部比例估计，不能自动视为准确 calibration 的 60% 购买概率。

K 为 1 时，一个误标邻居就能改变结果；K 很大时，预测会向整体多数类或平均值靠近，丢失局部规律。通过交叉验证选 K，同时验证距离、特征缩放和权重。

高维下，无关特征会累积大量距离差异，附近样本也可能需要更多数据才能找到。先做有依据的特征选择或降维，确认距离与任务有关系。暴力查找单次查询大致要比较所有训练样本，每次距离计算还随特征数增长；索引在高维也未必有效。

## 面试追问

**kNN 为什么叫非参数方法？**
它没有用一组固定规模参数概括所有训练数据，模型存储和复杂度可随样本量增长。非参数不表示完全没有 K、距离等超参数。

**类别不平衡会怎样影响 kNN？**
多数类更容易占据邻域投票。可以验证距离权重、类别权重或合适 sampling，但仍要确认少数类邻域有足够真实样本。
