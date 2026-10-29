---
id: coding-rope
section: coding
order: 6
level: A
title: 白板：RoPE 对 q/k 旋转，偶数维成对，decode 的 position
quick: >-
  把 q、k 的偶奇相邻两维成对，按位置 $t$ 旋转 $t\theta_i$，让点积带上相对位置信息；v 保持不变。Decode 的 $t$ 是已有
  cache 长度，历史 K 不再旋转；加载 checkpoint 时还要确认偶奇配对还是 half-rotate 布局。
tags:
  - 完整编程练习
  - Coding
  - RoPE
  - Llama
  - Meta
  - 题面补全 2026-10-27
realInterview: false
status: published
format: markdown
updatedAt: '2026-10-27'
sources:
  - title: RoFormer — Enhanced Transformer with Rotary Position Embedding
    url: 'https://arxiv.org/abs/2104.09864'
    type: primary
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: 'https://arxiv.org/abs/2307.09288'
    type: primary
---

## 题目描述

实现使用相邻维度配对的 RoPE，支持完整序列与带缓存的单 token decoding。

以下 interface 与 edge-case behavior 是本手册重构练习的约定。假定输入满足所述合法范围。

### 接口、输入与输出要求

`rope_angles(dim,seqlen,base=10000.0,device=None)` 返回 `[seqlen,dim/2]` 的 cos、sin 表。dim 为正偶数；第 i 对维度的频率为 `base^(-2*i/dim)`，位置 t 的旋转角为 t 乘该频率。

`apply_rope(x,cos,sin)` 输入 x `[B,H,T,D]`，每对相邻分量 `(a,b)` 按 `(a*cos-b*sin,a*sin+b*cos)` 旋转，返回同形张量。

`decode_rope(q,k,cos,sin,pos)` 输入 q、k `[B,H,1,D]`，pos 是合法的绝对位置，也是此前缓存长度；使用表中该位置旋转，返回 `(rotated_q,rotated_k)`。

### 示例

```text
x=[[[[1,2,3,4]]]]。
cos=[[1,1]], sin=[[0,0]] 时 apply_rope 返回原 x。
cos=[[0,0]], sin=[[1,1]] 时返回 [[[[-2,1,-4,3]]]]。
rope_angles(dim=4,seqlen=1) 的第 0 行 cos=[1,1], sin=[0,0]。
```

## 解题思路与参考答案

我会先按位置生成 cos/sin，把 q、k 的相邻偶奇维拆成两半，分别做二维旋转，再交错拼回原形状。位置 0 应保持原向量，旋转后范数也应不变；decode 用 cache 长度查角度表，这样才能和完整前向对齐。


## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定。Python 3 + PyTorch，CPU 上验证。

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
        raise ValueError(
            f"position {pos} is outside the RoPE table of length {cos.shape[0]}"
        )
    cos_t = cos[pos : pos + 1]
    sin_t = sin[pos : pos + 1]
    return apply_rope(q, cos_t, sin_t), apply_rope(k, cos_t, sin_t)
```

### 简单测试怎么写

把完整参考实现和题中的可执行测试按顺序放进 `solution.py`，运行 `python3 solution.py`。测试依赖的库与参考实现相同。

例如，测试中的 `assert torch.allclose(y[..., 0, :], x[..., 0, :])` 就是一条结果检查；连同它前面的输入准备一起运行，不能只复制断言这一行。

数值结果用 `allclose` 一类带容差的断言检查，并同时确认形状；随机输入固定种子。手算预期值或选独立的参考公式，避免把待测实现再抄一遍当答案。

先确认一个小场景的预期值，再运行题中的完整测试；出现断言失败时，从第一条失败的检查定位。断言全部通过只说明已覆盖的场景通过，还需要按本题约束补充 edge-case tests。

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

Su et al. 提出的 RoPE 是 Llama / Qwen / GPT-NeoX 的默认位置编码。Meta 问 GQA 时常顺带问 RoPE；OpenAI 的 Transformer debug 题会把逐 token 生成（decode）的位置写成 0，导致有 cache 和没 cache 的结果对不上。Apple 手写 MHA 的追问也常是“位置怎么加”。attention 的 shape 见 `apple-mha-code`，位置偏移的 bug 见 `openai-transformer-debug`。

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

**为什么不旋转 $v$？**
相对位置信息要进入 attention 权重，而不是被加权的值。旋转 $v$ 会把位置混进内容向量里，破坏两者的解耦。
**长上下文怎么外推？**
改 $\theta$ 的 base（NTK）、YaRN，或者位置插值。面试时要说清：这些方法改的是旋转频率，不是重新训练一套绝对位置 embedding。
**头维是奇数会怎样？**
奇数维没法两两配对旋转。实现里要检查 `dim % 2 == 0`。

## 相关题

- [[coding-rope-cache]]：同一个 RoPE，重点换成预计算 cos/sin 表、用 `position_ids` 查表，还覆盖 packed 和越界。
- [[openai-rope-offset]]：decode 位置写成 0 不会报错，那张卡讲怎么用有 / 无 cache 的输出对齐把它查出来。
- [[coding-qk-norm]]：RoPE 之前先对 $q,k$ 做 RMSNorm，顺序不能反。
- [[coding-alibi]]：另一种位置编码，直接在 scores 上加线性偏置，decode 时同样用 cache 长度当 query 位置。
- [[meta-llama-rope]]：口述 RoPE 的相对位置性质和长上下文外推，不写代码。
