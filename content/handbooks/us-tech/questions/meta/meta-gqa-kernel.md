---
id: meta-gqa-kernel
section: meta
order: 20
level: A
title: Meta：GQA 实现——repeat KV、kernel 融合，别只背论文配置
quick: "Cache 只存 $H_{\\mathrm{kv}}$ 组 KV，kernel 里按 `h_q // g` 取对应的 KV head；在 HBM 里先 repeat 成 $H_q$ 份，会把省下的带宽又花回去。"
tags:
  - 完整编程练习
  - Meta
  - Llama
  - GQA
  - Kernel
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: Llama 2 — Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
  - title: GQA — Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints
    url: https://arxiv.org/abs/2305.13245
    type: primary
  - title: FlashAttention-2
    url: https://arxiv.org/abs/2307.08691
    type: primary
  - title: PyTorch scaled_dot_product_attention GQA
    url: https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html
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

`meta-llama-gqa` 问的是 Llama 2 70B 为什么用 $32$ 个 query head、$8$ 个 KV head。本题问的是实现：repeat 发生在哪一步，cache 里存几组，kernel 融合了什么。Llama 和推理岗的白板常要求画出 shape，只背一句「GQA 是 4:1」过不了。选型上的公式对比可以看 `google-gqa-mqa`。

## Shape 和 repeat 发生在哪

Llama 2 70B 的配置是 $H_q=32$，$H_{\mathrm{kv}}=8$，每组 $g=H_q/H_{\mathrm{kv}}=4$ 个 query head，$d=256$。投影之后：

- $Q$：$[B, H_q, S_q, d]$
- $K,V$：$[B, H_{\mathrm{kv}}, S_{kv}, d]$

参考写法（Meta 早期 `llama` 仓库里的 `repeat_kv`）沿 head 维把 KV 重复 $g$ 次，得到 $[B, H_q, S_{kv}, d]$，然后按普通 MHA 计算。数学上就是每组 $4$ 个 query 共用同一份 K/V。

**Cache 里必须仍然只存 $H_{\mathrm{kv}}$ 组。** decode 每一步写入 $8$ 组，不是 $32$ 组。如果把 repeat 之后的张量写进 cache，显存和读带宽都回到了 MHA 的水平，GQA 就白做了。正确的顺序是：从 cache 读出 $[B, 8, S, d]$，计算时在逻辑上 repeat（或在 kernel 里按下标去取），输出 $[B, 32, 1, d]$。

```python
def repeat_kv(x, n_rep):
    """[B, H_kv, S, D] -> [B, H_kv * n_rep, S, D]，每个 KV head 连续重复 n_rep 次。"""
    if n_rep == 1:
        return x
    batch, kv_heads, seq_len, head_dim = x.shape
    x = x[:, :, None, :, :].expand(batch, kv_heads, n_rep, seq_len, head_dim)
    return x.reshape(batch, kv_heads * n_rep, seq_len, head_dim)
```

`expand` 本身不分配新内存，但如果后面的 kernel 要求 contiguous，`reshape` 仍可能把它物化成 $4$ 倍大小。这就是「naive GQA」在逐 token 生成（decode）时省不了带宽的原因。

## Kernel 融合：别把 KV 在 HBM 里摊开

FlashAttention 和 PyTorch SDPA 的 GQA 路径**不会物化 repeat**。线程块按 query head 调度，用整数除法 `h_kv = h_q // g` 找到对应的 KV head。同一组的 $4$ 个 query head 共用 SRAM 里同一份 K/V tile，I/O 从「读 $32$ 份 KV」降到「读 $8$ 份，在 SRAM 里复用」。decode 实际变快，靠的就是这一点。

PyTorch 里是 `scaled_dot_product_attention(..., enable_gqa=True)`，要求 $H_q$ 能被 $H_{\mathrm{kv}}$ 整除。math 后端仍可能调用 `repeat_interleave`，flash / mem-efficient 后端才走下标索引。面试时要讲清楚：**API 打开了 GQA，不代表底层没有 repeat**，要看实际选中的 backend。如果用 `TORCH_LOGS=kernel` 或 profiler 看到先有一个很大的 `repeat_interleave`、后面才是 attention，就说明走了慢路径。

prefill 和 decode 的成本结构不一样。prefill 是大 GEMM / FlashAttention，受算力限制，GQA 主要省的是写入 KV 的体积。decode 时 $S_q=1$，几乎没有大 GEMM，时间都花在读历史 KV 上，naive repeat 在这里最吃亏。长上下文（如 Llama 3.1 的 128k）把 $S_{kv}$ 拉大，融合路径的相对收益也更大。再往下是 KV 量化和 paging，见 `sys-kv-quant`、`sys-paged-attn`。

RoPE 只作用在 $Q,K$ 上，而且要在 repeat **之前**、按 $H_{\mathrm{kv}}$ 份去转 K。先 repeat 再转，会把同样的旋转重复做 $4$ 遍。位置下标仍然从 cache 长度开始，见 `meta-llama-rope`。

## 训练侧别踩的坑

Llama 2/3 **训练时就是 GQA**，K/V 投影直接输出 $H_{\mathrm{kv}}$ 组。不要先训成 MHA，再在推理时 repeat；从 MHA checkpoint 转成 GQA 是 GQA 论文里的 upcycle 做法，会带来转换误差。训练时的输入预填充（prefill，即处理整段输入并建立缓存）直接用融合 kernel 即可，没必要为了「和 decode 一致」去物化 repeat。

`torch.compile` 可能把 `expand + reshape` 融合掉，也可能在 graph break 之后留下一次拷贝。和 FSDP 的情况一样，要看 break 日志下结论，见 `meta-pytorch-compile`，不要断言 compile 之后 naive repeat 就没有成本。

## 追问

- **$g$ 必须是 $4$ 吗？** 只要求能整除。$32/8=4$ 是 Llama 2 70B 的选择，不是规律。Llama 3 8B 也是 GQA，head 数要看具体配置，不要背成所有尺寸都是 $32/8$。
- **MQA 就是 $H_{\mathrm{kv}}=1$，kernel 会更简单吗？** 索引更简单，但质量更脆弱。70B 对话模型对质量敏感，所以 Meta 停在了 GQA。在 kernel 里，MQA 只是 $g=H_q$ 的 GQA 特例。
- **能不能在 batch 维 repeat？** 不能。要重复的是 head，不是 batch。在 batch 维扩 KV 会把不同请求的 cache 混在一起。
- **和张量并行（TP）一起时怎么切？** query head 按 TP 切分，每张卡上的 $H_q$ 仍要能被本卡的 $H_{\mathrm{kv}}$ 整除。如果切得让一个 GQA 组跨了卡，还得额外为 KV 通信，见 `sys-3d-parallel`。

## 相关题

- [[coding-gqa-repeat]]：白板版，只写 `repeat_interleave` 和 shape 断言，不讲 kernel 里怎么免掉 repeat。
- [[meta-llama-gqa]]：同为 Meta 问法，口述 70B 为什么选 32/8、decode 省在哪，这张接着问实现。
- [[coding-mq-attn]]：MQA 是这里 $g=H_q$ 的特例，那张讲单 KV head 怎么 broadcast。
- [[coding-decode-step]]：把 GQA 放进完整的一步 decode，cache 按 $H_{\mathrm{kv}}$ 存，只在算分数时扩展。
