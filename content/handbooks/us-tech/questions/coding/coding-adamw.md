---
id: coding-adamw
section: coding
order: 3
level: A
title: 白板：AdamW 一步更新，m/v、bias correction、decoupled decay
quick: >-
  $m,v$ 是梯度的一/二阶 EMA；$\hat m,\hat v$ 除以 $1-\beta^t$ 纠偏。权重衰减直接打在 $\theta$ 上，不进自适应分母。不要写成
  $g \leftarrow g+\lambda\theta$ 再走 Adam，那是耦合 L2。
tags:
  - Coding
  - AdamW
  - Optimizer
  - Meta
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Decoupled Weight Decay Regularization
    url: https://arxiv.org/abs/2101.03961
    type: primary
  - title: torch.optim.AdamW
    url: https://pytorch.org/docs/stable/generated/torch.optim.AdamW.html
    type: primary
---

## 题怎么来的

Llama / GPT 训练栈默认 AdamW，不是「Adam 加一点 L2」。Meta、OpenAI、Anthropic 的研究岗会让你在白板上写一步更新，追问耦合衰减为什么让大 lr 的参数衰不动。论文是 Loshchilov & Hutter；PyTorch `AdamW` 按 decoupled 实现。NVIDIA 还会问 mixed precision 下这一步和 GradScaler 的顺序。

## 一步：$m,v$ → 纠偏 → 自适应步 → 再 decay

梯度 $g_t=\nabla_\theta L(\theta_{t-1})$（不含权重衰减）：

$$
\begin{aligned}
m_t&=\beta_1 m_{t-1}+(1-\beta_1)g_t,\\
v_t&=\beta_2 v_{t-1}+(1-\beta_2)g_t^2,\\
\hat m_t&=m_t/(1-\beta_1^t),\quad \hat v_t=v_t/(1-\beta_2^t).
\end{aligned}
$$

$t$ 从 1 起。早期 $m,v$ 偏向 0，不除 $1-\beta^t$ 等于步长被压扁。然后：

$$
\theta_t=\theta_{t-1}-\eta\Big(\hat m_t/(\sqrt{\hat v_t}+\varepsilon)+\lambda\theta_{t-1}\Big).
$$

等价写法：`theta *= (1 - lr * wd)`，再 `theta -= lr * m_hat / (sqrt(v_hat) + eps)`。衰减用的是更新前的 $\theta$，不经过 $\sqrt{v}$。

```python
import math
import torch

def adamw_step(p, g, m, v, t, lr=1e-3, b1=0.9, b2=0.999, eps=1e-8, wd=0.01):
    m = b1 * m + (1.0 - b1) * g
    v = b2 * v + (1.0 - b2) * g * g
    m_hat = m / (1.0 - b1 ** t)
    v_hat = v / (1.0 - b2 ** t)
    p = p * (1.0 - lr * wd)
    p = p - lr * m_hat / (v_hat.sqrt() + eps)
    return p, m, v


def demo():
    p = torch.tensor([1.0, -2.0])
    m = torch.zeros_like(p)
    v = torch.zeros_like(p)
    g = torch.tensor([0.5, 0.25])
    p, m, v = adamw_step(p, g, m, v, t=1)
    assert torch.isfinite(p).all()
    return p
```

`m,v` 和参数同 shape，每个 param 一份 state。Bias 通常不 decay；LN / RMSNorm 的 $\gamma$ 很多 recipe 也不 decay。白板先写 dense 参数，再口头排除。

## 耦合 L2 错在哪

Adam 把 L2 写进损失：$g \leftarrow g+\lambda\theta$，再除 $\sqrt{v}$。$|g|$ 大的坐标 $v$ 大，衰减被自适应项缩小，正则强度变得和梯度尺度缠在一起。AdamW 把 $\lambda\theta$ 留在参数空间，和论文标题里的 decoupled 是同一件事。不要答成「AdamW 就是 Adam 换了个名」。

混合精度：先 `unscale_` 再 clip 再 `optimizer.step()`。clip 见 `coding-grad-clip`。$t$ 是 optimizer step 计数，gradient accumulation 多 micro-step 才加一次 $t$。

## 追问

- **$\beta_1=0.9,\beta_2=0.999$ 在纠偏上差在哪？** $1-\beta_2^t$ 要到几千 step 才接近 1，$v$ 的纠偏窗口比 $m$ 长。漏掉 $\beta_2$ 纠偏，前期步长会偏小。
- **weight decay 进 $g$ 会怎样？** 衰减被 $1/\sqrt{v}$ 缩放，和 $\eta,\lambda$ 的直觉对不上，大梯度坐标几乎不 decay。
- **和 SGD+L2 比？** SGD 的 L2 本来就是 $\theta \leftarrow (1-\eta\lambda)\theta-\eta g$，已经 decoupled。是 Adam 的自适应分母把 L2 搞耦合了。
