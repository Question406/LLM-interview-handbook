---
id: code-layernorm
section: coding
order: 41
level: A
title: 手写 LayerNorm：减均值、除以 D 的方差，以及和 RMSNorm 差哪一项
quick: >-
  最后一维上 $\mu=\mathrm{mean}(x)$，$\sigma^2=\mathrm{mean}((x-\mu)^2)$（除以 $D$，不是
  $D-1$），再 $w\odot(x-\mu)/\sqrt{\sigma^2+\varepsilon}+b$。RMSNorm 不减 $\mu$、也没有
  $b$。Llama / Qwen 用 RMSNorm；BERT / GPT-2 用 LayerNorm。eps 常见 $10^{-5}$，统计转到 fp32。
tags:
  - LayerNorm
  - Normalization
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Layer Normalization
    url: https://arxiv.org/abs/1607.06450
    type: primary
---

和 `code-rmsnorm` 成对出现。面试官要的是：归一化轴、有没有减均值、方差除以 $D$ 还是 $D-1$，以及仿射参数的形状是 `[D]` 而不是 `[B,T,D]`。

## 公式

$x\in\mathbb{R}^{D}$（最后一维）：

$$
\mu=\frac1D\sum_i x_i,\quad
\sigma^2=\frac1D\sum_i(x_i-\mu)^2,\quad
y=w\odot\frac{x-\mu}{\sqrt{\sigma^2+\varepsilon}}+b.
$$

`unbiased=False`。PyTorch `F.layer_norm` 默认就是除以 $D$。写成 `x.var(unbiased=True)` 会和框架差一项 $D/(D-1)$，单测对不上。

```python
import torch
import torch.nn as nn

class LayerNorm(nn.Module):
    def __init__(self, dim, eps=1e-5):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.bias = nn.Parameter(torch.zeros(dim))
        self.eps = eps

    def forward(self, x):
        z = x.float()
        mu = z.mean(-1, keepdim=True)
        var = z.var(-1, keepdim=True, unbiased=False)
        y = (z - mu) * torch.rsqrt(var + self.eps)
        return y.to(x.dtype) * self.weight + self.bias
```

RMSNorm 是 $x/\mathrm{RMS}(x)\odot w$，没有 $b$。Pre-Norm 把 LN / RMSNorm 放在子层前面，残差走未归一化的流，见 `code-decoder-block`。不要在序列维上做 LN：那会让不同 token 参与同一组归一化统计；训练和推理的序列长度变化时，统计分布也会改变。

## 追问

- **为什么最后一维？** hidden 维是特征。batch / 时间维的统计在推理时对不上。
- **fp16 为什么先转 fp32？** 平方和在低精度下容易丢小数，也容易溢出。
- **没有 bias 还叫 LayerNorm 吗？** 有的实现去掉 $b$，只留 $w$。和 RMSNorm 仍差一个减均值。
