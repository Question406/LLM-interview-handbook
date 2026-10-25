---
id: "ml101-initialization"
section: "neural-networks"
order: 5
level: "A"
title: "Xavier 和 He 初始化为什么与输入维度有关？"
quick: "一个神经元要累加很多输入，输入维度越大，输出方差越容易被放大，所以权重方差要随 fan-in 缩小。Xavier 兼顾输入输出维度，He 为 ReLU 常用约 2/fan-in 的方差；还要核对权重矩阵的布局。"
tags: ["ML101", "neural-networks"]
realInterview: false
status: published
format: "markdown"
updatedAt: "2026-10-22"
sources:
  - title: "PyTorch: torch.nn.init"
    url: https://docs.pytorch.org/docs/2.14/nn.init.html
    type: primary
---

Xavier 和 He 初始化都在控制信号尺度，让激活与梯度经过多层后尽量不过大或过小。fan-in 是进入一个单元的输入数，fan-out 是它连接的输出数；输入项越多，权重若不缩小，累加结果的方差就越大。 [PyTorch: torch.nn.init](https://docs.pytorch.org/docs/2.14/nn.init.html)

在独立、零均值等近似下，$z=\sum_i w_i x_i$ 的方差约为 $n_{\mathrm{in}}\mathrm{Var}(w)\mathrm{Var}(x)$。因此 Xavier 常用权重方差 $2/(n_{\mathrm{in}}+n_{\mathrm{out}})$；He 的 ReLU fan-in 版本常用 $2/n_{\mathrm{in}}$，补偿激活截去负半轴造成的尺度变化。

例如 ReLU 层有 100 个输入，He 正态初始化的标准差约为 $\sqrt{2/100}$。输入变成 400 个时，标准差约减半。这个估算建立在分布假设上，并非任意网络都保证方差不变。

实现时还要看参数布局。PyTorch Linear 通常把权重存成输出维乘输入维；自己采用相反乘法约定时，要确认初始化函数计算的 fan 值没有倒置。

## 追问

**Xavier 是把权重都设成同一个数吗？**
不是。它规定随机分布的尺度，仍需打破单元对称性。

**bias 也按同样规则随机吗？**
通常可以从零偏置开始。这里主要讨论权重的方差传播。

**有归一化就不用管初始化了吗？**
仍要管。初始化还影响梯度、残差分支和前几步的数值范围。
