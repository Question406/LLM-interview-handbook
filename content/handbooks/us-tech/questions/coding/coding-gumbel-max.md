---
id: coding-gumbel-max
section: coding
order: 13
level: A
title: 白板：Gumbel-max 采样，和 softmax 温度的关系
quick: >-
  $y=\arg\max_i(\log\pi_i+g_i)$，$g_i$ 是 Gumbel$(0,1)$，精确等于从 $\pi$ 里 categorical 采样。温度是
  $\arg\max(( \log\pi+g)/\tau)$；$\tau\to 0$ 变硬 argmax，$\tau\to\infty$ 变均匀。Gumbel-softmax 用 softmax 代替
  argmax 才能反传。
tags:
  - Coding
  - Gumbel
  - Sampling
  - OpenAI
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: Categorical Reparameterization with Gumbel-Softmax
    url: https://arxiv.org/abs/1611.01144
    type: primary
  - title: torch.nn.functional.gumbel_softmax
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.gumbel_softmax.html
    type: primary
---

## 题怎么来的

Jang et al. / Maddison et al. 把 Gumbel-max 写成可微松弛，研究岗爱问「和 softmax 温度是不是一回事」。OpenAI 的采样题有时不走 multinomial，改写 Gumbel 噪声加 logits。Apple / Anthropic 较少，但作为「离散采样怎么反传」的标准答案要能写。普通温度采样见 `coding-topk-nucleus`。

## Gumbel-max：argmax 即采样

$g_i=-\log(-\log U_i)$，$U_i\sim\mathrm{Uniform}(0,1)$。对概率 $\pi$ 或等价地对 logits $z=\log\pi+c$：

$$
y=\arg\max_i(z_i+g_i).
$$

这和 `multinomial(softmax(z))` 同分布。实现时 $U$ 要离开 $0$ 和 $1$，否则 $\log$ 炸。白板用 `tiny` clamp。

温度 $\tau$：

$$
y_\tau=\arg\max_i\bigl((z_i+g_i)/\tau\bigr)=\arg\max_i(z_i/\tau+g_i/\tau).
$$

$z/\tau$ 就是 softmax 温度：$\tau\to 0$ 质量集中到 $\arg\max z$；$g/\tau$ 同时放大，离散 argmax 仍由噪声打破平手，但相对 $z$ 的尖锐程度和 $\mathrm{softmax}(z/\tau)$ 一致。$\tau\to\infty$ 接近均匀。Gumbel-max 加温度，等价于对 $\mathrm{softmax}(z/\tau)$ 做 categorical 采样，不是两套无关机制。

```python
import torch

def gumbel_noise(shape, eps=1e-20, generator=None):
    u = torch.rand(shape, generator=generator)
    u = u.clamp(min=eps, max=1.0 - eps)
    return -torch.log(-torch.log(u))

def gumbel_max(logits, tau=1.0, generator=None):
    # logits: [B, V]
    g = gumbel_noise(logits.shape, generator=generator)
    return torch.argmax((logits + g) / tau, dim=-1)

def gumbel_softmax(logits, tau=1.0, hard=False, generator=None):
    g = gumbel_noise(logits.shape, generator=generator)
    y = torch.softmax((logits + g) / tau, dim=-1)
    if not hard:
        return y
    idx = y.argmax(dim=-1, keepdim=True)
    one_hot = torch.zeros_like(y).scatter_(-1, idx, 1.0)
    return one_hot + (y - y.detach())  # straight-through
```

`hard=True` 的 straight-through：前向 one-hot，反向当 softmax。$\tau$ 太小 softmax 仍会 overflow，减 max 那套见 `coding-softmax-stable`。PyTorch `F.gumbel_softmax` 是这条路。

## 什么时候用，什么时候不要

训练里需要对离散选择反传（硬注意力、离散 bottleneck）才上 Gumbel-softmax。纯生成采样，`multinomial` 或 Gumbel-max 都对，Gumbel-max 在 GPU 上有时更好融合（加噪声 + argmax，免归一化）。Nucleus / top-k 截断后再加 Gumbel，等于在截后的子单纯形上采样，顺序仍是先截再噪。

不要和「对 softmax 输出再除温度」混用：温度只作用一次，在 logits 上。Mask 先打 $-\infty$，再加 Gumbel；对 $-\infty$ 加噪声仍是 $-\infty$，argmax 不会选中。全 mask 要 raise。

## 追问

- **为什么等价于 softmax 采样？** Gumbel 是指数族里 categorical 的 max-stable 噪声；证明可说「$\pi_i e^{g_i}$ 的 argmax 服从 $\pi$」，面试点到即可。
- **$\tau$ 和 softmax 温度是不是同一个？** 是，都作用在 logits 上。Gumbel-softmax 的 $\tau$ 还控制松弛有多硬，训练常从大 $\tau$ anneal 到小。
- **能替代 nucleus 吗？** 不能自动截尾。要 nucleus 仍先按 `coding-topk-nucleus` 截，再在核上 Gumbel-max。
