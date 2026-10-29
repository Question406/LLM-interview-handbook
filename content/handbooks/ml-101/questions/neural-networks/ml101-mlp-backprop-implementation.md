---
id: ml101-mlp-backprop-implementation
section: neural-networks
order: 9
level: A
title: 不用 autograd，手写两层网络的前向、cross entropy 与 backpropagation
quick: >-
  先保存线性层与 ReLU 的前向结果，用稳定的 softmax cross entropy 计算损失。反向从 (预测概率−one-hot 标签)/batch
  size 开始，依次计算第二层、ReLU 和第一层的梯度；偏置梯度沿 batch 维求和。全部梯度算完后再更新参数，并用有限差分检查每个参数的梯度和形状。
companies:
  - google
tags:
  - Machine Learning
  - Backpropagation
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-22T00:00:00.000Z
sources:
  - title: Google NG 候选人面经：白板前反向传播、loss 与参数更新
    url: 'https://www.1point3acres.com/interview/thread/1166705'
    type: secondary
  - title: 'Stanford CS231n, Backpropagation and vectorized gradients'
    url: 'https://cs231n.github.io/optimization-2/'
    type: primary
  - title: 'Dive into Deep Learning, Forward and Backward Propagation'
    url: 'https://d2l.ai/chapter_multilayer-perceptrons/backprop.html'
    type: primary
---

## 题目描述

本题采用手册重构练习约定；下列接口、edge cases 和样例是为了独立完成练习而明确的要求。

仅用 NumPy 实现两层分类网络的前向、平均 cross entropy、全部参数与输入梯度，再提供一次梯度下降更新。不调用自动微分。

### 输入与接口

实现 `mlp_loss_grad`(X,y,params) 和 `mlp_train_step`(X,y,params,`learning_rate`)。X 为 N×D 有限矩阵；params 包含 W1(D×H)、b1(H)、W2(H×C)、b2(C)；N、D、H、C 均为正。y 是长度 N 的整数向量，标签在 [0,C)；`learning_rate` 为正有限数。

### 输出与约束

网络为 Z=XW1+b1，A=ReLU(Z)，logits=AW2+b2；loss 是逐样本 softmax cross entropy 的 batch 平均，不加正则。ReLU 在0点导数约定为0。应能稳定处理整体很大的 logits，合法输入中中间线性结果不溢出。

`mlp_loss_grad` 返回 (float loss,gradients)，gradients 含 W1、b1、W2、b2、X，形状与对应输入一致，均为同一平均 loss 的导数。`train_step` 返回 (更新前 loss,updated 参数字典)，按 parameter-`learning_rate`×gradient 同步更新四个参数；不更新 X，不原地修改输入参数。

### 示例

```text
X=[[2]]，y=[0]
params={W1:[[1]],b1:[0],W2:[[0,0]],b2:[0,0]}
loss -> log(2)≈0.693147
gradients.W2 -> [[-1,1]]，gradients.b2 -> [-0.5,0.5]
gradients.W1、b1、X 均为0
learning_rate=0.1 时 updated.W2 -> [[0.1,-0.1]]，updated.b2 -> [0.05,-0.05]
```

## 解题思路与参考答案

手写 backpropagation 时，先固定网络、损失和各张量形状，再按链式法则从 loss 向输入推回去。每个参数的梯度都算完后，才执行更新，避免上游梯度用到已经改变的权重。

Google 原帖明确要求在白板写公式、说明前向、loss、链式法则与更新，没有指定这份 NumPy 编程接口。下面是手册重构练习：输入 X 为 N×D，隐藏宽度 H，类别数 C；W1 为 D×H，b1 为 H，W2 为 H×C，b2 为 C。网络为线性层、ReLU、线性层，损失为 batch 平均 softmax cross entropy。只用 NumPy，不调用 autograd；ReLU 在零点约定导数为 0，不加正则。

记 $Z=XW_1+b_1$，$A=\max(Z,0)$，$S=AW_2+b_2$，P 为逐行 softmax 概率，Y 为 one-hot 标签。输出层梯度为 $G=(P-Y)/N$。随后有

$$
\nabla W_2=A^TG,\quad \nabla b_2=\sum_iG_i,\quad
G_Z=(GW_2^T)\odot\mathbf1[Z>0],
$$

$$
\nabla W_1=X^TG_Z,\quad \nabla b_1=\sum_i(G_Z)_i,\quad
\nabla X=G_ZW_1^T.
$$

偏置在前向广播给所有样本，反向要汇总这些样本的贡献。N 只在输出层梯度中除一次；后面每个矩阵乘法沿用这份缩放，再除 N 会把梯度额外缩小 N 倍。

```python
import numpy as np


def mlp_loss_grad(X, y, params):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    W1, b1, W2, b2 = [
        np.asarray(params[key], dtype=float) for key in ("W1", "b1", "W2", "b2")
    ]
    if X.ndim != 2 or min(X.shape) == 0 or not np.isfinite(X).all():
        raise ValueError("X must be a nonempty finite matrix")
    if W1.ndim != 2 or W2.ndim != 2 or min(W1.shape) == 0 or min(W2.shape) == 0:
        raise ValueError("weights must be nonempty matrices")
    n, d = X.shape
    h, c = W1.shape[1], W2.shape[1]
    if W1.shape[0] != d or W2.shape[0] != h or b1.shape != (h,) or b2.shape != (c,):
        raise ValueError("parameter shapes do not match")
    if not all(np.isfinite(v).all() for v in (W1, b1, W2, b2)):
        raise ValueError("parameters must be finite")
    if y.shape != (n,) or not np.issubdtype(y.dtype, np.integer):
        raise ValueError("y must be an integer vector of length n")
    if (y < 0).any() or (y >= c).any():
        raise ValueError("class index out of range")

    Z = X @ W1 + b1
    A = np.maximum(Z, 0)
    S = A @ W2 + b2
    if not np.isfinite(Z).all() or not np.isfinite(S).all():
        raise ValueError("forward overflow; rescale inputs or parameters")
    shifted = S - S.max(axis=1, keepdims=True)
    exp_scores = np.exp(shifted)
    totals = exp_scores.sum(axis=1, keepdims=True)
    loss = np.mean(np.log(totals[:, 0]) - shifted[np.arange(n), y])

    G = exp_scores / totals
    G[np.arange(n), y] -= 1
    G /= n
    dW2 = A.T @ G
    db2 = G.sum(axis=0)
    dZ = (G @ W2.T) * (Z > 0)
    gradients = {
        "W1": X.T @ dZ,
        "b1": dZ.sum(axis=0),
        "W2": dW2,
        "b2": db2,
        "X": dZ @ W1.T,
    }
    return float(loss), gradients


def mlp_train_step(X, y, params, learning_rate):
    if not np.isfinite(learning_rate) or learning_rate <= 0:
        raise ValueError("learning_rate must be finite and positive")
    loss, gradients = mlp_loss_grad(X, y, params)
    updated = {
        key: np.asarray(params[key], dtype=float) - learning_rate * gradients[key]
        for key in ("W1", "b1", "W2", "b2")
    }
    return loss, updated
```

取一个样本 X=[[2]]、标签 0，W1=[[1]]、b1=[0]、W2=[[0,0]]、b2=[0,0]。隐藏激活为 2，两类概率各 0.5，loss 为 log 2。W2 梯度是 [[−1,1]]，b2 梯度是 [−0.5,0.5]；因为当前 W2 为零，传回 W1 与 b1 的梯度都是零。用 0.1 的学习率更新，类别 0 的分数升高，重新计算 loss 会下降。

两个线性层的主要计算量为 $O(NDH+NHC)$；反向与前向同阶。参数、梯度和缓存约需 $O(DH+HC+NH+NC+ND)$ 空间。本代码返回输入梯度用于验证，但训练分类器时通常不更新 X。

**怎样做 gradient check？**
对参数的一个坐标做中心差分 $[L(\theta+\epsilon)-L(\theta-\epsilon)]/(2\epsilon)$，与解析梯度比较。用 float64、小网络和合适步长，检查所有参数及输入坐标。ReLU 在零点不可微，要选扰动不会跨越零点的测试数据，不能拿不可微点的差分结果判定实现错误。

**为什么 softmax 要减行最大值？**
减去同一常数不改变概率，能避免直接指数化大正数溢出。损失直接从移位后的 logits 和 log-sum-exp 算，不先取可能下溢为零的真实类概率再做 log；稳定 softmax 加上 `log(0)` 仍然会出问题。

**共享参数或多条路径怎么处理？**
各使用位置的梯度贡献需要相加。偏置的 batch 求和就是一个例子；如果同一个权重还出现在另一个分支，需要再把该分支贡献加上。用赋值覆盖已有梯度会漏掉路径。

## 简单测试怎么写

把上面的实现保存为 `solution.py`，以下测试放在实现之后。数值测试使用参考实现相同的 PyTorch 或 NumPy 环境；浮点结果用带容差的比较。运行 `python3 solution.py`，成功时输出 `simple tests passed`，失败时按断言报错行定位。不要加 `-O`，它会跳过 `assert`。

一维隐藏层激活为 2，输出权重全零时两类概率都为 0.5，loss=log(2)，W2 梯度为 [-1,1]。更新一步后损失应下降，原参数字典保持原值。

```python
import numpy as np
import math

params = {
    "W1": np.array([[1.0]]),
    "b1": np.array([0.0]),
    "W2": np.array([[0.0, 0.0]]),
    "b2": np.array([0.0, 0.0]),
}
loss, gradient = mlp_loss_grad([[2]], [0], params)
assert abs(loss - math.log(2)) < 1e-10
np.testing.assert_allclose(gradient["W2"], [[-1, 1]])
_, updated = mlp_train_step([[2]], [0], params, 0.1)
assert mlp_loss_grad([[2]], [0], updated)[0] < loss
np.testing.assert_allclose(params["W2"], 0)
print("simple tests passed")
```
