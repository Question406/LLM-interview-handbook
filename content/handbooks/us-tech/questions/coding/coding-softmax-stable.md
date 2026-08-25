---
id: coding-softmax-stable
section: coding
order: 1
level: S
title: 白板：数值稳定 softmax，为什么减 max，轴怎么选
quick: >-
  沿分类轴减该轴 max 再 exp、归一化。减 max 不改变 softmax，但让指数落在 $(0,1]$，避免 overflow。轴必须和「谁跟谁比概率」一致：分类是最后一维，注意力是 key 长。
tags:
  - Coding
  - Softmax
  - OpenAI
  - Numerical Stability
realInterview: false
status: published
format: markdown
updatedAt: 2026-08-23
sources:
  - title: torch.nn.functional.softmax
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.softmax.html
    type: primary
  - title: scaled_dot_product_attention
    url: https://pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html
    type: primary
---

## 题怎么来的

OpenAI / Apple / Meta 的 ML coding 几乎都会碰到 softmax：手写一层、改带 bug 的 Transformer、或者算 entropy。公开 debug 卷里最常见的植入就是 **轴写错** 和 **直接 `exp` 溢出**。生产路径已经走 `scaled_dot_product_attention`，但白板要你能把 fused kernel 里那步拆开。相关真题形态见 `openai-transformer-debug`、`openai-entropy-l1`。

## 减 max：平移不变，数值不炸

$$
\mathrm{softmax}(z)_i=\frac{e^{z_i}}{\sum_j e^{z_j}}=\frac{e^{z_i-m}}{\sum_j e^{z_j-m}},\quad m=\max_j z_j.
$$

减的是**同一条比较轴上的 max**，不是整个 tensor 一个标量。$e^{z-m}\in(0,1]$，fp16 里原始 logits 到几十就会 `inf`，一归一化全是 NaN。减 max 不改分布，只改中间量级。

我会主动写 `keepdims=True`：否则 `[B, T]` 的 max 对不上 `[B, T, D]`，NumPy 会 silent 广播到错误的轴。

```python
import numpy as np

def softmax(x, axis=-1):
    x = np.asarray(x, dtype=np.float64)
    m = np.max(x, axis=axis, keepdims=True)
    z = np.exp(x - m)
    return z / np.sum(z, axis=axis, keepdims=True)


def log_softmax(x, axis=-1):
    x = np.asarray(x, dtype=np.float64)
    z = x - np.max(x, axis=axis, keepdims=True)
    return z - np.log(np.sum(np.exp(z), axis=axis, keepdims=True))


if __name__ == "__main__":
    a = np.array([[1.0, 2.0, 3.0], [1000.0, 1000.0, 1001.0]])
    p = softmax(a, axis=-1)
    assert np.allclose(p.sum(axis=-1), 1.0)
    assert np.all(np.isfinite(p))
```

后续要接交叉熵时优先留 `log_softmax`，不要先 softmax 再 `log`，见 `coding-cross-entropy`。

## 轴：谁和谁抢概率

Shape 先写死再选 `axis`：

- 分类 logits `[B, T, V]`：沿 $V$。
- 注意力 scores `[B, H, T, S]`：沿 key 长 $S$，也就是最后一维。`dim=0` 或沿 head 是 OpenAI 卷里的经典 bug。
- 不要对整个 batch 减同一个 max：那不是 softmax 的平移不变，只是碰巧没炸。

Mask 必须在 softmax **之前**打成 $-\infty$，不能打 $0$。$0$ 仍吃正质量。全位置都是 $-\infty$ 时 max 是 $-\infty$，`exp` 变 NaN，要先检查有没有有限值。温度 $z/T$ 也在 softmax 之前，顺序见 `coding-topk-nucleus`。

NVIDIA 口味会追：reduction 沿最后一维才能走 warp 连续读写；轴在中间会多一次 transpose。白板先写对，再提 fused SDPA 把 mask、scale、softmax 糊在一块。

## 追问

- **为什么不能对整个 batch 减一个标量？** 平移必须发生在每条分布自己的轴上。全局 max 只是运气好没 overflow，语义已经偏了。
- **fp16 还要升精度吗？** 减 max 之后多数情况够。极端 logits 或 entropy 这种 reduction，我会把这一步放到 fp32，再 cast 回去。
- **和 log-sum-exp 的关系？** $\log\sum e^{z}=m+\log\sum e^{z-m}$。softmax 的分母就是它；CE 直接吃 log-sum-exp，不必物化 $p$。
