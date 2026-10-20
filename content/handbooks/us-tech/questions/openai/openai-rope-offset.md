---
id: openai-rope-offset
section: openai
order: 7
level: S
title: OpenAI：RoPE 在 decode 时位置偏移写错会 silently 错，怎么查
quick: "decode 时新 token 的 RoPE 位置必须从 `cache_len` 开始而不是 0；写错不报错，只能靠有/无 cache 的 greedy 输出对齐发现。"
tags:
  - 完整编程练习
  - OpenAI
  - RoPE
  - KV Cache
  - Debug
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: OpenAI Research Engineer Interview Guide
    url: https://www.tryexponent.com/guides/openai-research-engineer-interview-guide
    type: secondary
  - title: RoFormer — Enhanced Transformer with Rotary Position Embedding
    url: https://arxiv.org/abs/2104.09864
    type: primary
  - title: Attention Is All You Need
    url: https://arxiv.org/abs/1706.03762
    type: primary
---

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

## 题怎么来的

公开的 Transformer debug 轮会植入位置编码错误。加上 KV cache 之后，位置从「一整段 `[0..S)`」变成了「每步一个标量」。现在主流实现用 RoPE，不是原论文的正弦绝对位置，所以这里按 RoPE 讲逐 token 生成（decode）时的位置偏移。Exponent 上没有哪条报告单独写出「RoPE offset」，它是 `openai-kv-cache-impl` 里有/无 cache 对不齐时的第一嫌疑。

面试官喜欢这题，是因为它错得很安静：没有异常，shape 断言也能过，短 prompt 有时还看不出问题。

## 相对位置写错后，注意力会读取错误的位置关系

RoPE 把每一对维度旋转一个角度 $\theta_i m$，其中 $m$ 是 token 的位置。query 在位置 $m$、key 在位置 $n$ 时，两者的点积只依赖相对差 $m-n$。这是优点，也是 debug 的陷阱：如果给每个 decode token 都按位置 0 旋转，模型做的仍然是「合法的注意力」，只是每一步都以为自己站在句首。

典型错误写法和正确写法：

```python
# 错：q_len = 1 时 pos 永远是 [0]
pos = torch.arange(q.size(2), device=q.device)
q, k = apply_rope(q, k, cos[pos], sin[pos])

# 对：新 token 的绝对位置从 cache 长度开始
pos = torch.arange(cache_len, cache_len + q.size(2), device=q.device)
q, k = apply_rope(q, k, cos[pos], sin[pos])
```

prefill 一次旋转 `[0, S)` 没问题，问题从第二步开始。cache 里的 $K$ 已经按 $0..S-1$ 旋转过，不能再转一遍；新写入的 $k_t$ 只按 $t=S$ 旋转。如果对 cache 里的旧 $K$ 再做一次 RoPE，相对差会变成 $m-(n+\delta)$，整段历史的位置全部偏掉。

绝对位置编码也是一样的道理：decode 时查 embedding 表要用 `cache_len`，不能用 `pos_emb[0]`。

## 怎么查：先对齐，再查表

1. **greedy 对齐。** 同一份权重、同一个前缀，full forward 和 cached decode 必须逐 token 相同，这是总开关，见 `openai-kv-cache-impl`。对不上时不要先怀疑数值误差，先打印每一层的 `position_ids`。
2. **打印下标。** 第 $t$ 步 decode 时，`position_ids` 应该是 $t$，不是 0，也不是 `arange(1)`。cos/sin 表的长度要覆盖 `max_seq`；超长时要插值或报错，不能悄悄回绕。
3. **小矩阵探针。** 把 $q,k$ 固定成同一个向量，只改位置。RoPE 下 $m=n$（相对差为 0）时点积最大；如果每一步 decode 都表现得像相对差为 0，说明 offset 没加上。
4. **别只看 loss。** 训练时每步都是完整序列，RoPE 是对的；bug 只出现在推理的 cache 路径上。所以「训练 loss 正常，serving 一开 cache 就胡言乱语」正是这类 bug 的特征。

GQA 不改变位置逻辑：旋转的是每个 KV head 的 $D$ 维，head 数见 `meta-llama-gqa`。分块输入预填充（chunked prefill）时，一块新 token 内部仍用连续递增的绝对下标，并接在 `cache_len` 后面。

它和 softmax / mask 类 bug 的区别在于：那些 bug 会破坏归一化或泄漏未来位置，常常一个单测就能抓到，见 `openai-softmax-bug`。RoPE offset 写错时，注意力仍然是合法的概率分布，`attn.sum(-1) == 1` 照样成立，只能靠有 cache 和无 cache 两条路径的结果对齐来发现。

## 追问

- **为什么说它是 silent 的？** shape 合法，softmax 仍然归一，输出范数也正常。只有和不带 cache 的 teacher 路径对比才会暴露。
- **ALiBi 会不会同样出错？** 会。ALiBi 的偏置取决于距离；decode 时如果只按「当前块内的距离」算，就等于忽略了 cache 里已有的 $S$ 个 token。
- **投机解码拒绝草稿后，位置怎么回滚？** 把 cache 截到被接受的前缀，下一步的 offset 就是新的 `cache_len`，见 `openai-speculative-decoding`。
- **长上下文插值算不算 offset 问题？** 不算，那是 cos/sin 表怎么延拓的问题。先保证 $m=\mathrm{cache\_len}$，再谈 NTK / YaRN。

## 相关题

- [[openai-kv-cache-impl]]：编程练习和本题一字不差，问法是从零实现 KV cache 并对齐 greedy。
- [[openai-transformer-debug]]：编程练习也一字不差，问法是给一份带 bug 的 Transformer 先排查再加 cache。
- [[coding-rope-cache]]：只写 cos/sin 表和 `position_ids`，不碰注意力本身。
- [[openai-speculative-decoding]]：拒绝草稿后 cache 被截断，下一步的 offset 也要跟着回退。
- [[coding-decode-step]]：白板写一步 decode，第一行就是用 `cache_len` 做 RoPE，是这个 bug 的正确写法。
- [[coding-rope]]：白板写 RoPE 旋转，decode 的 position 取 cache 长度，是本题要查的那条不变量的正面写法。
