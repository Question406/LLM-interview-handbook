---
id: coding-rope
section: coding
order: 6
level: A
title: 白板：RoPE 对 q/k 旋转，偶数维成对，decode 的 position
quick: "把 q、k 的偶奇相邻两维当成复数，按位置 $t$ 旋转 $t\\theta_i$；v 不转；decode 时 $t$ 是 cache 长度，不是 0。"
tags:
  - 完整编程练习
  - Coding
  - RoPE
  - Llama
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
sources:
  - title: RoFormer — Enhanced Transformer with Rotary Position Embedding
    url: https://arxiv.org/abs/2104.09864
    type: primary
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
---

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，CPU 上验证。

### 题面、接口与约束

- `rope_angles(dim, seqlen, base=10000.0) -> (cos, sin)`：预计算角度表，`cos`、`sin` 形状都是 `[T, dim/2]`。`dim` 必须是正偶数。
- `apply_rope(x, cos, sin)`：`x` 形状 `[B, H, T, D]`，按偶数维和奇数维相邻成对旋转，`cos`、`sin` 是这 `T` 个位置对应的 `[T, D/2]`。
- `decode_rope(q, k, cos, sin, pos)`：decode 一步，`q`、`k` 形状 `[B, H, 1, D]`，`pos` 等于已有 cache 长度，必须落在角度表范围内，否则抛 `ValueError`。

### 输入输出示例

```text
位置 0：cos = 1, sin = 0，apply_rope 是恒等变换
完整序列第 3 个 token（下标 2）的结果 == decode_rope(..., pos=2) 的结果
decode_rope(..., pos=8)，表长只有 8 -> ValueError
```

### 解题思路与正确性

第 $i$ 对维度 $(x_{2i}, x_{2i+1})$ 用同一个角度 $t\theta_i$ 做二维旋转。旋转是正交变换，所以每个向量的范数不变，位置 0 处是恒等变换。

decode 时新 token 的绝对位置从 cache 长度开始计，所以要从角度表里取第 `pos` 行，而不是第 0 行。这样逐 token 生成的结果和一次性算完整序列的结果一致，测试直接比较这两条路径。

### 完整参考实现（Python 3）

```python
import torch


def rope_angles(dim, seqlen, base=10000.0, device=None):
    """返回 cos, sin，形状 [seqlen, dim/2]；第 i 对维度的频率是 base^(-2i/dim)。"""
    if dim <= 0 or dim % 2 != 0:
        raise ValueError(f"RoPE needs a positive even head dim, got {dim}")
    inv_freq = 1.0 / (base ** (torch.arange(0, dim, 2, device=device).float() / dim))
    positions = torch.arange(seqlen, device=device).float()
    freqs = torch.outer(positions, inv_freq)  # [T, D/2]
    return torch.cos(freqs), torch.sin(freqs)


def apply_rope(x, cos, sin):
    """x: [B, H, T, D]；cos, sin: [T, D/2]。偶奇相邻两维成对旋转。"""
    x_even = x[..., 0::2]
    x_odd = x[..., 1::2]
    cos = cos[None, None, :, :]
    sin = sin[None, None, :, :]
    y_even = x_even * cos - x_odd * sin
    y_odd = x_even * sin + x_odd * cos
    return torch.stack((y_even, y_odd), dim=-1).flatten(-2)


def decode_rope(q, k, cos, sin, pos):
    """decode 一步：pos 是已有 cache 长度，取这一行的 cos/sin 旋转 q、k（不要用 0）。"""
    if not 0 <= pos < cos.shape[0]:
        raise ValueError(f"position {pos} is outside the RoPE table of length {cos.shape[0]}")
    cos_t = cos[pos:pos + 1]
    sin_t = sin[pos:pos + 1]
    return apply_rope(q, cos_t, sin_t), apply_rope(k, cos_t, sin_t)
```

### 可执行测试

```python
torch.set_num_threads(1)
torch.manual_seed(0)


def expect_value_error(fn, *args):
    try:
        fn(*args)
    except ValueError:
        return
    raise AssertionError(f"expected ValueError from {fn.__name__}")


cos, sin = rope_angles(4, 8)
x = torch.randn(2, 3, 5, 4)
y = apply_rope(x, cos[:5], sin[:5])

# 位置 0 是恒等变换
assert torch.allclose(y[..., 0, :], x[..., 0, :])

# 旋转不改变范数
assert torch.allclose(y.square().sum(-1), x.square().sum(-1), atol=1e-6)

# decode 用 pos = 2 和完整序列的第 3 个位置一致
q_t, k_t = decode_rope(x[:, :, 2:3], x[:, :, 2:3], cos, sin, 2)
assert torch.allclose(q_t, y[:, :, 2:3])
assert torch.allclose(q_t, k_t)

# 点积只依赖相对位置：(m, n) = (3, 1) 和 (4, 2) 的结果相同
q_vec = torch.randn(1, 1, 1, 4).expand(1, 1, 5, 4)
k_vec = torch.randn(1, 1, 1, 4).expand(1, 1, 5, 4)
q_rot = apply_rope(q_vec, cos[:5], sin[:5])
k_rot = apply_rope(k_vec, cos[:5], sin[:5])
dot = lambda m, n: (q_rot[0, 0, m] * k_rot[0, 0, n]).sum()
assert torch.allclose(dot(3, 1), dot(4, 2), atol=1e-5)

# 奇数维和越界位置被拒绝
expect_value_error(rope_angles, 3, 8)
expect_value_error(decode_rope, x[:, :, :1], x[:, :, :1], cos, sin, 8)
```

### 复杂度与追问

设 batch 为 $B$、head 数 $H$、序列长 $T$、头维 $D$。旋转的时间是 $O(BHTD)$，角度表占 $O(TD)$。

- 追问「旧版的 decode 有什么隐患」：如果不检查 `pos`，越界时 `cos[pos:pos+1]` 是空切片，广播后会悄悄返回空张量，不报错。

## 题怎么来的

Su et al. 提出的 RoPE 是 Llama / Qwen / GPT-NeoX 的默认位置编码。Meta 问 GQA 时常顺带问 RoPE；OpenAI 的 Transformer debug 题会把逐 token 生成（decode）的位置写成 0，导致有 cache 和没 cache 的结果对不上。Apple 手写 MHA 的追问也常是“位置怎么加”。注意力的 shape 见 `apple-mha-code`，位置偏移的 bug 见 `openai-transformer-debug`。

## 偶数维成对旋转

头维 $d$ 必须是偶数。第 $i$ 对 $(x_{2i},x_{2i+1})$ 看成一个复数，在位置 $t$ 上旋转角度 $t\theta_i$，其中 $\theta_i=10000^{-2i/d}$：

$$
\begin{bmatrix} y_{2i}\\ y_{2i+1} \end{bmatrix}
=
\begin{bmatrix} \cos(t\theta_i) & -\sin(t\theta_i)\\ \sin(t\theta_i) & \cos(t\theta_i) \end{bmatrix}
\begin{bmatrix} x_{2i}\\ x_{2i+1} \end{bmatrix}.
$$

旋转后的点积 $q_m^\top k_n$ 只依赖 $m-n$，这就是 RoPE 编码相对位置的方式。只对 $q,k$ 做旋转，$v$ 不转。cos/sin 按位置预计算，再广播到 `[B, H, T, d/2]`。

另一种常见写法是 `rotate_half`：把前 $d/2$ 维和后 $d/2$ 维配对（Llama / GPT-NeoX 的实现）。它和论文里偶奇成对的排布不同，加载 checkpoint 时必须用训练时的同一套。白板上先写偶奇成对，再补一句“读权重前要确认实现方式”。

## Decode：position 是 cache 长度

prefill 阶段位置是 $0..T-1$，整段 $K$ 旋转后写入 cache。decode 时新 token 的位置是 `cache_len`，只旋转当前的 $q_t, k_t$；历史 $K$ 已经旋转过，不要每步重做。packed 样本或 left padding 时，必须用真实的 `position_ids` 去索引 cos/sin，不能假设位置就是 `arange(T)`。

要保持的不变量：同一个前缀做 greedy 生成，用 KV cache 和每步重算完整 attention，逐 token 结果相同。位置写成 0 不会报错，只会悄悄算错。GQA 时 RoPE 仍然按头维旋转，和 $H_{\mathrm{kv}}$ 无关，见 `meta-llama-gqa`。

## 追问

- **为什么不旋转 $v$？** 相对位置信息要进入注意力权重，而不是被加权的值。旋转 $v$ 会把位置混进内容向量里，破坏两者的解耦。
- **长上下文怎么外推？** 改 $\theta$ 的 base（NTK）、YaRN，或者位置插值。面试时要说清：这些方法改的是旋转频率，不是重新训练一套绝对位置 embedding。
- **头维是奇数会怎样？** 奇数维没法两两配对旋转。实现里要检查 `dim % 2 == 0`。

## 相关题

- [[coding-rope-cache]]：同一个 RoPE，重点换成预计算 cos/sin 表、用 `position_ids` 查表，还覆盖 packed 和越界。
- [[openai-rope-offset]]：decode 位置写成 0 不会报错，那张卡讲怎么用有 / 无 cache 的输出对齐把它查出来。
- [[coding-qk-norm]]：RoPE 之前先对 $q,k$ 做 RMSNorm，顺序不能反。
- [[coding-alibi]]：另一种位置编码，直接在 scores 上加线性偏置，decode 时同样用 cache 长度当 query 位置。
- [[meta-llama-rope]]：口述 RoPE 的相对位置性质和长上下文外推，不写代码。
