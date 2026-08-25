---
id: coding-rmsnorm
section: coding
order: 5
level: A
title: 白板：RMSNorm 比 LayerNorm 少了什么，Llama 为什么用
quick: >-
  少了减均值，也通常没有 $\beta$。只做 $x/\mathrm{RMS}(x)$ 再乘 $\gamma$。Llama 用它是算得少、和 LN 质量接近，不是数学等价。轴仍是最后一维 $D$。
tags:
  - Coding
  - RMSNorm
  - Llama
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Root Mean Square Layer Normalization
    url: https://arxiv.org/abs/1910.07467
    type: primary
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
  - title: torch.nn.RMSNorm
    url: https://pytorch.org/docs/stable/generated/torch.nn.RMSNorm.html
    type: primary
---

## 题怎么来的

Zhang & Sennrich 2019 提出 RMSNorm；LLaMA / Llama 2 / 3 公开实现全部用它，不用 LayerNorm。Meta GenAI 岗会让你对照着写两行，并说清「少了什么」和「为什么不改回去」。LN 的完整形态见 `coding-layernorm`。Apple 端侧也会问：少一次 mean reduction 对 kernel 意味着什么。

## 少了 centering，通常也少 $\beta$

LayerNorm：减 $\mu$，除 $\sqrt{\sigma^2+\varepsilon}$，再 $\gamma,\beta$。RMSNorm：

$$
\mathrm{RMS}(x)=\sqrt{\frac{1}{D}\sum_{i=1}^{D}x_i^2+\varepsilon},\qquad
y=\gamma\odot\frac{x}{\mathrm{RMS}(x)}.
$$

没有 $\mu$，因此 **不把均值打成 0**；均值那一分量留在残差里。论文论证：LN 里真正起作用的多半是缩放，centering 可以省。Llama 的 $\gamma$ 仍在，**没有 bias $\beta$**。输入仍是 `[B, T, D]`，reduction 只沿 $D$。

```python
import torch
from torch import nn

class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x):
        # x: [B, T, D]
        z = x.float()
        inv = torch.rsqrt(z.pow(2).mean(dim=-1, keepdim=True) + self.eps)
        return (z * inv).to(x.dtype) * self.weight


def vs_layernorm(x, eps=1e-6):
    mu = x.mean(-1, keepdim=True)
    ln = (x - mu) * torch.rsqrt(x.var(-1, keepdim=True, unbiased=False) + eps)
    rms = x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + eps)
    return ln, rms
```

`eps` 在 Llama 里常见 $10^{-5}$ 或 $10^{-6}$。norm 在 fp32 里做：平方均值在 bf16 下容易攒误差。`nn.RMSNorm` 从较新的 PyTorch 进了核心库，白板仍要能手写。

## Llama 为什么换

不是因为 RMSNorm 和 LN 等价。公开理由是：**少一次 mean、少一套 $\beta$、kernel 更简单**，在 7B–70B 上质量不掉。GQA、RoPE、SwiGLU 是同一套 Llama 积木，RMSNorm 是其中最便宜的一块，见 `meta-llama-gqa`。不要答「RMSNorm 一定更准」。

Pre-norm：每个 attention / FFN 子层入口做 RMSNorm，残差在外面加。Decode $T=1$ 和训练 $T$ 长时统计量仍是沿 $D$，逐步生成不漂移。NVIDIA 追问：RMS 是一次 reduction + rsqrt，比 LN 少一次减均值的读写，带宽敏感的 decode 有点用，但不是主要的显存账。

## 追问

- **把均值再减掉还叫 RMSNorm 吗？** 不叫。那就是 LN 去掉 $\beta$ 的变体。Llama 明确不减均值。
- **$\gamma$ 能不能去掉？** 能跑，但失去按通道恢复尺度的自由度。公开 checkpoint 都留了 `weight`。
- **和 BatchNorm / 在 $T$ 上标准化？** 都不是。轴仍是 feature 维 $D$。沿 $T$ 会让 padding 污染，逐步 decode 还对不上训练。
