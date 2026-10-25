---
id: ml101-optimizer-implementation
section: optimization
order: 9
level: A
title: 手写 SGD、Momentum 和 Adam，怎样管理状态与偏差校正？
quick: SGD 直接沿梯度更新；Momentum 保存累计方向；Adam 保存梯度一阶矩和平方梯度二阶矩，并按步数校正从零初始化产生的偏差。状态必须跨 step 保留且与对应参数绑定，全部梯度算好后再更新。练习采用经典 Momentum 累积梯度约定，不含 Nesterov、weight decay 或 AdamW。
tags: [ML Fundamentals, Optimization, Coding]
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-23
sources:
  - title: Adam, A Method for Stochastic Optimization
    url: https://arxiv.org/abs/1412.6980
    type: primary
  - title: Stanford CS231n, Parameter updates
    url: https://cs231n.github.io/neural-networks-3/
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、边界和样例是为了独立完成练习而明确的要求，不代表面试帖逐字题面。

用 NumPy 为一个参数数组实现 SGD、Momentum 和 Adam，并维护跨 step 的优化器状态。

### 输入与接口

实现 ArrayOptimizer(mode="adam",*,lr=0.01,momentum=0.9,beta1=0.9,beta2=0.999,eps=1e-8) 与 step(parameter,gradient)。mode 为 sgd/momentum/adam；lr、eps 为正有限数；三个衰减系数在 [0,1)。parameter、gradient 为同形非空有限数组；一个实例的所有 step 使用同一形状。

### 输出与约束

step 返回新参数数组，不原地修改 parameter 或 gradient；每调用一次计数 t 增加1。初始化状态 m、v 为同形全0。SGD 更新量为当前梯度。Momentum 使用 m=momentum×m+gradient，更新量为 m，不乘 (1-momentum)，不采用 Nesterov。

Adam 使用 m=beta1×m+(1-beta1)×g、v=beta2×v+(1-beta2)×g²；以当前 t 做一阶、二阶偏差修正，更新量为修正后m/(sqrt(修正后v)+eps)。三种模式均执行 parameter-lr×更新量；不加权重衰减。状态保留在优化器实例中，每个参数数组应有独立实例。

### 示例

```text
初始 parameter=[1]，lr=0.1，每次 gradient=[2]，连续两次 step
SGD -> 第一次[0.8]，第二次[0.6]
Momentum(momentum=0.9) -> 第一次[0.8]，第二次[0.42]
两种优化器最后 t -> 2
```

## 解题思路与参考答案

优化器把已经算好的梯度转换为参数更新。实现时要明确状态如何初始化、何时推进步数，以及 Momentum 采用哪种约定，否则看似相同的公式可能给出不同学习率尺度。

本练习中，SGD 更新为 $\theta_t=\theta_{t-1}-\alpha g_t$；Momentum 用 $u_t=\mu u_{t-1}+g_t$，再减去 $\alpha u_t$。这里没有把当前梯度乘 $1-\mu$。采用指数均值形式的其他教材也可以成立，但不能混用两套学习率解释。

Adam 保存 $m_t=\beta_1m_{t-1}+(1-\beta_1)g_t$ 和 $v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2$。从零初始化时使用 $\hat m_t=m_t/(1-\beta_1^t)$、$\hat v_t=v_t/(1-\beta_2^t)$，更新为

$$
\theta_t=\theta_{t-1}-\alpha\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon}.
$$

每个实例只管理一个参数数组。参数和梯度形状固定、值有限；step 返回新数组，不修改调用者的参数。训练循环负责计算 loss 和梯度。本练习不含权重衰减、梯度裁剪、稀疏状态或混合精度。

```python
import numpy as np


class ArrayOptimizer:
    def __init__(self, mode="adam", *, lr=0.01, momentum=0.9,
                 beta1=0.9, beta2=0.999, eps=1e-8):
        if mode not in ("sgd", "momentum", "adam"):
            raise ValueError("unknown optimizer")
        if not np.isfinite(lr) or lr <= 0 or not np.isfinite(eps) or eps <= 0:
            raise ValueError("lr and eps must be positive")
        if not all(0 <= value < 1 for value in (momentum, beta1, beta2)):
            raise ValueError("decay coefficients must be in [0, 1)")
        self.mode, self.lr, self.eps = mode, lr, eps
        self.momentum, self.beta1, self.beta2 = momentum, beta1, beta2
        self.t, self.m, self.v = 0, None, None

    def step(self, parameter, gradient):
        parameter, gradient = [np.asarray(v, dtype=float) for v in (parameter, gradient)]
        if parameter.size == 0 or parameter.shape != gradient.shape:
            raise ValueError("nonempty parameter and gradient shapes must match")
        if not np.isfinite(parameter).all() or not np.isfinite(gradient).all():
            raise ValueError("parameter and gradient must be finite")
        if self.m is None:
            self.m, self.v = np.zeros_like(parameter), np.zeros_like(parameter)
        if self.m.shape != parameter.shape:
            raise ValueError("optimizer state belongs to a different shape")
        self.t += 1
        if self.mode == "sgd":
            update = gradient
        elif self.mode == "momentum":
            self.m = self.momentum * self.m + gradient
            update = self.m
        else:
            self.m = self.beta1 * self.m + (1-self.beta1) * gradient
            self.v = self.beta2 * self.v + (1-self.beta2) * gradient ** 2
            corrected_m = self.m / (1-self.beta1 ** self.t)
            corrected_v = self.v / (1-self.beta2 ** self.t)
            update = corrected_m / (np.sqrt(corrected_v) + self.eps)
        return parameter - self.lr * update
```

例如 theta=1、梯度恒为 2、学习率 0.1。SGD 两步到 0.6。Momentum 系数 0.9 时，方向先为 2，再为 3.8，两步到 0.42。Adam 第一轮校正后的均值为 2、二阶矩为 4，更新量约为 0.1；第二轮恒定梯度下仍约为 0.1，参数约为 0.8。误把 t 每轮重置为 1，会破坏后续的偏差校正。

每步时间和状态空间均为 $O(P)$，P 为参数元素数；Adam 额外保存两份矩数组。对整个网络，要为各参数保存相应状态，并一致推进优化器步；不能把同一个数组实例的状态轮流借给两个无关参数。

**二阶矩是不是梯度方差？**
不是。这里平均的是梯度平方，没有减去均值平方。称为“平方梯度的指数平均”更准确，也能避免把分母错误实现成方差的平方根。

**怎样验证状态真的保留了？**
先核对上面的两步恒定梯度，再用梯度序列 [2,−1] 独立手算每轮 m、v 和校正值。只测第一步无法发现状态清零、步数错误或第二轮更新方向的问题。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

从参数 1 开始，每次梯度为 2、学习率 0.1，SGD 两步后为 0.6。动量为 0.9 的版本第二步多累积历史梯度，两步后为 0.42。每种模式重新创建优化器。

```python
import numpy as np
for mode, expected in [("sgd", 0.6), ("momentum", 0.42)]:
    optimizer = ArrayOptimizer(mode, lr=0.1, momentum=0.9)
    value = np.array([1.])
    for _ in range(2):
        value = optimizer.step(value, [2])
    np.testing.assert_allclose(value, [expected])
    assert optimizer.t == 2
print("simple tests passed")
```
