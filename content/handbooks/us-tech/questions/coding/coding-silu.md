---
id: coding-silu
section: coding
order: 24
level: A
title: 白板：SiLU / Swish 手写，数值上哪里会炸
quick: >-
  $\mathrm{SiLU}(x)=x\cdot\sigma(x)$，即 $\beta=1$ 的 Swish。$\sigma$ 在大负数上
  $e^{-x}$ 会 overflow，要按正负分支或 `tanh` 形式写。它不是奇函数。Llama 的 SwiGLU 只把它放在
  gate 支路。
tags:
  - Coding
  - SiLU
  - Swish
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: torch.nn.functional.silu
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.silu.html
    type: primary
  - title: Sigmoid-Weighted Linear Units for Neural Network Function Approximation in Reinforcement Learning
    url: https://arxiv.org/abs/1702.03118
    type: primary
  - title: Searching for Activation Functions (Swish)
    url: https://arxiv.org/abs/1710.05941
    type: primary
---

## 题怎么来的

Llama MLP 的门控是 SiLU，不是 ReLU / GELU。Meta 会让你手写；Apple 端侧会问 fp16 下大负值。SwiGLU 怎么接三张权重见 `coding-swiglu`。PyTorch 的 `F.silu` 是这条，白板不要调用完事，要能写出稳定的 $\sigma$。

## 定义和稳定 sigmoid

$$
\mathrm{SiLU}(x)=x\,\sigma(x)=\frac{x}{1+e^{-x}},\qquad
\sigma(x)=\tfrac12\big(1+\tanh(x/2)\big).
$$

Swish$_\beta(x)=x\,\sigma(\beta x)$；SiLU 就是 $\beta=1$。$x\to+\infty$ 时 SiLU $\to x$；$x\to-\infty$ 时 $\to 0$。过原点：$\mathrm{SiLU}(0)=0$，小正数区域略大于 $0$，像「平滑 ReLU」。它 **不是奇函数**：$\mathrm{SiLU}(-x)=-x\sigma(-x)=-x(1-\sigma(x))$，和 $-\mathrm{SiLU}(x)$ 差一项 $x$。

直接 `x / (1 + exp(-x))`：大正 $x$ 时 $e^{-x}$ 下溢成 $0$，结果是 $x$，没问题；**大负 $x$** 时 $-x$ 为正，$e^{-x}$ overflow 成 inf，分母 inf，得到 NaN。按符号拆：

$$
\sigma(x)=\begin{cases}
1/(1+e^{-x}) & x\ge 0\\
e^{x}/(1+e^{x}) & x<0.
\end{cases}
$$

或全程用 $\tanh$ 形式。乘法 $x\cdot\sigma(x)$ 在 $x$ 极负、$\sigma\approx 0$ 时是 $0$，不要先 overflow 再乘。

```python
import torch
import torch.nn.functional as F

def sigmoid_stable(x):
    x = x.float()
    neg = x < 0
    z = torch.exp(-torch.abs(x))
    return torch.where(neg, z / (1 + z), 1 / (1 + z))


def silu(x):
    return x * sigmoid_stable(x)


def silu_tanh(x):
    x32 = x.float()
    return x * (0.5 * (1.0 + torch.tanh(0.5 * x32)))


def check():
    x = torch.tensor([0.0, 2.0, -2.0, 40.0, -40.0])
    y = silu(x)
    assert torch.allclose(y, F.silu(x.float()), atol=1e-5)
    assert torch.isfinite(y).all()
    assert silu(x[:1]).item() == 0.0
```

`F.silu` 对半精度有 fused kernel。自己写时先升 fp32 再 cast 回，和 RMSNorm 同一习惯，见 `coding-rmsnorm`。

## 和 GELU、在 MLP 里的位置

GELU 是 $x\Phi(x)$，形状接近 SiLU，GPT-2 用 GELU。Llama 把 SiLU 放在 **gate**：`silu(x W_g) * (x W_u)`，不是 `silu(x W)` 再线性。导函数 $\mathrm{SiLU}'(x)=\sigma(x)+x\sigma(x)(1-\sigma(x))$，反向手推时别漏第二项。面试若问「为什么不用 ReLU」：门控需要光滑、非零负半轴，dead ReLU 和 GLU 不搭。

## 追问

- **`x * sigmoid(x)` 在 fp16 里 $-20$ 会怎样？** 不稳定实现会在 `exp(20)` 炸掉。稳定分支应给出 $\approx 0$。
- **SiLU 和 Swish 要不要当成两个函数？** 论文里 Swish 带 $\beta$；实现和 Llama 说的 SiLU 就是 $\beta=1$。别答成无关激活。
- **能 inplace 吗？** $x$ 还要给 backward 用 $\sigma(x)$。除非 fused backward 存了中间件，否则别 `silu_` 掉唯一的一份。
- **和 z-loss 有关吗？** 无关。z-loss 钉 logits 的 log-partition，见 `coding-z-loss`。SiLU 是 MLP 非线性。
