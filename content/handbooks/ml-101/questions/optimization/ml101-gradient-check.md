---
id: ml101-gradient-check
section: optimization
order: 8
level: A
title: 如何用数值差分检查梯度实现？
quick: >-
  数值梯度检查把某个参数略微加减扰动，用损失差估计该坐标的导数，再与 backpropagation
  结果比较。检查时固定数据和随机性，优先用双精度、小模型与中心差分，并同时看绝对和相对误差。扰动过小会受浮点抵消影响，过大又不再近似局部导数。
tags:
  - ML Fundamentals
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: 'Stanford CS231n: Gradient Checks'
    url: 'https://cs231n.github.io/neural-networks-3/#gradcheck'
    type: primary
  - title: 'SciPy: check_grad'
    url: >-
      https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.check_grad.html
    type: primary
---

检查梯度时，我会暂时不做参数更新，直接比较 backpropagation 导数和损失的数值变化。这样可以定位符号、转置、漏项或归约系数等实现错误。

设损失是 $L(\theta)$，参数向量为 $\theta$，第 i 个单位向量为 $e_i$。中心差分为 $g_i^{num}=[L(\theta+h e_i)-L(\theta-h e_i)]/(2h)$，h 是小扰动。两边只改同一个参数，其他参数、输入和随机状态固定。例如 $L(w)=w^2$，在 w=3 处，这个式子给出约 6，应与解析梯度一致。方法见 [Stanford CS231n 梯度检查](https://cs231n.github.io/neural-networks-3/#gradcheck)。

先用 64 位浮点数（float64）和少量参数检查，再抽查大模型坐标；比较时兼顾绝对误差与相对误差，接近零的梯度不能只看比例。试几个不同 h，看误差是否有稳定的合理范围。对 ReLU 的折点等不可微位置，差分可能跨越两条分支，应换测试点；dropout、random sampling 或会更新状态的层也要先固定行为。

## 追问

**h 越小越准确吗？**
不是。太小时两次损失几乎相同，相减会放大舍入误差；太大时则增加局部近似误差。

**为什么不拿它直接训练？**
逐坐标中心差分每个参数需要两次损失计算，参数多时很贵。它适合调试，backpropagation 更适合训练。
