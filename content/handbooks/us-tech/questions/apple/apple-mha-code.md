---
id: apple-mha-code
section: apple
order: 1
level: A
title: Apple / Siri MLE：手写 Multi-Head Attention，shape 和 mask 怎么收？
quick: >-
  我会先把 $[B,T,d]$ 的输入投影并拆成 $[B,H,T,d_h]$ 的 Q/K/V，计算 $QK^\top/\sqrt{d_h}$，在
  softmax 前加 causal 和 padding mask，再乘 V、合并 heads。比如带 cache decoding 时，新 query
  的绝对位置从旧 cache 长度开始，完整序列与逐 token 结果应一致。
tags:
  - 完整编程练习
  - Apple
  - Siri
  - Attention
  - Coding
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: Apple Siri MLE Phone Screen 面经
    url: 'https://www.1point3acres.com/bbs/thread-1170553-1-1.html'
    type: candidate-first-hand
  - title: Attention Is All You Need
    url: 'https://arxiv.org/abs/1706.03762'
    type: primary
---

## 题目描述

用 NumPy 实现支持紧凑 KV cache、GQA 和可选 RoPE 的 causal multi-head attention；完整序列与逐段 decoding 应表示同一 attention 运算。

以下接口、edge cases 和规模限制是手册重构的练习约定；输入默认满足所列合法约束。

### 接口与规则

- `mha(x, wq, wk, wv, wo, heads, kv_heads=None, cache=None, key_valid=None, use_rope=False)`：用 NumPy 写 causal multi-head attention，返回 `(output, new_cache)`。`Q=x@wq`、新 `K=x@wk`、新 `V=x@wv`；query head `h` 对应 KV head `h // (heads/Hkv)`。attention 权重为可见 Q/K 缩放点积的 softmax，缩放因子为 `1/sqrt(d)`，值向量加权结果经 `wo` 输出；绝对位置 `prefix+t` 的 query 仅可见不晚于自身的 key。
- `rope(x, start)`：对 `[B, H, T, d]` 的 tensor 做旋转 positional encoding，返回同形数组。相邻分量 `(2j,2j+1)` 按角度 `(start+t) * 10000^(-2j/d)` 做二维旋转，第 `t` 个 token 的绝对位置是 `start + t`。
- 形状：`x` 是 `[B, T, D]`，`wq`、`wo` 是 `[D, D]`，`wk`、`wv` 是 `[D, Hkv * d]`，其中 `d = D / heads`、`Hkv = kv_heads`（默认等于 `heads`）。`heads` 必须整除 `D`，也必须是 `Hkv` 的整数倍。
- `cache` 是一对 `[B, Hkv, prefix, d]` 的 K/V，只存紧凑的 KV heads。返回的新 cache 长度是 `prefix + T`。
- `key_valid` 是 `[B, prefix + T]` 的布尔数组，True 表示这个 key 可见。某个 query 的 key 全被屏蔽时，输出 0，不能出现 NaN。
- 打开 RoPE 时 `d` 必须是偶数。当前这段 token 的位置从 `prefix` 开始编号；cache 里的旧 K 已经旋转过，不能再转一次。
- 没有 dropout 和 bias。输入有限，B ≤ 8、T ≤ 256、D ≤ 128。输出形状为 `[B, T, D]`。

### 输入输出示例

```text
x = [[[2, 4], [6, 8]]], heads = kv_heads = 1
wq = wk = 全零 2×2 矩阵，wv = wo = 2×2 单位矩阵
cache = None, key_valid = None, use_rope = False
mha(...) 的 output -> [[[2, 4], [4, 6]]]
new_cache 的 K、V 形状均为 [1, 1, 2, 2]。
```

## 解题思路与参考答案

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。只用 NumPy，CPU 上验证。

### 题面、接口与约束

- `mha(x, wq, wk, wv, wo, heads, kv_heads=None, cache=None, key_valid=None, use_rope=False)`：用 NumPy 写 causal multi-head attention，返回 `(output, new_cache)`。依次做 Q/K/V 投影、缩放点积、causal mask、数值稳定的 softmax、合并 heads 和输出投影。
- `rope(x, start)`：对 `[B, H, T, d]` 的 tensor 做旋转 positional encoding，第 `t` 个 token 的绝对位置是 `start + t`。
- 形状：`x` 是 `[B, T, D]`，`wq`、`wo` 是 `[D, D]`，`wk`、`wv` 是 `[D, Hkv * d]`，其中 `d = D / heads`、`Hkv = kv_heads`（默认等于 `heads`）。`heads` 必须整除 `D`，也必须是 `Hkv` 的整数倍。
- `cache` 是一对 `[B, Hkv, prefix, d]` 的 K/V，只存紧凑的 KV heads。返回的新 cache 长度是 `prefix + T`。
- `key_valid` 是 `[B, prefix + T]` 的布尔数组，True 表示这个 key 可见。某个 query 的 key 全被屏蔽时，输出 0，不能出现 NaN。
- 打开 RoPE 时 `d` 必须是偶数。当前这段 token 的位置从 `prefix` 开始编号；cache 里的旧 K 已经旋转过，不能再转一次。
- 没有 dropout 和 bias。输入有限，B ≤ 8、T ≤ 256、D ≤ 128。形状不合法时抛 `ValueError`。

### 输入输出示例

```text
单 head，wq = wk = 0（所以 Q = K = 0），wv = wo = I，x = [[2, 4], [6, 8]]
query 0 只能看 key 0             -> [2, 4]
query 1 对 key 0、1 均匀平均      -> [4, 6]

任意固定权重下：
mha(完整序列) == 逐 token 带 cache 调用 mha，再沿时间维拼接
```

### 解题思路与正确性

先把输入投影成 Q/K/V 并拆成多头，再按当前这段 token 的绝对位置对 Q 和新 K 做 RoPE，最后把新 K/V 接到 cache 后面。旧 K 在写进 cache 之前就转过了，这里不再碰它。

当前段的第 `i` 个 query 位于绝对位置 `prefix + i`，只能看下标 `j ≤ prefix + i` 的 key。prefill（`prefix = 0`）、单 token decode 和一次喂多个 token 的分块 decode 都用这同一条规则，所以三种调用方式拼出来的结果一致。

softmax 沿 key 维做，先减去每行的最大值，`exp` 就不会溢出。一行 key 全被屏蔽时，最大值是 `-inf`，先换成 0，此时分母为 0，按约定输出 0。

GQA 里 query head `h` 读第 `h // group` 个 KV head，`group = heads / Hkv`。参考实现用 `np.repeat` 把 KV 展开后算 attention，只是为了写出直观的基准；cache 本身始终只存 `Hkv` 份。

### 完整参考实现（Python 3）

```python
import numpy as np


def rope(x, start):
    """对 x: [B, H, T, d] 做 RoPE，第 t 个 token 的绝对位置是 start + t。"""
    head_dim = x.shape[-1]
    if head_dim % 2:
        raise ValueError(f"RoPE requires an even head dimension, got {head_dim}")
    positions = np.arange(start, start + x.shape[2])[:, None]  # [T, 1]
    inv_freq = 10000.0 ** (-np.arange(0, head_dim, 2) / head_dim)  # [d/2]
    angles = positions * inv_freq  # [T, d/2]
    cos, sin = np.cos(angles), np.sin(angles)
    even, odd = x[..., 0::2], x[..., 1::2]
    out = np.empty_like(x)
    out[..., 0::2] = even * cos - odd * sin
    out[..., 1::2] = even * sin + odd * cos
    return out


def split_heads(x, num_heads):
    """[B, T, num_heads * d] -> [B, num_heads, T, d]。"""
    B, T, width = x.shape
    return x.reshape(B, T, num_heads, width // num_heads).transpose(0, 2, 1, 3)


def mha(
    x, wq, wk, wv, wo, heads, kv_heads=None, cache=None, key_valid=None, use_rope=False
):
    """因果 multi-head attention，支持 GQA、KV cache、key padding mask 和 RoPE。

    x: [B, T, D]；wq, wo: [D, D]；wk, wv: [D, kv_heads * d]，d = D // heads。
    cache: (k, v)，各为 [B, kv_heads, prefix, d]，其中 k 已按绝对位置旋转过。
    key_valid: [B, prefix + T] 的布尔数组，True 表示该 key 可见。
    返回 (output [B, T, D], 新 cache (k, v)，各为 [B, kv_heads, prefix + T, d])。
    """
    x = np.asarray(x, dtype=float)
    wq, wk, wv, wo = (np.asarray(w, dtype=float) for w in (wq, wk, wv, wo))
    kv_heads = heads if kv_heads is None else kv_heads
    if x.ndim != 3:
        raise ValueError(f"x must be [B, T, D], got shape {x.shape}")
    if heads <= 0 or kv_heads <= 0 or heads % kv_heads:
        raise ValueError(
            f"heads={heads} must be a positive multiple of kv_heads={kv_heads}"
        )
    B, T, D = x.shape
    if B == 0 or T == 0:
        raise ValueError(f"empty input, got shape {x.shape}")
    if D % heads:
        raise ValueError(f"model dim {D} is not divisible by heads={heads}")
    d = D // heads
    if wq.shape != (D, D) or wo.shape != (D, D):
        raise ValueError(f"wq and wo must be [{D}, {D}], got {wq.shape} and {wo.shape}")
    if wk.shape != (D, kv_heads * d) or wv.shape != (D, kv_heads * d):
        raise ValueError(
            f"wk and wv must be [{D}, {kv_heads * d}], got {wk.shape} and {wv.shape}"
        )

    q = split_heads(x @ wq, heads)  # [B, heads, T, d]
    k = split_heads(x @ wk, kv_heads)  # [B, kv_heads, T, d]
    v = split_heads(x @ wv, kv_heads)  # [B, kv_heads, T, d]

    prefix = 0
    if cache is not None:
        cached_k, cached_v = (np.asarray(a, dtype=float) for a in cache)
        if (
            cached_k.ndim != 4
            or cached_k.shape != cached_v.shape
            or cached_k.shape[:2] != (B, kv_heads)
            or cached_k.shape[-1] != d
        ):
            raise ValueError(
                f"cache must hold two [{B}, {kv_heads}, prefix, {d}] arrays, "
                f"got {cached_k.shape} and {cached_v.shape}"
            )
        prefix = cached_k.shape[2]
    if use_rope:
        # 新 token 的位置从 prefix 开始编号；cache 里的旧 K 已旋转过，不再转第二次
        q = rope(q, prefix)
        k = rope(k, prefix)
    if cache is not None:
        k = np.concatenate((cached_k, k), axis=2)  # [B, kv_heads, S, d]
        v = np.concatenate((cached_v, v), axis=2)
    S = k.shape[2]

    # cache 只存 kv_heads 份；这里 repeat 只是为了写出正确性基准，
    # 融合 kernel 会让 query head h 直接读第 h // group 个 KV head
    group = heads // kv_heads
    k_rep = np.repeat(k, group, axis=1)  # [B, heads, S, d]
    v_rep = np.repeat(v, group, axis=1)
    scores = q @ k_rep.swapaxes(-1, -2) / np.sqrt(d)  # [B, heads, T, S]

    # query i 的绝对位置是 prefix + i，只能看 key j <= prefix + i
    causal = np.arange(S)[None, :] <= prefix + np.arange(T)[:, None]  # [T, S]
    allowed = np.broadcast_to(causal, (B, heads, T, S))
    if key_valid is not None:
        valid = np.asarray(key_valid, dtype=bool)
        if valid.shape != (B, S):
            raise ValueError(f"key_valid must be [{B}, {S}], got shape {valid.shape}")
        allowed = allowed & valid[:, None, None, :]
    scores = np.where(allowed, scores, -np.inf)

    # 稳定 softmax：先减行最大值；全屏蔽行的最大值是 -inf，换成 0
    row_max = scores.max(axis=-1, keepdims=True)
    row_max = np.where(np.isfinite(row_max), row_max, 0.0)
    weights = np.exp(scores - row_max)
    denom = weights.sum(axis=-1, keepdims=True)
    # 全屏蔽行的分母是 0，约定输出 0，避免 0 / 0 = NaN
    weights = np.divide(weights, denom, out=np.zeros_like(weights), where=denom > 0)

    context = weights @ v_rep  # [B, heads, T, d]
    output = context.transpose(0, 2, 1, 3).reshape(B, T, D) @ wo
    return output, (k, v)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.allclose(full, np.concatenate(pieces, axis=1))` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制 assertion 这一行。

数值结果用 `allclose` 一类带容差的 assertion 检查，并同时确认形状；随机输入固定 seed。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现 assertion 失败时，从第一条失败的检查定位。assertion 全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

### 可执行测试

```python
def expect_value_error(fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except ValueError:
        return
    raise AssertionError(f"{fn.__name__} should raise ValueError")


def loop_reference(x, wq, wk, wv, wo, heads):
    """逐 batch、逐 head、逐 query 的朴素因果 MHA（无 cache、无 RoPE），作独立对照。"""
    B, T, D = x.shape
    d = D // heads
    q, k, v = x @ wq, x @ wk, x @ wv
    context = np.zeros((B, T, D))
    for b in range(B):
        for h in range(heads):
            cols = slice(h * d, (h + 1) * d)
            for i in range(T):
                logits = k[b, : i + 1, cols] @ q[b, i, cols] / np.sqrt(d)
                probs = np.exp(logits - logits.max())
                probs /= probs.sum()
                context[b, i, cols] = probs @ v[b, : i + 1, cols]
    return context @ wo


rng = np.random.default_rng(7)
x = rng.normal(size=(2, 5, 8))  # B=2, T=5, D=8；heads=4 时 d=2

for kv_heads in (1, 2, 4):
    weights = [
        rng.normal(size=(8, width)) for width in (8, kv_heads * 2, kv_heads * 2, 8)
    ]
    for use_rope in (False, True):
        # 一次算完整序列，和逐 token 带 cache decoding 再拼接，结果一致
        full, _ = mha(x, *weights, heads=4, kv_heads=kv_heads, use_rope=use_rope)
        pieces = []
        cache = None
        for step in range(5):
            out, cache = mha(
                x[:, step : step + 1],
                *weights,
                heads=4,
                kv_heads=kv_heads,
                cache=cache,
                use_rope=use_rope,
            )
            pieces.append(out)
        assert np.allclose(full, np.concatenate(pieces, axis=1))

        # cache 只存紧凑的 kv_heads 份
        assert cache[0].shape == (2, kv_heads, 5, 2)

        # 大幅改动最后一个 token，前 4 个位置的输出不变：没有未来信息泄漏
        changed = x.copy()
        changed[:, 4] += 100
        other, _ = mha(changed, *weights, heads=4, kv_heads=kv_heads, use_rope=use_rope)
        assert np.allclose(full[:, :4], other[:, :4])

    # 所有 key 都被屏蔽：输出全 0，没有 NaN
    zero, _ = mha(
        x, *weights, heads=4, kv_heads=kv_heads, key_valid=np.zeros((2, 5), bool)
    )
    assert np.isfinite(zero).all()
    assert np.allclose(zero, 0)

# 和逐 head 循环的朴素实现对照：能抓住缩放、softmax 轴、head 合并写错
weights = [rng.normal(size=(8, 8)) for _ in range(4)]
full, _ = mha(x, *weights, heads=4)
assert np.allclose(full, loop_reference(x, *weights, heads=4))

# 已知数值：Q = K = 0 时 attention 是对可见 key 的均匀平均
known_x = np.array([[[2.0, 4.0], [6.0, 8.0]]])
identity = np.eye(2)
zeros = np.zeros((2, 2))
out, _ = mha(known_x, zeros, zeros, identity, identity, heads=1)
assert np.allclose(out, [[[2.0, 4.0], [4.0, 6.0]]])

# 带 cache 一次喂多个 token（分块 decode）：因果 mask 也要加上 prefix 偏移
identity_weights = [np.eye(8)] * 4
full, _ = mha(x, *identity_weights, heads=4, use_rope=True)
_, cache = mha(x[:, :2], *identity_weights, heads=4, use_rope=True)
tail, _ = mha(x[:, 2:], *identity_weights, heads=4, cache=cache, use_rope=True)
assert np.allclose(full[:, 2:], tail)

# padding：屏蔽 key 0 后，query 0 无 key 可看输出 0；其余位置等于去掉 token 0 重新算
key_valid = np.ones((2, 5), bool)
key_valid[:, 0] = False
masked, _ = mha(x, *identity_weights, heads=4, key_valid=key_valid)
without_first, _ = mha(x[:, 1:], *identity_weights, heads=4)
assert np.allclose(masked[:, 0], 0)
assert np.allclose(masked[:, 1:], without_first)

# 非法输入抛 ValueError：D=8 不能被 heads=3 整除；heads=4 不是 kv_heads=3 的倍数；缺 batch 维
expect_value_error(mha, x, *identity_weights, heads=3)
expect_value_error(mha, x, *identity_weights, heads=4, kv_heads=3)
expect_value_error(mha, x[0], *identity_weights, heads=4)

# key_valid 长度和 prefix + T 对不上；cache 的 K、V 形状不一致
expect_value_error(mha, x, *identity_weights, heads=4, key_valid=np.ones((2, 4), bool))
bad_cache = (np.zeros((2, 4, 3, 2)), np.zeros((2, 4, 2, 2)))
expect_value_error(mha, x, *identity_weights, heads=4, cache=bad_cache)

# RoPE 要求 head 维为偶数：heads=8 时 d=1
expect_value_error(mha, x, *identity_weights, heads=8, use_rope=True)
```

### 复杂度与追问

设总 KV 长度 S = prefix + T。投影是 O(B·T·D²)，attention 是 O(B·heads·T·S·d)。参考实现把整块 scores 放在内存里，额外空间 O(B·heads·T·S)；cache 占 O(B·Hkv·S·d)。这是 NumPy 写的正确性基准，不是融合 GPU kernel。

- 追问「这些测试能抓住哪些 bug」：去掉 causal mask，未来扰动测试会失败；softmax 轴、缩放或合并 heads 写错，逐 head 循环对照会失败；RoPE offset 写成 0 或 mask 没加 prefix，有/无 cache 对照会失败；已知均值例子能直接看出 normalization 对不对。
- 原始面试里的完整 Transformer 代码没有公开，不要把这段练习说成原帖的 300 行源码。

## 真题记录

- 公司：Apple
- 岗位：Siri / Apple Intelligence 相关 MLE
- 来源：一亩三分地 2026-03 Siri MLE phone screen 讨论。公开回复里提到的高频 ML coding 有：sampling（top-k / top-p）、k-means、attention、KV caching、MLP backpropagation。
- 各组差异很大：有的是 30 分钟 coding 加 30 分钟 ML 问答，有的偏 case study。具体以 recruiter 邮件为准。

我会按投影、拆 head、加 mask、softmax、乘 V 和合并的顺序实现，再用完整序列与逐 token cache 对照检查。比如一段 token 接在旧 cache 后面，causal mask 和 RoPE 都要从旧长度开始，不能把位置重新当成 0。完整 attention 见 `code-attention`，单步 cache 更新见 `code-kv-cache-step`，sampling 见 `code-sampling`。

## 从 shape 推到 mask

要求 $d_{\mathrm{model}}$ 能被 $H$ 整除，每个 head 的维度是 $d_h=d_{\mathrm{model}}/H$。

1. `qkv = Linear(x)`，切成 $Q,K,V$，每个是 `[B,T,H,d_h]`，再 transpose 成 `[B,H,T,d_h]`。
2. `scores = einsum("bhtd,bhsd->bhts", q, k) / sqrt(d_h)`。
3. 先加 mask，再做 softmax。causal mask 把 key 位置 $s$ 晚于 query 位置 $t$（即 $s>t$）的分数设成 $-\infty$，padding mask 同理。mask 的形状要能广播到 `[B,H,T,S]`，否则可能在 head 维上悄悄错位。
4. `attn = softmax(scores, dim=-1)`，乘上 V，transpose 回 `[B,T,H,d_h]`，view 成 `[B,T,d]`，最后过输出投影。

电面 30 分钟里能把 forward 写完就很好。可以主动补几句：fp16 下不做缩放，点积会溢出；eval 时要关 dropout；逐 token 生成（decode）时每一步只算当前 token 的 $q$，K/V 从 cache 里读。KV cache 是同一条评论里的高频追问，查法见 `openai-transformer-debug`。

同一批面经里还有 sampling 追问：先除温度，再做 top-k / top-p；nucleus 是在温度缩放之后的分布上截断的。不要先截断再除 $T$。细节见 `code-sampling`。

## on-device 还要检查 KV 和数值

Siri 的 attention 题常会转到 on-device 约束：head 数怎么定，KV 要不要用 GQA，quantization 之后 mask 还能不能用 $-\infty$。on-device 实现需要额外检查 KV 带宽和 quantization 后的数值。可以这样说：on-device decode 更受 KV 带宽限制，所以 GQA 和 quantization cache 比继续加 head 更重要；在 int8 scores 上做 mask 时要用足够负的数，不能默认 fp32 里的 `-1e9` 也一定安全。

如果组里做语音，可能会追问 self-attention 和 cross-attention 的区别。cross-attention 是另一套 shape：Q 来自 decoder 当前的状态，K/V 来自 encoder 的输出（encoder 记忆），并且 cross 这一层不加 causal mask。

## 追问

**为什么要除以 $\sqrt{d_h}$？**
点积的方差随维数增长，不缩放的话 softmax 容易饱和。
**换成 Multi-Query / GQA，代码差在哪？**
$K,V$ 的 head 维变成 $H_{\mathrm{kv}}$，算 attention 前 repeat 一下（上面的参考实现就是这样）。产品约束见 `apple-siri-grounded`，选型对照见 `google-gqa-mqa`。
**k-means 为什么也会出现？**
同一条面经把聚类也当作 ML coding 基本功。不要把时间全押在 Transformer 上，准备一个 20 行左右的向 quantization k-means。

## 相关题

- [[openai-softmax-bug]]：两题的编程练习是同一份 MHA 实现和测试；那题从 debug 角度问 softmax 轴和 mask 填 0 的错误，本题重点在 shape 和拆 head。
- [[coding-attn-mask]]：把本题第 3 步的 mask 单独拿出来，causal、padding、document boundaries 合成一张加性 bias。
- [[apple-ondevice-quant]]：本题「Apple 口味」一节的展开，on-device quantization 后 mask 的 $-\infty$ 为什么不安全。
