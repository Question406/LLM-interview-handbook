---
id: coding-rope-cache
section: coding
order: 21
level: A
title: 白板：RoPE 的 cos/sin cache，decode 时怎么 index
quick: >-
  预计算 `[max_seq, D/2]` 的 $\cos,\sin$，用 `position_ids` 索引，不要每步 `arange(q_len)`。Prefill
  是 $0..T-1$；decode 一步是 `cache_len`。历史 $K$ 已经旋过，只旋当前 $q_t,k_t$。
tags:
  - Coding
  - RoPE
  - KV Cache
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

旋转公式见 `coding-rope`。这题是工程：cos/sin 表怎么建、decode 下标怎么取。OpenAI Transformer debug 的经典植入是 `pos = arange(q_len)`——decode 时 $q_{\mathrm{len}}=1$，永远旋位置 $0$，和 full attention greedy 对不齐，还不报错。查法见 `openai-rope-offset`。Meta / Apple 手写 MHA 会跟一句「cache 里的 $K$ 还要不要再转」。

## 表：按位置预计算

头维 $D$ 偶数。$\theta_i=10000^{-2i/D}$，$t=0..T_{\max}-1$：

$$
\mathrm{cos}[t,i]=\cos(t\theta_i),\quad \mathrm{sin}[t,i]=\sin(t\theta_i).
$$

形状 `[max_seq, D/2]`，register buffer，不进优化器。Apply 时按偶奇对（或 Llama 的 half-rotate）broadcast 到 `[B, H, T, D/2]`。**索引键是位置，不是「当前这段的局部 0..L」**。有 KV cache 时局部 arange 和绝对位置不是一回事。

```python
import torch
from torch import nn

class RopeCache(nn.Module):
    def __init__(self, dim, max_seq=4096, base=10000.0):
        super().__init__()
        assert dim % 2 == 0
        inv = 1.0 / (base ** (torch.arange(0, dim, 2).float() / dim))
        t = torch.arange(max_seq).float()
        freqs = torch.outer(t, inv)  # [max_seq, D/2]
        self.register_buffer("cos", freqs.cos(), persistent=False)
        self.register_buffer("sin", freqs.sin(), persistent=False)

    def at(self, position_ids):
        # position_ids: [B, T] 或 [T]
        return self.cos[position_ids], self.sin[position_ids]


def position_ids_for(cache_len, q_len, batch, device=None):
    # prefill: cache_len=0, q_len=T -> 0..T-1
    # decode:  cache_len=S, q_len=1 -> [S]
    pos = torch.arange(cache_len, cache_len + q_len, device=device)
    return pos.unsqueeze(0).expand(batch, -1)


def apply_rope(x, cos, sin):
    # x: [B, H, T, D]; cos/sin: [T, D/2] 或 [B, T, D/2]
    if cos.dim() == 2:
        cos, sin = cos[None, None, :, :], sin[None, None, :, :]
    elif cos.dim() == 3:
        cos, sin = cos[:, None, :, :], sin[:, None, :, :]
    xe, xo = x[..., 0::2], x[..., 1::2]
    ye = xe * cos - xo * sin
    yo = xe * sin + xo * cos
    return torch.stack((ye, yo), dim=-1).flatten(-2)
```

Prefill：`cache_len=0`，整段 $Q,K$ 用 $0..T-1$ 旋转后，$K,V$ 写入 cache。Decode：`position_ids = cache_len`（或 left pad / packed 的真实下标），只旋当前长度 $1$ 的 $q,k$。历史 $K$ **已经在写入时旋过**，不要对 cache 里的 $K$ 再 apply 一遍，否则角度变成 $2t\theta$。

## packed 和越界

`position_ids` 可以不是 `arange`。Left pad 的有效 token 从 pad 长度开始；文档 packing 可能每篇从 $0$ 重置，见 `coding-packed-lm`。下标 $\ge max_seq$ 会越界：要么建更大的表，要么 NTK / YaRN 改 $\theta$，不要静默 `pos % max_seq`。GQA 时 RoPE 仍按 $D$ 转，$H_{\mathrm{kv}}$ 不管，见 `coding-gqa-repeat`。

不变量：同一前缀 greedy，逐步 decode 和一次满量 forward 的下一 token 相同。对不齐先打印 `position_ids`，再怀疑 kernel。

## 追问

- **为什么不能 `arange(q_len)`？** $q_{\mathrm{len}}$ 是本步 query 数，不是在文档里的下标。Decode 永远是 $1$，位置却在涨。
- **$V$ 要不要过 cache 里的 cos？** 不要。RoPE 不旋 $V$；cache 的 $V$ 是内容。
- **cos 表要不要和权重一起存 checkpoint？** 不必。由 `dim, base, max_seq` 重算。换 base（长上下文）必须和训练一致。
- **batch 内不同序列不同 cache_len？** `position_ids` 做成 `[B, T]`，不要假设一个标量 $S$。连续 batch 见系统题，白板至少提到 per-row 下标。
