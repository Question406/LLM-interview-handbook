---
id: openai-softmax-bug
section: openai
order: 6
level: S
title: OpenAI：attention 里 softmax 轴和 mask 用 0 会怎样，怎么单测
quick: "softmax 要沿 key 维（`dim=-1`）归一，因果 mask 要在 softmax 前填 $-\\infty$；乘 0 的 mask 会让未来 token 分到 $e^0=1$ 的权重。"
tags:
  - 完整编程练习
  - OpenAI
  - Attention
  - Softmax
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

## 真题记录

- 公司：OpenAI
- 岗位：Research Engineer / MLE
- 轮次：给一份带 bug 的 Transformer。公开复述里，softmax 的维度和因果 mask 是高频的植入点。
- 来源：Exponent 2025 报告；整体查法见 `openai-transformer-debug`。

这类 bug 不会产生 NaN，生成的文字也「看起来像语言」，所以没法靠 loss 曲线找。更可靠的做法是用 shape 和一块小矩阵把错误固定下来。

## 题怎么来的

Attention 论文写的是 $\mathrm{softmax}(QK^\top / \sqrt{d_k})$。落到四维张量上之后，softmax 的 `dim` 和 mask 的填充值都有好几种「能跑」的写法。OpenAI 这一轮要你说明哪一种在数学上才是注意力。和 `openai-entropy-l1` 一样，先确保得到的是合法分布，再谈数值问题。

## 两种错法，两种失败模式

scores 的形状是 `[B, H, T, S]`，$T$ 是 query 长度，$S$ 是 key 长度。

**轴错了。** `softmax(scores, dim=0)` 或 `dim=1` 是在 batch 或 head 上归一化。结果是每个 query 对所有 key 的权重和不等于 1，不同样本的概率质量还会混在一起。短序列偶尔能通过肉眼检查，一上 batch 就乱。正确写法是 `dim=-1`（或 `dim=3`），要满足的不变量是：

$$
\sum_{s=1}^{S} a_{bhts} = 1.
$$

**mask 用 0。** 有人写 `scores = scores * causal`，把未来位置的分数变成 0。但 softmax 里 $e^{0}=1$，未来位置仍然分到一块正的概率；没被遮住的 logit 越接近 0，泄漏越大。正确做法是在 softmax 之前 `masked_fill(..., -inf)`，这样 $e^{-\infty}=0$。加法 mask 用 $-1\mathrm{e}9$ 在 fp16 里可能溢出，也可能不够负，所以优先用真正的 $-\infty$；softmax 内部会先减最大值，结果仍然稳定。

第三类是漏掉缩放 $1/\sqrt{d_k}$：fp16 下点积的方差随 $d_k$ 增大，softmax 会饱和成 one-hot，甚至直接出现 inf。它要和轴、mask 分开测。

## 最小单测

下面两个测试分别固定 mask 和轴的错误：

```python
def test_causal_mask_zero_leaks():
    scores = torch.tensor([[[[2.0, 1.0, 0.5]]]])  # [1, 1, 1, 3]
    future = torch.tensor([[[[False, False, True]]]])

    # 乘 0 的 mask：未来位置仍然分到正概率
    bad = torch.softmax(scores * (~future).float(), dim=-1)
    assert bad[0, 0, 0, 2] > 0

    # softmax 前填 -inf：未来位置概率精确为 0，每行和为 1
    good = torch.softmax(scores.masked_fill(future, float("-inf")), dim=-1)
    assert good[0, 0, 0, 2].item() == 0.0
    assert torch.allclose(good.sum(dim=-1), torch.ones(1, 1, 1))


def test_softmax_axis():
    scores = torch.randn(2, 4, 3, 5)
    attn = torch.softmax(scores, dim=-1)
    assert attn.shape == scores.shape
    assert torch.allclose(attn.sum(dim=-1), torch.ones(2, 4, 3), atol=1e-5)
```

还可以加一条序列级的测试：`T=4` 的下三角 mask，位置 $t$ 只能看到 $s\le t$，把未来位置的注意力取出来，应该全为 0。更强的端到端检查是 greedy 下有/无 cache 对齐，见 `openai-kv-cache-impl`。

先 `eval()` 并固定 seed，再写断言。不要把「生成结果看起来是对的」当成测试。

## 追问

- **padding mask 和因果 mask 谁先？** 都放在 softmax 之前，两者取逻辑或之后一次性填充。padding 的 key 也必须是 $-\infty$，否则短序列会去看 pad。
- **为什么要减 max？** 防止 `exp` 溢出。轴要对：`max` 沿 key 维取，`keepdims=True`，不要对整个 batch 减同一个标量。
- **逐 token 生成（decode）一步还要 mask 吗？** 单个 token 且 cache 已是合法前缀时，通常不需要。一次送入多个新 token 时，仍然要加相对 cache 的因果块。

## 相关题

- [[apple-mha-code]]：编程练习和本题是同一份 MHA 实现与测试；Apple 那题从零写起，重点在 shape、拆 head 和 GQA，本题重点在找 bug。
- [[coding-attn-mask]]：mask 怎么正确构造，因果、padding、文档边界三个条件合成一张 bias。
- [[coding-swa-mask]]：滑动窗口 mask 同样要求窗口外填 $-\infty$，并区分 prefill 和 decode 的 bias 形状。
- [[apple-ondevice-quant]]：本题说「优先用真正的 $-\infty$」，但端侧量化图里反而要换成 fp16 大负数，可以对照看。
- [[openai-transformer-debug]]：编程练习和本题一字不差，题面是整份 Transformer 按五类查 bug 再加 KV cache，softmax 和 mask 只是其中两类。
- [[coding-softmax-stable]]：白板题，单独讲 softmax 减 max 和「沿谁和谁比概率的那一维」选轴。
