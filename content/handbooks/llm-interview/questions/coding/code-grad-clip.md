---
id: code-grad-clip
section: coding
order: 43
level: A
title: 手写 global-norm 梯度裁剪：总 L2、缩放系数、遇到 inf/nan 怎么办
quick: >-
  把所有参数梯度的 L2 拼成一个标量
  $n=\sqrt{\sum\|g_i\|_2^2}$。$n>\texttt{max\_norm}$ 时每个梯度乘 $\texttt{max\_norm}/(n+\varepsilon)$，否则不动。$n$
  非有限就把梯度清零并跳过这一 step，不要用 NaN 去除法。AMP 下必须先 unscale 再量 $n$。
tags:
  - GradClip
  - Training
  - Coding
realInterview: false
status: published
format: markdown
updatedAt: 2026-09-28
sources:
  - title: On the difficulty of training Recurrent Neural Networks
    url: https://arxiv.org/abs/1211.5063
    type: primary
---

面试常和 AMP 连问。常见误区是：按参数各自 clip（那是 clip-by-value / per-tensor）；或先 clip 再 unscale，阈值和真实 $n$ 差一个 scale。Llama 常见 `max_grad_norm=1.0`。

## 总范数

$$
n=\Big(\sum_{p\in\theta}\|g_p\|_2^2\Big)^{1/2},\qquad
g_p\leftarrow g_p\cdot\min\Big(1,\frac{\texttt{max\_norm}}{n+\varepsilon}\Big).
$$

$n$ 是标量，所有张量共用一个系数。`stack` 各张量自己的 `norm` 再对外层 `norm`，和把全部元素 flatten 再 norm 一样。

```python
import torch

def clip_grad_norm_(params, max_norm):
    grads = [p.grad for p in params if p.grad is not None]
    if not grads:
        return torch.tensor(0.0)
    total = torch.norm(torch.stack([g.detach().float().norm(2) for g in grads]), 2)
    if not torch.isfinite(total):
        for g in grads:
            g.zero_()
        return total
    scale = (max_norm / (total + 1e-6)).clamp(max=1.0)
    for g in grads:
        g.mul_(scale)
    return total
```

`n` 非有限时清梯度：这一 step 的 Adam 状态不要被 inf 写脏。AMP 的做法是先 `unscale_`，再 clip，再看有没有 inf 决定要不要 `step` / 降 scale，见 `code-grad-accum-amp`。

## 追问

- **为什么不用 per-layer clip？** 层之间的相对比例会被改掉。global norm 只缩放步长。
- **和 clip-by-value？** `clamp(-c,c)` 改方向。global norm 只改长度。
- **FSDP / ZeRO 下 $n$ 怎么算？** 各 rank 先算本地平方和，再 all-reduce 再开方。手写单卡即可，要提这一句。
