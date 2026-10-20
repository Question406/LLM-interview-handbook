---
id: code-softmax-stable
section: coding
order: 40
level: A
title: 手写数值稳定 Softmax：减 max、全 mask 行、以及和 CE 的关系
quick: "沿计算轴先减最大值再 $\\exp$ 和归一化，分布不变，指数落在 $(0,1]$ 不会上溢。整行被 mask 成 $-\\infty$ 会出 NaN，要把这一行概率置 0。"
tags:
  - Softmax
  - Numerics
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: Deep Learning (Goodfellow et al.), §4.1 / softmax overflow
    url: https://www.deeplearningbook.org/contents/numerical.html
    type: primary
---

白板最常写错两处：直接 `exp(x)` 再除；以及 causal / padding 把一整行打成 $-\infty$ 之后还去 softmax。Attention 的分数矩阵见 `code-attention`，交叉熵见 `pdd-ce-handwrite`。

## 公式

$$
\mathrm{softmax}(x)_i=\frac{e^{x_i-m}}{\sum_j e^{x_j-m}},\qquad m=\max_j x_j.
$$

$m$ 是当前计算轴上的最大值。Attention 沿 key 维计算，将 `[B,H,T,S]` 归约为 `[B,H,T,1]`。减 $m$ 之后最大项是 $e^0=1$，其余 $\le 1$，fp16 下不容易上溢。

全 mask 行：$x_i=-\infty$ 对所有 $i$，于是 $m=-\infty$，$x-m$ 是 NaN。逐 token 生成（decode）遇到左 padding，或滑动窗口排除了所有可见 key 时，就可能出现这种情况。工程上把那一行概率写成 0，残差才不会被 NaN 污染。

```python
import torch

def softmax_stable(x, dim=-1, mask=None):
    # mask: True=keep。全被挡住的行压成 0，避免 NaN。
    if mask is not None:
        x = x.masked_fill(~mask, float("-inf"))
    z = x.float()
    z = z - z.amax(dim=dim, keepdim=True)
    p = torch.exp(z)
    p = p / p.sum(dim=dim, keepdim=True)
    return p.nan_to_num(0.0).to(x.dtype)
```

和交叉熵：$\ell=-z_y+\mathrm{logsumexp}(z)$，不要先 softmax 再 `log`。`logsumexp` 内部也是减 max。FlashAttention 的 online 版本把 max 和 sum 拆成递推，见 `code-flash-attn-fwd`。

## 追问

- **减 max 改分布吗？** 分子分母同乘 $e^{-m}$，分布不变。
- **为什么常转 fp32？** 低精度下 $e^{x-m}$ 的小项容易下溢成 0，累加时这种误差会更明显，因此常先用 fp32 计算，再转回原来的类型。
- **和 temperature？** 先 $z/T$ 再走上面这段。$T\to 0$ 不要真除 0，直接 argmax。顺序见 `code-sampling`。
