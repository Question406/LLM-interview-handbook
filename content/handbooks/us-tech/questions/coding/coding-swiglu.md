---
id: coding-swiglu
section: coding
order: 17
level: A
title: 白板：SwiGLU / Llama MLP，门控和中间维为什么是 8/3
quick: >-
  $\mathrm{SwiGLU}(x)=(\mathrm{SiLU}(xW_g)\odot xW_u)W_d$，三个无 bias 的线性层；中间维取 $\tfrac{8}{3}D$ 再向上对齐，参数量和 $4D$ 宽的旧 FFN 大致持平。
tags:
  - 完整编程练习
  - Coding
  - SwiGLU
  - Llama
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-10-18
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

## 完整编程练习（手册重构版）

> 下面的接口、约束和测试是手册补的练习约定，不是面试官原题。Python 3 + PyTorch，只在 CPU 上用小维度验证，不分配真实的 4096 维模型。

### 题面、接口与约束

- `llama_ffn_hidden(dim, multiple_of=256, ffn_mult=None) -> int`：按 Llama 的规则算中间维。先取 $h=\lfloor 8D/3\rfloor$；给了 `ffn_mult` 就再乘它并向下取整；最后向上取整到 `multiple_of` 的倍数。
- `SwiGLU(dim, hidden=None)`：三个无 bias 的线性层，gate 和 up 是 $D\to H$，down 是 $H\to D$。`hidden` 不给时用 `llama_ffn_hidden(dim)`。
- `SwiGLU.forward(x)`：输入 `[..., D]`，输出同形状，计算 `down(silu(gate(x)) * up(x))`。

### 输入输出示例

```text
llama_ffn_hidden(4096)                 -> 11008   # floor(8 * 4096 / 3) = 10922，对齐到 256
llama_ffn_hidden(8192, 4096, 1.3)      -> 28672   # Llama 2 70B 的设置
SwiGLU(4, hidden=6)(x: [2, 3, 4])      -> [2, 3, 4]
```

### 解题思路与正确性

gate 分支过 SiLU，up 分支保持线性，两者在 $H$ 维上逐元素相乘，再由 down 投回 $D$。三次线性变换都作用在最后一维，所以任意前缀形状都能直接用。测试用 `F.linear` 按公式手算一遍，对比模块输出，并检查三个权重都拿到了梯度。

### 完整参考实现（Python 3）

```python
import torch
from torch import nn
import torch.nn.functional as F


def llama_ffn_hidden(dim, multiple_of=256, ffn_mult=None):
    """Llama 的 FFN 中间维：floor(8D/3)，可选乘 ffn_mult，再向上对齐到 multiple_of。"""
    hidden = int(2 * 4 * dim / 3)  # 8/3 D
    if ffn_mult is not None:
        hidden = int(ffn_mult * hidden)
    return multiple_of * ((hidden + multiple_of - 1) // multiple_of)


class SwiGLU(nn.Module):
    """Llama MLP：down(silu(gate(x)) * up(x))，三个线性层都没有 bias。"""

    def __init__(self, dim, hidden=None):
        super().__init__()
        hidden = llama_ffn_hidden(dim) if hidden is None else hidden
        self.w_gate = nn.Linear(dim, hidden, bias=False)
        self.w_up = nn.Linear(dim, hidden, bias=False)
        self.w_down = nn.Linear(hidden, dim, bias=False)

    def forward(self, x):
        # x: [..., D] -> [..., D]
        return self.w_down(F.silu(self.w_gate(x)) * self.w_up(x))
```

### 可执行测试

```python
torch.set_num_threads(1)
torch.manual_seed(0)

# Llama 7B 和 70B 的中间维
assert llama_ffn_hidden(4096) == 11008
assert llama_ffn_hidden(8192, multiple_of=4096, ffn_mult=1.3) == 28672

# 默认 hidden 走 llama_ffn_hidden
assert SwiGLU(48).w_gate.out_features == llama_ffn_hidden(48)

# 输出与按公式手算一致，形状不变
module = SwiGLU(4, hidden=6)
x = torch.randn(2, 3, 4, requires_grad=True)
y = module(x)
gate = F.silu(F.linear(x, module.w_gate.weight))
up = F.linear(x, module.w_up.weight)
expected = F.linear(gate * up, module.w_down.weight)
assert y.shape == x.shape
assert torch.allclose(y, expected)

# 没有 bias，三个权重都有梯度
assert all(layer.bias is None for layer in (module.w_gate, module.w_up, module.w_down))
y.sum().backward()
assert all(param.grad is not None for param in module.parameters())

# 先乘后激活是错的写法，结果不同
wrong = F.linear(F.silu(F.linear(x, module.w_gate.weight) * up), module.w_down.weight)
assert not torch.allclose(y, wrong)
```

### 复杂度与追问

设 batch 为 $B$、长度为 $T$、模型维 $D$、中间维 $H$。时间 $O(BTDH)$，参数 $3DH$，中间激活 $O(BTH)$。

- 追问「gate 和 up 能合成一次 GEMM 吗」：可以。把 $W_g$、$W_u$ 拼成 `[D, 2H]`，做一次矩阵乘再 chunk 成两半，数值一样，更容易融合。白板上先写两支。
- 追问「为什么对齐到 256」：不是数学要求，是 Llama 实现为了 kernel 分块和张量并行（TP）切分方便做的对齐。

## 题怎么来的

Shazeer 提出的几种 GLU 变体里，Llama 选了 SwiGLU。Meta 手写 Transformer 时会要求写 MLP 这一块：它不是 `Linear-ReLU-Linear`，而是门控乘上投影，再做下投影。如果把中间宽度写成 $4D$，参数量会超过论文的设定。激活函数本身见 `coding-silu`；前面的归一化是 RMSNorm，见 `coding-rmsnorm`。

## 门控，不是两层 MLP

输入 $x$ 的形状是 `[B, T, D]`：

$$
y=\big(\mathrm{SiLU}(x W_g)\odot (x W_u)\big) W_d.
$$

其中 $W_g,W_u\in\mathbb{R}^{D\times H}$，$W_d\in\mathbb{R}^{H\times D}$，Llama 不用 bias。SiLU 只作用在 gate 那一支，up 那一支是线性的。两支在 $H$ 维上逐元素相乘，再投回 $D$。不要写成 `silu(gate(x) * up(x))`：那是先乘后激活，和权重的训练方式对不上。

普通 FFN 是 $D\to 4D\to D$，两个矩阵；SwiGLU 有三个。如果 $H=4D$，参数大约是旧 FFN 的 $1.5$ 倍。Llama 把 $H$ 缩到 $\tfrac{2}{3}\cdot 4D=\tfrac{8}{3}D$，三个矩阵的参数量就和原来两个 $4D$ 宽的矩阵接近。之后再按 `multiple_of=256` 向上取整。以 7B 为例，$D=4096$，$\lfloor\tfrac{8}{3}D\rfloor=10922$，对齐到 $11008$。

HuggingFace 里这三个矩阵叫 `gate_proj` / `up_proj` / `down_proj`。

## 别和 GELU FFN 混

GPT-2 风格是 `gelu(x W_1) W_2`，中间维 $4D$。PaLM 也用 SwiGLU，但中间维的取整规则不同。对 checkpoint 时要看 `intermediate_size` 和有没有 bias，不要按 $4D$ 去猜。如果有 Dropout，它放在 MLP 输出之后、加回残差之前；Llama 预训练默认不用，见 `coding-dropout`。

## 追问

- **为什么是 $8/3$ 而不是 $4$？** 门控多了一张 $D\times H$ 的矩阵。取 $H=\tfrac{8}{3}D$，三张矩阵的参数量约等于旧的两张 $4D$ 宽矩阵，目的是匹配参数量。
- **SiLU 和 Swish 是什么关系？** $\mathrm{SiLU}(x)=x\cdot\sigma(x)$，就是 $\beta=1$ 的 Swish。手写数值见 `coding-silu`。
- **gate 和 up 能共用一张权重吗？** 那就不是 SwiGLU 了。参数会变少，质量一般会下降。
