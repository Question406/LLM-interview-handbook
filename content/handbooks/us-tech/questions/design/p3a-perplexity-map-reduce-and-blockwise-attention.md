---
id: p3a-perplexity-map-reduce-and-blockwise-attention
section: design
order: 615
level: S
title: "Perplexity：Map-Reduce、上下文并行与分块 Attention"
quick: "按 key 分块做在线 softmax：每个 query 保存最大分数、指数和与未归一化加权输出，新块到来时先按新最大值重缩放，再累加。这样保留了所有 key 的共同分母，结果才能与完整 attention 一致。"
companies:
  - ai-labs
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - Perplexity
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Perplexity · map-reduce-and-blockwise-attention"
    url: https://www.1point3acres.com/interview/problems/company/perplexity/map-reduce-and-blockwise-attention
    type: secondary
---

## 题目描述

给定单头 attention 的 Q、K、V，计算完整注意力的输出，但每次至多读取一个指定大小的 key 块。Q 和 K 的长度可以不同，不能长期保存完整的 T×S 注意力分数矩阵。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `block_attention(q, k, v, block)`：单头 attention，q 的形状是 `(T, D)`，k 是 `(S, D)`，v 是 `(S, Dv)`，返回 $\text{softmax}(q k^\top / \sqrt{D}) \, v$，形状 `(T, Dv)`。
- 每次只处理 `block` 个 key，不能存完整的 $T \times S$ 分数矩阵。
- `block >= 1`，`S > 0`，`D > 0`，形状要对得上。输入是有限浮点数，各维度不超过 512。
- 这份练习不含 causal mask；下一步可以按全局位置给分数加 mask。

### 示例

```text
block_attention(q=[[1]], k=[[0], [0]], v=[[2], [4]], block=1) -> [[3]]
```

## 解题思路与参考答案

## 题目

技术筛选里讨论向量化操作、把 QKV 按序列切段计算，以及数值稳定的 softmax。练习落到一个具体任务：按 key 分块计算 attention，结果要和一次性计算完全一致。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

我会用在线 softmax，把各块的分数累加到同一个尺度，最后才归一化。因为 softmax 的分母要覆盖全部 key，每块单独 softmax 再平均会丢掉块之间的真实权重。

每个 query 行保留 `row_max`，记作 $m$，表示已见最大分数；`denom`，记作 $z$，保存 $\sum_j \exp(s_j - m)$；以及尚未除分母的 `out`，记作 $o$，保存 $\sum_j \exp(s_j - m) \, v_j$。新块让最大值变大时，旧 `denom` 与 `out` 先乘 $\exp(m_{\text{old}} - m_{\text{new}})$，换到新尺度，再加新块贡献。全部处理后用 `out / denom` 得到答案。

例如下面两个 key 的分数都是 0，最后各占一半权重，输出是两个 value 的平均。上下文并行把块分到多个设备，也沿用这个合并规则：交换各设备的 $(m, z, o)$，重缩放后合并。计算通信量前，先列出每个设备上 Q、K、V 的形状与切分维度，再算哪些张量需要传、各占多少字节。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `block_attention(q, k, v, block)`：单头 attention，q 的形状是 `(T, D)`，k 是 `(S, D)`，v 是 `(S, Dv)`，返回 $\text{softmax}(q k^\top / \sqrt{D}) \, v$，形状 `(T, Dv)`。
- 每次只处理 `block` 个 key，不能存完整的 $T \times S$ 分数矩阵。
- `block >= 1`，`S > 0`，`D > 0`，形状要对得上，否则抛 `ValueError`。输入是有限浮点数，各维度不超过 512。
- 这份练习不含 causal mask；下一步可以按全局位置给分数加 mask。

### 输入输出示例

```text
block_attention(q=[[1]], k=[[0], [0]], v=[[2], [4]], block=1) -> [[3]]
```

两个 key 的分数都是 0，权重各占一半，输出是 2 和 4 的平均。

### 解题思路与正确性

循环不变式是：处理完前若干块之后，`denom` 和 `out` 都是相对当前 `row_max` 的指数和，覆盖了已经处理过的所有 key。新块到来时，重缩放让旧量换到新的最大值上，再加上新块，不变式继续成立。处理完所有块后，`out / denom` 里分子分母共有的因子 $\exp(-m)$ 相互抵消，等于标准 softmax 的结果。

因为每次都减去当前最大值，所有指数的参数都不超过 0，不会上溢。第一块时 `row_max` 是 $-\infty$，`rescale` 等于 $\exp(-\infty) = 0$，正好把初始的零清掉，不需要特判。

### 完整参考实现（Python 3）

```python
import numpy as np


def block_attention(q, k, v, block):
    """单头 attention：softmax(q k^T / sqrt(D)) v，按 key 分块计算，不存完整的 T x S 分数矩阵。

    q: (T, D)，k: (S, D)，v: (S, Dv)，返回 (T, Dv)。
    """
    q, k, v = (np.asarray(x, dtype=float) for x in (q, k, v))
    if block < 1:
        raise ValueError(f"block must be >= 1, got {block}")
    if q.ndim != 2 or k.ndim != 2 or v.ndim != 2:
        raise ValueError("q, k, v must be 2-D")
    if q.shape[1] != k.shape[1] or k.shape[0] != v.shape[0]:
        raise ValueError(f"shape mismatch: q{q.shape} k{k.shape} v{v.shape}")
    if k.shape[0] == 0 or q.shape[1] == 0:
        raise ValueError("need at least one key and a non-empty head dim")

    num_queries, head_dim = q.shape
    # 每个 query 行维护三样东西，都相对同一个最大值 row_max：
    #   row_max: 目前见过的最大分数      (T, 1)
    #   denom:   sum(exp(score - row_max)) (T, 1)
    #   out:     sum(exp(score - row_max) * v)，尚未归一化 (T, Dv)
    row_max = np.full((num_queries, 1), -np.inf)
    denom = np.zeros((num_queries, 1))
    out = np.zeros((num_queries, v.shape[1]))

    for start in range(0, k.shape[0], block):
        k_block = k[start:start + block]                     # (b, D)
        v_block = v[start:start + block]                     # (b, Dv)
        scores = q @ k_block.T / np.sqrt(head_dim)           # (T, b)

        new_max = np.maximum(row_max, scores.max(axis=1, keepdims=True))
        # 最大值变大后，旧的累计量要乘 exp(旧最大值 - 新最大值) 换到新尺度
        rescale = np.exp(row_max - new_max)
        weights = np.exp(scores - new_max)                   # (T, b)

        out = out * rescale + weights @ v_block
        denom = denom * rescale + weights.sum(axis=1, keepdims=True)
        row_max = new_max

    return out / denom
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.allclose(block_attention(q, k, v, block), expected)` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")

# 和一次性计算的稳定 softmax attention 对比；块大小整除、不整除、超过 S 都要对
rng = np.random.default_rng(3)
q = rng.normal(size=(7, 4))
k = rng.normal(size=(11, 4))
v = rng.normal(size=(11, 3))
scores = q @ k.T / 2  # sqrt(D) = 2
weights = np.exp(scores - scores.max(axis=1, keepdims=True))
expected = weights @ v / weights.sum(axis=1, keepdims=True)
for block in (1, 3, 11, 20):
    assert np.allclose(block_attention(q, k, v, block), expected)

# 两个 key 分数相同，输出是 value 的平均
assert np.allclose(block_attention([[1]], [[0], [0]], [[2], [4]], 1), [[3]])

# 分数很大时也不溢出
big = block_attention([[100.0]], [[100.0], [99.0]], [[1.0], [0.0]], 1)
assert np.all(np.isfinite(big))

# 非法输入
expect_value_error(block_attention, q, k, v, 0)
expect_value_error(block_attention, q, k[:, :3], v, 2)
expect_value_error(block_attention, q, k[:0], v[:0], 2)
```

### 复杂度与追问

设 query 数为 T、key 数为 S、head 维度为 D、value 维度为 Dv。算术量是 $O(TSD + TSD_v)$，和一次性计算相同；额外空间是 $O(T \cdot \text{block} + T D_v)$，不含输入。

如果追问上下文并行怎么合并：每个设备算出自己那段 key 的 $(m, z, o)$，合并时取全局最大值，按各自的 $\exp(m_i - m)$ 重缩放再相加。不能只对各设备已经归一化的输出做 all-reduce 求平均。

如果追问 causal mask：在算完 `scores` 后，把全局 key 位置大于 query 位置的分数设成 $-\infty$。整块都被 mask 的行要小心，`new_max` 可能仍是 $-\infty$，此时 `exp(-inf - (-inf))` 会得到 NaN，需要跳过这一块或者特判。
