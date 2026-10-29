---
id: ml101-activations
section: neural-networks
order: 3
level: A
title: Sigmoid、tanh、ReLU 和 GELU 怎么选择？
quick: >-
  隐藏层常从 ReLU 或 GELU 开始，再按模型与验证结果选择；Sigmoid 常用于二分类概率或 gating，tanh
  输出零中心但也会饱和。选择要同时看梯度、输出范围和计算代价，不能用一个激活替换所有位置。
tags:
  - ML101
  - neural-networks
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-22'
sources:
  - title: 'PyTorch: Non-linear activations'
    url: 'https://docs.pytorch.org/docs/2.14/nn.html#non-linear-activations-other'
    type: primary
  - title: 'PyTorch: GELU'
    url: 'https://docs.pytorch.org/docs/2.14/generated/torch.nn.GELU.html'
    type: primary
---

激活函数要按它在网络里的位置选择。Sigmoid 把输入压到 0 到 1，适合概率或 gating；tanh 压到 -1 到 1、输出零中心，两者在输入绝对值很大时都会饱和，导数变小。ReLU 保留正半轴、把负值变成 0，隐藏层计算简单，但负半轴没有梯度。 [PyTorch: Non-linear activations](https://docs.pytorch.org/docs/2.14/nn.html#non-linear-activations-other)

GELU 写成 $x\Phi(x)$，其中 $\Phi$ 是标准正态分布的累积分布函数，平滑地调节输入，负值也可能留下部分响应。常见实现还提供 tanh 近似，选择时需与已有网络和计算预算一起验证。 [PyTorch: GELU](https://docs.pytorch.org/docs/2.14/generated/torch.nn.GELU.html)

例如二分类网络的隐藏层可以用 ReLU，最后输出一个 logit；若使用接收 logits 的 binary cross entropy，损失内部已做稳定处理，不要先重复加 Sigmoid。需要向用户展示概率时，再对 logit 做 Sigmoid。

## 追问

**ReLU 能彻底解决梯度消失吗？**
不能。正半轴导数为 1 有帮助，但长期落在负半轴的单元可能不再更新，整网梯度还受权重连乘影响。

**GELU 一定优于 ReLU 吗？**
不能这样保证。它更平滑，但计算和网络搭配不同，要比较同预算下的验证表现。

**回归输出也要 Sigmoid 吗？**
只在目标确实需要这个有界范围时考虑。无界数值回归通常用线性输出。
