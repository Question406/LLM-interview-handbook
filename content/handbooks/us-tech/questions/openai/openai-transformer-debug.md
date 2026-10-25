---
id: openai-transformer-debug
section: openai
order: 1
level: S
title: OpenAI：给一份带 bug 的 Transformer，怎么查？KV cache 怎么加？
quick: "先用 eval、greedy 和固定 seed 得到可复现结果，再检查 mask、softmax 轴、缩放、位置偏移和 target shift。修好后再加 KV cache，并让有/无 cache 输出逐 token 一致；比如 cache 路径每步误用位置 0，shape 虽然正常，结果仍会偏。"
tags:
  - 完整编程练习
  - OpenAI
  - Transformer
  - KV Cache
  - Debug
realInterview: true
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: OpenAI Research Engineer Interview Experience (2025)
    url: https://www.tryexponent.com/experiences/openai-machine-learning-engineer-interview-c7b6a2
    type: candidate-first-hand
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
  - title: OpenAI MLE phone screen Transformer debugging (1Point3Acres)
    url: https://www.1point3acres.com/interview/thread/1134115
    type: candidate-first-hand
---

## 题目描述

完成一个可用于 Transformer 正确性排查的因果多头注意力实现。给定投影权重、输入、历史 KV 和有效 key 信息，返回注意力输出与更新缓存；全量计算、增量解码和前缀复用必须遵守相同语义。

以下为手册重构练习约定，不表示面经披露了这些完整接口。默认输入满足合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `mha(x, wq, wk, wv, wo, heads, kv_heads=None, cache=None, key_valid=None, use_rope=False)`：用 NumPy 写因果多头注意力，返回 `(output, new_cache)`。其数学输出为各 query 对可见 key 的缩放点积 softmax 加权 V，再按 head 拼接并右乘 `wo`；分数除以 `sqrt(d)`。query head h 使用 KV head `floor(h/(heads/Hkv))`。
- `rope(x, start)`：对 `[B, H, T, d]` 的张量做旋转位置编码，第 `t` 个 token 的绝对位置是 `start + t`。
- 形状：`x` 是 `[B, T, D]`，`wq`、`wo` 是 `[D, D]`，`wk`、`wv` 是 `[D, Hkv * d]`，其中 `d = D / heads`、`Hkv = kv_heads`（默认等于 `heads`）。`heads` 必须整除 `D`，也必须是 `Hkv` 的整数倍。
- `cache` 是一对 `[B, Hkv, prefix, d]` 的 K/V，只存紧凑的 KV heads。返回的新 cache 长度是 `prefix + T`。
- `key_valid` 是 `[B, prefix + T]` 的布尔数组，True 表示这个 key 可见。某个 query 的 key 全被屏蔽时，输出 0，不能出现 NaN。
- 打开 RoPE 时 `d` 必须是偶数。当前这段 token 的位置从 `prefix` 开始编号；cache 里的旧 K 已经旋转过，不能再转一次。
- 没有 dropout 和 bias。输入有限，B ≤ 8、T ≤ 256、D ≤ 128。假定形状满足上述条件。

- `output` 形状为 `[B,T,D]`；query 绝对位置为 `prefix+t`，只允许访问 key 下标不超过该值且 `key_valid=True` 的位置。投影采用右乘权重，不转置传入矩阵。
- RoPE 对相邻坐标对 `(x[2i],x[2i+1])` 作角度 `position*10000^(-2i/d)` 的二维旋转，即 `(a*cos(theta)-b*sin(theta), a*sin(theta)+b*cos(theta))`。只旋转 Q 和 K，V 不旋转。
### 示例

```text
单 head，wq = wk = 0（所以 Q = K = 0），wv = wo = I，x = [[[2, 4], [6, 8]]]（B=1）
query 0 只能看 key 0             -> [2, 4]
query 1 对 key 0、1 均匀平均      -> [4, 6]
完整 output = [[[2,4],[4,6]]]，new_cache 的 K/V 形状均为 [1,1,2,2]

任意固定权重下：
mha(完整序列) == 逐 token 带 cache 调用 mha，再沿时间维拼接
```

## 解题思路与参考答案

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是原帖题面或官方测试。只用 NumPy，CPU 上验证。

### 题面、接口与约束

- `mha(x, wq, wk, wv, wo, heads, kv_heads=None, cache=None, key_valid=None, use_rope=False)`：用 NumPy 写因果多头注意力，返回 `(output, new_cache)`。依次做 Q/K/V 投影、缩放点积、因果 mask、数值稳定的 softmax、合并 heads 和输出投影。
- `rope(x, start)`：对 `[B, H, T, d]` 的张量做旋转位置编码，第 `t` 个 token 的绝对位置是 `start + t`。
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

GQA 里 query head `h` 读第 `h // group` 个 KV head，`group = heads / Hkv`。参考实现用 `np.repeat` 把 KV 展开后算注意力，只是为了写出直观的基准；cache 本身始终只存 `Hkv` 份。

### 完整参考实现（Python 3）

```python
import numpy as np


def rope(x, start):
    """对 x: [B, H, T, d] 做 RoPE，第 t 个 token 的绝对位置是 start + t。"""
    head_dim = x.shape[-1]
    if head_dim % 2:
        raise ValueError(f"RoPE requires an even head dimension, got {head_dim}")
    positions = np.arange(start, start + x.shape[2])[:, None]      # [T, 1]
    inv_freq = 10000.0 ** (-np.arange(0, head_dim, 2) / head_dim)  # [d/2]
    angles = positions * inv_freq                                  # [T, d/2]
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


def mha(x, wq, wk, wv, wo, heads, kv_heads=None, cache=None,
        key_valid=None, use_rope=False):
    """因果多头注意力，支持 GQA、KV cache、key padding mask 和 RoPE。

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
            f"heads={heads} must be a positive multiple of kv_heads={kv_heads}")
    B, T, D = x.shape
    if B == 0 or T == 0:
        raise ValueError(f"empty input, got shape {x.shape}")
    if D % heads:
        raise ValueError(f"model dim {D} is not divisible by heads={heads}")
    d = D // heads
    if wq.shape != (D, D) or wo.shape != (D, D):
        raise ValueError(
            f"wq and wo must be [{D}, {D}], got {wq.shape} and {wo.shape}")
    if wk.shape != (D, kv_heads * d) or wv.shape != (D, kv_heads * d):
        raise ValueError(f"wk and wv must be [{D}, {kv_heads * d}], "
                         f"got {wk.shape} and {wv.shape}")

    q = split_heads(x @ wq, heads)     # [B, heads, T, d]
    k = split_heads(x @ wk, kv_heads)  # [B, kv_heads, T, d]
    v = split_heads(x @ wv, kv_heads)  # [B, kv_heads, T, d]

    prefix = 0
    if cache is not None:
        cached_k, cached_v = (np.asarray(a, dtype=float) for a in cache)
        if (cached_k.ndim != 4 or cached_k.shape != cached_v.shape
                or cached_k.shape[:2] != (B, kv_heads) or cached_k.shape[-1] != d):
            raise ValueError(
                f"cache must hold two [{B}, {kv_heads}, prefix, {d}] arrays, "
                f"got {cached_k.shape} and {cached_v.shape}")
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
            raise ValueError(
                f"key_valid must be [{B}, {S}], got shape {valid.shape}")
        allowed = allowed & valid[:, None, None, :]
    scores = np.where(allowed, scores, -np.inf)

    # 稳定 softmax：先减行最大值；全屏蔽行的最大值是 -inf，换成 0
    row_max = scores.max(axis=-1, keepdims=True)
    row_max = np.where(np.isfinite(row_max), row_max, 0.0)
    weights = np.exp(scores - row_max)
    denom = weights.sum(axis=-1, keepdims=True)
    # 全屏蔽行的分母是 0，约定输出 0，避免 0 / 0 = NaN
    weights = np.divide(weights, denom, out=np.zeros_like(weights),
                        where=denom > 0)

    context = weights @ v_rep  # [B, heads, T, d]
    output = context.transpose(0, 2, 1, 3).reshape(B, T, D) @ wo
    return output, (k, v)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert np.allclose(full, np.concatenate(pieces, axis=1))` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补边界。

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
                logits = k[b, :i + 1, cols] @ q[b, i, cols] / np.sqrt(d)
                probs = np.exp(logits - logits.max())
                probs /= probs.sum()
                context[b, i, cols] = probs @ v[b, :i + 1, cols]
    return context @ wo


rng = np.random.default_rng(7)
x = rng.normal(size=(2, 5, 8))  # B=2, T=5, D=8；heads=4 时 d=2

for kv_heads in (1, 2, 4):
    weights = [rng.normal(size=(8, width))
               for width in (8, kv_heads * 2, kv_heads * 2, 8)]
    for use_rope in (False, True):
        # 一次算完整序列，和逐 token 带 cache 解码再拼接，结果一致
        full, _ = mha(x, *weights, heads=4, kv_heads=kv_heads, use_rope=use_rope)
        pieces = []
        cache = None
        for step in range(5):
            out, cache = mha(x[:, step:step + 1], *weights, heads=4,
                             kv_heads=kv_heads, cache=cache, use_rope=use_rope)
            pieces.append(out)
        assert np.allclose(full, np.concatenate(pieces, axis=1))

        # cache 只存紧凑的 kv_heads 份
        assert cache[0].shape == (2, kv_heads, 5, 2)

        # 大幅改动最后一个 token，前 4 个位置的输出不变：没有未来信息泄漏
        changed = x.copy()
        changed[:, 4] += 100
        other, _ = mha(changed, *weights, heads=4, kv_heads=kv_heads,
                       use_rope=use_rope)
        assert np.allclose(full[:, :4], other[:, :4])

    # 所有 key 都被屏蔽：输出全 0，没有 NaN
    zero, _ = mha(x, *weights, heads=4, kv_heads=kv_heads,
                  key_valid=np.zeros((2, 5), bool))
    assert np.isfinite(zero).all()
    assert np.allclose(zero, 0)

# 和逐 head 循环的朴素实现对照：能抓住缩放、softmax 轴、head 合并写错
weights = [rng.normal(size=(8, 8)) for _ in range(4)]
full, _ = mha(x, *weights, heads=4)
assert np.allclose(full, loop_reference(x, *weights, heads=4))

# 已知数值：Q = K = 0 时注意力是对可见 key 的均匀平均
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
expect_value_error(mha, x, *identity_weights, heads=4,
                   key_valid=np.ones((2, 4), bool))
bad_cache = (np.zeros((2, 4, 3, 2)), np.zeros((2, 4, 2, 2)))
expect_value_error(mha, x, *identity_weights, heads=4, cache=bad_cache)

# RoPE 要求 head 维为偶数：heads=8 时 d=1
expect_value_error(mha, x, *identity_weights, heads=8, use_rope=True)
```

### 复杂度与追问

设总 KV 长度 S = prefix + T。投影是 O(B·T·D²)，注意力是 O(B·heads·T·S·d)。参考实现把整块 scores 放在内存里，额外空间 O(B·heads·T·S)；cache 占 O(B·Hkv·S·d)。这是 NumPy 写的正确性基准，不是融合 GPU kernel。

- 追问「这些测试能抓住哪些 bug」：去掉 causal mask，未来扰动测试会失败；softmax 轴、缩放或合并 heads 写错，逐 head 循环对照会失败；RoPE offset 写成 0 或 mask 没加 prefix，有/无 cache 对照会失败；已知均值例子能直接看出归一化对不对。
- 原始面试里的完整 Transformer 代码没有公开，不要把这段练习说成原帖的 300 行源码。

## 真题记录

- 公司：OpenAI
- 岗位：Research Engineer / Machine Learning Engineer
- 轮次：ML debugging（onsite 技术轮），也有 phone screen 的变体。
- 来源：Exponent 2025 候选人报告；一亩三分地 MLE phone screen 摘要。
- 题面大意：给一份约 300 行的 Transformer，四个标注区间里各有一个 bug。修好之后实现 KV cache。几乎不给提示。

我会先让结果可复现，再按张量约定定位 bug，修完后才加 KV cache。比如位置偏移写错，代码不报错，cache 路径却会悄悄偏离完整前向；固定 greedy 和 eval 后，逐 token 对照才能判断改动是否正确。

## 先固定观测，再按五类查

打开 `eval()`，用 greedy / argmax，关掉 dropout。训练态和采样的随机性混在一起时，就算改对了也看不出来。然后对每个标注区间逐一检查：

1. **因果 mask**：`masked_fill` 必须在 softmax 之前，非法位置填 $-\infty$，不是 $0$。用 $0$ 去乘权重，softmax 仍会把注意力分给未来 token。
2. **softmax 轴**：必须沿 key 长度那一维。`dim=0` 或沿 head 维归一化，是公开复述里很常见的植入 bug。
3. **缩放**：$QK^\top/\sqrt{d_k}$。漏掉之后 fp16 很容易溢出，loss 变成 NaN。
4. **位置**：绝对位置编码在逐 token 生成（decode）时要用 `cache_len` 作 offset，不能每步都写位置 0。RoPE 同理，旋转用的是接在 cache 后面的绝对下标。
5. **训练对齐**：next-token 预测要把 target 移一位；不能先对 logits 做 softmax 再送进交叉熵损失（CE）。

shape 断言比读代码快：decode 时 `q` 是 `[B,H,1,D]`，`k` 是 `[B,H,S,D]`，`scores` 是 `[B,H,1,S]`。head 维和时间维互换是另一类高发 bug。完整的手写实现见 `code-attention`。

公开报告里的四个区间，大致落在位置编码、因果 mask、输出投影和训练循环这几类。不要把时间花在没有标注的「风格重构」上。

## 用同一前缀验证 KV cache

prefill 一次写下整段的 $K,V$。decode 时只算当前的 $q_t,k_t,v_t$，沿时间维接到 cache 后面，再用 $q_t$ 和所有历史 key 做点积。单步成本从 $O(t^2 d)$ 降到 $O(t d)$。张量步骤见 `code-kv-cache-step`，显存公式见 `arch-kv-cache`。

面试里要主动说出不变量：同一前缀、greedy 解码，有 cache 和没 cache 必须逐 token 相同。最常见的错误是位置：新 token 用 `cache_len`，不是 0。cache 非空且一次只 decode 1 个 token 时，没有「未来位置」需要 mask；chunked decode（一次多个新 token）仍要加一块相对 cache 的因果 mask。

cache 要贯穿每一层，不能只改最外层的 attention。GQA 时 cache 的 head 维是 $H_{\mathrm{kv}}$，不是 $H_q$，repeat 或广播发生在注意力计算内部。

先保证正确，再提 MQA/GQA、paged attention 和量化 cache。面试官追问优化时再讲带宽：decode 的瓶颈是读历史 KV，和训练时 $O(T^2)$ 的计算量不是一回事。

## 追问

**为什么 mask 不能用 0？**
$\mathrm{softmax}([s, 0])$ 仍会给未来位置正的权重。必须填 $-\infty$，softmax 之后才是 0。
**cache 显存怎么降？**
显存和 $H_{\mathrm{kv}}\cdot T\cdot d$ 成正比。可以用 GQA/MQA、量化、paged 共享，见 `arch-gqa`。
**投机解码（speculative decoding）和 cache 怎么配合？**
拒绝草稿 token 时，要把 cache 回滚到验证通过的前缀，不能只改输出文本。

## 相关题

- [[openai-kv-cache-impl]]：编程练习和本题一字不差，题面只问从零实现 KV cache。
- [[openai-rope-offset]]：编程练习也一字不差，专讲五类 bug 里的位置偏移。
- [[coding-rope-cache]]：RoPE 表和 `position_ids` 的单独白板题。
- [[openai-speculative-decoding]]：把追问里的投机解码回滚单独拿出来讲。
- [[p3a-openai-transformer-bug-hunt]]：同类 OpenAI 题的另一份整理，练习只缩到注意力函数，排查顺序多了 label shift 和小数据过拟合验证。
- [[openai-softmax-bug]]：编程练习也一字不差，专讲五类 bug 里的 softmax 轴和 mask 填 0。
