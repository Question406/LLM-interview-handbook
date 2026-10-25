---
id: ml101-momentum-adam
section: optimization
order: 6
level: A
title: "Momentum、AdaGrad、RMSProp 和 Adam 的思路有什么区别？"
quick: "Momentum 平滑并积累梯度方向，AdaGrad 用每个坐标的历史平方梯度调节步长，RMSProp 让这份历史逐渐遗忘，Adam 再结合梯度动量与平方梯度滑动平均，并做初始偏差校正。它们改善更新方式，不替代学习率和泛化验证，也没有对所有任务都最优的统一赢家。"
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22
sources:
  - title: "Stanford CS229: Introduction to Deep Learning, optimization slide"
    url: https://cs229.stanford.edu/lectures-spring2023/cs229-conv_nets_slides.pdf
    type: primary
  - title: "Adam: A Method for Stochastic Optimization"
    url: https://arxiv.org/abs/1412.6980
    type: primary
---

动量法（Momentum）主要让更新方向更连贯，自适应方法则进一步给不同参数不同的有效步长。Adam 把这两种思路放在一起，但依然需要选择基础学习率。

Momentum 维护过去梯度的加权平均，反复一致的方向被累积，来回摆动的方向会被平滑。AdaGrad 累加每个坐标的平方梯度，用其平方根缩放更新；常出现大梯度的坐标步长变小，少出现的特征相对保留步长，但长期累积可能让后期更新太小。RMSProp 改用指数滑动平均，让很久以前的平方梯度逐渐淡出。四种方法的比较见 [Stanford CS229 课程材料](https://cs229.stanford.edu/lectures-spring2023/cs229-conv_nets_slides.pdf)。

Adam 同时维护梯度均值 m 和平方梯度均值 v，用校正后的 $\hat m/(\sqrt{\hat v}+\epsilon)$ 更新参数；这里 $\epsilon$ 防止分母太小。初始均值从零起步会偏小，偏差校正补偿这一点。原理见 [Adam 原论文](https://arxiv.org/abs/1412.6980)。例如两个参数的梯度尺度差很多，v 会让持续大梯度的坐标得到更小的相对步长。

## 追问

**Adam 的 v 就是梯度方差吗？**
是平方梯度的滑动平均，也就是原始二阶矩；没有减均值平方，不能直接当成方差。

**用了 Adam 还要调学习率吗？**
要。它调节各坐标的相对尺度，基础学习率仍控制整体更新幅度，最终还要比较验证表现。
