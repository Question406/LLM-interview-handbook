---
id: p3a-meta-attention-implementation-and-follow-ups
section: meta
order: 813
level: A
title: "Meta Superintelligence/MLE：Attention 与 Flash/Linear 追问"
quick: "标准 attention 先算缩放后的 QK 转置，屏蔽不可见位置，再沿 key 轴 softmax 并乘 V。权重矩阵带来二次空间；FlashAttention 用分块和在线 softmax 保持精确结果，linear attention 则改变计算形式，输出也不同。"
companies:
  - meta
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - meta
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Meta Superintelligence/MLE：Attention 与 Flash/Linear 追问"
    url: https://www.1point3acres.com/interview/problems/company/meta/attention-implementation-and-follow-ups
    type: secondary
---

## 题目描述

实现一个 NumPy 版本的多头缩放点积注意力，正确处理广播 mask 和因果可见性。

以下接口和边界行为是本手册重构练习的约定。假定输入满足所述合法范围。

`attention(q, k, v, mask=None, causal=False)` 接收 float64 数组：q 为 `[B,H,T,D]`，k 为 `[B,H,S,D]`，v 为 `[B,H,S,Dv]`；返回 `[B,H,T,Dv]`。每个 query 对 key 的分数为内积除以 `sqrt(D)`，在可见 key 上按 `exp(score)/sum(exp(score))` 归一化为 softmax 概率，再对 v 加权求和。

mask 是可广播到 `[B,H,T,S]` 的布尔数组，True 表示可见。causal=True 时 T=S，位置 i 只能看到 j<=i；该约束与 mask 同时生效。某一 query 没有可见 key 时，其输出为全零且不含 NaN。B、H 不超过 4，T、S 不超过 128，各特征维均为正。

### 示例

```text
q = k = 全 1 数组，形状 [1,1,2,1]
v = [[[[2],[4]]]], causal = True
返回 [[[[2],[3]]]]。
相同输入但 mask 全为 False 时，返回同形全零数组。
```

## 解题思路与参考答案

## 题目

先手写一个标准的缩放点积注意力，然后分析时间和空间复杂度，最后口头回答两个追问：FlashAttention 是怎么省显存的，linear attention 和它有什么本质区别。

> 来源：一亩三分地 Meta Superintelligence/MLE 题卡摘要（2026-10-18 用 Chrome 读取），没有核实完整题干或原帖；网站收录不等于公司官方确认，也不能把这条归到 Meta 其他岗位。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

我会按 QK 转置、除以 $\sqrt{D}$、套 mask、沿 key 轴 softmax、乘 V 的顺序实现。比如某一行没有任何可见 key，就要明确返回全 0，避免全是负无穷时产生 NaN。复杂度的瓶颈在中间 `[T, S]` 权重矩阵，序列拉长后它占用二次空间。

FlashAttention 用分块和在线 softmax，减少整张权重矩阵的 HBM 读写，结果仍是精确的标准注意力。Linear attention 则用核函数近似替代 softmax，获得对序列长度线性的复杂度，输出也随之改变。下面先实现标准版本，最后再比较两种优化。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `attention(q, k, v, mask=None, causal=False)`：用 NumPy 实现缩放点积注意力。`q` 形状 `[B, H, T, D]`，`k` 形状 `[B, H, S, D]`，`v` 形状 `[B, H, S, Dv]`，返回 `[B, H, T, Dv]`。
- `mask` 是 bool 数组，可广播到 `[B, H, T, S]`，`True` 表示这个 key 可见。
- `causal=True` 只允许 $T = S$，第 $i$ 个 query 只能看 $j \le i$ 的 key。
- 某一行 key 全被屏蔽时，这一行输出全 0。形状不匹配、key 长度为 0 或特征维为 0 时抛 `ValueError`。
- 用 float64 做数值验证，$B, H \le 4$，$T, S \le 128$。
- 调试练习：常见的错误版本把缩放写成除以 $D$、把 softmax 轴写成 `-2`、把 padding mask 里的 `True` 当成「屏蔽」。先说清每处错在哪里，再换成下面的正确版本。

### 输入输出示例

```text
q = k = ones((1, 1, 2, 1)), v = [[[[2], [4]]]]
attention(q, k, v, causal=True)                     -> [[[[2], [3]]]]
attention(q, k, v, mask=zeros((2, 2), dtype=bool))  -> [[[[0], [0]]]]
```

因果版本里第 0 个位置只能看自己，输出 2；第 1 个位置两个分数相同，取两个 value 的平均 3。

### 解题思路与正确性

先算 $QK^\top / \sqrt{D}$ 得到 `[B, H, T, S]` 的分数，再把不可见位置设成 $-\infty$，然后沿最后一维（key 轴）做 softmax，最后乘 `v`。顺序必须是先屏蔽再归一化，这样被屏蔽的位置权重恰好是 0，剩下的权重和仍为 1。

softmax 前减去每行最大值，防止 `exp` 溢出。全屏蔽行的最大值是 $-\infty$，直接相减会得到 `-inf - (-inf) = NaN`，所以把这种行的最大值换成 0，分母为 0 的行再用 `np.divide(..., where=denom > 0)` 输出 0。

测试要分别覆盖缩放、归一化轴和 mask 语义。缩放写错在 $D$ 不是 1 时才容易发现，所以随机对照用 $D = 4$；$T \ne S$ 能暴露 softmax 轴错误，因为每个 query 的权重和应为 1；因果和全屏蔽用例则检查 mask 是否反了。

### 完整参考实现（Python 3）

```python
import numpy as np


def check_shapes(q, k, v):
    """q: [B, H, T, D]，k: [B, H, S, D]，v: [B, H, S, Dv]。"""
    if q.ndim != 4 or k.ndim != 4 or v.ndim != 4:
        raise ValueError("q, k, v must all be 4-D [B, H, len, dim]")
    if q.shape[:2] != k.shape[:2]:
        raise ValueError("q and k must share batch and head dims")
    if k.shape[:3] != v.shape[:3]:
        raise ValueError("k and v must share batch, head and key-length dims")
    if q.shape[-1] != k.shape[-1]:
        raise ValueError("q and k must have the same feature dim D")
    if k.shape[2] == 0:
        raise ValueError("key length S must be positive")
    if q.shape[-1] == 0:
        raise ValueError("feature dim D must be positive")


def attention(q, k, v, mask=None, causal=False):
    """缩放点积注意力。mask 可广播到 [B, H, T, S]，True 表示可见；返回 [B, H, T, Dv]。

    被全部屏蔽的 query 行输出全 0。
    """
    q, k, v = (np.asarray(x, dtype=np.float64) for x in (q, k, v))
    check_shapes(q, k, v)
    query_len, key_len, dim = q.shape[2], k.shape[2], q.shape[3]

    scores = np.einsum("bhtd,bhsd->bhts", q, k) / np.sqrt(dim)  # [B, H, T, S]

    allowed = np.ones(scores.shape, dtype=bool)
    if mask is not None:
        allowed &= np.broadcast_to(np.asarray(mask, dtype=bool), scores.shape)
    if causal:
        if query_len != key_len:
            raise ValueError("causal attention requires T == S")
        allowed &= np.tril(np.ones((query_len, key_len), dtype=bool))
    scores = np.where(allowed, scores, -np.inf)

    # 减去每行最大值防止 exp 溢出；全屏蔽行的最大值是 -inf，换成 0 以免出现 -inf - (-inf) = NaN
    row_max = np.max(scores, axis=-1, keepdims=True)
    row_max = np.where(np.isfinite(row_max), row_max, 0.0)
    weights = np.exp(scores - row_max)
    denom = weights.sum(axis=-1, keepdims=True)
    weights = np.divide(weights, denom, out=np.zeros_like(weights), where=denom > 0)

    return np.einsum("bhts,bhsv->bhtv", weights, v)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.allclose(attention(q, q, v, causal=True), [[[[2.0], [3.0]]]])` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

### 可执行测试

```python
def reference_row(q_row, keys, values):
    """单个 query 的朴素循环版本，用来对照 einsum 实现。"""
    scores = keys @ q_row / np.sqrt(q_row.shape[-1])
    weights = np.exp(scores - scores.max())
    weights /= weights.sum()
    return weights @ values

def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")

# 因果 mask：第 0 个位置只看自己，第 1 个位置平均两个 value
q = np.ones((1, 1, 2, 1))
v = np.array([[[[2.0], [4.0]]]])
assert np.allclose(attention(q, q, v, causal=True), [[[[2.0], [3.0]]]])

# 全部屏蔽时输出 0，而不是 NaN
out = attention(q, q, v, mask=np.zeros((2, 2), dtype=bool))
assert np.all(out == 0)

# 随机输入与逐行循环版本对照（T != S，Dv != D）
rng = np.random.default_rng(2)
q = rng.normal(size=(2, 2, 3, 4))
k = rng.normal(size=(2, 2, 5, 4))
v = rng.normal(size=(2, 2, 5, 2))
out = attention(q, k, v)
for b in range(2):
    for h in range(2):
        for t in range(3):
            assert np.allclose(out[b, h, t], reference_row(q[b, h, t], k[b, h], v[b, h]))

# 非法输入
expect_value_error(attention, q, k, v, causal=True)          # T != S 不能用 causal
expect_value_error(attention, q, k[:, :, :, :3], v)          # D 不一致
expect_value_error(attention, q, k[:, :, :0], v[:, :, :0])   # 空 key
```

### 复杂度与追问

设 batch 为 $B$、head 数为 $H$、query 长度 $T$、key 长度 $S$、特征维 $D$、value 维 $D_v$。时间是 $O(BHTS(D + D_v))$，注意力权重矩阵占 $O(BHTS)$ 空间，序列一长这部分就是瓶颈。

- FlashAttention：把 Q、K、V 分块读进片上 SRAM，用在线 softmax（边走边维护每行的最大值和分母）累积输出，不把 $T \times S$ 的权重矩阵写回 HBM。它算出来的仍是精确的标准注意力，省的是显存读写，不是 FLOPs。
- Linear attention：把 softmax 换成核函数特征映射 $\phi(q)^\top \phi(k)$，利用结合律先算 $\phi(K)^\top V$，复杂度变成对序列长度线性。但输出和 softmax 注意力不同，属于换了一个模型，不能说成同一个函数的等价优化。
