---
id: coding-online-softmax
section: coding
order: 15
level: S
title: 白板：FlashAttention 的 online softmax，两遍归约怎么写
quick: >-
  朴素 softmax 要对分数扫三遍：max、$\sum\exp$、再除。Online 把 max 和 sumexp
  合成一遍流式归约，第二遍才归一化。FlashAttention 用同一套递推去 rescale 已写出的
  $O$，分数矩阵不必落 HBM。单 tile 自己做 softmax 是错的。
tags:
  - Coding
  - Softmax
  - FlashAttention
  - NVIDIA
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: FlashAttention — Fast and Memory-Efficient Exact Attention with IO-Awareness
    url: https://arxiv.org/abs/2205.14135
    type: primary
  - title: Online normalizer calculation for softmax
    url: https://arxiv.org/abs/1805.02867
    type: primary
  - title: FlashAttention-2 — Faster Attention with Better Parallelism and Work Partitioning
    url: https://arxiv.org/abs/2307.08691
    type: primary
---

## 题怎么来的

NVIDIA / OpenAI 的 kernel 白板不让你背 fused kernel 名字，要你把 softmax 的归约拆开。Dao et al. 的 FlashAttention 把 Milakov 的 online softmax 嵌进 SRAM tiling：分数 `[T, S]` 从不写回 HBM。IO 账见 `nvidia-flash-attn`。稳定但物化全表的写法见 `coding-softmax-stable`。要说清：为什么不能对每个 K 块单独 softmax，以及 running max 变了以后旧输出怎么乘回去。

## 三遍、两遍、online

对一行 logits $x\in\mathbb{R}^{S}$：

$$
m=\max_j x_j,\quad
\ell=\sum_j e^{x_j-m},\quad
p_j=e^{x_j-m}/\ell.
$$

三遍：先 max，再 sumexp，再除。两遍归约是把后两步合成「带着 $m$ 做一次 $\sum\exp$ + 写出 $p$」，仍要整行都在。Online 是流式维护 $(m,\ell)$：

$$
m_i=\max(m_{i-1},x_i),\quad
\ell_i=e^{m_{i-1}-m_i}\ell_{i-1}+e^{x_i-m_i}.
$$

扫完 $m_S,\ell_S$ 就是全局 max 和 sumexp，和两遍数学等价。第二遍 $p_i=\exp(x_i-m_S)/\ell_S$。注意力不需要物化 $p$：把这块 $p$ 乘 $V$，max 更新时把已有输出乘 $e^{m_{\mathrm{old}}-m_{\mathrm{new}}}$。

```python
import numpy as np

def online_stats(x):
    m, ell = -np.inf, 0.0
    for xi in np.asarray(x, dtype=np.float64):
        m2 = max(m, xi)
        ell = ell * np.exp(m - m2) + np.exp(xi - m2)
        m = m2
    return m, ell

def softmax_from_stats(x, m, ell):
    return np.exp(np.asarray(x, dtype=np.float64) - m) / ell

def online_attn_row(q, k, v, scale, tile=16):
    # q: [D], k,v: [S, D]；按 K 块扫，O 在线 rescale
    s_len, d = k.shape
    m, ell = -np.inf, 0.0
    o = np.zeros(d, dtype=np.float64)
    for j in range(0, s_len, tile):
        s = (k[j : j + tile] @ q) * scale
        m2 = max(m, float(np.max(s)))
        p = np.exp(s - m2)
        alpha = np.exp(m - m2)
        o = o * alpha + p @ v[j : j + tile]
        ell = ell * alpha + float(p.sum())
        m = m2
    return o / ell
```

单测：`online_stats` 对上 `x.max()` 和 `exp(x-m).sum()`；`online_attn_row` 对上 `(softmax(scale K q) @ V)`。对不上就是 rescale 漏乘。

## Tile 上不能各自归一化

FlashAttention 外层沿 $K,V$ 块走。块 $j$ 的局部 $\mathrm{softmax}(Q K_j^\top)$ 的分母不是全局 $\ell$，权重对不上后面的块，结果不是精确注意力。必须保留行上的 $(m,\ell,O)$，新块只提供增量。因果 mask 在 tile 内打 $-\infty$，全 $-\infty$ 的行 $\ell=0$，要跳过或先看有没有有限值，否则 $O/\ell$ 是 NaN。

Decode 时 $T_q=1$，分数已经是 `[1, S]`，online 省的是不写 $S$，但墙钟多半在读 KV cache，和 prefill 的 $T^2$ IO 不是同一笔。白板先写对递推，再提这句。

## 追问

- **和减 max 的稳定 softmax 什么关系？** 每一步减的是当前 running max，不是最后的全局 max；用 $e^{m_{\mathrm{old}}-m_{\mathrm{new}}}$ 把旧的 $\ell$ 和 $O$ 变到新标尺上，等价于从头减全局 max。
- **为什么 FlashAttention 还要第二遍的味道？** 统计 $m,\ell$ 可以一遍扫完；写出归一化后的 $P$ 仍要 $x$。注意力把「第二遍」融进 $PV$，训练再在反向重算。
- **fp16 的 $\ell$ 要不要升精度？** 要。running sumexp 和 rescale 系数放 fp32，和 `coding-softmax-stable` 同一条。
- **块内先 softmax 再加权平均能凑合吗？** 不能。那是错误的归一化，不是近似 FlashAttention。
