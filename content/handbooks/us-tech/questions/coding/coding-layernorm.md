---
id: coding-layernorm
section: coding
order: 4
level: S
title: 白板：LayerNorm vs 在 feature 维上的标准化，eps 和仿射
quick: >-
  对 $[B,T,D]$ 沿 $D$ 减均值、除 $\sqrt{\sigma^2+\varepsilon}$，再 $\gamma\odot(\cdot)+\beta$。一条 token
  自己的 feature 标准化，不看 batch。$\varepsilon$ 防零方差；$\gamma,\beta$ 把尺度和偏移学回来。
tags:
  - Coding
  - LayerNorm
  - Normalization
  - Apple
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Layer Normalization
    url: https://arxiv.org/abs/1607.06450
    type: primary
  - title: torch.nn.LayerNorm
    url: https://pytorch.org/docs/stable/generated/torch.nn.LayerNorm.html
    type: primary
---

## 题怎么来的

Ba et al. 2016 的 LayerNorm 是 Transformer 的默认前置件。Apple 手写 MHA 前后会要你接 LN；OpenAI debug 会把 `eps` 写成 $0$ 或把轴收到时间维。评委要听的不是「做了归一化」，而是 **沿哪一维、和 BatchNorm 差在哪、仿射参数 shape 是什么**。Llama 把 LN 换成 RMSNorm，对照见 `coding-rmsnorm`。

## 公式：每个 token 沿 $D$ 标准化

输入 $x$ 形状 `[B, T, D]`。对每个 $(b,t)$：

$$
\mu=\frac{1}{D}\sum_{i=1}^{D}x_i,\quad
\sigma^2=\frac{1}{D}\sum_{i=1}^{D}(x_i-\mu)^2,\quad
\hat x=\frac{x-\mu}{\sqrt{\sigma^2+\varepsilon}},\quad
y=\gamma\odot\hat x+\beta.
$$

$\gamma,\beta\in\mathbb{R}^{D}$，跟 $D$ 广播，**不**跟 $T$ 走。这就是「在 feature 维上的标准化」：同一条样本、同一个位置，自己的 $D$ 个通道均值为 0、方差为 1。不同 token 互不看；不同 batch 行互不看。所以 LN 在小 batch、decode 一步 $T=1$ 时行为不变，端侧和训练对齐，Apple 爱听这句。

BatchNorm 是沿 $B$（再加空间维）对每个通道估 $\mu,\sigma$，推理要 running stats。LN 没有 running stats，训练/推理同一份代码。

```python
import torch
from torch import nn

class LayerNorm(nn.Module):
    def __init__(self, dim, eps=1e-5):
        super().__init__()
        self.eps = eps
        self.gamma = nn.Parameter(torch.ones(dim))
        self.beta = nn.Parameter(torch.zeros(dim))

    def forward(self, x):
        # x: [B, T, D], reduce last dim only
        x32 = x.float()
        mu = x32.mean(dim=-1, keepdim=True)
        var = x32.var(dim=-1, keepdim=True, unbiased=False)
        y = (x32 - mu) * torch.rsqrt(var + self.eps)
        return (self.gamma * y + self.beta).to(x.dtype)


def check():
    ln = LayerNorm(4)
    x = torch.randn(2, 3, 4)
    y = ln(x)
    assert y.shape == x.shape
    assert torch.allclose(y.float().mean(-1), torch.zeros(2, 3), atol=1e-5)
```

方差用 **有偏** $1/D$（`unbiased=False`），对齐论文和 `nn.LayerNorm`。用 $1/(D-1)$ 会对不上海外实现。reduction 放 fp32：低精度下平方和更容易 underflow。

## $\varepsilon$ 和仿射不要省略

$\varepsilon$ 典型 $10^{-5}$。全零向量时 $\sigma=0$，没有 $\varepsilon$ 就是除零。$\varepsilon$ 太大等于没标准化；太小在 fp16 里 `rsqrt` 仍可能 inf。

$\gamma,\beta$ 让模型把「单位方差」再拉回需要的尺度。Pre-LN（块入口 LN）训练比 Post-LN 稳，GPT-2 之后是默认；白板先写对 forward，再提残差旁边的位置。轴写错成 `dim=1`（时间维）等于在序列长度上标准化，padding 会把均值拉歪，必须配 mask，那已经不是 LN。

## 追问

- **和 BatchNorm 差在哪？** BN 沿 batch 估每个通道的统计，推理依赖 running mean；LN 沿 feature，逐步 decode 不需要改代码。
- **$\gamma$ 初始化？** 1，$\beta$ 为 0，启动时 $y\approx\hat x$。有人把 $\gamma$ 初始化成很小来做 Pre-LN 热身，那是训练 trick，不是定义。
- **padding 要不要 mask？** 标准 LN 对 pad 位置也会规范化，但那些 hidden 后面会被 loss ignore。不要在 LN 里偷偷沿 $T$ 做均值。
