---
id: "ml101-neural-debug"
section: "neural-networks"
order: 8
level: "A"
title: "神经网络训练不收敛，如何从一个小批次开始排查？"
quick: "先取一小批固定样本，关掉随机增强和强正则，检查模型能否把训练误差降得很低。若这一步失败，先查输入标签、loss、梯度与参数更新；通过后再恢复完整数据和随机性，排查泛化与优化问题。"
tags: ["ML101", "neural-networks"]
realInterview: false
status: published
format: "markdown"
updatedAt: "2026-10-22"
sources:
  - title: "Stanford CS231n: Learning and Sanity Checks"
    url: https://cs231n.github.io/neural-networks-3/
    type: primary
---

我会先固定一个很小的批次，尝试让模型把它记住，再扩大训练范围。这里验证的是数据到梯度更新这条路径是否工作；如果连少量样本都拟合不了，继续全量训练通常只会放大排查成本。 [Stanford CS231n: Learning and Sanity Checks](https://cs231n.github.io/neural-networks-3/)

例如挑一小组标签明确的分类样本，先逐个核对图像和标签，暂时去掉随机增强与强正则。检查输出维度、标签范围、损失是否接收 logits；再确认参数在优化器中、梯度有限且非空、更新后权重确实变化。观察 loss 是否持续下降，并尝试合理范围内的学习率。

如果失败，按数据、前向、loss、反向、更新的顺序缩小范围，必要时用小张量做数值梯度检查。若小批能拟合，逐步恢复正则、增强和更大数据，找出哪一步开始退化，再看训练与验证曲线。

## 追问

**小批拟合成功就说明实现完全正确吗？**
不能。模型可能记住了被错误打乱的输入，或者完整数据管道才有 bug，仍要检查样本语义和验证表现。

**训练 loss 低、验证差，先加大学习率吗？**
先检查过拟合、划分与分布差异。训练已能拟合，问题可能不在更新速度。

**一开始就换大模型有用吗？**
只有确认容量不足后才值得试。标签错位、断梯度和错误 loss 都不会因加深网络自动消失。
