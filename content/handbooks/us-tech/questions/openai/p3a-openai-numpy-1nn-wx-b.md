---
id: p3a-openai-numpy-1nn-wx-b
section: openai
order: 604
level: S
title: "OpenAI：NumPy 1-NN 向量化与神经网络形式"
quick: "展开平方欧氏距离后，查询自身范数对所有候选都相同，可以去掉，剩下比较 2q·x - ||x||²。把训练点的两倍作权重、负平方范数作偏置，一次 Wx + b 再 argmax 就得到 1-NN。L1 没有同样的点积展开，要另算广播距离，并注意中间内存。"
companies:
  - openai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - OpenAI
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · OpenAI · numpy-1nn-wx-b"
    url: https://www.1point3acres.com/interview/problems/company/openai/numpy-1nn-wx-b
    type: secondary
---

## 题目描述

实现批量 1-最近邻分类。给定训练点、各训练点的标签和多个查询点，按指定距离为每个查询返回最近训练点的标签；另实现与 L2 最近邻排序一致的线性打分接口。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `nearest(train, labels, query, metric="l2")`：`train` 形状 $(N, D)$，`query` 形状 $(M, D)$，`labels` 长度 $N$；返回 $M$ 个 label。`"l2"` 是平方欧氏距离，`"l1"` 是曼哈顿距离，`metric` 只取这两个合法值。距离并列时取训练下标最小的样本。不允许按查询写 Python 循环。
- `network_scores(train, query)`：返回 $(M, N)$ 的分数矩阵，等于 $q W^\top + b$，其中 $W = 2 \cdot \text{train}$、$b_i = -\|x_i\|^2$；分数最大的列就是 L2 最近邻。
- 训练集非空，维度要一致。$N, M \le 1000$，$D \le 128$。

### 示例

```text
train = [[0, 0], [2, 0]], labels = ["a", "b"]
nearest(train, labels, [[1.9, 0], [1, 0]])   -> ["b", "a"]
```

## 解题思路与参考答案

我会先确认距离定义：平方欧氏距离可以展开后用一次矩阵乘法评分，L1 则要广播求绝对差。比如查询 [1, 0] 距离训练点 [0, 0]、[2, 0] 相同，要按约定取较小下标。写成神经网络形式时，每个输出单元对应一个训练样本，权重直接由训练点确定。

用 NumPy 实现 1-最近邻（1-NN）分类：给训练向量和它们的 label，对每个查询向量返回距离最近的训练样本的 label，不能写 Python 循环。然后把这个分类器改写成神经网络前向的形式：一层 $Wx + b$ 再接一个激活（这里是 argmax）。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；`realInterview` 只表示网站收录了这类面经，不代表公司确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

先和面试官确认距离是平方欧氏距离还是 L1 距离，因为只有前者能改写成线性层。

平方欧氏距离可以展开成

$$\|q - x_i\|^2 = \|q\|^2 - 2\, q \cdot x_i + \|x_i\|^2$$

对同一个查询 $q$，$\|q\|^2$ 对所有候选都一样，比较时可以去掉。于是「找距离最小的 $x_i$」等价于「找 $2\, q \cdot x_i - \|x_i\|^2$ 最大的 $x_i$」。把每个训练样本看成一个输出单元，权重是 $2 x_i$、偏置是 $-\|x_i\|^2$，整个分类器就是一层 $Wx + b$ 加 argmax。向量化时一次矩阵乘法就能算出所有查询对所有训练样本的分数。

L1 距离 $\sum_d |q_d - x_{i,d}|$ 没有这种点积展开，只能用广播算出 $(M, N, D)$ 的差再求和，内存会大很多。

后续常被追问的是显存：距离矩阵是 $M \times N$，数据大时要分块。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `nearest(train, labels, query, metric="l2")`：`train` 形状 $(N, D)$，`query` 形状 $(M, D)$，`labels` 长度 $N$；返回 $M$ 个 label。`"l2"` 是平方欧氏距离，`"l1"` 是曼哈顿距离，其他值抛 `ValueError`。距离并列时取训练下标最小的样本。不允许按查询写 Python 循环。
- `network_scores(train, query)`：返回 $(M, N)$ 的分数矩阵，等于 $q W^\top + b$，其中 $W = 2 \cdot \text{train}$、$b_i = -\|x_i\|^2$；分数最大的列就是 L2 最近邻。
- 训练集非空，维度要一致，否则抛 `ValueError`。$N, M \le 1000$，$D \le 128$。

### 输入输出示例

```text
train = [[0, 0], [2, 0]], labels = ["a", "b"]
nearest(train, labels, [[1.9, 0], [1, 0]])   -> ["b", "a"]
```

第二个查询 `[1, 0]` 到两个训练点的距离都是 1，按约定取下标小的 `"a"`。

### 解题思路与正确性

L2 分支直接用 `network_scores` 的 argmax：对固定查询，分数等于「负的平方距离加上一个与候选无关的常数 $\|q\|^2$」，所以分数最大的列就是距离最小的样本。`np.argmax` 在并列时返回第一个下标，正好满足并列规则。

这是用训练点做权重的固定分类器，不是训练出来的普通线性分类器：输出单元数等于训练样本数，不是类别数。另外浮点舍入可能让本来非常接近的两个距离在展开形式下比较结果不同，需要严格并列语义时要直接算距离。

L1 分支用广播得到 $(M, N)$ 的距离矩阵，再 `argmin`。

### 完整参考实现（Python 3）

```python
import numpy as np


def _as_matrices(train, query):
    """转成 float 矩阵并检查形状：train 是 (N, D)，query 是 (M, D)，N >= 1。"""
    train = np.asarray(train, dtype=float)
    query = np.asarray(query, dtype=float)
    if train.ndim != 2 or query.ndim != 2:
        raise ValueError("train and query must be 2-D arrays")
    if train.shape[1] != query.shape[1]:
        raise ValueError(f"feature dims differ: {train.shape[1]} vs {query.shape[1]}")
    if len(train) == 0:
        raise ValueError("train must be non-empty")
    return train, query


def network_scores(train, query):
    """把 1-NN（平方欧氏距离）写成 Wx + b：每个训练样本是一个输出单元。

    W = 2 * train，b = -||train_i||²，分数越大距离越近。返回 (M, N)。
    """
    train, query = _as_matrices(train, query)
    weights = 2 * train  # (N, D)
    bias = -np.sum(train * train, axis=1)  # (N,)
    return query @ weights.T + bias  # (M, N)


def nearest(train, labels, query, metric="l2"):
    """对每个查询返回最近训练样本的 label；并列时取训练下标最小的。"""
    train, query = _as_matrices(train, query)
    labels = np.asarray(labels)
    if len(labels) != len(train):
        raise ValueError(f"expected {len(train)} labels, got {len(labels)}")

    if metric == "l2":
        index = np.argmax(network_scores(train, query), axis=1)
    elif metric == "l1":
        # L1 没有点积展开，只能广播出 (M, N, D) 的差再求和
        distances = np.abs(query[:, None, :] - train[None, :, :]).sum(axis=-1)  # (M, N)
        index = np.argmin(distances, axis=1)
    else:
        raise ValueError(f"unknown metric: {metric!r}")
    return labels[index]
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert nearest(train, ["a", "b"], query).tolist() == ["b", "a"]` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__}{args} should raise ValueError")

# 第二个查询到两个训练点距离相同，取下标小的 a
train = np.array([[0, 0], [2, 0]])
query = np.array([[1.9, 0], [1, 0]])
assert nearest(train, ["a", "b"], query).tolist() == ["b", "a"]

# 和逐个计算距离的暴力解对照
rng = np.random.default_rng(4)
train = rng.normal(size=(7, 3))
query = rng.normal(size=(5, 3))
distance_fns = {
    "l1": lambda u, v: np.abs(u - v).sum(),
    "l2": lambda u, v: ((u - v) ** 2).sum(),
}
for metric, distance in distance_fns.items():
    expected = [
        min(range(len(train)), key=lambda i: distance(point, train[i]))
        for point in query
    ]
    assert np.array_equal(nearest(train, np.arange(len(train)), query, metric), expected)

# 形状、label 数量和 metric 校验
expect_value_error(nearest, [[0, 0]], ["a"], [[0, 0, 0]])
expect_value_error(nearest, [[0, 0]], ["a", "b"], [[0, 0]])
expect_value_error(nearest, [[0, 0]], ["a"], [[0, 0]], "cosine")
expect_value_error(network_scores, np.zeros((0, 2)), [[0, 0]])
```

### 复杂度与追问

L2：矩阵乘法 O(MND) 时间，分数矩阵 O(MN) 空间。L1：同样 O(MND) 时间，但广播的中间结果要 O(MND) 空间。

数据放不进内存或显存时，按查询块和训练块双重分块：每处理一个训练块，就和当前记录的最优分数比较，更新每个查询的最优距离和下标。比较时只在严格更优时才替换，这样跨块之后仍能保持「并列取下标最小」。
