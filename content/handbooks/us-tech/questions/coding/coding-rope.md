---
id: coding-rope
section: coding
order: 6
level: A
title: 白板：RoPE 对 q/k 旋转，偶数维成对，decode 的 position
quick: >-
  把 $q,k$ 的偶数维和奇数维当成复平面上的一对，乘 $\cos(t\theta_i),\sin(t\theta_i)$。只旋 $q,k$，不旋 $v$。decode
  时 $t$ 是 cache 长度，不是 0。
tags:
  - Coding
  - RoPE
  - Llama
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: RoFormer — Enhanced Transformer with Rotary Position Embedding
    url: https://arxiv.org/abs/2104.09864
    type: primary
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
---

## 题怎么来的

Su et al. 的 RoPE 是 Llama / Qwen / GPT-NeoX 的默认位置编码。Meta 问 GQA 时会顺手问 RoPE；OpenAI 的 Transformer debug 把 decode 位置写成 0，有 cache 和没 cache 对不上。Apple 手写 MHA 的 follow-up 也是「位置怎么加」。注意力 shape 见 `apple-mha-code`，位置偏移见 `openai-transformer-debug`。

## 偶数维成对旋转

头维度 $d$ 必须是偶数。第 $i$ 对 $(x_{2i},x_{2i+1})$ 看成复数，位置 $t$ 上转角 $t\theta_i$，$\theta_i=10000^{-2i/d}$：

$$
\begin{bmatrix} y_{2i}\\ y_{2i+1} \end{bmatrix}
=
\begin{bmatrix} \cos(t\theta_i) & -\sin(t\theta_i)\\ \sin(t\theta_i) & \cos(t\theta_i) \end{bmatrix}
\begin{bmatrix} x_{2i}\\ x_{2i+1} \end{bmatrix}.
$$

点积 $q_m^\top k_n$ 只依赖 $m-n$，这就是相对位置。只对 $q,k$ 做；$v$ 不转。cos/sin 按位置预计算，broadcast 到 `[B, H, T, d/2]`。

```python
import torch

def rope_angles(dim, seqlen, base=10000.0, device=None):
    inv = 1.0 / (base ** (torch.arange(0, dim, 2, device=device).float() / dim))
    t = torch.arange(seqlen, device=device).float()
    freqs = torch.outer(t, inv)  # [T, d/2]
    return torch.cos(freqs), torch.sin(freqs)

def apply_rope(x, cos, sin):
    # x: [B, H, T, D], cos/sin: [T, D/2]
    xe, xo = x[..., 0::2], x[..., 1::2]
    cos = cos[None, None, :, :]
    sin = sin[None, None, :, :]
    ye = xe * cos - xo * sin
    yo = xe * sin + xo * cos
    return torch.stack((ye, yo), dim=-1).flatten(-2)

def decode_rope(q, k, cos, sin, pos):
    # pos = cache_len；取该位置的一对 cos/sin，不要用 0
    c, s = cos[pos : pos + 1], sin[pos : pos + 1]
    return apply_rope(q, c, s), apply_rope(k, c, s)
```

另一种常见写法是 `rotate_half`：前 $d/2$ 和后 $d/2$ 配对（Llama / GPT-NeoX）。和论文的偶奇成对频率排布不同，checkpoint 必须和训练时同一套。白板先写偶奇对，再提「读权重前确认实现」。

## Decode：position 是 cache 长度

Prefill：位置 $0..T-1$，整段 $K,V$ 旋转后写入 cache。Decode 新 token 的下标是 `cache_len`，只旋当前 $q_t,k_t$。历史 $K$ 已经旋过，不要每次重放。packed sample 或 left padding 必须用真实 `position_ids` 索引 cos/sin，不能假设等于 `arange(T)`。

不变量：同一前缀 greedy，有 KV cache 和满量 attention 逐 token 相同。位置写 0 是 silent 错。GQA 时 RoPE 仍按 head dim 转，和 $H_{\mathrm{kv}}$ 无关，见 `meta-llama-gqa`。

## 追问

- **为什么不旋 $v$？** 相对位置要进注意力权重，不进被加权的值。旋 $v$ 会破坏「内容向量与位置解耦」。
- **长上下文怎么外推？** 改 $\theta$ 的 base（NTK）、YaRN、或位置插值。面试说清「频率变了，不是再训一套绝对 embedding」。
- **偶数维不成对会怎样？** $d$ 为奇数没法两两转。实现上 assert `dim % 2 == 0`。
