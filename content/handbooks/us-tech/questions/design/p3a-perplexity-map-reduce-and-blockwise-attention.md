---
id: p3a-perplexity-map-reduce-and-blockwise-attention
section: design
order: 615
level: S
title: "Perplexity：Map-Reduce、上下文并行与分块 Attention"
quick: "分块 attention 为每个 query 维护最大分数、指数和与未归一化的加权输出，每来一块就按新最大值重缩放旧量再累加；不能每块各做 softmax 再平均。"
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

## 题目

技术筛选里讨论向量化操作、把 QKV 按序列切段计算，以及数值稳定的 softmax。练习落到一个具体任务：按 key 分块计算 attention，结果要和一次性计算完全一致。

> 来源：一亩三分地 Perplexity 题卡摘要（2026-10-18 读取），是网站对候选人报告的二手整理，没有逐条核对原帖。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

softmax 的分母要对所有 key 求和，所以不能每块各算一次 softmax 再平均：每块的分母不同，平均会丢掉各块真正应有的权重。正确的做法是在线 softmax，每个 query 行维护三个量：

- `row_max`（记作 $m$）：目前见过的最大分数，用来做数值稳定；
- `denom`（记作 $z$）：$\sum_j \exp(s_j - m)$；
- `out`（记作 $o$）：$\sum_j \exp(s_j - m) \, v_j$，还没除以分母。

处理新的一块时，先求新的最大值。如果最大值变大了，旧的 `denom` 和 `out` 都要乘上 $\exp(m_{\text{old}} - m_{\text{new}})$，换到新尺度上，再加上这一块的贡献。全部处理完后 `out / denom` 就是答案。

上下文并行把序列切到多个设备上，问题就从「块之间怎么合并」变成「设备之间怎么合并」，合并规则一样：交换各自的 $(m, z, o)$ 再按上面的方式重缩放。分析网络成本前，先把每个设备上 Q、K、V 的形状和切分维度列清楚，再看哪些张量需要传、传多少字节。

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
