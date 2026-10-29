---
id: meta-gqa-kernel
section: meta
order: 20
level: A
title: Meta：GQA 实现——repeat KV、kernel 融合，别只背论文配置
quick: >-
  GQA 的 cache 只保存 $H_{\mathrm{kv}}$ 组，query head 用 `h_q // g` 找到共享 KV。先用基准实现验证
  mask、RoPE 和 cache，再检查实际 GPU 后端：若在 HBM 里物化成 $H_q$ 份，就会多花原本要节省的带宽。
tags:
  - 完整编程练习
  - Meta
  - Llama
  - GQA
  - Kernel
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18T00:00:00.000Z
sources:
  - title: Llama 2 — Open Foundation and Fine-Tuned Chat Models
    url: 'https://arxiv.org/abs/2307.09288'
    type: primary
  - title: >-
      GQA — Training Generalized Multi-Query Transformer Models from Multi-Head
      Checkpoints
    url: 'https://arxiv.org/abs/2305.13245'
    type: primary
  - title: FlashAttention-2
    url: 'https://arxiv.org/abs/2307.08691'
    type: primary
  - title: PyTorch scaled_dot_product_attention GQA
    url: >-
      https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html
    type: primary
---

## 题目描述

用 NumPy 实现支持 GQA、可选 RoPE 和增量 KV cache 的因果 multi-head attention，使整段计算与带 cache 的逐 token 计算结果一致。

以下为手册重构练习约定。默认输入满足列出的合法约束，不要求额外的非法输入校验。

### 接口、输入与输出

- `mha(x,wq,wk,wv,wo,heads,kv_heads=None,cache=None,key_valid=None,use_rope=False)` 返回 (output,`new_cache`)，output 为 [B,T,D]；x 为 [B,T,D]，wq/wo 为 [D,D]，wk/wv 为 [D,Hkv*d]，d=D/heads，Hkv 默认 heads。D % heads = 0，heads % Hkv = 0。
- Q/K/V 的投影定义为 x@wq、x@wk、x@wv，无 bias。Q 有 heads 个头，K/V 有 Hkv 个头；query head h 使用 KV head floor(h/(heads/Hkv))。每个 query 输出为 softmax(QKᵀ/sqrt(d)) 对 V 的加权和，按 head 编号拼接后右乘 wo。
- cache 为 (K,V)，各为 [B,Hkv,prefix,d]，None 表示 prefix=0；新 cache 长度 prefix+T，仍只存紧凑 KV heads，不修改旧 cache。
- query t 的绝对位置为 prefix+t，只允许绝对 key 位置<=它自身；`key_valid` 为 [B,prefix+T] bool，True 可见，None 表示无额外屏蔽。没有可见 key 时该 query 的输出为0。
- `rope(x,start)` 对 [B,H,T,d] 相邻二元组旋转，theta[t,j]=(start+t)*10000**(-2*j/d)，(a,b) 变为 (a*cos-b*sin,a*sin+b*cos)。`use_rope`=True 时 d 为偶数，仅旋转新 Q/K，旧缓存 K 已经旋转，V 不旋转。
- 输入有限，1<=B<=8、1<=T<=256、D<=128，无 dropout。整段前向与按 token 调用并携带 cache 的输出应一致。

### 输入输出示例

```text
单 head，wq = wk = 0（所以 Q = K = 0），wv = wo = I，x = [[2, 4], [6, 8]]
query 0 只能看 key 0             -> [2, 4]
query 1 对 key 0、1 均匀平均      -> [4, 6]

任意固定权重下：
mha(完整序列) == 逐 token 带 cache 调用 mha，再沿时间维拼接
```

## 解题思路与参考答案

GQA 的实现要让 cache 只保存紧凑的 KV head，并让 query head 在计算时找到所属的 KV 组。下面先用 NumPy 写一个能验证 cache、RoPE 和 mask 的正确性基准，再讨论 GPU kernel 怎样避免真正复制 KV。

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。只用 NumPy，CPU 上验证。

### 题面、接口与约束

- `mha(x, wq, wk, wv, wo, heads, kv_heads=None, cache=None, key_valid=None, use_rope=False)`：用 NumPy 写因果 multi-head attention，返回 `(output, new_cache)`。依次做 Q/K/V 投影、缩放点积、因果 mask、数值稳定的 softmax、合并 heads 和输出投影。
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

我会先投影并拆出 Q/K/V 多头，再按当前 token 的绝对位置旋转 Q 和新 K。旧 K 已经在缓存前做过 RoPE，保持不动，只将新 K/V 追加到 cache。

因果 mask 用绝对位置比较：当前段第 `i` 个 query 在 `prefix + i`，只允许读取 `j ≤ prefix + i`。这样 prefill 的 `prefix = 0`、单 token decode、分块 decode 共用一套判断，结果才能与整段计算对齐。

Softmax 沿 key 维 normalization，先减行最大值来避免 `exp` 溢出。若这一行全被 mask，最大值为 `-inf`，先换成 0，再按零分母的约定输出 0，避免 NaN。

GQA 用 `group = heads / Hkv` 将 query 分组，head `h` 对应 KV head `h // group`。NumPy 基准为了直观用 `np.repeat` 展开参与计算，但返回 cache 仍只有 `Hkv` 份，后面融合路径要保留这个紧凑布局。

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

例如，测试中的 `assert np.allclose(full, np.concatenate(pieces, axis=1))` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

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

## 从基准到融合 kernel

`meta-llama-gqa` 讨论 Llama 2 70B 的 $32$ query head、$8$ KV head 选择，这里将它落实为 shape、cache 与内存访问。选型公式也可对照 `google-gqa-mqa`，练习不是原帖完整 Transformer 源码。

### 先对齐 shape

按这张卡的 Llama 2 70B 配置，$H_q=32$、$H_{\mathrm{kv}}=8$、每组 $g=H_q/H_{\mathrm{kv}}=4$，$d=256$，投影后的形状为：

- $Q$：$[B, H_q, S_q, d]$
- $K,V$：$[B, H_{\mathrm{kv}}, S_{kv}, d]$

Meta 早期 `llama` 的 `repeat_kv` 沿 head 维将 KV 重复 $g$ 次，形成 $[B, H_q, S_{kv}, d]$，即可按 MHA 算。每组 $4$ 个 query 虽有各自 Q，读的 K/V 相同。

Cache 始终保存 $H_{\mathrm{kv}}$ 组，decode 每步只写 $8$ 组。若缓存展开后的 $32$ 组，就回到 MHA 的空间和读取量。正确路径先读取 $[B, 8, S, d]$，计算时逻辑展开或按下标读取，最后输出 $[B, 32, 1, d]$。

```python
def repeat_kv(x, n_rep):
    """[B, H_kv, S, D] -> [B, H_kv * n_rep, S, D]，每个 KV head 连续重复 n_rep 次。"""
    if n_rep == 1:
        return x
    batch, kv_heads, seq_len, head_dim = x.shape
    x = x[:, :, None, :, :].expand(batch, kv_heads, n_rep, seq_len, head_dim)
    return x.reshape(batch, kv_heads * n_rep, seq_len, head_dim)
```

`expand` 只是视图，不过下游 kernel 若要求 contiguous，随后的 `reshape` 可能真的生成 $4$ 倍张量。这样即使 cache 紧凑，decode 计算仍额外花了展开与读取的带宽。

### 检查实际后端是否复制

融合 GQA 路径可以直接按 query head 调度，用 `h_kv = h_q // g` 索引 KV，无需在 HBM 展开。组内 $4$ 个 query 共用 SRAM 中的 K/V tile，将读取从 $32$ 份降到 $8$ 份并在片上复用，这是 decode 节省 I/O 的来源。

PyTorch 的 `scaled_dot_product_attention(..., enable_gqa=True)` 要求 $H_q$ 能被 $H_{\mathrm{kv}}$ 整除，还需确认选中的 backend：math 后端可能调用 `repeat_interleave`，flash / mem-efficient 路径才用索引。可用 `TORCH_LOGS=kernel` 或 profiler 检查，若 attention 前还有大型 `repeat_interleave`，就没有避开展开成本。

Prefill 的大 GEMM / FlashAttention 更受算力限制，GQA 主要减少 KV 写入；decode 的 $S_q=1$，读取历史 KV 更关键，展开会尤其浪费。Llama 3.1 的 128k 等长上下文使 $S_{kv}$ 增大，更值得核对融合路径，再考虑 KV 量化与 paging，见 `sys-kv-quant`、`sys-paged-attn`。

RoPE 只转 $Q,K$，K 在 repeat 前按 $H_{\mathrm{kv}}$ 组转即可，展开后再转会重复 $4$ 遍。新位置从 cache 长度开始编号，见 `meta-llama-rope`。

### 训练与推理保持同一布局

Llama 2/3 训练时就让 K/V 投影输出 $H_{\mathrm{kv}}$ 组。MHA checkpoint 转 GQA 则是论文里的 upcycle 路径，有转换误差需要评估。训练处理整段输入时可直接用融合 kernel，不必为了对齐 decode 而显式展开。

`torch.compile` 有时能融合 `expand + reshape`，graph break 后也可能留下一次复制。要结合 break 日志和 profiler 验证，见 `meta-pytorch-compile`，不能仅凭打开 compile 就认定没有成本。

## 追问

**$g$ 必须是 $4$ 吗？**
只要求能整除。$32/8=4$ 是 Llama 2 70B 的选择，不是规律。Llama 3 8B 也是 GQA，head 数要看具体配置，不要背成所有尺寸都是 $32/8$。
**MQA 就是 $H_{\mathrm{kv}}=1$，kernel 会更简单吗？**
索引更简单，但质量更脆弱。70B 对话模型对质量敏感，所以 Meta 停在了 GQA。在 kernel 里，MQA 只是 $g=H_q$ 的 GQA 特例。
**能不能在 batch 维 repeat？**
不能。要重复的是 head，不是 batch。在 batch 维扩 KV 会把不同请求的 cache 混在一起。
**和张量并行（TP）一起时怎么切？**
query head 按 TP 切分，每张卡上的 $H_q$ 仍要能被本卡的 $H_{\mathrm{kv}}$ 整除。如果切得让一个 GQA 组跨了卡，还得额外为 KV 通信，见 `sys-3d-parallel`。

## 相关题

- [[coding-gqa-repeat]]：白板版，只写 `repeat_interleave` 和 shape 断言，不讲 kernel 里怎么免掉 repeat。
- [[meta-llama-gqa]]：同为 Meta 问法，口述 70B 为什么选 32/8、decode 省在哪，这张接着问实现。
- [[coding-mq-attn]]：MQA 是这里 $g=H_q$ 的特例，那张讲单 KV head 怎么 broadcast。
- [[coding-decode-step]]：把 GQA 放进完整的一步 decode，cache 按 $H_{\mathrm{kv}}$ 存，只在算分数时扩展。
