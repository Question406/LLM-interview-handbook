---
id: ml101-vanishing-exploding
section: neural-networks
order: 4
level: A
title: 梯度消失和梯度爆炸为什么发生？
quick: >-
  深层网络 backpropagation
  要连续乘各层的权重与激活导数，乘积反复缩小就梯度消失，反复放大就爆炸。先看各层梯度和激活，结合初始化、normalization、残差与学习率排查；gradient
  clipping 主要限制爆炸，无法补回已经消失的信号。
tags:
  - ML101
  - neural-networks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-22'
sources:
  - title: 'Dive into Deep Learning: Numerical Stability and Initialization'
    url: >-
      https://d2l.ai/chapter_multilayer-perceptrons/numerical-stability-and-init.html
    type: primary
---

梯度消失和爆炸来自 backpropagation 中的连乘：损失传到早期层，要经过许多局部导数和权重矩阵。若沿某个方向反复收缩，早期层几乎学不到；若反复放大，更新会剧烈震荡，甚至出现非有限数值。 [Dive into Deep Learning: Numerical Stability and Initialization](https://d2l.ai/chapter_multilayer-perceptrons/numerical-stability-and-init.html)

用标量类比，连续十次乘 0.1 只剩 $10^{-10}$，连续十次乘 10 变成 $10^{10}$。真实网络是矩阵乘积，不能仅凭某个权重的大小判断，但这个例子解释了深度为何会放大尺度问题。Sigmoid 饱和时局部导数很小，会加重收缩。

我会记录每层梯度范数、激活分布和非有限值的位置。选择匹配激活的初始化，检查输入尺度；normalization 与 residual connection 有助于训练深网，学习率过大也要单独排查。若偶发梯度尖峰，可按范数裁剪，再查异常样本和损失缩放。

## 追问

**loss 没有 NaN 就没有梯度问题吗？**
不是。早期层梯度可能已经很小，网络仍能输出有限 loss，但训练缓慢或停滞。

**裁剪能治梯度消失吗？**
不能。裁剪把大梯度压到上限，不会恢复缺失信号。

**初始化合理后还会爆炸吗？**
会。训练中权重、数据和优化状态都在变化，需要持续监测。
