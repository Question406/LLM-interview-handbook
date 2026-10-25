---
id: p3a-openai-transformer-bug-hunt
section: openai
order: 603
level: S
title: "OpenAI：Transformer Bug Hunt：让训练与输出恢复正确"
quick: "按 shape、因果 mask、位置索引和 label shift 逐项排查，每项都用最小输入验证。每修一处就对照 loss 和小样本输出，最后看几条数据能否过拟合，确认梯度链接通。摘要只说大约四处 bug，这份练习单独验证缩放、softmax 轴和 mask 语义。"
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
  - title: "1Point3Acres · OpenAI · transformer-bug-hunt"
    url: https://www.1point3acres.com/interview/problems/company/openai/transformer-bug-hunt
    type: secondary
---

## 题目描述

实现一个注意力调试练习的正确目标函数，明确分数缩放、mask 可见性与全屏蔽行语义。原面试未公开完整 Transformer 程序，本练习仅重构可验证的注意力子问题。

以下为手册重构练习约定，不声称是面试官原题原文。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `attention(q,k,v,mask=None,causal=False)` 输入 NumPy 数组 q[B,H,T,D]、k[B,H,S,D]、v[B,H,S,Dv]，返回 [B,H,T,Dv]。
- 对每个 query/key 的分数定义为 dot(q,k)/sqrt(D)，输出为可见 key 分数的 softmax 概率对 V 的加权和。softmax 的归一化范围是同一 query 的 key 轴。
- mask 是可广播到 [B,H,T,S] 的 bool 数组，True 表示可见；None 表示没有额外屏蔽。causal=True 时 T=S，位置 i 只允许 key j<=i，且须同时满足 mask。
- 没有任何可见 key 的行输出全0。使用 float64 验证，输入有限；1<=B,H<=4，1<=T,S<=128，D,Dv>=1。不得修改输入。

### 输入输出示例

```text
q = k = ones((1, 1, 2, 1)), v = [[[[2], [4]]]]
attention(q, k, v, causal=True)                     -> [[[[2], [3]]]]
attention(q, k, v, mask=zeros((2, 2), dtype=bool))  -> [[[[0], [0]]]]
```

因果版本里第 0 个位置只能看自己，输出 2；第 1 个位置两个分数相同，取两个 value 的平均 3。

## 解题思路与参考答案

我会先用最小样本逐项验证 shape、因果 mask、位置索引和 label shift，每修一处就重新对照输出。比如 attention 的 softmax 沿错轴可能完全不报错，却让每个 query 的权重不再归一化。最后用几条数据过拟合检查梯度链，完整模型的缺陷不能只凭“能运行”验收。

面试给一份 Transformer 模型代码、训练脚本和测试，里面被故意植入了错误。候选人要定位并修好这些 bug，让训练能正常收敛、输出恢复正确。

> 来源：一亩三分地 OpenAI 题卡摘要（2026-10-18 用 Chrome 读取），是网站对候选人报告的二手整理，没有逐条核对原帖；网站收录为面经题型不代表公司官方确认。摘要提到大约有四处 bug，但具体是哪几行无法从摘要推断。下面的接口、约束和测试是手册补的练习约定，不是原题。

## 思路

植入的 bug 通常不会让代码崩溃，而是让结果悄悄变错，所以「能跑」不等于「修好了」。建议按下面的顺序排查，每一项都有能直接验证的检查方法：

- 形状：在注意力、残差、输出层处打印或断言张量形状，确认 batch、head、序列、特征维没有被转置错。
- 因果 mask：检查 mask 是下三角，并且 `True` 的含义和代码其他地方一致。
- 位置索引：位置编码的下标是否从 0 开始、是否和序列对齐。
- label shift：语言模型的目标是输入左移一位，第 $t$ 个位置的输出要预测第 $t+1$ 个 token。

每修一处都重新跑一次，看 loss 和一两个最小输出有没有变化。最后拿几条样本反复训练，loss 应该能降到接近 0；如果降不下去，说明梯度链上还有问题，比如某处 `detach` 或缩放错误。

下面的练习把范围缩小到注意力函数本身，用来练习三类最常见的注意力 bug。

## 完整编程练习（手册重构版）

### 题面、接口与约束

- `attention(q, k, v, mask=None, causal=False)`：用 NumPy 实现缩放点积注意力。`q` 形状 `[B, H, T, D]`，`k` 形状 `[B, H, S, D]`，`v` 形状 `[B, H, S, Dv]`，返回 `[B, H, T, Dv]`。
- `mask` 是 bool 数组，可广播到 `[B, H, T, S]`，`True` 表示这个 key 可见。
- `causal=True` 只允许 $T = S$，第 $i$ 个 query 只能看 $j \le i$ 的 key。
- 某一行 key 全被屏蔽时，这一行输出全 0。形状不匹配、key 长度为 0 或特征维为 0 时抛 `ValueError`。
- 用 float64 做数值验证，$B, H \le 4$，$T, S \le 128$。
- 调试练习：常见的错误版本把缩放写成除以 $D$、把 softmax 轴写成 `-2`、把 padding mask 里的 `True` 当成「屏蔽」。先说清每处错在哪里，再换成下面的正确版本。完整的 Transformer 代码没有公开，这里不声称还原了原题的四处 bug。

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

## 相关题

- [[openai-transformer-debug]]：手册里已有的同类题；两份题面契约不完全一致，这里的接口只描述本练习。那张是整份 Transformer 按五类查 bug，再加 KV cache。
- [[us-debug-vs-leetcode]]：解释美国 lab 为什么出这种 debug 题、和 LeetCode 测的能力差在哪，适合做题前先看。
