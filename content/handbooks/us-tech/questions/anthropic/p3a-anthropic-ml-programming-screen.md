---
id: p3a-anthropic-ml-programming-screen
section: anthropic
order: 618
level: S
title: "Anthropic：ML Programming：QKV Attention 与 einsum"
quick: "先标清 batch、head、序列和特征各是哪一维，再按 QK 转置、缩放、mask、沿 key 轴 softmax、乘 V 的顺序实现，并单独处理全屏蔽的行。"
companies:
  - anthropic
tags:
  - 完整编程练习
  - 1Point3Acres
  - Frontier-2026-10
  - ML
  - Anthropic
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: "1Point3Acres · Anthropic · ml-programming-screen"
    url: https://www.1point3acres.com/interview/problems/company/anthropic/ml-programming-screen
    type: secondary
---

## 题目

面试官给出数学公式，要求照着实现一个序列模型组件，典型就是缩放点积注意力。考察点是能不能把公式里的下标准确翻译成张量维度和 `einsum`，以及 mask、数值稳定这些细节有没有想到。

> 来源：一亩三分地 Anthropic 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；网站收录为面经题型不代表公司官方确认。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

动手前先把每个张量的维度写下来：`q` 是 `[B, H, T, D]`，`k` 是 `[B, H, S, D]`，`v` 是 `[B, H, S, Dv]`。这样 `einsum("bhtd,bhsd->bhts")` 里被求和消掉的就是 `d`，读代码的人能直接对上公式 $\mathrm{softmax}(QK^\top / \sqrt{D})V$ 里的求和下标。

写完后重点自查两处：

- softmax 是沿 key 轴（最后一维）归一化，每个 query 的权重和应该是 1；
- 一行 key 全被屏蔽时会不会出 NaN，以及你打算让它输出什么。

最后拿一个极小的例子，用两层 for 循环直接按公式算一遍，和向量化版本对照。值得问面试官的是 mask 的语义（`True` 是可见还是屏蔽）和全屏蔽行的期望输出。

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

三个常见错误各自破坏一个不变量，也各有能抓住它的测试：缩放写错只在 $D$ 不是 1 时露馅，所以随机对照测试用 $D = 4$；softmax 轴写错会让每个 query 的权重和不再是 1，$T \ne S$ 的输入能暴露；mask 语义反了，因果测试和全屏蔽测试都会失败。

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
