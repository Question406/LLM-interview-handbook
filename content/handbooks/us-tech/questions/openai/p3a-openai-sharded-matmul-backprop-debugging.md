---
id: p3a-openai-sharded-matmul-backprop-debugging
section: openai
order: 626
level: S
title: OpenAI：分片矩阵乘法与多设备反向调试
quick: >-
  先标出每个 rank 的切分轴和全局 shape：切分维保留在输出里就拼接，切在被求和的 K 维上就归约部分和。反向用 dA = G Bᵀ、dB = Aᵀ
  G，再据同样的分片推通信。用单卡结果、有限差分和空分片测试，分别验证 forward、gradients 与 edge cases。
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
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: 1Point3Acres · OpenAI · sharded-matmul-backprop-debugging
    url: >-
      https://www.1point3acres.com/interview/problems/company/openai/sharded-matmul-backprop-debugging
    type: secondary
---

## 题目描述

在小矩阵上模拟数据并行和参数分片的矩阵乘法，并实现矩阵乘法 backpropagation；分片数可以超过某一维长度。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `dp_matmul(a, b, world_size)`：数据并行。`a` 形状 `[M, K]` 按行切成 `world_size` 段，每个 rank 持有完整的 `b`（`[K, N]`），算出自己那几行结果，最后拼成 `[M, N]`。
- `fsdp_matmul(a, b, world_size)`：`a` 照样按行切，`b` 按列切，每个 rank 起初只有一个列分片。用线程模拟 rank，每个 rank 一个无界 `Queue` 作收件箱，列分片沿环传递，消息里带着分片的原始 owner。
- `backward(a, b, grad_out)`：对 $Y = AB$，给定 $G = \partial L / \partial Y$，返回 `(dA, dB)`。
- `world_size` 是正整数；允许不整除和空分片（例如 `world_size` 大于 N）。两个前向函数的完整输出都必须等于 `a @ b`。输入形状合法，`grad_out` 为 `[M,N]`，返回梯度分别为 `[M,K]`、`[K,N]`。小矩阵，各维不超过 100。

### 输入输出示例

```text
a = [[1, 2], [3, 4]], b = [[5], [6]], world_size = 2
dp_matmul(a, b, 2)   -> [[17], [39]]
fsdp_matmul(a, b, 2) -> [[17], [39]]
```

## 解题思路与参考答案

我会先画全局矩阵和每张卡持有的范围，再判断输出该拼接还是求和。比如 A 按行切，各卡得到不同输出行，可以拼接；如果沿 K 切，各卡得到相同输出形状的部分和，就要 all-reduce。反向同样从公式和切分推通信，再与单设备结果对照。

推导矩阵乘法 $Y = AB$ 在多设备分片后的前向和反向计算，并找出、修复给定代码里的缺陷。核心是弄清每个设备持有张量的哪一块，以及前向和反向分别需要什么通信。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理。题卡没有给出原始缺陷代码；下面的接口、约束和测试是手册补的练习约定。

## 思路

先写清每张卡的切分轴和全局张量形状，再判断结果该拼接还是求和。判断规则很简单：如果被切开的维度出现在输出里，各分片结果就是输出的不同部分，拼接即可；如果被切开的是被求和掉的维度（矩阵乘里的 K），每张卡只得到部分和，必须 all-reduce。

反向通信和前向切分是对应的：

- $A$ 按行切（DP）时，$dA = G B^\top$ 的行也按同样方式切，每张卡本地算；$dB = A^\top G = \sum_r A_r^\top G_r$ 是对各卡求和，需要 all-reduce。
- $B$ 按列切时，$dB$ 的列是本地的；$dA = \sum_c G_{:,c} B_c^\top$ 要对各列分片求和。

常见的缺陷正是把这两类通信混用：该求和的地方做了 all-gather 拼接，或者转置方向写反导致形状碰巧对上但数值错。调试时用三种手段：和单设备的 `a @ b` 对比、用有限差分检查梯度、专门测不整除的尺寸（例如 3 行切给 4 张卡）。

相关题：[[p3a-xai-distributed-matmul-dp-fsdp]]（同一份参考实现，那张卡侧重 FSDP 的环形 all-gather 和避免死锁）。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `dp_matmul(a, b, world_size)`：数据并行。`a` 形状 `[M, K]` 按行切成 `world_size` 段，每个 rank 持有完整的 `b`（`[K, N]`），算出自己那几行结果，最后拼成 `[M, N]`。
- `fsdp_matmul(a, b, world_size)`：`a` 照样按行切，`b` 按列切，每个 rank 起初只有一个列分片。用线程模拟 rank，每个 rank 一个无界 `Queue` 作收件箱，列分片沿环传递，消息里带着分片的原始 owner。
- `backward(a, b, grad_out)`：对 $Y = AB$，给定 $G = \partial L / \partial Y$，返回 `(dA, dB)`。
- `world_size` 是正整数；允许不整除和空分片（例如 `world_size` 大于 N）。两个前向函数的完整输出都必须等于 `a @ b`。形状不合法时抛 `ValueError`。小矩阵，各维不超过 100。

### 输入输出示例

```text
a = [[1, 2], [3, 4]], b = [[5], [6]], world_size = 2
dp_matmul(a, b, 2)   -> [[17], [39]]
fsdp_matmul(a, b, 2) -> [[17], [39]]
```

### 解题思路与正确性

DP 版本最简单：行分片各自乘 `b`，结果按 rank 顺序拼接。注意必须按 rank 顺序拼，不能按线程完成的先后拼，`pool.map` 本身就按输入顺序返回。

FSDP 版本是一个环形 all-gather。第 s 轮时，rank r 手上是原本属于 rank $(r - s) \bmod p$ 的列分片。它用自己的行分片乘这块列分片，把结果写进输出里这块分片对应的列范围，然后把分片发给 rank $r + 1$，再从自己的收件箱取下一块。走完 p 轮，每个 rank 都乘过全部列分片，自己那几行的输出就填满了。因为分片会在 rank 之间移动，消息里必须带着 owner，否则不知道结果该写到哪几列。

不会死锁的原因：队列是无界的，`put` 不会阻塞；所有 rank 都按「先发后收」的同一顺序执行，每一轮每个收件箱都恰好会收到一条消息。如果换成有界队列或「先收后发」，所有 rank 可能同时卡在等待上。

反向公式由 $dL = \operatorname{tr}(G^\top dY)$、$dY = dA\,B + A\,dB$ 推出：$dA = G B^\top$，$dB = A^\top G$。

这只是用线程和队列做的模拟，用来检查分片和通信顺序，不是 PyTorch FSDP 的完整训练实现。

### 完整参考实现（Python 3）

```python
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

import numpy as np


def _check_inputs(a, b, world_size):
    a = np.asarray(a, dtype=float)  # [M, K]
    b = np.asarray(b, dtype=float)  # [K, N]
    if type(world_size) is not int or world_size < 1:
        raise ValueError(f"world_size must be a positive int, got {world_size!r}")
    if a.ndim != 2 or b.ndim != 2:
        raise ValueError("a and b must be 2-D")
    if a.shape[1] != b.shape[0]:
        raise ValueError(f"inner dims differ: {a.shape} @ {b.shape}")
    return a, b


def dp_matmul(a, b, world_size):
    """数据并行：每个 rank 拿 a 的一段行和完整的 b，结果按 rank 顺序拼回去。"""
    a, b = _check_inputs(a, b, world_size)
    row_shards = np.array_split(a, world_size, axis=0)  # 允许不整除和空分片
    with ThreadPoolExecutor(world_size) as pool:
        # pool.map 按输入顺序返回，所以拼接顺序就是 rank 顺序
        outputs = list(pool.map(lambda rows: rows @ b, row_shards))
    return np.concatenate(outputs, axis=0)  # [M, N]


def fsdp_matmul(a, b, world_size):
    """FSDP 模拟：a 按行切、b 按列切，b 的列分片沿环传递 world_size - 1 轮。"""
    a, b = _check_inputs(a, b, world_size)
    row_shards = np.array_split(a, world_size, axis=0)
    col_shards = np.array_split(b, world_size, axis=1)
    # 第 r 个列分片对应输出的 [col_offsets[r], col_offsets[r + 1]) 列
    col_offsets = np.cumsum([0] + [shard.shape[1] for shard in col_shards])
    inboxes = [Queue() for _ in range(world_size)]  # 无界队列，put 不会阻塞

    def worker(rank):
        rows = row_shards[rank]
        out = np.zeros((rows.shape[0], b.shape[1]))
        owner, shard = rank, col_shards[rank]
        for step in range(world_size):
            # 消息里带着 owner，才知道这块结果该写到哪几列
            out[:, col_offsets[owner] : col_offsets[owner + 1]] = rows @ shard
            if step + 1 < world_size:
                # 所有 rank 都先发后收，环上每一轮都有消息可取，不会互相等死
                inboxes[(rank + 1) % world_size].put((owner, shard))
                owner, shard = inboxes[rank].get(timeout=10)
        return out

    with ThreadPoolExecutor(world_size) as pool:
        parts = list(pool.map(worker, range(world_size)))
    return np.concatenate(parts, axis=0)  # [M, N]


def backward(a, b, grad_out):
    """Y = A @ B 的反向：给定 dL/dY，返回 (dL/dA, dL/dB) = (G B^T, A^T G)。"""
    a = np.asarray(a, dtype=float)  # [M, K]
    b = np.asarray(b, dtype=float)  # [K, N]
    grad_out = np.asarray(grad_out, dtype=float)  # [M, N]
    if a.ndim != 2 or b.ndim != 2 or a.shape[1] != b.shape[0]:
        raise ValueError(f"bad matmul shapes: {a.shape} @ {b.shape}")
    if grad_out.shape != (a.shape[0], b.shape[1]):
        raise ValueError(
            f"grad_out shape {grad_out.shape} != {(a.shape[0], b.shape[1])}"
        )
    return grad_out @ b.T, a.T @ grad_out
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.allclose(dp_matmul(a, b, 2), [[17], [39]])` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


def numeric_grad(loss, x, index, h=1e-5):
    plus = x.copy()
    minus = x.copy()
    plus[index] += h
    minus[index] -= h
    return (loss(plus) - loss(minus)) / (2 * h)


# 手算的小例子
a = [[1, 2], [3, 4]]
b = [[5], [6]]
assert np.allclose(dp_matmul(a, b, 2), [[17], [39]])
assert np.allclose(fsdp_matmul(a, b, 2), [[17], [39]])

# 随机形状：整除、不整除、world_size 大于 N（有空列分片）、单卡
rng = np.random.default_rng(6)
for m, k, n, world_size in ((8, 6, 4, 2), (3, 2, 5, 4), (2, 3, 1, 1), (5, 3, 2, 3)):
    a = rng.normal(size=(m, k))
    b = rng.normal(size=(k, n))
    grad_out = rng.normal(size=(m, n))
    assert np.allclose(dp_matmul(a, b, world_size), a @ b)
    assert np.allclose(fsdp_matmul(a, b, world_size), a @ b)

    # 用有限差分核对解析梯度，损失取 sum(Y * G)
    grad_a, grad_b = backward(a, b, grad_out)

    def loss_of_a(x):
        return ((x @ b) * grad_out).sum()

    def loss_of_b(x):
        return ((a @ x) * grad_out).sum()

    for index in ((0, 0), (m - 1, k - 1)):
        assert np.isclose(numeric_grad(loss_of_a, a, index), grad_a[index])
    for index in ((0, 0), (k - 1, n - 1)):
        assert np.isclose(numeric_grad(loss_of_b, b, index), grad_b[index])

# 非法输入
expect_value_error(dp_matmul, [[1, 2]], [[1, 2]], 1)
expect_value_error(fsdp_matmul, [[1]], [[1]], 0)
expect_value_error(backward, [[1]], [[1]], [[1, 2]])
```

### 复杂度与追问

设 $A$ 为 `[M, K]`，$B$ 为 `[K, N]`，rank 数为 p。前向和反向的计算量都是 O(MKN)。FSDP 模拟中每个 rank 收到 p - 1 个列分片，全环通信量约 $(p - 1)KN$ 个元素。模拟没有覆盖网络延迟和每张卡的真实显存。

- 如果 $A$ 按列、$B$ 按行切（都切在 K 上），每张卡算出的是完整形状的部分和 $A_{:,k} B_{k,:}$，前向就需要 all-reduce，这正是张量并行里 row-parallel 线性层的情况。
- 有限差分测试为什么用损失 $L = \sum Y \odot G$？因为它对 $Y$ 的梯度正好是 $G$，可以直接核对 `backward` 的输出。
