---
id: ml101-feature-scaling
section: optimization
order: 3
level: S
title: "哪些模型需要特征缩放？标准化和归一化怎么选？"
quick: "依赖距离、梯度优化或系数惩罚的模型通常需要关注尺度，比如 kNN、SVM 和正则线性模型；常规阈值树通常不依赖同一尺度。标准化按训练均值与标准差缩放，Min-Max 压到指定范围，两者都只在训练集拟合并复用于验证与上线。"
tags:
  - Machine Learning
  - optimization
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "scikit-learn: Preprocessing data"
    url: https://scikit-learn.org/stable/modules/preprocessing.html
    type: primary
---

缩放让不同单位的特征在距离和优化目标中更可比较。例如年龄只差几岁、收入差几万元，直接算欧氏距离时，收入数值会压过年龄，即使它在任务中并不更重要。

标准化对每列做 $(x-\mu)/s$，$\mu$ 和 $s$ 是训练集均值与标准差。它不会把任意分布变成正态分布。Min-Max 则根据训练最小和最大值缩到指定区间，对极端值更敏感，新样本也可能超出训练区间。

对 kNN、RBF SVM、PCA，以及带 L1/L2 惩罚的线性模型，尺度会改变距离、方差或惩罚的实际意义。梯度下降也可能因各方向尺度悬殊而走得很慢。对通常按大小阈值分裂的树，严格单调变换会保留候选分组，往往不需要缩放。

离群值很多时可以尝试中位数与分位距缩放；稀疏数据还要避免中心化导致矩阵变稠密。所有统计量在训练折内学习，保持推理时使用同一版本。

## 面试追问

**归一化一定指 Min-Max 吗？**
不一定。这个词有时指把每一行向量缩成单位范数，例如文本余弦相似度。面试时要明确是按列缩放还是按样本归一化。

**标准化后能直接比较系数大小吗？**
比原始单位更可比，但仍会受特征相关性、编码和正则影响，系数大小不自动等于真实重要性或因果影响。
