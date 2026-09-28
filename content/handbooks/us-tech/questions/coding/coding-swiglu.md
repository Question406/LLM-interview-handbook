---
id: coding-swiglu
section: coding
order: 17
level: A
title: 白板：SwiGLU / Llama MLP，门控和中间维为什么是 8/3
quick: >-
  $\mathrm{SwiGLU}(x)=(\mathrm{SiLU}(xW_g)\odot xW_u)W_d$。三份线性、无 bias。中间维取
  $\tfrac{8}{3}D$ 再向上对齐到 $256$ 的倍数，让门控多出来的那份参数和旧的 $4D$ 宽 FFN 大致打平。
tags:
  - Coding
  - SwiGLU
  - Llama
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: GLU Variants Improve Transformer
    url: https://arxiv.org/abs/2002.05202
    type: primary
  - title: LLaMA — Open and Efficient Foundation Language Models
    url: https://arxiv.org/abs/2302.13971
    type: primary
  - title: Llama 2 Open Foundation and Fine-Tuned Chat Models
    url: https://arxiv.org/abs/2307.09288
    type: primary
---

## 题怎么来的

Shazeer 的 GLU 变体里，Llama 选了 SwiGLU。Meta 手写 Transformer 会要 MLP 这一块：不是 `Linear-ReLU-Linear`，是门控 × 上投影，再下投影。中间宽写成 $4D$ 会让参数比论文多一块。激活函数本身见 `coding-silu`。前层归一化是 RMSNorm，见 `coding-rmsnorm`。

## 门控，不是两层 MLP

输入 $x$ 形状 `[B, T, D]`：

$$
y=\big(\mathrm{SiLU}(x W_g)\odot (x W_u)\big) W_d.
$$

$W_g,W_u\in\mathbb{R}^{D\times H}$，$W_d\in\mathbb{R}^{H\times D}$。Llama 没 bias。`SiLU` 只作用在 gate 那支；up 那支是线性。两支在 $H$ 维上逐点乘，再投回 $D$。不要写成 `silu(gate(x) * up(x))`，那是先乘后激活，对不上权重。

普通 FFN 是 $D\to 4D\to D$ 两份矩阵。SwiGLU 有三份。若 $H=4D$，参数大约是旧 FFN 的 $1.5$ 倍。Llama 把 $H$ 收到 $\tfrac{2}{3}\cdot 4D=\tfrac{8}{3}D$，三份矩阵的参数量和原来的两份 $4D$ 宽层接近。再按 `multiple_of=256` 向上取整，方便分核 / TP。7B：$D=4096$，$\tfrac{8}{3}D\approx 10923$，对齐到 $11008$。

```python
import torch
from torch import nn
import torch.nn.functional as F

def llama_ffn_hidden(dim, multiple_of=256, ffn_mult=None):
    h = int(2 * 4 * dim / 3)  # 8/3 D
    if ffn_mult is not None:
        h = int(ffn_mult * h)
    return multiple_of * ((h + multiple_of - 1) // multiple_of)

class SwiGLU(nn.Module):
    def __init__(self, dim, hidden=None):
        super().__init__()
        hidden = llama_ffn_hidden(dim) if hidden is None else hidden
        self.w_gate = nn.Linear(dim, hidden, bias=False)
        self.w_up = nn.Linear(dim, hidden, bias=False)
        self.w_down = nn.Linear(hidden, dim, bias=False)

    def forward(self, x):
        # x: [B, T, D] -> [B, T, D]
        return self.w_down(F.silu(self.w_gate(x)) * self.w_up(x))

def check():
    m = SwiGLU(4096)
    assert m.w_gate.out_features == 11008
    y = m(torch.randn(2, 3, 4096))
    assert y.shape == (2, 3, 4096)
```

`gate_proj` / `up_proj` / `down_proj` 是 HuggingFace 名。有的实现把 $W_g$ 和 $W_u$ 拼成一次 `[B, T, 2H]` 的 GEMM 再 chunk，数值相同、更好融合。白板可以提，先写两支。

## 别和 GELU FFN 混

GPT-2 风格是 `gelu(x W_1) W_2`，中间 $4D$。PaLM 用 SwiGLU 但中间宽的取整规则不同。对 checkpoint 时看 `intermediate_size` 和有没有 bias，不要按 $4D$ 猜。Dropout 若存在，是在 MLP 输出、进残差之前，Llama 预训练默认不用，见 `coding-dropout`。

## 追问

- **为什么是 $8/3$ 不是 $4$？** 门控多一张 $D\times H$ 的表。$H=\tfrac{8}{3}D$ 让三张表的参数约等于旧的两张 $4D$ 表，不是神秘超参。
- **SiLU 和 Swish？** $\mathrm{SiLU}(x)=x\cdot\sigma(x)$，就是 $\beta=1$ 的 Swish。手写数值见 `coding-silu`。
- **能把 gate 和 up 共用一张权重吗？** 那就不是 SwiGLU。参数会少，质量一般掉。
- **中间维必须整除 $256$？** 不是数学要求，是 Llama 实现的对齐。面试先写 $\tfrac{8}{3}D$ 再 `round_up`。
