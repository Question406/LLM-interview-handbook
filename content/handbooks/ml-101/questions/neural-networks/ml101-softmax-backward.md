---
id: ml101-softmax-backward
section: neural-networks
order: 10
level: A
title: 推导 Softmax 的 Jacobian，并实现任意上游梯度的 backward
quick: >-
  Softmax 的 Jacobian 是 diag(p)−ppᵀ，单个输出同时依赖所有输入。给定上游梯度 g，输入梯度可直接算成
  p⊙(g−sum(g⊙p))，无需构造完整矩阵。先减去每行最大值再指数化，可以稳定前向；p−y 则是接 cross entropy
  后的组合梯度，不能当成通用 Softmax backward。
tags:
  - ML Fundamentals
  - Backpropagation
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-23T00:00:00.000Z
sources:
  - title: 'Stanford CS231n, Backpropagation and vectorized gradients'
    url: 'https://cs231n.github.io/optimization-2/'
    type: primary
  - title: 'Stanford CS231n, Linear classification and Softmax'
    url: 'https://cs231n.github.io/linear-classify/'
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

实现逐行 Softmax 前向，以及接收任意上游梯度的通用 backward，并说明相应 Jacobian 的数学含义。

### 输入与接口

实现 `softmax_forward`(logits) 与 `softmax_backward`(upstream,probabilities)。logits 为非空 N×C 有限实数矩阵；probabilities 是前向得到的同形非负概率矩阵，每行和为1；upstream 是同形有限矩阵，表示标量目标对每个概率的导数。数值运算处于 float64 可表示范围内。

### 输出与约束

forward 返回逐行 normalization 概率，与输入同形；应对 logits 每行整体加常数保持相同结果，并稳定处理大正数。backward 返回标量目标对 logits 的梯度，与 logits 同形。

backward 必须支持任意 upstream，不能限定为分类 cross entropy 标签，不自动再除 batch size。无需构造 N×C×C 的显式 Jacobian。不修改输入。单类别时概率为1、输入梯度为0。

### 示例

```text
softmax_forward([[0,0]]) -> [[0.5,0.5]]
softmax_backward([[2,0]],[[0.5,0.5]]) -> [[0.5,-0.5]]
softmax_backward([[1,1]],[[0.5,0.5]]) -> [[0,0]]
softmax_forward([[1000,1001]]) 与 softmax_forward([[0,1]]) 相同
```

## 解题思路与参考答案

Softmax 的反向需要考虑同一行所有类别之间的依赖。输入某个分量改变时，分母也改变，其他输出概率会一起变化。

对一行 logits z，$p_i=e^{z_i}/\sum_j e^{z_j}$。求导得到

$$
\frac{\partial p_i}{\partial z_j}=p_i(\mathbf1[i=j]-p_j),\qquad J=\operatorname{diag}(p)-pp^T.
$$

设上游传来 $g_i=\partial L/\partial p_i$，链式法则要求计算 $J^Tg$。整理后，第 j 个输入的梯度为 $p_j(g_j-\sum_i g_ip_i)$。每行只需一次加权求和，计算量随类别数线性增长。

以下通用练习约定 logits 与上游梯度均为非空 N×C 有限矩阵，沿最后一维 normalization；数值运算需在 float64 可表示范围内。backward 接收前向得到的概率，不负责对 loss 再做 batch 平均。

```python
import numpy as np


def softmax_forward(logits):
    logits = np.asarray(logits, dtype=float)
    if logits.ndim != 2 or min(logits.shape) == 0 or not np.isfinite(logits).all():
        raise ValueError("logits must be a nonempty finite matrix")
    shifted = logits - logits.max(axis=1, keepdims=True)
    exponentials = np.exp(shifted)
    return exponentials / exponentials.sum(axis=1, keepdims=True)


def softmax_backward(upstream, probabilities):
    g = np.asarray(upstream, dtype=float)
    p = np.asarray(probabilities, dtype=float)
    if g.ndim != 2 or min(g.shape) == 0 or p.shape != g.shape:
        raise ValueError("gradient and probability matrices must match")
    if not np.isfinite(g).all() or not np.isfinite(p).all():
        raise ValueError("inputs must be finite")
    if (p < 0).any() or not np.allclose(p.sum(axis=1), 1):
        raise ValueError("each probability row must sum to one")
    return p * (g - (g * p).sum(axis=1, keepdims=True))
```

例如 z=[0,0]，概率为 [0.5,0.5]；上游梯度为 [2,0] 时，输入梯度是 [0.5,−0.5]。如果上游为 [1,1]，梯度为零，因为这时 L 是所有概率之和，恒等于 1。每行输入梯度之和也应为零，对应给整行 logits 加相同常数不会改变输出。

前向和反向耗时、输出及主要临时空间都是 $O(NC)$。显式保存每行 C×C Jacobian 会占 $O(NC^2)$ 空间，这里只用它推导，不在实现中构造。

**为什么常见代码直接写 p−y？**
当 loss 是 one-hot 标签的 cross entropy 时，loss 对概率的导数与 Softmax 的 Jacobian 结合后恰好简化为 p−y；若 loss 按 batch 平均，还要除 N。其他上游 loss 应使用通用表达式。

**怎样验证梯度？**
固定任意 g，把标量目标设为 $L=\sum_{n,c}g_{nc}p_{nc}$，对每个 logit 做中心差分，再比较解析梯度。另检查大 logits、平移不变性、单类别输出与梯度行和，避免只验证 cross entropy 这个特殊情形。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

两类等概率时，上游梯度 [2,0] 应得到 [0.5,-0.5]；常数上游梯度应得到零。加 1000 后分布不变，同时覆盖数值稳定性。

```python
import numpy as np

p = softmax_forward([[0, 0]])
np.testing.assert_allclose(p, [[0.5, 0.5]])
np.testing.assert_allclose(softmax_backward([[2, 0]], p), [[0.5, -0.5]])
np.testing.assert_allclose(softmax_backward([[1, 1]], p), 0)
np.testing.assert_allclose(softmax_forward([[1000, 1001]]), softmax_forward([[0, 1]]))
print("simple tests passed")
```
