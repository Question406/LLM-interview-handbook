---
id: ml101-backprop
section: neural-networks
order: 2
level: A
title: backpropagation 怎样用链式法则计算梯度？
quick: >-
  backpropagation
  从损失往回走，把上游梯度乘当前运算的局部导数；一个变量影响多条路径时，把各路径贡献相加。前向保存必要中间值，反向复用它们算所有参数的梯度，优化器随后才更新参数。
tags:
  - ML101
  - neural-networks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-22'
sources:
  - title: 'Dive into Deep Learning: Forward and Backward Propagation'
    url: 'https://d2l.ai/chapter_multilayer-perceptrons/backprop.html'
    type: primary
---

backpropagation 用链式法则，从标量损失倒着计算每个参数的梯度。每个节点接收“损失对自己输出的导数”，再乘本节点的局部导数，传给输入；同一变量有多条下游路径时，要把贡献相加。 [Dive into Deep Learning: Forward and Backward Propagation](https://d2l.ai/chapter_multilayer-perceptrons/backprop.html)

例如 $z=wx+b$，$a=\mathrm{ReLU}(z)$，$L=(a-y)^2/2$。先有 $\partial L/\partial a=a-y$，在 $z>0$ 时，传到 $z$ 的梯度仍是 $a-y$，于是 $\partial L/\partial w=(a-y)x$、$\partial L/\partial b=a-y$。

取 $x=2,w=1,b=0,y=1$，得到 $z=a=2$，所以权重梯度是 2，偏置梯度是 1。这个小例子可以手算，也能与自动微分对照。矩阵层采用相同原则，只是梯度形状必须匹配输入与参数。

前向保留激活等必要中间值，反向按依赖顺序复用。算完梯度后，SGD 或 Adam 等优化器才负责参数更新。

## 追问

**backward 就等于训练一步吗？**
还不够。它主要计算并累积梯度，通常还要清理上一步梯度、执行优化器更新。

**共享参数的梯度怎么办？**
把所有使用位置的贡献相加，例如同一个权重在多条路径中出现。

**自动微分和数值差分一样吗？**
不同。自动微分按运算规则应用链式法则；差分通过扰动参数近似导数，适合抽样验算，但有步长和浮点误差。
