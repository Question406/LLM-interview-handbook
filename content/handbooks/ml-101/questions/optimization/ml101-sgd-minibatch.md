---
id: ml101-sgd-minibatch
section: optimization
order: 2
level: S
title: 全批量、SGD 和小批量梯度下降有什么区别？
quick: >-
  全批量每次用全部训练样本算梯度，SGD
  每次用一个样本，小批量用一组样本。它们在梯度精度、更新频率、内存和硬件效率之间取舍；小批量通常能兼顾向量化与更新速度，批量大小也需要和学习率一起调整。
tags:
  - Machine Learning
  - optimization
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'scikit-learn: Stochastic Gradient Descent'
    url: 'https://scikit-learn.org/stable/modules/sgd.html'
    type: primary
---

三种方法优化的是同一个经验目标，主要区别是一次更新用多少样本估计梯度。全批量方向稳定，但每走一步都要扫完数据；单样本更新便宜但噪声大，小批量在两者之间。

如果目标是各样本损失的平均，均匀随机抽取的单样本梯度就是整体梯度的 unbiased estimate。独立抽样等理想条件下，平均更多样本会降低梯度方差；实际无放回抽样和样本相关性会影响具体数值。

例如一百万个样本，批量 256 的一次更新只使用其中一小部分，能在完整读完数据前完成很多次参数调整，同时利用矩阵运算。批量太大可能占满内存，减少同样样本预算下的更新次数；批量太小又可能让硬件利用率很低。

比较配置时要说明按 epoch、更新步数还是墙钟时间比较。扩大批量后直接复用原学习率和轮数，结果差异未必来自批量本身。

## 面试追问

**SGD 是一种模型吗？**
它是优化方法。逻辑回归、线性 SVM 和神经网络都可以用它训练，具体学到什么由模型和损失决定。

**为什么通常每轮要打乱训练数据？**
减少固定样本顺序带来的相关更新。时间预测的验证切分仍应保持 time boundaries，训练内部是否打乱则取决于模型和样本是否包含序列状态。
