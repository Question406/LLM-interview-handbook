---
id: apple-kmeans
section: apple
order: 8
level: A
title: Apple coding：k-means / nearest neighbors，作为电面算法题怎么答到 ML 岗标准？
quick: >-
  我会用向 quantization 距离计算实现 Lloyd 迭代：每个点分到最近中心，再把中心更新为均值，empty cluster
  按约定处理，结束后重新分配标签。时间是 $O(n k d I)$，距离可写成 $[n,k]$；广播实现还要检查中间 tensor 内存，再讨论
  k-means++ 和 16 个中心 $\approx$ 4-bit 的码本。
tags:
  - 完整编程练习
  - Apple
  - K-means
  - Coding
  - Nearest Neighbor
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: Introducing Apple’s On-Device and Server Foundation Models
    url: >-
      https://machinelearning.apple.com/research/introducing-apple-foundation-models
    type: primary
  - title: Apple Intelligence Foundation Language Models
    url: >-
      https://machinelearning.apple.com/research/apple-intelligence-foundation-language-models
    type: primary
  - title: Apple Machine Learning Engineer Interview Guide
    url: >-
      https://www.tryexponent.com/guides/apple-machine-learning-engineer-interview
    type: secondary
---

## 题目描述

给定 N 个 D 维数据点、K 个初始中心和迭代停止参数，实现本题约定的 K-means。返回最终中心、每个样本的 cluster ID 与 within-cluster SSE。不能调用现成的聚类训练接口。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `kmeans(x, k, initial, max_iter=100, tol=1e-8) -> (centers, labels, sse)`：Lloyd 迭代，不允许调用聚类库。
- 输入：`x` 是有限的二维浮点数组 `[N, D]`，`initial` 是初始中心 `[K, D]`，要求 `1 <= K <= N`、`D >= 1`、`max_iter` 为正整数、`tol` 非负且有限。不修改调用方传入的 `initial`。
- 赋值：每个点按平方欧氏距离分到最近的中心，距离相同时选编号较小的 cluster。
- 更新：中心换成 cluster 内各点的均值；empty cluster 保持原来的中心不动。
- 停止：跑满 `max_iter` 轮，或者本轮所有中心的最大位移（L2 范数）不超过 `tol`。
- 返回：最终中心、按最终中心重新分配的 `labels`，以及误差平方和 SSE（Python `float`）。

### 示例

```text
x = [[0], [2], [10], [12]],  initial = [[0], [10]],  k = 2
-> centers = [[1], [11]],  labels = [0, 0, 1, 1],  sse = 4.0
```

## 解题思路与参考答案

我会用 Lloyd 迭代做 k-means：先把点分给最近中心，再把非 empty cluster 的中心换成均值，直到位移足够小或达到轮数上限。比如示例里两团点最后聚到 1 和 11，SSE 是 4；结束后还要按最终中心重算标签，保证返回值一致。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + NumPy。

### 题面、接口与约束

- `kmeans(x, k, initial, max_iter=100, tol=1e-8) -> (centers, labels, sse)`：Lloyd 迭代，不允许调用聚类库。
- 输入：`x` 是有限的二维浮点数组 `[N, D]`，`initial` 是初始中心 `[K, D]`，要求 `1 <= K <= N`、`D >= 1`、`max_iter` 为正整数、`tol` 非负且有限；不满足时抛 `ValueError`。不修改调用方传入的 `initial`。
- 赋值：每个点按平方欧氏距离分到最近的中心，距离相同时选编号较小的 cluster。
- 更新：中心换成 cluster 内各点的均值；empty cluster 保持原来的中心不动。
- 停止：跑满 `max_iter` 轮，或者本轮所有中心的最大位移（L2 范数）不超过 `tol`。
- 返回：最终中心、按最终中心重新分配的 `labels`，以及误差平方和 SSE（Python `float`）。

### 输入输出示例

```text
x = [[0], [2], [10], [12]],  initial = [[0], [10]],  k = 2
-> centers = [[1], [11]],  labels = [0, 0, 1, 1],  sse = 4.0
```

### 解题思路与正确性

k-means 的目标是 SSE。每轮分两步，每一步都不会让 SSE 变大：中心固定时，把每个点分给最近的中心，SSE 只会变小或不变；分配固定时，一组点到某个中心的平方距离之和在中心取均值时最小，所以把非 empty cluster 的中心换成均值也不会增加 SSE。empty cluster 没有点，保持原中心对 SSE 没有影响。因此 SSE 单调不增，但只保证收敛到局部最优，不保证全局最优。

循环结束后要按最终中心再分配一次 labels。如果是因为跑满 `max_iter` 而停下，循环里最后一次算的 labels 对应的是更新前的中心，直接返回就会和 `centers` 对不上。

`argmin` 在多个最小值时返回第一个，正好实现「距离相同选较小 cluster ID」。

### 完整参考实现（Python 3）

```python
import numpy as np


def kmeans(x, k, initial, max_iter=100, tol=1e-8):
    """Lloyd k-means：返回 (centers [K, D], labels [N], sse)。empty cluster 保持原中心。"""
    x = np.asarray(x, dtype=float)
    centers = np.array(initial, dtype=float, copy=True)  # 复制，不修改调用方的 initial
    if x.ndim != 2 or x.shape[1] == 0:
        raise ValueError(f"x must be a non-empty [N, D] array, got shape {x.shape}")
    if not 1 <= k <= len(x):
        raise ValueError(f"k must be in [1, N={len(x)}], got {k}")
    if centers.shape != (k, x.shape[1]):
        raise ValueError(
            f"initial must have shape {(k, x.shape[1])}, got {centers.shape}"
        )
    if max_iter < 1:
        raise ValueError(f"max_iter must be positive, got {max_iter}")
    if not (np.isfinite(tol) and tol >= 0):
        raise ValueError(f"tol must be finite and non-negative, got {tol}")
    if not (np.isfinite(x).all() and np.isfinite(centers).all()):
        raise ValueError("x and initial must be finite")

    def assign(current_centers):
        # [N, 1, D] - [1, K, D] -> [N, K, D] -> 平方距离 [N, K]
        distances = ((x[:, None, :] - current_centers[None, :, :]) ** 2).sum(axis=-1)
        return distances.argmin(axis=1)  # 平局时取较小 cluster ID

    for _ in range(max_iter):
        labels = assign(centers)
        updated = centers.copy()
        for cluster in range(k):
            members = x[labels == cluster]
            if len(members):  # empty cluster 保持原中心
                updated[cluster] = members.mean(axis=0)
        shift = np.linalg.norm(updated - centers, axis=1).max()
        centers = updated
        if shift <= tol:
            break

    labels = assign(centers)  # 按最终中心重新分配
    sse = ((x - centers[labels]) ** 2).sum()
    return centers, labels, float(sse)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.allclose(centers, [[1.0], [11.0]])` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

数值结果用 `allclose` 一类带容差的 assertion 检查，并同时确认形状；随机输入固定 seed。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(action):
    try:
        action()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def brute_force_labels(x, centers):
    return ((x[:, None, :] - centers[None, :, :]) ** 2).sum(-1).argmin(1)


x = np.array([[0.0], [2.0], [10.0], [12.0]])

# 题面示例：两个 clusters 收敛到 1 和 11，SSE = 4
centers, labels, sse = kmeans(x, 2, [[0.0], [10.0]])
assert np.allclose(centers, [[1.0], [11.0]])
assert labels.tolist() == [0, 0, 1, 1]
assert sse == 4
assert isinstance(sse, float)

# empty cluster 保持原中心，且不修改调用方的 initial
initial = np.array([[0.0], [100.0]])
centers, labels, sse = kmeans([[0.0], [0.0]], 2, initial)
assert np.array_equal(centers, initial)
assert labels.tolist() == [0, 0]
assert sse == 0
assert np.array_equal(initial, [[0.0], [100.0]])

# 跑满 max_iter 停下时，labels 也对应最终中心
centers, labels, _ = kmeans(x, 2, [[0.0], [1.0]], max_iter=1)
assert np.array_equal(labels, brute_force_labels(x, centers))

# SSE 随迭代轮数单调不增
_, _, previous = kmeans(x, 2, [[0.0], [1.0]], max_iter=1)
for rounds in range(2, 6):
    _, _, current = kmeans(x, 2, [[0.0], [1.0]], max_iter=rounds)
    assert current <= previous + 1e-12
    previous = current

# 距离相同时选编号较小的 cluster
_, labels, _ = kmeans([[5.0]], 1, [[5.0]])
assert labels.tolist() == [0]
assert brute_force_labels(np.array([[1.0]]), np.array([[0.0], [2.0]])).tolist() == [0]

# 二维数据：两团点各自聚成一个 cluster
points = np.array([[0.0, 0.0], [0.0, 1.0], [9.0, 9.0], [9.0, 10.0]])
centers, labels, sse = kmeans(points, 2, points[[0, 2]])
assert np.allclose(centers, [[0.0, 0.5], [9.0, 9.5]])
assert np.isclose(sse, 1.0)

# 非法输入
expect_value_error(lambda: kmeans(x, 0, np.zeros((0, 1))))
expect_value_error(lambda: kmeans(x, 5, np.zeros((5, 1))))
expect_value_error(lambda: kmeans(x, 2, [[0.0, 1.0], [1.0, 2.0]]))
expect_value_error(lambda: kmeans(x, 2, [[0.0], [1.0]], max_iter=0))
expect_value_error(lambda: kmeans(x, 2, [[0.0], [1.0]], tol=-1.0))
expect_value_error(lambda: kmeans([[np.nan], [1.0]], 1, [[0.0]]))
```

### 复杂度与追问

设样本数 N、中心数 K、维度 D、迭代轮数 I。时间 O(I·N·K·D)。这份实现用广播算距离，中间 tensor 是 `[N, K, D]`，峰值内存 O(N·K·D)，而不只是距离 matrix 的 O(N·K)。

- 追问「N 或 D 很大时内存爆了」：用 $\lVert x-\mu\rVert^2 = \lVert x\rVert^2 - 2x^\top\mu + \lVert\mu\rVert^2$ 展开，交叉项是一次 matrix 乘法，峰值内存降到 O(N·K)；或者按 N 分块计算。
- 追问「初始化为什么作为参数传入」：显式给定初始中心，测试才可复现。k-means++ 可以另写一个函数生成 `initial`，见下文。

## 题怎么来的

公开的 Siri MLE 电面讨论里，k-means 和 attention、sampling 并列，都算 ML coding 基本功，见 `apple-mha-code`。Exponent 也提到，Apple 有的组考应用型 ML 题，有的组考常规编码。电面可以先给出 15–20 行的向 quantization 版本，再解释初始化、empty cluster 和规模变大后的内存开销。

## 先写对迭代，再谈技巧

输入 $X\in\mathbb{R}^{n\times d}$，number of clusters 为 $k$。目标是同时选分配 $c$ 和中心 $\mu$，使

$$
\min_{c,\mu}\sum_{i=1}^{n}\lVert x_i-\mu_{c_i}\rVert_2^2.
$$

这个问题是 NP-hard 的，Lloyd 迭代只保证目标单调不增，最后停在局部最优。面试时先把这一点说出来，面试官问「为什么换个 random seed 分数就变」时就有了答案。

下面是另一种常见写法：随机选初始中心，empty cluster 随机重启。它和上面练习的约定（empty cluster 保持原中心）不同，两种都可以，面试时说清楚选的是哪种。

```python
import numpy as np


def kmeans(x, k, n_iter=20, seed=0):
    n, d = x.shape
    rng = np.random.default_rng(seed)
    mu = x[rng.choice(n, size=k, replace=False)]
    for _ in range(n_iter):
        dist = ((x[:, None, :] - mu[None, :, :]) ** 2).sum(-1)  # [n, k]
        labels = dist.argmin(axis=1)
        new_mu = mu.copy()
        for j in range(k):
            members = labels == j
            if members.any():
                new_mu[j] = x[members].mean(axis=0)
            else:
                new_mu[j] = x[rng.integers(n)]  # empty cluster：随机挑一个点重启
        if np.allclose(new_mu, mu):
            break
        mu = new_mu
    # 跑满 n_iter 时 labels 还对应上一轮的 mu，按最终中心重新分配
    labels = ((x[:, None, :] - mu[None, :, :]) ** 2).sum(-1).argmin(axis=1)
    return mu, labels
```

复杂度是 $O(n k d I)$。距离 matrix 本身是 $O(n k)$，但这种广播写法的中间 tensor 是 $[n, k, d]$。$n$ 到百万、$d$ 到几百时内存会爆，要改成分块或 mini-batch：每次只用 $b$ 条样本做一次赋值，再增量更新均值。电面里 $n$ 很小，写全量版本即可，但要主动说出内存上限在哪。

empty cluster 必须处理，否则对空集合取 `mean` 会得到 `NaN`，下一轮所有距离都变成 `NaN`。

k-means++ 的初始化是：第一个中心从所有点里均匀抽；之后抽第 $j$ 个中心时，每个点被抽中的概率正比于它到已选中心的最近平方距离 $\min_{t<j}\lVert x-\mu_t\rVert^2$。这样期望的初始代价更低。不要把 ++ 写成「每次直接选最远的点」，那是 greedy 的另一种变体，最坏情况下会被离群点带偏。

距离的选择：欧氏距离和均值更新是配套的。如果数据是单位化的 embedding，用 $2-2\cos$ 做距离等价于欧氏距离。不要一边用 cosine 做赋值、一边用算术均值更新中心，均值会离开单位球面；这种情况应该用 spherical k-means（求均值后再 normalization），或者换算法。

## nearest neighbors：同一套距离，不同的题

「最 nearest neighbors」有时指 k-means 的赋值步骤，即每个点找最近的中心，相当于在 $k$ 个原型上做 1-NN；有时指真正的 $k$NN 分类或检索。

**原型。**
inference 时只存 $k$ 个中心，占 $O(k d)$，这就是向量 quantization。Apple on-device 的 palettization 就是把投影权重按块做 k-means，$k=16$ 个中心对应一本 4-bit 码本，见 `apple-ondevice-quant`。这也说明聚类代码如何用于权重压缩。
**检索。**
例如在用户私有的消息或照片 embedding 里找 top-k 邻居。精确检索是 $O(n d)$；on-device 的 $n$ 只是用户自己的数据量，暴力扫描往往就够了。需要更快时再上 IVF（先用 k-means 做粗 quantization，查询时只扫最近的几个倒排表）或图索引。不要一上来就画分布式集群，这和「数据不出设备」的要求冲突，见 `apple-personalize`。
**kNN 和 k-means 的区别。**
分类问题如果 $n$ 小、decision boundaries 不规则，kNN 更直接；要压缩模型或者做码本，才用 k-means。先说清楚任务是什么，别把两个 $k$ 混在一起。

评测：上面的目标函数（inertia）只衡量 cluster 有多紧，不反映下游效果。Palettization 要看恢复 adapter 之后的任务分数；检索要看 recall@$k$ 和延迟。聚类没有唯一正确的标签，不要硬报 accuracy。

## ML 岗标准的口头清单

写完代码后，我会按这个顺序补充，面试官通常会在其中某一条打断追问：

1. 复杂度，以及什么时候改用 mini-batch。
2. 初始化、empty cluster 和局部最优，以及多跑几个 seed。
3. 和 quantization 码本或 on-device 检索的关系。
4. $k$ 怎么选：看下游任务指标随 $k$ 的变化曲线，而不是只看肘部法则。高维 embedding 上肘部往往不明显。

时间不够时，可以优先解释复杂度和 quantization 码本的联系。三层循环适合说明计算过程，最终实现仍用向 quantization。sampling 题也需要解释 edge cases 和用途，见 `apple-topk-sample`。

## 追问

**和 GMM 什么关系？**
k-means 是 GMM 在各向同性协方差、硬赋值下的极限情况；需要协方差或软赋值时再用 EM 训练 GMM。on-device 码本很少用完整的 GMM，成本太高。
**Mini-batch 会不会不收敛？**
会有噪声。用衰减的 learning rate，或者最后几轮换成全量数据精修。生产里做 palettization，往往离线跑多次，取恢复误差最低的那本码本。
**高维下距离失效怎么办？**
维数灾难会让所有点两两之间的距离趋于接近。先降维，或者用余弦距离加 normalization；这也是检索通常用训练过的 embedding、而不是原始像素的原因。
**为什么电面爱出这题？**
题短，结果是可验证的数值，还能自然地拐到 quantization 话题。准备好这 20 行，比再刷一道 hard 图论题更划算。
