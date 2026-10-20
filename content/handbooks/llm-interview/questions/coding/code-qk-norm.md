---
id: code-qk-norm
section: coding
order: 47
level: A
title: 手写 QK-Norm：RMSNorm 必须在 RoPE 之前
quick: >-
  投影得到 $Q,K$ 之后，对每个 head 的 $d_h$ 维做 RMSNorm，再 RoPE，再打 $QK^\top$。顺序写反会把旋转毁掉：norm
  会重缩放已经转过的二维对。Qwen2.5 / 部分 Llama 变体用它压 attention logits 的尺度。$V$ 通常不 norm。
tags:
  - QK-Norm
  - RoPE
  - Attention
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Query-Key Normalization for Transformers
    url: https://arxiv.org/abs/2302.05442
    type: primary
---

普通 MHA 的 $QK^\top/\sqrt{d}$ 在深网里仍可能漂。QK-Norm 让每个 query / key 向量的模接近 $\sqrt{d_h}$ 量级，logits 更稳。和 `code-rmsnorm`、`code-rope` 拼起来写。

## 顺序

$$
Q=\mathrm{RoPE}(\mathrm{RMSNorm}(X W_Q)),\quad
K=\mathrm{RoPE}(\mathrm{RMSNorm}(X W_K)),\quad
V=X W_V.
$$

RMSNorm 的轴是 $d_h$，权重形状 `[Dh]`，每个 head 共享或每 head 一份都可以，先写共享。

```python
import torch
import torch.nn as nn

class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.eps, self.weight = eps, nn.Parameter(torch.ones(dim))

    def forward(self, x):
        z = x.float()
        y = z * torch.rsqrt(z.pow(2).mean(-1, keepdim=True) + self.eps)
        return self.weight * y.to(x.dtype)

def apply_rope_half(x, cos, sin):
    x1, x2 = x.chunk(2, -1)
    return x * cos + torch.cat((-x2, x1), -1) * sin

def qk_norm_rope(q, k, q_norm, k_norm, cos, sin):
    # q,k: [B,H,T,Dh]；先 norm 再转
    q, k = q_norm(q), k_norm(k)
    return apply_rope_half(q, cos, sin), apply_rope_half(k, cos, sin)
```

decode 时，新 token 只对自己的 $q_t,k_t$ 做 norm 和 RoPE。cache 里存的是已经转过的 $K$，不要再 norm 一遍。

## 追问

- **为什么 $V$ 不 norm？** logits 的尺度由 $Q,K$ 决定。$V$ 是加权内容，再 norm 会把值通路的幅度掐掉。
- **和 QK clip / softcap？** 都是压 logits。softcap 加在 scores 上，见 `code-softcap`；QK-Norm 改的是向量本身。
- **和 LayerNorm？** 用 RMSNorm 就够，少一个均值。写成 LN 也能跑，和常见 checkpoint 对不上。
