---
id: ml101-mlp
section: neural-networks
order: 1
level: A
title: 多层感知机为什么需要非线性激活函数？
quick: >-
  多个线性层连起来仍然等价于一个线性变换，非线性激活才让 MLP 能表示 nonlinear decision boundary 和特征交互。比如 XOR
  的正例在两个对角，单条直线分不开，加隐藏单元和非线性后可以组合出这样的区域。
tags:
  - ML101
  - neural-networks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-22'
sources:
  - title: 'Dive into Deep Learning: Multilayer Perceptrons'
    url: 'https://d2l.ai/chapter_multilayer-perceptrons/mlp.html'
    type: primary
---

MLP（多层感知机）需要非线性激活，才能通过多层组合表达复杂关系。假如每层只有矩阵乘法和偏置，两层 $W_2(W_1x+b_1)+b_2$ 可以合成一个仿射变换，加深不会扩大这类函数的表达范围。 [Dive into Deep Learning: Multilayer Perceptrons](https://d2l.ai/chapter_multilayer-perceptrons/mlp.html)

隐藏层通常先算 $z=Wx+b$，再算 $h=\phi(z)$，其中 $\phi$ 是 ReLU 等非线性函数。下一层便可以组合不同隐藏单元提取的模式，而不只是继续旋转、缩放输入。

例如 XOR 中，输入是两个二进制数，只有恰好一个为 1 时输出 1。两个正例在对角，无法用单条直线与负例分开。隐藏单元可以先表示不同区域，再由输出层组合。这个例子说明需要非线性；实际能否学到，还取决于容量、初始化与优化。

## 追问

**每一层都必须有非线性吗？**
隐藏层之间需要足够的非线性来增加表达能力。输出层按任务决定：回归可直接输出数值，分类通常输出 logits。

**把所有权重初始化为 0 可以吗？**
隐藏层同组单元会得到相同输出和梯度，难以学到不同功能，通常用随机权重打破对称性。

**网络越深就一定越好吗？**
不一定。深度增加表达方式，也增加优化和 overfitting 风险，要用验证结果与成本判断。
