---
id: code-moe-router-aux-loss
section: coding
order: 17
level: S
title: 手写 MoE router（softmax + top-k）和 Switch 风格 aux loss
quick: >-
  $x\in\mathbb{R}^{T\times d}$，$W_r$ 得到 logits，softmax 成 $P$，top-$k$ 取门控。Aux 用
  $N\sum_i f_i P_i$，$f_i$ 是实际被选频率，$P_i$ 是平均门控概率。我会处理 $k=1$ 和 $k\gt 1$，并说清 capacity / ties。
tags:
  - MoE
  - Router
  - Aux Loss
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-21
sources:
  - title: Switch Transformers
    url: https://arxiv.org/abs/2101.03961
    type: primary
---

把 router 写成「分数 → 离散选择 → 可反传的频率惩罚」。现场允许伪代码，但形状必须对。

## 定义

$N$ 个 expert，token 矩阵 $x\in\mathbb{R}^{T\times d}$，router $W_r\in\mathbb{R}^{d\times N}$：

$$
P=\mathrm{softmax}(xW_r)\in\mathbb{R}^{T\times N}.
$$

Top-$k$ 沿 expert 维取出下标和门控。$k=1$ 时门控就是 $P_{t,i^\star}$；$k\gt 1$ 时常对选中的 $k$ 个概率再归一化。Aux（Switch）：

$$
\mathcal{L}_{\mathrm{aux}}=N\sum_{i=1}^N f_i P_i,\quad
P_i=\frac{1}{T}\sum_t P_{t,i},\quad
f_i=\frac{1}{T}\sum_t \mathbf{1}[i\in\mathrm{TopK}(t)].
$$

$f$ 对离散选择计数，对 logits 的梯度主要走 $P$。完全均匀时 $f_i=P_i=1/N$，$\mathcal{L}_{\mathrm{aux}}=1$。

## 实现要点

- **Ties**：`topk` 在分数相等时不稳定，应用唯一次序（加极小噪声或稳定 sort）。
- **Capacity**：真正 dispatch 时还要截断到 $C$；aux 统计的是「想选谁」，容量截断是系统层，别混进这一行公式。
- **DeepSeek 无辅助**：选择用 `sigmoid(score)+bias` 的 top-$k$，gates 用未加 bias 的分数；本题若追问，说 aux 被 bias 控制器替换，见 `arch-moe-noaux`。

```python
import torch
import torch.nn.functional as F

def moe_router_aux(x, W_r, k=1):
    # x: [T, d], W_r: [d, N]
    logits = x @ W_r
    P = F.softmax(logits, dim=-1)
    T, N = P.shape
    val, idx = torch.topk(P, k, dim=-1)
    gates = val / val.sum(dim=-1, keepdim=True)
    chosen = torch.zeros_like(P)
    chosen.scatter_(1, idx, 1.0)
    f = chosen.mean(dim=0)
    P_bar = P.mean(dim=0)
    aux = N * (f * P_bar).sum()
    return idx, gates, aux
```

## 追问

- **$f$ 要不要 detach？** Switch 原文 $f$ 当经验频率；实现里常对 one-hot 用 STE 或直接当常数。我会说「$f$ 统计负载，$P$ 可导」即可。
- **和 CE 怎么加？** $\mathcal{L}=\mathcal{L}_{\mathrm{LM}}+\lambda\mathcal{L}_{\mathrm{aux}}$，$\lambda$ 过大伤语义路由。
- **测什么？** 均匀输入下 $f$ 应接近 $1/N$；构造一个 expert 分数恒大的输入，aux 应明显大于 1。
