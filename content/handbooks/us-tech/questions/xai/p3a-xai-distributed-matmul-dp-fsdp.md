---
id: p3a-xai-distributed-matmul-dp-fsdp
section: xai
order: 601
level: S
title: xAI：分布式 matmul：DP 与 FSDP 模拟
quick: >-
  我会先画分片坐标：A 按行切，DP 每卡乘完整 B 后按 rank 拼行；FSDP 模拟则把 B 的列分片沿环传递，按 owner 写入输出列。所有
  rank 在无界队列上先发后收，既避免互等，也要处理不整除与空分片。
companies:
  - xai
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - xAI
  - 题面补全 2026-10-27
realInterview: true
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: 1Point3Acres · xAI · distributed-matmul-dp-fsdp
    url: >-
      https://www.1point3acres.com/interview/problems/company/xai/distributed-matmul-dp-fsdp
    type: secondary
  - title: xAI ML/Infra 原帖与作者补充
    url: 'https://www.1point3acres.com/interview/thread/1171574'
    type: candidate-first-hand
---

## 题目描述

用本地工作者模拟数据并行和分片权重的矩阵乘法，并实现其反向梯度。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`dp_matmul(a,b,world_size)` 与 `fsdp_matmul(a,b,world_size)` 都返回 a@b。a 为 `[M,K]`、b 为 `[K,N]`，`world_size` 为正整数，各维不超过 100，维度不能整除工作者数时也应支持，允许空分片。

`dp_matmul` 中每个工作者只负责部分 a 行，持有完整 b。`fsdp_matmul` 中 a 按行分片、b 按列分片，每个工作者初始只有自己的 b 列；以线程和 Queue 模拟带分片所有者编号的环形传输，最终还原正确输出顺序，不允许预先让所有工作者持有完整 b。

`backward(a,b,grad_out)` 接收 `[M,N]` 的输出梯度，返回 `(dA,dB)`，形状分别与 a、b 相同。

### 示例

```text
a=[[1,2],[3,4]], b=[[5],[6]], world_size=2。
dp_matmul 与 fsdp_matmul 均返回 [[17],[39]]。
grad_out=[[1],[1]]：backward 返回
 dA=[[5,6],[5,6]], dB=[[4],[6]]。
```

## 解题思路与参考答案

我会先写清每个 rank 拿到哪些行、哪些列，再决定结果放回哪里。DP 可以直接按 rank 拼行；FSDP 模拟要让列分片沿环传递，消息始终带着原始 owner，否则分片换了卡，结果就可能写错输出列。

## 题目

给一个基于 `Queue` 的通信器，用它模拟多卡矩阵乘法 $Y = AB$。分两个版本：数据并行（DP）下每张卡算一段行；FSDP 下权重 $B$ 也被切开，每张卡只持有一个分片，需要通过循环 all-gather 轮流拿到其他分片。

> 来源：一亩三分地 xAI 题卡摘要，本次（2026-10-18 整理）另外读取了原帖正文和作者补充，核实了 DP/FSDP starter 的分片方向；题卡本身是网站的二手整理。第二轮的 patchify 题见独立练习卡。下面的接口、约束和测试是手册补的练习约定。

## 思路

这份练习固定 $A$ 按行切：DP 下每张卡有完整的 $B$，FSDP 下 $B$ 按列切。输入分片确定后，每个局部矩阵乘法对应的输出坐标就能直接推出来。

- DP：每张卡算 `rows @ B`，得到输出的若干行，按 rank 顺序 gather 起来即可。
- FSDP：每张卡每一轮用自己的行分片乘手上的列分片，把结果写到这个列分片对应的输出列，然后把分片传给下一张卡。传 p - 1 轮后，每张卡都见过全部列分片。

通信顺序上，所有 rank 都先发后收。若一起先收，大家都等不到消息；队列有容量上限并被写满时，发送也可能互相等待，所以练习使用无界队列。尺寸不整除时还要接受 `np.array_split` 产生的长短不同、甚至为空的分片。

相关题：[[p3a-openai-sharded-matmul-backprop-debugging]]（同一份参考实现，那张卡侧重 backpropagation 和分片后的梯度通信）。

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

设 $A$ 为 `[M, K]`，$B$ 为 `[K, N]`，rank 数为 p。总计算量 O(MKN)，输出 O(MN)。FSDP 模拟中每个 rank 收到 p - 1 个列分片，全环通信量约 $(p - 1)KN$ 个元素。模拟进程里保留了全部输入，所以不能用它衡量每张卡的真实显存，网络延迟和线程开销也没有模拟。

- 为什么不让每张卡直接从 owner 拉分片？那样每张卡要和 p - 1 个对端通信，owner 的出口带宽会成为瓶颈；环形传递让每张卡每轮只收发一块，带宽均匀分摊。
- 计算和通信能否重叠？可以在乘当前分片的同时先把它发出去（或预取下一块），这正是真实 FSDP 里预取下一层参数的思路。
