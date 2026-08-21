---
id: code-lora
section: coding
order: 13
level: A
title: 手写 LoRA 前向：$y=Wx+(\alpha/r)BAx$
quick: >-
  冻住 $W$，只训 $A\in\mathbb{R}^{r\times d_{\mathrm{in}}}$、$B\in\mathbb{R}^{d_{\mathrm{out}}\times r}$。初始化 $A$
  高斯、$B$ 全零，保证起步等价于原模型。$\alpha/r$ 把更新幅度从 rank 里解耦。不要接在 LayerNorm 后面。
tags:
  - LoRA
  - PEFT
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-19
sources:
  - title: LoRA
    url: https://arxiv.org/abs/2106.09685
    type: primary
---

LoRA 把 $\Delta W$ 参数化成低秩：$W'=W+BA$ 再乘缩放 $\alpha/r$。前向必须保持和「先加再乘」一致，现场最常写的是对激活做两次小 GEMM。

## 公式

$$
y=Wx+\frac{\alpha}{r}B(Ax).
$$

$r\ll \min(d_{\mathrm{in}},d_{\mathrm{out}})$。$\alpha$ 固定（常见 16/32），改 $r$ 时学习率不必按 $r$ 重调。$B=0$ 起步 $\Rightarrow$ $y=Wx$。

## 坑

- **挂在 LN 后**：LN 输出分布和 $W$ 训练时看到的不一致，低秩适配器会学歪。美团卡写过「LoRA 不要接在 LayerNorm 后」。
- **合并权重**：推理可把 $(\alpha/r)BA$ 加回 $W$，去掉额外延迟。训练时不要每步 merge，否则和优化器状态对不上。
- **QLoRA**：$W$ 量化存储，前向反量化后再加 LoRA；手写本题用全精度 $W$ 即可。

```python
import torch
import torch.nn as nn

class LoRALinear(nn.Module):
    def __init__(self, W, r=8, alpha=16):
        super().__init__()
        d_out, d_in = W.shape
        self.register_buffer("W", W)
        self.A = nn.Parameter(torch.randn(r, d_in) * 0.02)
        self.B = nn.Parameter(torch.zeros(d_out, r))
        self.scale = alpha / r

    def forward(self, x):
        return x @ self.W.T + self.scale * (x @ self.A.T) @ self.B.T
```

形状：$x$ 为 `[..., d_in]`。不要写成 `B @ A @ x` 却把 batch 维挤掉。

## 追问

- **为什么 $B$ 零、$A$ 高斯？** 反之起步 $\Delta W\neq 0$，破坏基座。
- **rank 和 $\alpha$ 谁管幅度？** 有效步长 $\propto \alpha/r$；只加 $r$ 不加 $\alpha$ 会把更新变弱。
- **和 Adapter 差？** Adapter 在层间插小 FFN，改深度和延迟；LoRA 改现有矩阵，可 merge。
