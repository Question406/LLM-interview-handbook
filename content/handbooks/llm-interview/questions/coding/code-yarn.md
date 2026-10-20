---
id: code-yarn
section: coding
order: 49
level: A
title: 手写 NTK-aware / YaRN：哪些频率内插、哪些外推
quick: "NTK-aware 只把 RoPE 基频改成 $\\theta'=\\theta\\cdot s^{d/(d-2)}$。YaRN 按波长分段：高频维不动（外推），低频维 inv_freq 除以 $s$（内插），中间用 ramp 过渡。"
tags:
  - YaRN
  - RoPE
  - LongContext
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: "YaRN: Efficient Context Window Extension of Large Language Models"
    url: https://arxiv.org/abs/2309.00071
    type: primary
---

线性插值（PI）是 `pos / s` 再查原表，高频被压得太狠，近距离 token 的相对位置更难区分。NTK / YaRN 改频率本身。基础 RoPE 见 `code-rope`。

## 两种改法

NTK-aware（先写这个，公式短）：

$$
\theta'=\theta\cdot s^{d/(d-2)}.
$$

YaRN 对第 $i$ 个二维对（$i=0,2,\ldots,d-2$）算一个 ramp $r_i\in[0,1]$：波长短的 $r=0$（外推），波长长的 $r=1$（内插）。

$$
\omega_i'=\omega_i\big/ s^{r_i},\qquad \omega_i=\theta^{-2i/d}.
$$

论文用 $\beta_{\mathrm{fast}}=32$、$\beta_{\mathrm{slow}}=1$ 划界。还会乘一个 attention 温度 $m_{\mathrm{scale}}$，手写可以先不加。

```python
import torch

def ntk_base(base, scale, dh):
    return base * scale ** (dh / (dh - 2))

def yarn_ramp(dim_idx, dh, beta_fast=32.0, beta_slow=1.0):
    # 0=外推，1=内插
    inv_dim = dim_idx / dh
    lo, hi = 1.0 / beta_fast, 1.0 / beta_slow
    return ((inv_dim - lo) / (hi - lo)).clamp(0, 1)

def yarn_inv_freq(dh, scale, base=10000.0):
    dim_idx = torch.arange(0, dh, 2).float()
    inv = 1.0 / (base ** (dim_idx / dh))
    ramp = yarn_ramp(dim_idx, dh)
    return inv / (scale ** ramp)
```

$\cos(t\omega')$ 仍按绝对位置 $t$ 建表。KV cache 里的 $K$ 在写入时已经用当时的 $\omega'$ 转过；换 scale 等于换位置编码，旧 cache 不能直接复用。

## 追问

- **scale=1 呢？** ramp 无所谓，`s^r=1`，退回原 RoPE。
- **和 ALiBi？** ALiBi 不改 $Q,K$，外推靠相对距离 bias，见 `code-alibi`。YaRN 是 RoPE 模型的续训手段。
- **只改 $\theta$ 算 YaRN 吗？** 那是 NTK-aware。YaRN 多了分段 ramp 和 $m_{\mathrm{scale}}$。
